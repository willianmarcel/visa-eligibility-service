"""
Módulo para avaliação das rotas EB2 (Grau Avançado e Habilidade Excepcional).
Implementa a lógica de avaliação conforme especificado na documentação.
"""

from typing import Dict, List, Tuple
from app.schemas.eligibility import EligibilityAssessmentInput
from app.core.logging import scoring_logger, log_structured_data
from app.core.eligibility_config import EB2_CONFIG, STEM_HIGH_DEMAND_FIELDS, STEM_GENERAL_FIELDS


class EB2RouteEvaluator:
    """
    Avaliador das rotas EB2 (Advanced Degree e Exceptional Ability).
    
    Esta classe implementa a lógica de avaliação para as duas rotas possíveis
    de qualificação EB2 e determina qual é a mais vantajosa para o candidato.
    """
    
    def evaluate_advanced_degree_route(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia a elegibilidade pela rota de Grau Avançado para EB2 seguindo 
        os critérios USCIS específicos.
        
        Args:
            input_data: Dados da avaliação
            
        Returns:
            Pontuação (0.0 a 1.0) para a rota de Grau Avançado
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando rota de Grau Avançado", 
                           {"education_data": input_data.education.model_dump()})
        
        score = 0.0
        config = EB2_CONFIG["advanced_degree"]
        
        # Verificar grau acadêmico
        if input_data.education.highest_degree == "PHD":
            score = config["education_scores"]["PHD"]
        elif input_data.education.highest_degree == "MASTERS":
            score = config["education_scores"]["MASTERS"]
        elif input_data.education.highest_degree == "BACHELORS":
            # Para bacharelado, considerar anos de experiência
            score = config["education_scores"]["BACHELORS"]["base"]
            if input_data.experience.years_of_experience >= 7:
                score = config["education_scores"]["BACHELORS"]["experience_bonus"]["7+"]
            elif input_data.experience.years_of_experience >= 5:
                score = config["education_scores"]["BACHELORS"]["experience_bonus"]["5-6"]
        else:
            score = 0.0  # Não atende aos requisitos mínimos
            
        # Ajustar com base no ranking da instituição (bônus)
        if input_data.education.university_ranking:
            if input_data.education.university_ranking <= 50:
                score = min(1.0, score + config["university_ranking_bonus"]["TOP_50"])
            elif input_data.education.university_ranking <= 100:
                score = min(1.0, score + config["university_ranking_bonus"]["TOP_100"])
                
        # Ajustar com base na área de estudo (se for STEM)
        field = input_data.education.field_of_study.lower()
        
        if any(stem in field for stem in STEM_HIGH_DEMAND_FIELDS + STEM_GENERAL_FIELDS):
            score = min(1.0, score + config["stem_field_bonus"])
            
        log_structured_data(scoring_logger, "info", 
                           f"Score da rota de Grau Avançado: {score}")
        
        return score
        
    def evaluate_exceptional_ability_route(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia a elegibilidade pela rota de Habilidade Excepcional para EB2 
        usando os 6 critérios USCIS.
        
        Args:
            input_data: Dados de avaliação
            
        Returns:
            Pontuação (0.0 a 1.0) para a rota de Habilidade Excepcional
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando rota de Habilidade Excepcional")
        
        criteria_met = 0
        criteria_details = []
        config = EB2_CONFIG["exceptional_ability"]
        
        # 1. Grau acadêmico relacionado à área de habilidade excepcional
        if input_data.education.highest_degree in ["PHD", "MASTERS"]:
            criteria_met += 1
            criteria_details.append("Possui grau acadêmico avançado em área relacionada")
            
        # 2. Experiência profissional (10+ anos)
        if input_data.experience.years_of_experience >= 10:
            criteria_met += 1
            criteria_details.append(f"Possui {input_data.experience.years_of_experience} anos de experiência na área")
            
        # 3. Licença profissional ou certificações
        has_certification = (
            input_data.education.professional_license or 
            (hasattr(input_data.education, "certifications") and 
             input_data.education.certifications and 
             len(input_data.education.certifications) > 0)
        )
        
        if has_certification:
            criteria_met += 1
            criteria_details.append("Possui licença profissional ou certificações relevantes")
            
        # 4. Salário demonstrando habilidade excepcional
        high_salary = False
        if hasattr(input_data.experience, "salary_level") and input_data.experience.salary_level == "ABOVE_AVERAGE":
            high_salary = True
        elif hasattr(input_data.experience, "salary_percentile") and input_data.experience.salary_percentile is not None and input_data.experience.salary_percentile > 75:
            high_salary = True
        
        # Verificar o campo current_salary de maneira segura
        current_salary = getattr(input_data, "current_salary", None)
        if current_salary is not None and current_salary > 100000:
            high_salary = True
            
        if high_salary:
            criteria_met += 1
            criteria_details.append("Possui salário acima da média demonstrando reconhecimento excepcional")
            
        # 5. Membro de associações profissionais que exigem conquistas notáveis
        if hasattr(input_data.recognition, "professional_memberships") and input_data.recognition.professional_memberships >= 2:
            criteria_met += 1
            criteria_details.append("Associado a organizações profissionais reconhecidas")
            
        # 6. Reconhecimento por conquistas
        recognition = (
            (hasattr(input_data.recognition, "awards_count") and input_data.recognition.awards_count >= 2) or
            (hasattr(input_data.recognition, "peer_recognition") and input_data.recognition.peer_recognition) or
            (hasattr(input_data.recognition, "government_recognition") and input_data.recognition.government_recognition)
        )
        
        if recognition:
            criteria_met += 1
            criteria_details.append("Recebeu reconhecimento significativo por suas realizações")
            
        # Determinar score com base no número de critérios atendidos
        if criteria_met >= 5:
            score = config["criteria_scores"]["5+"]
        elif criteria_met == 4:
            score = config["criteria_scores"]["4"]
        elif criteria_met == 3:
            score = config["criteria_scores"]["3"]
        elif criteria_met == 2:
            score = config["criteria_scores"]["2"]
        elif criteria_met == 1:
            score = config["criteria_scores"]["1"]
        else:
            score = config["criteria_scores"]["0"]
            
        log_structured_data(scoring_logger, "info", 
                           f"Score da rota de Habilidade Excepcional: {score}", 
                           {"criteria_met": criteria_met, "criteria_details": criteria_details})
        
        return score
        
    def determine_recommended_route(self, 
                                  advanced_degree_score: float, 
                                  exceptional_ability_score: float,
                                  input_data: EligibilityAssessmentInput) -> Dict:
        """
        Determina qual rota é mais vantajosa para o candidato com base nas pontuações
        e gera uma explicação personalizada.
        
        Args:
            advanced_degree_score: Pontuação da rota de Grau Avançado
            exceptional_ability_score: Pontuação da rota de Habilidade Excepcional
            input_data: Dados da avaliação para personalização da explicação
            
        Returns:
            Dicionário com a rota recomendada, scores e explicação
        """
        config = EB2_CONFIG["exceptional_ability"]["score_diff_thresholds"]
        
        # Determinar a rota recomendada com base nos scores
        if advanced_degree_score >= exceptional_ability_score:
            recommended_route = "ADVANCED_DEGREE"
            
            # Gerar explicação personalizada para a rota de Grau Avançado
            if input_data.education.highest_degree == "PHD":
                explanation = f"Seu doutorado em {input_data.education.field_of_study} proporciona uma base sólida para a rota de Grau Avançado, que é mais vantajosa no seu caso."
            elif input_data.education.highest_degree == "MASTERS":
                explanation = f"Seu mestrado em {input_data.education.field_of_study} estabelece uma boa qualificação pela rota de Grau Avançado, que é mais favorável para o seu perfil."
            else:  # BACHELORS
                years = input_data.experience.years_of_experience
                explanation = f"Seu bacharelado combinado com {years} anos de experiência profissional qualifica você pela rota de Grau Avançado, que é a mais vantajosa no seu caso."
        else:
            recommended_route = "EXCEPTIONAL_ABILITY"
            explanation = "Sua combinação de realizações profissionais, reconhecimento e experiência indica maior vantagem pela rota de Habilidade Excepcional, que valoriza seu perfil diferenciado."
            
        # Formatar a diferença entre as rotas
        score_diff = abs(advanced_degree_score - exceptional_ability_score)
        if score_diff < config["slight"]:
            advantage = "ligeira"
        elif score_diff < config["moderate"]:
            advantage = "moderada"
        else:
            advantage = "significativa"
            
        # Complementar explicação com a vantagem comparativa
        if advanced_degree_score >= exceptional_ability_score:
            explanation += f" Há uma vantagem {advantage} em relação à rota de Habilidade Excepcional."
        else:
            explanation += f" Há uma vantagem {advantage} em relação à rota de Grau Avançado."
            
        log_structured_data(scoring_logger, "info", 
                          f"Rota recomendada: {recommended_route}", 
                          {
                              "advanced_degree_score": advanced_degree_score,
                              "exceptional_ability_score": exceptional_ability_score,
                              "score_difference": score_diff
                          })
        
        return {
            "recommended_route": recommended_route,
            "advanced_degree_score": advanced_degree_score,
            "exceptional_ability_score": exceptional_ability_score,
            "route_explanation": explanation
        }
