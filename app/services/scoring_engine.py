from typing import Dict, List, Tuple, Any
from app.schemas.eligibility import EligibilityAssessmentInput, RecommendationDetail, Recommendation
from app.core.scoring_config import (
    CATEGORY_WEIGHTS, EDUCATION_CRITERIA, EXPERIENCE_CRITERIA,
    ACHIEVEMENTS_CRITERIA, RECOGNITION_CRITERIA, VIABILITY_THRESHOLDS,
    STRENGTH_THRESHOLD, WEAKNESS_THRESHOLD, STEM_HIGH_DEMAND_FIELDS,
    STEM_GENERAL_FIELDS, MAX_RECOMMENDATIONS
)
from app.core.logging import scoring_logger, log_structured_data, log_metric, get_request_id, eligibility_logger
import time
from datetime import datetime
import uuid


class ScoringEngine:
    """
    Implementação do algoritmo de scoring conforme especificado na documentação.
    Esta classe foi refatorada para usar configurações centralizadas e logs.
    """
    
    def __init__(self):
        # Pesos das categorias principais
        self.category_weights = CATEGORY_WEIGHTS
        
        # Critérios de pontuação
        self.education_criteria = EDUCATION_CRITERIA
        self.experience_criteria = EXPERIENCE_CRITERIA
        self.achievements_criteria = ACHIEVEMENTS_CRITERIA
        self.recognition_criteria = RECOGNITION_CRITERIA
        
        # Limiares
        self.viability_thresholds = VIABILITY_THRESHOLDS
        self.strength_threshold = STRENGTH_THRESHOLD
        self.weakness_threshold = WEAKNESS_THRESHOLD
        
        # Campos STEM
        self.stem_high_demand_fields = STEM_HIGH_DEMAND_FIELDS
        self.stem_general_fields = STEM_GENERAL_FIELDS
        
        scoring_logger.info("ScoringEngine inicializado com configurações")
    
    def calculate_education_score(self, education_data: Dict) -> float:
        """Calcula a pontuação para educação."""
        log_structured_data(scoring_logger, "info", 
                           f"Calculando score de educação", 
                           {"education_data": education_data})
        
        # Pontuação para grau acadêmico
        degree_score = 0.0
        if education_data["highest_degree"] == "PHD":
            degree_score = self.education_criteria["degree"]["scores"]["PHD"]
        elif education_data["highest_degree"] == "MASTERS":
            degree_score = self.education_criteria["degree"]["scores"]["MASTERS"]
        elif education_data["highest_degree"] == "BACHELORS":
            degree_score = self.education_criteria["degree"]["scores"]["BACHELORS"]
        else:
            degree_score = self.education_criteria["degree"]["scores"]["OTHER"]
        
        # Determinar score da instituição baseado no ranking
        institution_score = 0.0
        if education_data.get("university_ranking"):
            if education_data["university_ranking"] <= 50:
                institution_score = self.education_criteria["institution"]["scores"]["TOP_50"]
            elif education_data["university_ranking"] <= 200:
                institution_score = self.education_criteria["institution"]["scores"]["TOP_200"]
            else:
                institution_score = self.education_criteria["institution"]["scores"]["NATIONAL"]
        else:
            institution_score = self.education_criteria["institution"]["scores"]["OTHER"]
        
        # Determinar relevância do campo 
        field = education_data["field_of_study"].lower()
        field_score = 0.0
        
        if any(stem in field for stem in self.stem_high_demand_fields):
            field_score = self.education_criteria["field_relevance"]["scores"]["STEM_HIGH_DEMAND"]
        elif any(stem in field for stem in self.stem_general_fields):
            field_score = self.education_criteria["field_relevance"]["scores"]["STEM_GENERAL"]
        elif any(art in field for art in ["art", "business", "humanities", "social"]):
            field_score = self.education_criteria["field_relevance"]["scores"]["ARTS_BUSINESS_HUMANITIES_NICHE"]
        else:
            field_score = self.education_criteria["field_relevance"]["scores"]["OTHER"]
        
        # Calcular score final de educação com pesos
        final_education_score = (
            degree_score * self.education_criteria["degree"]["weight"] +
            institution_score * self.education_criteria["institution"]["weight"] +
            field_score * self.education_criteria["field_relevance"]["weight"]
        )
        
        # Para BACHELORS, ajustar o score para estar entre 0.4 e 0.7
        if education_data["highest_degree"] == "BACHELORS":
            final_education_score = min(0.65, max(0.45, final_education_score))
        
        log_structured_data(scoring_logger, "info", 
                           f"Score final de educação: {final_education_score}", 
                           {"degree_score": degree_score, 
                            "institution_score": institution_score,
                            "field_score": field_score})
        
        return final_education_score
    
    def calculate_experience_score(self, experience_data: Dict) -> float:
        """Calcula a pontuação para experiência profissional."""
        log_structured_data(scoring_logger, "info", 
                           f"Calculando score de experiência", 
                           {"experience_data": experience_data})
        
        # Pontuação para anos de experiência
        years_score = 0.0
        years = experience_data["years_of_experience"]
        
        if years >= 10:
            years_score = self.experience_criteria["years"]["scores"]["10+"]
        elif 7 <= years <= 9:
            years_score = self.experience_criteria["years"]["scores"]["7-9"]
        elif 4 <= years <= 6:
            years_score = self.experience_criteria["years"]["scores"]["4-6"]
        elif 1 <= years <= 3:
            years_score = self.experience_criteria["years"]["scores"]["1-3"]
        else:
            years_score = self.experience_criteria["years"]["scores"]["<1"]
        
        # Pontuação para liderança (simplificado)
        leadership_score = 0.0
        if experience_data["leadership_roles"]:
            leadership_score = self.experience_criteria["leadership"]["scores"]["MANAGER"]
        else:
            leadership_score = self.experience_criteria["leadership"]["scores"]["NONE"]
        
        # Pontuação para especialização
        specialization_score = 0.0
        if experience_data["specialized_experience"]:
            specialization_score = self.experience_criteria["specialization"]["scores"]["GENERAL_SPECIALIST"]
        else:
            specialization_score = self.experience_criteria["specialization"]["scores"]["GENERALIST"]
        
        # Calcular score final de experiência com pesos
        final_experience_score = (
            years_score * self.experience_criteria["years"]["weight"] +
            leadership_score * self.experience_criteria["leadership"]["weight"] +
            specialization_score * self.experience_criteria["specialization"]["weight"]
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score final de experiência: {final_experience_score}", 
                           {"years_score": years_score, 
                            "leadership_score": leadership_score,
                            "specialization_score": specialization_score})
        
        return final_experience_score
    
    def calculate_achievements_score(self, achievements_data: Dict) -> float:
        """Calcula a pontuação para realizações."""
        log_structured_data(scoring_logger, "info", 
                           f"Calculando score de realizações", 
                           {"achievements_data": achievements_data})
        
        # Pontuação para publicações
        publications_score = 0.0
        pub_count = achievements_data["publications_count"]
        
        if pub_count >= 10:
            publications_score = self.achievements_criteria["publications"]["scores"]["10+"]
        elif 5 <= pub_count <= 9:
            publications_score = self.achievements_criteria["publications"]["scores"]["5-9"]
        elif 1 <= pub_count <= 4:
            publications_score = self.achievements_criteria["publications"]["scores"]["1-4"]
        else:
            publications_score = self.achievements_criteria["publications"]["scores"]["0"]
        
        # Pontuação para patentes
        patents_score = 0.0
        patent_count = achievements_data["patents_count"]
        
        if patent_count >= 3:
            patents_score = self.achievements_criteria["patents"]["scores"]["3+"]
        elif 1 <= patent_count <= 2:
            patents_score = self.achievements_criteria["patents"]["scores"]["1-2"]
        else:
            patents_score = self.achievements_criteria["patents"]["scores"]["0"]
        
        # Pontuação para projetos liderados
        projects_score = 0.0
        projects_count = achievements_data["projects_led"]
        
        if projects_count >= 3:
            projects_score = self.achievements_criteria["projects"]["scores"]["HIGH_IMPACT_3+"]
        elif 1 <= projects_count <= 2:
            projects_score = self.achievements_criteria["projects"]["scores"]["SIGNIFICANT_1-2"]
        elif projects_count == 0 and achievements_data.get("notable_contributions"):
            projects_score = self.achievements_criteria["projects"]["scores"]["CONTRIBUTOR"]
        else:
            projects_score = self.achievements_criteria["projects"]["scores"]["NONE"]
        
        # Calcular score final de realizações com pesos
        final_achievements_score = (
            publications_score * self.achievements_criteria["publications"]["weight"] +
            patents_score * self.achievements_criteria["patents"]["weight"] +
            projects_score * self.achievements_criteria["projects"]["weight"]
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score final de realizações: {final_achievements_score}", 
                           {"publications_score": publications_score, 
                            "patents_score": patents_score,
                            "projects_score": projects_score})
        
        return final_achievements_score
    
    def calculate_recognition_score(self, recognition_data: Dict) -> float:
        """Calcula a pontuação para reconhecimento."""
        log_structured_data(scoring_logger, "info", 
                           f"Calculando score de reconhecimento", 
                           {"recognition_data": recognition_data})
        
        # Pontuação para prêmios
        awards_score = 0.0
        awards_count = recognition_data["awards_count"]
        
        if awards_count >= 3:
            awards_score = self.recognition_criteria["awards"]["scores"]["NATIONAL"]
        elif awards_count >= 1:
            awards_score = self.recognition_criteria["awards"]["scores"]["REGIONAL"]
        else:
            awards_score = self.recognition_criteria["awards"]["scores"]["NONE"]
        
        # Pontuação para palestras
        speaking_score = 0.0
        speaking_count = recognition_data["speaking_invitations"]
        
        if speaking_count >= 5:
            speaking_score = self.recognition_criteria["speaking"]["scores"]["SPEAKER_INTERNATIONAL"]
        elif speaking_count >= 2:
            speaking_score = self.recognition_criteria["speaking"]["scores"]["SPEAKER_NATIONAL"]
        elif speaking_count >= 1:
            speaking_score = self.recognition_criteria["speaking"]["scores"]["SPEAKER_LOCAL"]
        else:
            speaking_score = self.recognition_criteria["speaking"]["scores"]["NONE"]
        
        # Pontuação para afiliações
        memberships_score = 0.0
        memberships_count = recognition_data["professional_memberships"]
        
        if memberships_count >= 3:
            memberships_score = self.recognition_criteria["memberships"]["scores"]["ACTIVE_MEMBER"]
        elif memberships_count >= 1:
            memberships_score = self.recognition_criteria["memberships"]["scores"]["BASIC_MEMBER"]
        else:
            memberships_score = self.recognition_criteria["memberships"]["scores"]["NONE"]
        
        # Calcular score final de reconhecimento com pesos
        final_recognition_score = (
            awards_score * self.recognition_criteria["awards"]["weight"] +
            speaking_score * self.recognition_criteria["speaking"]["weight"] +
            memberships_score * self.recognition_criteria["memberships"]["weight"]
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score final de reconhecimento: {final_recognition_score}", 
                           {"awards_score": awards_score, 
                            "speaking_score": speaking_score,
                            "memberships_score": memberships_score})
        
        return final_recognition_score
    
    def calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calcula a pontuação geral com base nas pontuações por categoria."""
        overall_score = 0.0
        
        for category, score in category_scores.items():
            if category in self.category_weights:
                overall_score += score * self.category_weights[category]
        
        # Converter para escala 0-100
        overall_score *= 100
        
        log_structured_data(scoring_logger, "info", 
                           f"Score geral calculado: {overall_score}", 
                           {"category_scores": category_scores})
        
        # Registrar a métrica do score geral
        log_metric("eligibility.overall_score", overall_score)
        
        return overall_score
    
    def determine_viability_level(self, final_score: float) -> str:
        """
        Determina o nível de viabilidade da petição EB2-NIW com base na pontuação final.
        
        Args:
            final_score: Pontuação final EB2-NIW (0-100)
            
        Returns:
            Nível de viabilidade: "Excelente", "Boa", "Moderada", "Baixa", "Muito Baixa"
        """
        log_structured_data(scoring_logger, "info", 
                           "Determinando nível de viabilidade", 
                           {"final_score": final_score})
                           
        if final_score >= 85:
            return "EXCELLENT"
        elif final_score >= 70:
            return "STRONG"
        elif final_score >= 60:
            return "PROMISING"
        elif final_score >= 45:
            return "CHALLENGING"
        else:
            return "INSUFFICIENT"
    
    def identify_strengths(self, category_scores: Dict[str, float]) -> List[str]:
        """Identifica pontos fortes com base nas pontuações por categoria."""
        strengths = []
        
        # Verificar categorias com pontuação alta (acima do limiar de força)
        for category, score in category_scores.items():
            if score >= self.strength_threshold:
                if category == "education":
                    strengths.append("Formação acadêmica sólida em área relevante")
                elif category == "experience":
                    strengths.append("Experiência profissional significativa na área")
                elif category == "achievements":
                    strengths.append("Realizações notáveis que demonstram excelência")
                elif category == "recognition":
                    strengths.append("Reconhecimento significativo de seus pares e indústria")
        
        log_structured_data(scoring_logger, "info", 
                           f"Pontos fortes identificados: {len(strengths)}", 
                           {"strengths": strengths})
        
        return strengths
    
    def identify_weaknesses(self, category_scores: Dict[str, float]) -> List[str]:
        """Identifica pontos fracos com base nas pontuações por categoria."""
        weaknesses = []
        
        # Verificar categorias com pontuação baixa (abaixo do limiar de fraqueza)
        for category, score in category_scores.items():
            if score <= self.weakness_threshold:
                if category == "education":
                    weaknesses.append("Formação acadêmica insuficiente para os requisitos do visto")
                elif category == "experience":
                    weaknesses.append("Experiência profissional limitada ou não especializada")
                elif category == "achievements":
                    weaknesses.append("Realizações insuficientes para demonstrar excelência")
                elif category == "recognition":
                    weaknesses.append("Reconhecimento limitado na indústria ou meio acadêmico")
        
        log_structured_data(scoring_logger, "info", 
                           f"Pontos fracos identificados: {len(weaknesses)}", 
                           {"weaknesses": weaknesses})
        
        return weaknesses
    
    def generate_recommendations(self, 
                               assessment_input: EligibilityAssessmentInput,
                               category_scores: Dict[str, float],
                               eb2_route_eval: Dict[str, float],
                               niw_eval: Dict[str, float],
                               strengths: List[str],
                               weaknesses: List[str]) -> List[Dict[str, str]]:
        """
        Gera recomendações personalizadas com base na avaliação de elegibilidade.
        
        Args:
            assessment_input: Dados de entrada da avaliação
            category_scores: Pontuações por categoria
            eb2_route_eval: Avaliação das rotas EB2 (advanced_degree e exceptional_ability)
            niw_eval: Avaliação NIW (merit, well_positioned, waiver_benefit)
            strengths: Lista de pontos fortes identificados
            weaknesses: Lista de pontos fracos identificados
            
        Returns:
            Lista de recomendações, cada uma com tipo e descrição
        """
        recommendations = []
        
        # Analisar pontuações de categoria para gerar recomendações específicas
        for category, score in category_scores.items():
            if score < 60:  # Categoria com pontuação baixa
                if category == "education":
                    recommendations.append({
                        "type": "education_improvement",
                        "description": "Considere obter credenciais educacionais adicionais ou certificações relevantes para fortalecer seu perfil."
                    })
                elif category == "experience":
                    recommendations.append({
                        "type": "experience_enhancement",
                        "description": "Busque oportunidades para aumentar seu impacto profissional ou assumir papéis de liderança em sua área."
                    })
                elif category == "achievements":
                    recommendations.append({
                        "type": "achievement_development",
                        "description": "Foque em desenvolver publicações, patentes ou projetos significativos em sua área de especialização."
                    })
                elif category == "recognition":
                    recommendations.append({
                        "type": "recognition_building",
                        "description": "Procure reconhecimento externo através de prêmios, menções na mídia ou participação em conferências prestigiadas."
                    })
        
        # Recomendações específicas com base nas avaliações EB2 e NIW
        if niw_eval["merit"] < 65:
            recommendations.append({
                "type": "merit_improvement",
                "description": "Fortaleça evidências do seu mérito substancial na área de atuação com credenciais adicionais ou reconhecimento da indústria."
            })
            
        if niw_eval["well_positioned"] < 65:
            recommendations.append({
                "type": "national_benefit_focus",
                "description": "Desenvolva documentação que demonstre claramente como seu trabalho beneficia interesses nacionais dos EUA."
            })
            
        if niw_eval["waiver_benefit"] < 65:
            recommendations.append({
                "type": "waiver_justification",
                "description": "Fortaleça a justificativa de por que a isenção da oferta de trabalho é de interesse nacional."
            })
            
        # Adicione recomendação sobre qual rota EB2 priorizar
        if eb2_route_eval["advanced_degree"] > eb2_route_eval["exceptional_ability"]:
            if eb2_route_eval["advanced_degree"] < 70:
                recommendations.append({
                    "type": "degree_credential",
                    "description": "Fortaleça suas credenciais acadêmicas para maximizar suas chances pela rota de grau avançado."
                })
        else:
            if eb2_route_eval["exceptional_ability"] < 70:
                recommendations.append({
                    "type": "exceptional_ability_evidence",
                    "description": "Reúna evidências adicionais que demonstrem sua habilidade excepcional em sua área de atuação."
                })
        
        # Recomendação de consultoria se tiver muitas fraquezas
        if len(weaknesses) >= 3:
            recommendations.append({
                "type": "professional_guidance",
                "description": "Considere buscar orientação profissional de um advogado especializado em imigração para fortalecer seu caso."
            })
        
        # Recomendação de documentação
        recommendations.append({
            "type": "documentation_preparation",
            "description": "Prepare documentação completa e bem organizada que destaque suas realizações e o impacto do seu trabalho."
        })
        
        log_structured_data(scoring_logger, "info", 
                           "Recomendações geradas", 
                           {"recommendation_count": len(recommendations)})
                           
        return recommendations
    
    def generate_next_steps(self, viability_level: str) -> List[str]:
        """Gera os próximos passos recomendados com base no nível de viabilidade."""
        next_steps = []
        
        # Próximos passos comuns para todos os níveis
        next_steps.append("Complete seu perfil para receber uma avaliação mais detalhada")
        
        if viability_level in ["EXCELLENT", "STRONG", "PROMISING"]:
            next_steps.append("Carregue documentos de apoio para fortalecer seu caso")
            next_steps.append("Consulte um especialista para verificar sua estratégia")
        
        if viability_level in ["PROMISING", "CHALLENGING"]:
            next_steps.append("Siga as recomendações para fortalecer seu perfil antes de prosseguir")
            next_steps.append("Considere um plano de desenvolvimento profissional de longo prazo")
        
        if viability_level == "INSUFFICIENT":
            next_steps.append("Considere alternativas de imigração mais adequadas ao seu perfil atual")
            next_steps.append("Desenvolva um plano de 1-2 anos para fortalecer suas qualificações")
        
        log_structured_data(scoring_logger, "info", 
                           f"Próximos passos gerados: {len(next_steps)}", 
                           {"viability_level": viability_level})
        
        return next_steps
    
    def generate_personal_message(self, overall_score: float, viability_level: str) -> str:
        """Gera uma mensagem personalizada com base no score e nível de viabilidade."""
        if viability_level == "EXCELLENT":
            message = "Seu perfil é excepcionalmente forte para uma petição EB2-NIW. Você tem excelentes chances de sucesso."
        elif viability_level == "STRONG":
            message = "Seu perfil mostra forte potencial para uma petição EB2-NIW. Com algumas melhorias direcionadas, você poderia fortalecer seu caso ainda mais."
        elif viability_level == "PROMISING":
            message = "Seu perfil tem potencial para uma petição EB2-NIW, mas há áreas que precisam ser fortalecidas para maximizar suas chances."
        elif viability_level == "CHALLENGING":
            message = "Sua petição EB2-NIW pode enfrentar desafios. Recomendamos fortalecer significativamente seu perfil antes de prosseguir."
        else:
            message = "Seu perfil atual não parece ser ideal para uma petição EB2-NIW. Considere fortalecer suas qualificações ou explorar outras opções de imigração."
        
        log_structured_data(scoring_logger, "info", 
                           "Mensagem personalizada gerada", 
                           {"viability_level": viability_level})
        
        return message
    
    def process_assessment(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Processa a avaliação de elegibilidade e retorna o resultado completo.
        
        Args:
            input_data: Dados de entrada para avaliação
            
        Returns:
            Dicionário com o resultado completo da avaliação
        """
        start_time = time.time()
        request_id = get_request_id()
        eligibility_logger.info(f"Iniciando avaliação de elegibilidade", extra={"request_id": request_id})
        
        # Gerar um ID único para este assessment
        assessment_id = str(uuid.uuid4())
        
        # Calcular scores por categoria
        education_score = self.calculate_education_score(input_data.education.model_dump())
        experience_score = self.calculate_experience_score(input_data.experience.model_dump())
        achievements_score = self.calculate_achievements_score(input_data.achievements.model_dump())
        recognition_score = self.calculate_recognition_score(input_data.recognition.model_dump())
        
        # Armazenar scores das categorias em um dicionário para uso posterior
        category_scores = {
            "education": education_score,
            "experience": experience_score,
            "achievements": achievements_score,
            "recognition": recognition_score
        }
        
        # Calcular score geral baseado nos pesos das categorias
        overall_score = self.calculate_overall_score(category_scores)
        
        # Avaliar as rotas EB2 (Grau Avançado e Habilidade Excepcional)
        from app.services.eb2_route_evaluator import EB2RouteEvaluator
        eb2_evaluator = EB2RouteEvaluator()
        
        advanced_degree_score = eb2_evaluator.evaluate_advanced_degree_route(input_data)
        exceptional_ability_score = eb2_evaluator.evaluate_exceptional_ability_route(input_data)
        
        # Determinar a rota EB2 recomendada
        eb2_route_eval = eb2_evaluator.determine_recommended_route(
            advanced_degree_score, 
            exceptional_ability_score,
            input_data
        )
        
        # Avaliar os critérios NIW (Matter of Dhanasar)
        from app.services.niw_evaluator import NIWEvaluator
        niw_evaluator = NIWEvaluator()
        
        # Avaliação completa do NIW com os três critérios
        niw_evaluation = niw_evaluator.evaluate_niw(input_data)
        
        # Calcular score final baseado nas avaliações EB2 e NIW
        eb2_score = advanced_degree_score if eb2_route_eval["recommended_route"] == "ADVANCED_DEGREE" else exceptional_ability_score
        niw_score = niw_evaluation["niw_overall_score"]
        
        final_score = self.calculate_final_score(eb2_score, niw_score)
        
        # Determinar o nível de viabilidade
        viability_level = self.determine_viability_level(final_score)
        
        # Nível de viabilidade legado (para compatibilidade)
        viability_mapping = {
            "EXCELLENT": "Strong",
            "STRONG": "Good",
            "PROMISING": "Moderate",
            "CHALLENGING": "Moderate",
            "INSUFFICIENT": "Low"
        }
        viability = viability_mapping.get(viability_level, "Moderate")
        
        # Identificar pontos fortes e fracos
        strengths = self.identify_strengths(category_scores)
        weaknesses = self.identify_weaknesses(category_scores)
        
        # Gerar recomendações detalhadas
        from app.services.recommendation_engine import RecommendationEngine
        recommendation_engine = RecommendationEngine()
        
        detailed_recommendations = recommendation_engine.generate_detailed_recommendations(
            input_data,
            category_scores,
            eb2_route_eval,
            niw_evaluation
        )
        
        # Lista simplificada de recomendações (para compatibilidade)
        recommendations = [rec.description for rec in detailed_recommendations[:5]] 
        
        # Gerar próximos passos e mensagem personalizada
        next_steps = self.generate_next_steps(viability_level)
        message = self.generate_personal_message(final_score, viability_level)
        
        # Estimar tempo de processamento
        estimated_processing_time = 4
        if viability_level in ["EXCELLENT", "STRONG"]:
            estimated_processing_time = 12
        elif viability_level == "PROMISING":
            estimated_processing_time = 16
        else:
            estimated_processing_time = 20
        
        # Preparar o resultado
        result = {
            "id": assessment_id,
            "user_id": input_data.user_id,
            "created_at": datetime.now(),
            
            # Pontuações
            "score": {
                "education": education_score,
                "experience": experience_score,
                "achievements": achievements_score,
                "recognition": recognition_score,
                "overall": final_score
            },
            
            # Avaliação EB2
            "eb2_route": {
                "recommended_route": eb2_route_eval["recommended_route"],
                "advanced_degree_score": eb2_route_eval["advanced_degree_score"],
                "exceptional_ability_score": eb2_route_eval["exceptional_ability_score"],
                "route_explanation": eb2_route_eval["route_explanation"]
            },
            
            # Avaliação NIW
            "niw_evaluation": {
                "merit_importance_score": niw_evaluation["subcriteria"]["merit_importance_score"],
                "well_positioned_score": niw_evaluation["subcriteria"]["well_positioned_score"],
                "benefit_waiver_score": niw_evaluation["subcriteria"]["benefit_waiver_score"],
                "niw_overall_score": niw_evaluation["niw_overall_score"]
            },
            
            # Classificação
            "viability_level": viability_level,
            "viability": viability,
            "probability": final_score,
            
            # Feedback
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            
            # Recomendações detalhadas
            "detailed_recommendations": [rec.model_dump() for rec in detailed_recommendations],
            
            # Próximos passos e mensagem
            "next_steps": next_steps,
            "message": message,
            
            # Dados adicionais
            "estimated_processing_time": estimated_processing_time
        }
        
        # Registrar métricas e informações
        processing_time = time.time() - start_time
        log_metric("assessment_processing_time", processing_time)
        log_structured_data(
            eligibility_logger, 
            "info", 
            f"Avaliação de elegibilidade concluída em {processing_time:.2f}s", 
            {
                "request_id": request_id,
                "assessment_id": assessment_id,
                "overall_score": final_score,
                "viability_level": viability_level,
                "processing_time": processing_time
            }
        )
        
        return result
    
    def evaluate_advanced_degree_route(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia a elegibilidade na rota de Grau Avançado para EB2.
        
        Args:
            input_data: Dados de avaliação
            
        Returns:
            Pontuação da rota de Grau Avançado (0.0 a 1.0)
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando rota de Grau Avançado", 
                           {"education_data": input_data.education.model_dump()})
        
        score = 0.0
        
        # Verificar grau acadêmico
        if input_data.education.highest_degree == "PHD":
            score = 1.0
        elif input_data.education.highest_degree == "MASTERS":
            score = 0.9
        elif input_data.education.highest_degree == "BACHELORS":
            # Para bacharelado, considerar anos de experiência
            if input_data.experience.years_of_experience >= 7:
                score = 0.85
            elif input_data.experience.years_of_experience >= 5:
                score = 0.75
            else:
                score = 0.4
        else:
            score = 0.2
            
        log_structured_data(scoring_logger, "info", 
                           f"Score da rota de Grau Avançado: {score}")
        
        return score
        
    def evaluate_exceptional_ability_route(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia a elegibilidade na rota de Habilidade Excepcional para EB2.
        
        Args:
            input_data: Dados de avaliação
            
        Returns:
            Pontuação da rota de Habilidade Excepcional (0.0 a 1.0)
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando rota de Habilidade Excepcional")
        
        criteria_met = 0
        
        # 1. Grau acadêmico
        if input_data.education.highest_degree in ["PHD", "MASTERS"]:
            criteria_met += 1
            
        # 2. Experiência profissional (10+ anos)
        if input_data.experience.years_of_experience >= 10:
            criteria_met += 1
            
        # 3. Licença profissional ou certificações
        if input_data.education.professional_license or (hasattr(input_data.education, "certifications") and input_data.education.certifications):
            criteria_met += 1
            
        # 4. Salário elevado - Corrigindo verificação de None
        high_salary = False
        if input_data.experience.salary_level == "ABOVE_AVERAGE":
            high_salary = True
        elif input_data.experience.salary_percentile is not None and input_data.experience.salary_percentile > 75:
            high_salary = True
        
        # Verificar o campo current_salary de maneira segura
        current_salary = getattr(input_data, "current_salary", None)
        if current_salary is not None and current_salary > 100000:
            high_salary = True
            
        if high_salary:
            criteria_met += 1
            
        # 5. Membro de associações profissionais
        if input_data.recognition.professional_memberships >= 2:
            criteria_met += 1
            
        # 6. Reconhecimento por conquistas
        if input_data.recognition.awards_count >= 2 or input_data.achievements.publications_count >= 5:
            criteria_met += 1
            
        # Determinar score com base no número de critérios atendidos
        if criteria_met >= 5:
            score = 1.0
        elif criteria_met == 4:
            score = 0.9
        elif criteria_met == 3:
            score = 0.8
        elif criteria_met == 2:
            score = 0.6
        elif criteria_met == 1:
            score = 0.4
        else:
            score = 0.2
            
        log_structured_data(scoring_logger, "info", 
                           f"Score da rota de Habilidade Excepcional: {score}", 
                           {"criteria_met": criteria_met})
        
        return score
        
    def evaluate_niw_merit_importance(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia o critério de "mérito e importância nacional" do NIW.
        
        Args:
            input_data: Dados de avaliação
            
        Returns:
            Pontuação do critério (0.0 a 1.0)
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando critério NIW: mérito e importância nacional")
        
        score = 0.5  # Pontuação inicial neutra
        
        if hasattr(input_data, "us_plans") and input_data.us_plans:
            # Áreas consideradas de alta importância nacional
            high_importance_keywords = ["saúde", "medicina", "cibersegurança", "energia renovável", 
                                      "inteligência artificial", "segurança", "defesa", "biotecnologia",
                                      "health", "medicine", "cybersecurity", "renewable energy",
                                      "artificial intelligence", "security", "defense", "biotechnology"]
            
            # Verificar campo de trabalho e trabalho proposto
            field = input_data.us_plans.field_of_work.lower()
            proposed_work = input_data.us_plans.proposed_work.lower()
            importance = input_data.us_plans.national_importance.lower() if input_data.us_plans.national_importance else ""
            
            # Pontuação com base em áreas de alta importância
            if any(keyword in field or keyword in proposed_work or keyword in importance 
                  for keyword in high_importance_keywords):
                score += 0.3
                
            # Avaliar potenciais beneficiários
            if input_data.us_plans.potential_beneficiaries and len(input_data.us_plans.potential_beneficiaries) > 20:
                score += 0.1
                
            # Avaliar detalhamento da importância nacional
            if input_data.us_plans.national_importance and len(input_data.us_plans.national_importance) > 50:
                score += 0.1
                
        # Limitar score ao máximo de 1.0
        score = min(score, 1.0)
        
        log_structured_data(scoring_logger, "info", 
                           f"Score do critério NIW - mérito e importância: {score}")
        
        return score
        
    def evaluate_niw_well_positioned(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia o critério "bem posicionado" do NIW.
        
        Args:
            input_data: Dados de avaliação
            
        Returns:
            Pontuação do critério (0.0 a 1.0)
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando critério NIW: bem posicionado")
        
        score = 0.0
        factors = 0
        
        # Fator 1: Formação acadêmica
        if input_data.education.highest_degree == "PHD":
            score += 0.3
            factors += 1
        elif input_data.education.highest_degree == "MASTERS":
            score += 0.2
            factors += 1
            
        # Fator 2: Experiência relevante
        if input_data.experience.years_of_experience >= 10:
            score += 0.3
            factors += 1
        elif input_data.experience.years_of_experience >= 7:
            score += 0.25
            factors += 1
        elif input_data.experience.years_of_experience >= 4:
            score += 0.15
            factors += 1
            
        # Fator 3: Publicações, patentes ou projetos
        if input_data.achievements.publications_count >= 10:
            score += 0.3
            factors += 1
        elif input_data.achievements.publications_count >= 5 or input_data.achievements.patents_count >= 2:
            score += 0.25
            factors += 1
        elif input_data.achievements.publications_count >= 2 or input_data.achievements.patents_count >= 1:
            score += 0.15
            factors += 1
            
        # Fator 4: Reconhecimento profissional
        if input_data.recognition.awards_count >= 3 or input_data.recognition.speaking_invitations >= 5:
            score += 0.3
            factors += 1
        elif input_data.recognition.awards_count >= 2 or input_data.recognition.speaking_invitations >= 3:
            score += 0.25
            factors += 1
            
        # Normalizar score se tiver menos fatores
        if factors > 0:
            score = min(score, 1.0)
            
        log_structured_data(scoring_logger, "info", 
                           f"Score do critério NIW - bem posicionado: {score}", 
                           {"factors_contributing": factors})
        
        return score
        
    def evaluate_niw_waiver_benefit(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia o critério "benefício de dispensa" do NIW.
        
        Args:
            input_data: Dados de avaliação
            
        Returns:
            Pontuação do critério (0.0 a 1.0)
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando critério NIW: benefício de dispensa")
        
        score = 0.5  # Pontuação inicial neutra
        
        if hasattr(input_data, "us_plans") and input_data.us_plans:
            # Avaliar caso para dispensa do processo padrão
            if input_data.us_plans.standard_process_impracticality:
                impracticality = input_data.us_plans.standard_process_impracticality.lower()
                
                # Fatores que justificam a dispensa
                waiver_justifications = [
                    "conhecimentos especializados", "expertise única", "escassez", 
                    "specialized knowledge", "unique expertise", "shortage", 
                    "insufficient", "urgência", "urgency", "critical need",
                    "tempo limitado", "perda de oportunidade", "time constraints"
                ]
                
                if any(justification in impracticality for justification in waiver_justifications):
                    score += 0.3
                    
                # Detalhe da justificativa
                if len(impracticality) > 100:
                    score += 0.1
                    
            # Avaliar perfil de qualificação
            if input_data.education.highest_degree == "PHD" or input_data.experience.years_of_experience >= 10:
                score += 0.1
                
        # Limitar score ao máximo de 1.0
        score = min(score, 1.0)
        
        log_structured_data(scoring_logger, "info", 
                           f"Score do critério NIW - benefício de dispensa: {score}")
        
        return score
        
    def calculate_niw_score(self, merit_score: float, well_positioned_score: float, waiver_benefit_score: float) -> float:
        """
        Calcula a pontuação NIW combinando os três critérios com seus respectivos pesos.
        
        Args:
            merit_score: Pontuação do critério de mérito e importância nacional
            well_positioned_score: Pontuação do critério bem posicionado
            waiver_benefit_score: Pontuação do critério benefício de dispensa
            
        Returns:
            Pontuação NIW (0 a 1)
        """
        # Pesos para cada critério NIW
        merit_weight = 0.35
        well_positioned_weight = 0.35
        waiver_benefit_weight = 0.30
        
        # Calcular pontuação ponderada
        niw_score = (
            (merit_score * merit_weight) +
            (well_positioned_score * well_positioned_weight) +
            (waiver_benefit_score * waiver_benefit_weight)
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score NIW calculado: {niw_score}", 
                           {
                               "merit_score": merit_score,
                               "well_positioned_score": well_positioned_score,
                               "waiver_benefit_score": waiver_benefit_score
                           })
        
        return niw_score
    
    def calculate_final_score(self, eb2_score: float, niw_score: float) -> float:
        """
        Calcula a pontuação final EB2-NIW combinando as pontuações EB2 e NIW.
        
        Args:
            eb2_score: Pontuação da rota EB2 (maior entre Grau Avançado e Habilidade Excepcional)
            niw_score: Pontuação NIW combinada
            
        Returns:
            Pontuação final (0 a 100)
        """
        # Pesos para componentes principais
        eb2_weight = 0.4
        niw_weight = 0.6
        
        # Calcular pontuação ponderada
        final_score = (
            (eb2_score * eb2_weight) +
            (niw_score * niw_weight)
        )
        
        # Converter para escala percentual (0-100)
        final_percentage = final_score * 100
        
        log_structured_data(scoring_logger, "info", 
                           f"Score final EB2-NIW calculado: {final_percentage}%", 
                           {
                               "eb2_score": eb2_score,
                               "niw_score": niw_score
                           })
        
        return final_percentage
    
    def evaluate_eligibility(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia a elegibilidade EB2-NIW com base nos dados de entrada.
        Método para testes e compatibilidade.
        
        Args:
            input_data: Dados de entrada para avaliação
            
        Returns:
            Dicionário com resultados da avaliação
        """
        request_id = get_request_id()
        log_structured_data(scoring_logger, "info", 
                           "Iniciando avaliação de elegibilidade para testes", 
                           {"request_id": request_id})
                           
        # Calcular pontuações por categoria
        education_score = self.calculate_education_score(input_data.education.model_dump())
        experience_score = self.calculate_experience_score(input_data.experience.model_dump())
        achievements_score = self.calculate_achievements_score(input_data.achievements.model_dump())
        recognition_score = self.calculate_recognition_score(input_data.recognition.model_dump())
        
        # Compilar scores em um dicionário
        category_scores = {
            "education": education_score,
            "experience": experience_score,
            "achievements": achievements_score,
            "recognition": recognition_score
        }
        
        # Calcular score geral
        overall_score = self.calculate_overall_score(category_scores)
        
        # Determinar viabilidade
        viability_level = self.determine_viability_level(overall_score)
        
        # Identificar pontos fortes e fracos
        strengths = self.identify_strengths(category_scores)
        weaknesses = self.identify_weaknesses(category_scores)
        
        # Compilar resultados
        results = {
            "request_id": request_id,
            "overall_score": overall_score,
            "viability_level": viability_level,
            "category_scores": category_scores,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
        
        return results 