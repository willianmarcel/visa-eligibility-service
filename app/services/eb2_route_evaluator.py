from typing import Dict, Tuple, List, Optional
from app.schemas.eligibility import EligibilityAssessmentInput

class EB2RouteEvaluator:
    """
    Avaliador das rotas EB2 (Grau Avançado e Habilidade Excepcional) para vistos EB2-NIW.

    Esta classe implementa os critérios específicos de avaliação para as duas
    possíveis rotas de qualificação EB2: Grau Avançado e Habilidade Excepcional.
    """

    def evaluate(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia as duas rotas possíveis para qualificação EB2 e determina a mais vantajosa.

        Args:
            input_data: Dados da avaliação de elegibilidade.

        Returns:
            Dicionário contendo a rota recomendada, pontuações e explicação.
        """
        # Calcular pontuação para cada rota
        advanced_degree_score = self.evaluate_advanced_degree_route(input_data)
        exceptional_ability_score = self.evaluate_exceptional_ability_route(input_data)

        # Determinar qual rota é mais vantajosa
        return self.determine_recommended_route(
            advanced_degree_score, 
            exceptional_ability_score, 
            input_data
        )

    def evaluate_advanced_degree_route(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia a elegibilidade pela rota de Grau Avançado.

        Esta rota requer:
        - Mestrado ou doutorado em área relevante, OU
        - Bacharelado + 5 anos de experiência progressiva na especialidade

        Args:
            input_data: Dados da avaliação de elegibilidade.

        Returns:
            Pontuação (0.0 a 1.0) para a rota de Grau Avançado.
        """
        # Normalizar o grau acadêmico para comparação
        degree = input_data.education.highest_degree.upper()
        years_experience = input_data.experience.years_of_experience

        # Verificar doutorado em área relevante
        if "PHD" in degree or "DOCTOR" in degree:
            return 1.0
        
        # Verificar mestrado em área relevante
        elif "MASTER" in degree:
            return 0.9
        
        # Verificar bacharelado + experiência progressiva
        elif "BACHELOR" in degree:
            if years_experience > 7:
                return 0.85
            elif years_experience >= 5:
                return 0.8
            else:
                return 0.0  # Experiência insuficiente
        
        # Não atende aos requisitos mínimos
        else:
            return 0.0

    def evaluate_exceptional_ability_route(self, input_data: EligibilityAssessmentInput) -> float:
        """
        Avalia a elegibilidade pela rota de Habilidade Excepcional.

        Esta rota requer atender pelo menos 3 dos 6 critérios específicos do USCIS:
        1. Grau acadêmico oficial relacionado à área de habilidade excepcional
        2. Cartas atestando pelo menos 10 anos de experiência em tempo integral
        3. Licença profissional ou certificação para exercer a profissão
        4. Salário demonstrando habilidade excepcional
        5. Associação a organizações profissionais que exigem conquistas notáveis
        6. Reconhecimento por realizações significativas

        Args:
            input_data: Dados da avaliação de elegibilidade.

        Returns:
            Pontuação (0.0 a 1.0) para a rota de Habilidade Excepcional.
        """
        # Avaliar cada critério
        criteria_scores = [0.0] * 6  # Inicializa com 0.0 para cada critério
        
        # 1. Grau acadêmico relacionado
        if input_data.education.highest_degree and input_data.education.field_of_study:
            # Se possui algum grau acadêmico formal, consideramos parcialmente atendido
            criteria_scores[0] = 0.5
            
            # Se o grau for bacharelado ou superior em área relacionada ao campo de atuação
            if any(deg in input_data.education.highest_degree.upper() for deg in ["BACHELOR", "MASTER", "PHD", "DOCTOR"]):
                criteria_scores[0] = 1.0
        
        # 2. Cartas atestando experiência
        if input_data.experience.years_of_experience >= 10:
            criteria_scores[1] = 1.0
        elif input_data.experience.years_of_experience >= 8:
            criteria_scores[1] = 0.5
        
        # 3. Licença profissional ou certificação
        if getattr(input_data.education, 'professional_license', False):
            criteria_scores[2] = 1.0
        elif getattr(input_data.education, 'certifications', []):
            # Avaliar certifications se disponíveis
            cert_count = len(input_data.education.certifications)
            if cert_count >= 2:
                criteria_scores[2] = 1.0
            elif cert_count == 1:
                criteria_scores[2] = 0.5
        
        # 4. Salário demonstrando habilidade excepcional
        salary_level = getattr(input_data.experience, 'salary_level', None)
        salary_percentile = getattr(input_data.experience, 'salary_percentile', None)
        
        if salary_level == "ABOVE_AVERAGE" or (salary_percentile and salary_percentile > 75):
            criteria_scores[3] = 1.0
        elif salary_level == "AVERAGE" or (salary_percentile and salary_percentile > 50):
            criteria_scores[3] = 0.5
        
        # 5. Associação a organizações profissionais
        prof_memberships = getattr(input_data.recognition, 'professional_memberships', 0)
        orgs_requiring_achievement = getattr(input_data.recognition, 'organizations_requiring_achievement', False)
        
        if orgs_requiring_achievement:
            criteria_scores[4] = 1.0
        elif prof_memberships >= 2:
            criteria_scores[4] = 0.5
        
        # 6. Reconhecimento por realizações significativas
        recognition_by_peers = getattr(input_data.recognition, 'recognition_by_peers_or_government', False)
        awards_count = getattr(input_data.recognition, 'awards_count', 0)
        
        if recognition_by_peers:
            criteria_scores[5] = 1.0
        elif awards_count >= 2:
            criteria_scores[5] = 0.5
        
        # Contar critérios atendidos (total ou parcialmente)
        full_criteria_met = sum(1 for score in criteria_scores if score >= 1.0)
        partial_criteria_met = sum(1 for score in criteria_scores if 0 < score < 1.0)
        
        # Determinar pontuação com base nos critérios atendidos
        if full_criteria_met >= 5:
            return 1.0
        elif full_criteria_met >= 4:
            return 0.9
        elif full_criteria_met >= 3:
            return 0.8
        elif full_criteria_met + partial_criteria_met >= 3:
            return 0.5
        else:
            return 0.0

    def determine_recommended_route(self, 
                                   advanced_degree_score: float, 
                                   exceptional_ability_score: float,
                                   input_data: EligibilityAssessmentInput) -> Dict:
        """
        Determina qual rota é mais vantajosa para o candidato.

        Args:
            advanced_degree_score: Pontuação da rota de Grau Avançado.
            exceptional_ability_score: Pontuação da rota de Habilidade Excepcional.
            input_data: Dados da avaliação para personalização da explicação.

        Returns:
            Dicionário com a rota recomendada, scores e explicação.
        """
        # Determinar a rota com maior pontuação
        if advanced_degree_score > exceptional_ability_score:
            recommended_route = "ADVANCED_DEGREE"
            eligibility_score = advanced_degree_score
            
            # Gerar explicação personalizada
            explanation = self._generate_advanced_degree_explanation(
                advanced_degree_score, input_data
            )
        else:
            recommended_route = "EXCEPTIONAL_ABILITY"
            eligibility_score = exceptional_ability_score
            
            # Gerar explicação personalizada
            explanation = self._generate_exceptional_ability_explanation(
                exceptional_ability_score, input_data
            )
        
        # Montar resultado
        return {
            "recommended_route": recommended_route,
            "advanced_degree_score": advanced_degree_score,
            "exceptional_ability_score": exceptional_ability_score,
            "route_explanation": explanation,
            "eligibility_score": eligibility_score
        }

    def _generate_advanced_degree_explanation(self, score: float, input_data: EligibilityAssessmentInput) -> str:
        """
        Gera uma explicação personalizada para a rota de Grau Avançado.

        Args:
            score: Pontuação obtida na rota.
            input_data: Dados da avaliação.

        Returns:
            Explicação personalizada.
        """
        degree = input_data.education.highest_degree.upper()
        field = input_data.education.field_of_study
        years = input_data.experience.years_of_experience
        
        if "PHD" in degree or "DOCTOR" in degree:
            return f"Sua qualificação com doutorado em {field} oferece uma base sólida para a rota de Grau Avançado. Este grau acadêmico é altamente valorizado pelo USCIS e atende plenamente o requisito principal desta rota."
        
        elif "MASTER" in degree:
            return f"Seu mestrado em {field} qualifica você para a rota de Grau Avançado. Este grau é reconhecido pelo USCIS como suficiente para atender ao critério principal desta categoria."
        
        elif "BACHELOR" in degree and years >= 5:
            return f"Sua combinação de bacharelado em {field} com {years} anos de experiência progressiva na área atende aos requisitos para a rota de Grau Avançado. O USCIS reconhece esta combinação como equivalente a um grau avançado."
        
        else:
            return "Sua formação atual não atende completamente aos requisitos para a rota de Grau Avançado. Considere as recomendações para fortalecer sua elegibilidade."

    def _generate_exceptional_ability_explanation(self, score: float, input_data: EligibilityAssessmentInput) -> str:
        """
        Gera uma explicação personalizada para a rota de Habilidade Excepcional.

        Args:
            score: Pontuação obtida na rota.
            input_data: Dados da avaliação.

        Returns:
            Explicação personalizada.
        """
        if score >= 0.8:
            return f"Seu perfil demonstra habilidade excepcional em sua área, atendendo a múltiplos critérios do USCIS para esta categoria. Suas qualificações profissionais, experiência e reconhecimento estabelecem uma base sólida para esta rota."
        
        elif score >= 0.5:
            return f"Seu perfil mostra elementos de habilidade excepcional, atendendo parcialmente aos critérios do USCIS. Fortalecer evidências específicas pode aumentar significativamente suas chances nesta rota."
        
        else:
            return "Seu perfil atual não atende suficientemente aos critérios de Habilidade Excepcional. Recomendamos focar nas áreas específicas indicadas para melhorar sua qualificação."
