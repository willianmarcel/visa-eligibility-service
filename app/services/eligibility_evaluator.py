"""
Serviço principal de avaliação de elegibilidade para vistos EB2-NIW.
Integra todos os componentes de avaliação e fornece interface unificada.
"""

from typing import Dict, List, Any
from datetime import datetime
import uuid
import time

from app.schemas.eligibility import (
    EligibilityAssessmentInput, 
    EligibilityAssessmentOutput,
    EligibilityScore,
    EB2RouteEvaluation,
    NIWEvaluation,
    RecommendationDetail
)
from app.models.eligibility import QuickAssessment

from app.services.eb2_route_evaluator import EB2RouteEvaluator
from app.services.niw_evaluator import NIWEvaluator
from app.services.recommendation_engine import RecommendationEngine
from app.services.db_manager import DBManager

from app.core.logging import (
    eligibility_logger,
    log_structured_data, 
    log_metric, 
    get_request_id
)
from app.core.eligibility_config import (
    CATEGORY_WEIGHTS, 
    STRENGTH_THRESHOLD, 
    WEAKNESS_THRESHOLD, 
    VIABILITY_THRESHOLDS,
    PERSONAL_MESSAGES,
    PROCESSING_TIME_ESTIMATES
)


class EligibilityEvaluator:
    """
    Serviço principal para avaliação de elegibilidade para vistos EB2-NIW.
    
    Esta classe orquestra o processo completo de avaliação, integrando os diferentes
    componentes de avaliação (EB2, NIW) e gerando resultados detalhados com recomendações.
    """
    
    def __init__(self):
        """Inicializa o avaliador de elegibilidade com seus subcomponentes."""
        # Inicializar avaliadores específicos
        self.eb2_evaluator = EB2RouteEvaluator()
        self.niw_evaluator = NIWEvaluator()
        self.recommendation_engine = RecommendationEngine()
        self.db_manager = DBManager()
        
        # Pesos das categorias principais - usa configuração centralizada
        self.category_weights = CATEGORY_WEIGHTS
        
        # Limiares para pontos fortes e fracos - usa configuração centralizada
        self.strength_threshold = STRENGTH_THRESHOLD
        self.weakness_threshold = WEAKNESS_THRESHOLD
        
        eligibility_logger.info("EligibilityEvaluator inicializado com todos os subcomponentes")
    
    def calculate_category_scores(self, input_data: EligibilityAssessmentInput) -> Dict[str, float]:
        """
        Calcula as pontuações para cada categoria principal.
        
        Args:
            input_data: Dados da avaliação
            
        Returns:
            Dicionário com pontuações por categoria
        """
        # Calcular score de educação
        education_score = 0.0
        if input_data.education.highest_degree == "PHD":
            education_score = 0.9
        elif input_data.education.highest_degree == "MASTERS":
            education_score = 0.7
        elif input_data.education.highest_degree == "BACHELORS":
            education_score = 0.5
        else:
            education_score = 0.3
            
        # Ajustar score com base em outros fatores
        if input_data.education.university_ranking and input_data.education.university_ranking <= 50:
            education_score = min(1.0, education_score + 0.1)
            
        # Calcular score de experiência
        experience_score = 0.0
        years = input_data.experience.years_of_experience
        
        if years >= 10:
            experience_score = 0.8
        elif years >= 7:
            experience_score = 0.7
        elif years >= 5:
            experience_score = 0.6
        elif years >= 3:
            experience_score = 0.5
        else:
            experience_score = 0.3
            
        # Ajustar com base em liderança e especialização
        if input_data.experience.leadership_roles:
            experience_score = min(1.0, experience_score + 0.1)
            
        if input_data.experience.specialized_experience:
            experience_score = min(1.0, experience_score + 0.1)
            
        # Calcular score de realizações
        achievements_score = 0.0
        
        # Base inicial de pontuação
        base_score = 0.3
        
        # Pontuação por publicações
        pub_count = input_data.achievements.publications_count
        if pub_count >= 10:
            base_score += 0.3
        elif pub_count >= 5:
            base_score += 0.2
        elif pub_count >= 1:
            base_score += 0.1
            
        # Pontuação por patentes
        patent_count = input_data.achievements.patents_count
        if patent_count >= 3:
            base_score += 0.2
        elif patent_count >= 1:
            base_score += 0.1
            
        # Pontuação por projetos liderados
        projects_led = input_data.achievements.projects_led
        if projects_led >= 3:
            base_score += 0.2
        elif projects_led >= 1:
            base_score += 0.1
            
        # Normalizar para máximo de 1.0
        achievements_score = min(1.0, base_score)
            
        # Calcular score de reconhecimento
        recognition_score = 0.0
        
        # Base inicial de pontuação
        base_score = 0.3
        
        # Pontuação por prêmios
        awards_count = input_data.recognition.awards_count
        if awards_count >= 3:
            base_score += 0.3
        elif awards_count >= 1:
            base_score += 0.2
            
        # Pontuação por palestras
        speaking_count = input_data.recognition.speaking_invitations
        if speaking_count >= 5:
            base_score += 0.2
        elif speaking_count >= 2:
            base_score += 0.1
            
        # Pontuação por afiliações
        memberships_count = input_data.recognition.professional_memberships
        if memberships_count >= 2:
            base_score += 0.2
        elif memberships_count >= 1:
            base_score += 0.1
            
        # Normalizar para máximo de 1.0
        recognition_score = min(1.0, base_score)
        
        # Retornar dicionário com todos os scores
        category_scores = {
            "education": education_score,
            "experience": experience_score,
            "achievements": achievements_score,
            "recognition": recognition_score
        }
        
        log_structured_data(eligibility_logger, "info", 
                           "Scores por categoria calculados", 
                           {"category_scores": category_scores})
        
        return category_scores
    
    def calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """
        Calcula a pontuação geral com base nas pontuações por categoria.
        
        Args:
            category_scores: Pontuações por categoria
            
        Returns:
            Pontuação geral (0-1)
        """
        overall_score = 0.0
        
        for category, score in category_scores.items():
            if category in self.category_weights:
                overall_score += score * self.category_weights[category]
        
        log_structured_data(eligibility_logger, "info", 
                           f"Score geral calculado: {overall_score}", 
                           {"category_scores": category_scores})
        
        return overall_score
    
    def determine_viability_level(self, final_score: float) -> str:
        """
        Determina o nível de viabilidade com base na pontuação final.
        
        Args:
            final_score: Pontuação final (0-100)
            
        Returns:
            Nível de viabilidade (EXCELLENT, STRONG, PROMISING, CHALLENGING, INSUFFICIENT)
        """
        log_structured_data(eligibility_logger, "info", 
                           "Determinando nível de viabilidade", 
                           {"final_score": final_score})
                           
        if final_score >= VIABILITY_THRESHOLDS["EXCELLENT"]:
            return "EXCELLENT"
        elif final_score >= VIABILITY_THRESHOLDS["STRONG"]:
            return "STRONG"
        elif final_score >= VIABILITY_THRESHOLDS["PROMISING"]:
            return "PROMISING"
        elif final_score >= VIABILITY_THRESHOLDS["CHALLENGING"]:
            return "CHALLENGING"
        else:
            return "INSUFFICIENT"
    
    def generate_personal_message(self, final_score: float, viability_level: str) -> str:
        """
        Gera uma mensagem personalizada com base no score e nível de viabilidade.
        
        Args:
            final_score: Pontuação final (0-100)
            viability_level: Nível de viabilidade
            
        Returns:
            Mensagem personalizada
        """
        return PERSONAL_MESSAGES.get(viability_level, PERSONAL_MESSAGES["INSUFFICIENT"])
    
    def estimate_processing_time(self, final_score: float) -> int:
        """
        Estima o tempo de processamento em meses com base no score.
        
        Args:
            final_score: Pontuação final (0-100)
            
        Returns:
            Tempo estimado em meses
        """
        viability_level = self.determine_viability_level(final_score)
        return PROCESSING_TIME_ESTIMATES.get(viability_level, PROCESSING_TIME_ESTIMATES["INSUFFICIENT"])
    
    def identify_strengths(self, category_scores: Dict[str, float], input_data: EligibilityAssessmentInput) -> List[str]:
        """
        Identifica pontos fortes com base nas pontuações por categoria.
        
        Args:
            category_scores: Pontuações por categoria
            input_data: Dados da avaliação
            
        Returns:
            Lista de pontos fortes
        """
        strengths = []
        
        # Verificar educação
        if category_scores["education"] >= self.strength_threshold:
            if input_data.education.highest_degree == "PHD":
                strengths.append("Doutorado em área relevante é um forte fundamento para EB2-NIW")
            elif input_data.education.highest_degree == "MASTERS":
                strengths.append("Mestrado em área relevante fortalece sua candidatura")
                
            if input_data.education.university_ranking and input_data.education.university_ranking <= 50:
                strengths.append(f"Formação em instituição de alto prestígio (top {input_data.education.university_ranking})")
                
            # Adicionar força específica para área STEM
            field = input_data.education.field_of_study.lower()
            stem_fields = ["computer", "engineering", "science", "technology", "math", "medicine"]
            if any(stem in field for stem in stem_fields):
                strengths.append(f"Formação em área STEM ({input_data.education.field_of_study})")
        
        # Verificar experiência
        if category_scores["experience"] >= self.strength_threshold:
            if input_data.experience.years_of_experience >= 10:
                strengths.append(f"Experiência profissional extensa ({input_data.experience.years_of_experience} anos) em sua área")
            elif input_data.experience.years_of_experience >= 7:
                strengths.append(f"Experiência profissional significativa ({input_data.experience.years_of_experience} anos)")
                
            if input_data.experience.leadership_roles:
                strengths.append("Experiência em posições de liderança demonstra reconhecimento profissional")
                
            if input_data.experience.specialized_experience:
                strengths.append("Especialização em área de nicho valorizada para EB2-NIW")
        
        # Verificar realizações
        if category_scores["achievements"] >= self.strength_threshold:
            if input_data.achievements.publications_count >= 10:
                strengths.append(f"Número expressivo de publicações ({input_data.achievements.publications_count}) demonstra contribuição ao campo")
            
            if input_data.achievements.patents_count >= 2:
                strengths.append(f"Patentes registradas ({input_data.achievements.patents_count}) evidenciam inovação significativa")
                
            if input_data.achievements.projects_led >= 3:
                strengths.append(f"Liderança em múltiplos projetos de impacto ({input_data.achievements.projects_led})")
        
        # Verificar reconhecimento
        if category_scores["recognition"] >= self.strength_threshold:
            if input_data.recognition.awards_count >= 3:
                strengths.append(f"Múltiplos prêmios e reconhecimentos ({input_data.recognition.awards_count}) em sua área")
                
            if input_data.recognition.speaking_invitations >= 5:
                strengths.append("Convites frequentes para palestras evidenciam reconhecimento pelos pares")
                
            if input_data.recognition.professional_memberships >= 2:
                strengths.append("Afiliações a associações profissionais relevantes")
        
        log_structured_data(eligibility_logger, "info", 
                           f"Pontos fortes identificados: {len(strengths)}", 
                           {"strengths": strengths})
        
        return strengths
    
    def identify_weaknesses(self, category_scores: Dict[str, float], input_data: EligibilityAssessmentInput) -> List[str]:
        """
        Identifica pontos fracos com base nas pontuações por categoria.
        
        Args:
            category_scores: Pontuações por categoria
            input_data: Dados da avaliação
            
        Returns:
            Lista de pontos fracos
        """
        weaknesses = []
        
        # Verificar educação
        if category_scores["education"] <= self.weakness_threshold:
            if input_data.education.highest_degree == "BACHELORS":
                weaknesses.append("Apenas bacharelado pode ser insuficiente para EB2-NIW sem experiência compensatória")
            
            if not input_data.education.university_ranking or input_data.education.university_ranking > 200:
                weaknesses.append("Formação em instituição sem reconhecimento internacional significativo")
        
        # Verificar experiência
        if category_scores["experience"] <= self.weakness_threshold:
            if input_data.experience.years_of_experience < 5:
                weaknesses.append(f"Experiência profissional limitada ({input_data.experience.years_of_experience} anos)")
                
            if not input_data.experience.leadership_roles:
                weaknesses.append("Ausência de experiência em posições de liderança")
                
            if not input_data.experience.specialized_experience:
                weaknesses.append("Falta de especialização em área de nicho")
        
        # Verificar realizações
        if category_scores["achievements"] <= self.weakness_threshold:
            if input_data.achievements.publications_count < 5:
                weaknesses.append(f"Número limitado de publicações ({input_data.achievements.publications_count})")
            
            if input_data.achievements.patents_count == 0:
                weaknesses.append("Ausência de patentes ou inovações documentadas")
                
            if input_data.achievements.projects_led < 2:
                weaknesses.append("Poucas evidências de liderança em projetos significativos")
        
        # Verificar reconhecimento
        if category_scores["recognition"] <= self.weakness_threshold:
            if input_data.recognition.awards_count < 2:
                weaknesses.append("Poucos prêmios ou reconhecimentos formais")
                
            if input_data.recognition.speaking_invitations < 2:
                weaknesses.append("Poucas evidências de convites para palestras ou apresentações")
                
            if input_data.recognition.professional_memberships < 2:
                weaknesses.append("Participação limitada em associações profissionais")
        
        log_structured_data(eligibility_logger, "info", 
                           f"Pontos fracos identificados: {len(weaknesses)}", 
                           {"weaknesses": weaknesses})
        
        return weaknesses
    
    def generate_next_steps(self, viability_level: str) -> List[str]:
        """
        Gera os próximos passos recomendados com base no nível de viabilidade.
        
        Args:
            viability_level: Nível de viabilidade
            
        Returns:
            Lista de próximos passos recomendados
        """
        next_steps = []
        
        # Próximos passos comuns para todos os níveis
        next_steps.append("Complete seu perfil para receber uma avaliação mais detalhada")
        
        if viability_level in ["EXCELLENT", "STRONG"]:
            next_steps.append("Carregue documentos de apoio para fortalecer seu caso")
            next_steps.append("Consulte um especialista para verificar sua estratégia")
        
        if viability_level in ["PROMISING", "CHALLENGING"]:
            next_steps.append("Siga as recomendações para fortalecer seu perfil antes de prosseguir")
            next_steps.append("Considere um plano de desenvolvimento profissional de médio prazo")
        
        if viability_level == "INSUFFICIENT":
            next_steps.append("Considere alternativas de imigração mais adequadas ao seu perfil atual")
            next_steps.append("Desenvolva um plano de 1-2 anos para fortalecer suas qualificações")
        
        log_structured_data(eligibility_logger, "info", 
                           f"Próximos passos gerados: {len(next_steps)}", 
                           {"viability_level": viability_level})
        
        return next_steps
    
    async def evaluate(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Realiza a avaliação completa de elegibilidade EB2-NIW.
        
        Args:
            input_data: Dados de entrada da avaliação
            
        Returns:
            Dicionário com resultados detalhados da avaliação
        """
        assessment_id = str(uuid.uuid4())
        request_id = get_request_id()
        start_time = time.time()
        
        log_structured_data(eligibility_logger, "info", 
                          f"Iniciando avaliação de elegibilidade: {assessment_id}", 
                          {"request_id": request_id, "user_id": input_data.user_id})
        
        try:
            # 1. Calcular pontuações por categoria
            category_scores = self.calculate_category_scores(input_data)
            
            # 2. Avaliar rotas EB2 (Grau Avançado e Habilidade Excepcional)
            advanced_degree_score = self.eb2_evaluator.evaluate_advanced_degree_route(input_data)
            exceptional_ability_score = self.eb2_evaluator.evaluate_exceptional_ability_route(input_data)
            
            # 3. Determinar a rota EB2 recomendada
            eb2_route_evaluation = self.eb2_evaluator.determine_recommended_route(
                advanced_degree_score,
                exceptional_ability_score,
                input_data
            )
            
            # 4. Avaliar critérios NIW
            niw_evaluation = self.niw_evaluator.evaluate_niw(input_data)
            
            # 5. Calcular pontuação final (combinando EB2 e NIW)
            # Usar a pontuação da rota EB2 recomendada
            recommended_route = eb2_route_evaluation["recommended_route"]
            eb2_score = advanced_degree_score if recommended_route == "ADVANCED_DEGREE" else exceptional_ability_score
            
            # Pontuação NIW
            niw_score = niw_evaluation["niw_overall_score"]
            
            # Cálculo da pontuação final (40% EB2, 60% NIW)
            final_score = (eb2_score * 0.4 + niw_score * 0.6) * 100  # Convertendo para escala 0-100
            
            # 6. Determinar viabilidade
            viability_level = self.determine_viability_level(final_score)
            
            # 7. Identificar pontos fortes e fracos
            strengths = self.identify_strengths(category_scores, input_data)
            weaknesses = self.identify_weaknesses(category_scores, input_data)
            
            # 8. Gerar recomendações detalhadas
            detailed_recommendations = self.recommendation_engine.generate_detailed_recommendations(
                input_data,
                category_scores,
                eb2_route_evaluation,
                niw_evaluation
            )
            
            # 9. Gerar próximos passos
            next_steps = self.generate_next_steps(viability_level)
            
            # 10. Gerar mensagem personalizada
            personal_message = self.generate_personal_message(final_score, viability_level)
            
            # 11. Estimar tempo de processamento
            processing_time_months = self.estimate_processing_time(final_score)
            
            # 12. Compilar resultados completos
            results = {
                "id": assessment_id,
                "user_id": input_data.user_id,
                "created_at": datetime.utcnow().isoformat(),
                
                # Scores
                "category_scores": category_scores,
                "overall_score": final_score,
                
                # EB2 Route
                "eb2_route_evaluation": eb2_route_evaluation,
                
                # NIW Evaluation
                "niw_evaluation": niw_evaluation,
                
                # Classificação
                "viability_level": viability_level,
                
                # Feedback
                "strengths": strengths,
                "weaknesses": weaknesses,
                "detailed_recommendations": [rec.dict() for rec in detailed_recommendations],
                "next_steps": next_steps,
                "message": personal_message,
                
                # Estimativas
                "estimated_processing_time": processing_time_months,
                
                # Metadados
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
            
            # 13. Salvar resultados no banco de dados
            if input_data.user_id:
                db_assessment = QuickAssessment(
                    id=assessment_id,
                    user_id=input_data.user_id,
                    overall_score=final_score,
                    viability_level=viability_level,
                    education_score=category_scores["education"],
                    experience_score=category_scores["experience"],
                    achievements_score=category_scores["achievements"],
                    recognition_score=category_scores["recognition"],
                    input_data=input_data.dict(),
                    strengths=strengths,
                    weaknesses=weaknesses,
                    recommendations=[rec.dict() for rec in detailed_recommendations],
                    is_latest=True
                )
                
                # Marcar como não-mais-atual todas as avaliações anteriores do usuário
                # e salvar a nova avaliação
                await self._save_assessment(db_assessment)
            
            log_structured_data(eligibility_logger, "info", 
                              f"Avaliação concluída: {assessment_id}", 
                              {
                                  "request_id": request_id,
                                  "user_id": input_data.user_id, 
                                  "score": final_score,
                                  "viability": viability_level,
                                  "processing_time_ms": int((time.time() - start_time) * 1000)
                              })
            
            return results
            
        except Exception as e:
            log_structured_data(eligibility_logger, "error", 
                              f"Erro ao processar avaliação: {str(e)}", 
                              {"request_id": request_id, "user_id": input_data.user_id})
            raise
    
    async def _save_assessment(self, assessment: QuickAssessment) -> None:
        """
        Salva uma nova avaliação no banco de dados, atualizando flags de 'is_latest'.
        
        Args:
            assessment: Avaliação a ser salva
        """
        try:
            # Buscar avaliações anteriores do usuário
            if assessment.user_id:
                # Marcar todas as avaliações anteriores como não sendo mais a mais recente
                await self.db_manager.update_previous_assessments(assessment.user_id)
            
            # Salvar a nova avaliação
            await self.db_manager.create_eligibility_assessment(assessment)
            
        except Exception as e:
            log_structured_data(eligibility_logger, "error", 
                              f"Erro ao salvar avaliação: {str(e)}", 
                              {"assessment_id": assessment.id, "user_id": assessment.user_id})
            # Não propagar a exceção para não afetar a resposta ao usuário
            # A falha no salvamento não deve impedir que o usuário receba a avaliação
