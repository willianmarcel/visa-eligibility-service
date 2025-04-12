from typing import Dict, List, Optional
from app.schemas.eligibility import EligibilityAssessmentInput

class NIWEvaluator:
    """
    Avaliador dos critérios NIW (National Interest Waiver) para vistos EB2-NIW.

    Esta classe implementa a avaliação dos três critérios fundamentais do NIW
    segundo o precedente Matter of Dhanasar:
    1. O trabalho proposto tem mérito substancial e importância nacional
    2. O solicitante está bem posicionado para avançar o empreendimento proposto
    3. Seria benéfico para os EUA dispensar os requisitos de oferta de emprego
    """

    def evaluate(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia os três critérios do NIW e calcula a pontuação geral.

        Args:
            input_data: Dados da avaliação de elegibilidade.

        Returns:
            Dicionário contendo as pontuações para cada critério e a pontuação geral.
        """
        # Avaliar cada critério do NIW
        merit_importance_result = self.evaluate_merit_and_national_importance(input_data)
        well_positioned_result = self.evaluate_well_positioned(input_data)
        benefit_waiver_result = self.evaluate_benefit_waiver(input_data)
        
        # Extrair pontuações
        merit_importance_score = merit_importance_result['score']
        well_positioned_score = well_positioned_result['score']
        benefit_waiver_score = benefit_waiver_result['score']
        
        # Calcular pontuação NIW geral
        niw_score = self.calculate_niw_score(
            merit_importance_score,
            well_positioned_score,
            benefit_waiver_score
        )
        
        # Montar resultado completo
        return {
            "merit_importance": merit_importance_result,
            "well_positioned": well_positioned_result,
            "benefit_waiver": benefit_waiver_result,
            "merit_importance_score": merit_importance_score,
            "well_positioned_score": well_positioned_score,
            "benefit_waiver_score": benefit_waiver_score,
            "niw_score": niw_score
        }

    def evaluate_merit_and_national_importance(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia o critério de mérito substancial e importância nacional.

        Este critério avalia:
        - Relevância da área para interesses nacionais dos EUA
        - Impacto potencial do trabalho proposto
        - Sustentação por evidências documentais

        Args:
            input_data: Dados da avaliação de elegibilidade.

        Returns:
            Dicionário contendo a pontuação geral e subcritérios.
        """
        # Inicializar subcritérios
        area_relevance_score = 0.0
        potential_impact_score = 0.0
        evidence_support_score = 0.0
        
        # 1. Avaliar relevância da área
        field = input_data.us_plans.field_of_work.lower() if hasattr(input_data.us_plans, 'field_of_work') else ""
        
        # Áreas críticas de alto interesse nacional
        critical_fields = [
            "cybersecurity", "cyber security", 
            "renewable energy", "sustainable energy",
            "artificial intelligence", "machine learning",
            "public health", "epidemiology", 
            "national defense", "defense", "security",
            "quantum computing", "quantum technology"
        ]
        
        # Áreas de interesse significativo
        significant_fields = [
            "biotech", "biotechnology", "pharma", "pharmaceutical",
            "clean tech", "clean technology", "climate", 
            "aerospace", "aviation", "space",
            "advanced manufacturing", "robotics",
            "healthcare", "medicine", "medical"
        ]
        
        # Áreas de importância moderada
        moderate_fields = [
            "finance", "economics", "business", 
            "education", "teaching",
            "sustainability", "environment",
            "agriculture", "food security",
            "transportation", "logistics"
        ]
        
        # Avaliar relevância da área
        if any(critical in field for critical in critical_fields):
            area_relevance_score = 1.0
        elif any(significant in field for significant in significant_fields):
            area_relevance_score = 0.8
        elif any(moderate in field for moderate in moderate_fields):
            area_relevance_score = 0.6
        else:
            area_relevance_score = 0.3
        
        # 2. Avaliar impacto potencial
        # Analisar descrição do trabalho proposto
        proposed_work = input_data.us_plans.proposed_work.lower() if hasattr(input_data.us_plans, 'proposed_work') else ""
        national_importance = input_data.us_plans.national_importance.lower() if hasattr(input_data.us_plans, 'national_importance') else ""
        potential_beneficiaries = input_data.us_plans.potential_beneficiaries.lower() if hasattr(input_data.us_plans, 'potential_beneficiaries') else ""
        
        # Palavras-chave indicando impacto amplo
        broad_impact_keywords = [
            "nationwide", "across the us", "national scale", "broad impact",
            "multiple industries", "cross-sector", "transformative", 
            "revolutionary", "many sectors", "entire industry"
        ]
        
        # Palavras-chave indicando impacto significativo em setor específico
        significant_impact_keywords = [
            "industry leader", "major advance", "significant improvement",
            "leading company", "cutting edge", "pioneering", 
            "substantial impact", "key player", "breakthrough"
        ]
        
        # Palavras-chave indicando impacto moderado
        moderate_impact_keywords = [
            "improve", "enhance", "better than", "advance the field",
            "contribute to", "help develop", "support growth"
        ]
        
        combined_text = f"{proposed_work} {national_importance} {potential_beneficiaries}"
        
        # Avaliar impacto potencial
        if any(keyword in combined_text for keyword in broad_impact_keywords):
            potential_impact_score = 1.0
        elif any(keyword in combined_text for keyword in significant_impact_keywords):
            potential_impact_score = 0.8
        elif any(keyword in combined_text for keyword in moderate_impact_keywords):
            potential_impact_score = 0.6
        else:
            potential_impact_score = 0.3
        
        # 3. Avaliar sustentação por evidências
        # Use o número de publicações e patentes como proxy para evidências
        publications = getattr(input_data.achievements, 'publications_count', 0)
        patents = getattr(input_data.achievements, 'patents_count', 0)
        awards = getattr(input_data.recognition, 'awards_count', 0)
        
        evidence_total = publications + patents + awards
        
        if evidence_total >= 10:
            evidence_support_score = 1.0
        elif evidence_total >= 5:
            evidence_support_score = 0.7
        elif evidence_total >= 1:
            evidence_support_score = 0.4
        else:
            evidence_support_score = 0.1
        
        # Calcular pontuação final com pesos
        final_score = (
            area_relevance_score * 0.4 +  # 40%
            potential_impact_score * 0.4 +  # 40%
            evidence_support_score * 0.2    # 20%
        )
        
        # Montar resultado
        return {
            "score": final_score,
            "subcriteria": {
                "area_relevance": area_relevance_score,
                "potential_impact": potential_impact_score,
                "evidence_support": evidence_support_score
            }
        }

    def evaluate_well_positioned(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia o critério de estar bem posicionado para avançar o empreendimento.

        Este critério avalia:
        - Qualificações do solicitante para o trabalho proposto
        - Histórico de sucesso na área
        - Plano e recursos disponíveis

        Args:
            input_data: Dados da avaliação de elegibilidade.

        Returns:
            Dicionário contendo a pontuação geral e subcritérios.
        """
        # Inicializar subcritérios
        qualifications_score = 0.0
        success_history_score = 0.0
        plan_resources_score = 0.0
        
        # 1. Avaliar qualificações do solicitante
        # Considerar grau acadêmico e experiência combinados
        degree = input_data.education.highest_degree.upper() if hasattr(input_data.education, 'highest_degree') else ""
        years_experience = input_data.experience.years_of_experience if hasattr(input_data.experience, 'years_of_experience') else 0
        leadership = getattr(input_data.experience, 'leadership_roles', False)
        specialized = getattr(input_data.experience, 'specialized_experience', False)
        
        # Avaliar qualificações
        if ("PHD" in degree or "DOCTOR" in degree) and years_experience >= 5:
            qualifications_score = 1.0
        elif ("MASTER" in degree and years_experience >= 7) or ("PHD" in degree):
            qualifications_score = 0.8
        elif ("MASTER" in degree) or ("BACHELOR" in degree and years_experience >= 10):
            qualifications_score = 0.6
        else:
            qualifications_score = 0.3
        
        # Ajustar para liderança e especialização
        if leadership and specialized and qualifications_score < 1.0:
            qualifications_score = min(qualifications_score + 0.2, 1.0)
        elif (leadership or specialized) and qualifications_score < 1.0:
            qualifications_score = min(qualifications_score + 0.1, 1.0)
        
        # 2. Avaliar histórico de sucesso
        # Considerar publicações, patentes, projetos e prêmios
        publications = getattr(input_data.achievements, 'publications_count', 0)
        patents = getattr(input_data.achievements, 'patents_count', 0)
        projects_led = getattr(input_data.achievements, 'projects_led', 0)
        awards = getattr(input_data.recognition, 'awards_count', 0)
        speaking = getattr(input_data.recognition, 'speaking_invitations', 0)
        
        # Calcular pontuação de sucesso histórico
        success_points = (
            min(publications, 10) * 0.1 +  # Até 1.0 por publicações
            min(patents, 3) * 0.2 +        # Até 0.6 por patentes
            min(projects_led, 5) * 0.1 +   # Até 0.5 por projetos
            min(awards, 5) * 0.1 +         # Até 0.5 por prêmios
            min(speaking, 5) * 0.05        # Até 0.25 por palestras
        )
        
        success_history_score = min(success_points, 1.0)  # Limitar a 1.0
        
        # 3. Avaliar plano e recursos
        # Analisar a qualidade do plano proposto
        proposed_work = input_data.us_plans.proposed_work if hasattr(input_data.us_plans, 'proposed_work') else ""
        
        # Verificar presença de elementos importantes no plano
        has_detailed_plan = len(proposed_work) > 300  # Plano detalhado tem pelo menos 300 caracteres
        
        if has_detailed_plan:
            plan_resources_score = 0.7
            
            # Verificar menções a recursos específicos
            resources_keywords = [
                "resource", "funding", "grant", "laboratory", "lab", 
                "equipment", "facility", "team", "collaborat", "partner"
            ]
            
            if any(keyword in proposed_work.lower() for keyword in resources_keywords):
                plan_resources_score = 1.0
        else:
            plan_resources_score = 0.4
        
        # Calcular pontuação final com pesos
        final_score = (
            qualifications_score * 0.35 +    # 35%
            success_history_score * 0.35 +   # 35%
            plan_resources_score * 0.3       # 30%
        )
        
        # Montar resultado
        return {
            "score": final_score,
            "subcriteria": {
                "qualifications": qualifications_score,
                "success_history": success_history_score,
                "plan_resources": plan_resources_score
            }
        }

    def evaluate_benefit_waiver(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia o critério de benefício ao dispensar requisitos de oferta de emprego.

        Este critério avalia:
        - Urgência da contribuição
        - Impraticabilidade do processo padrão
        - Benefícios vs. requisitos

        Args:
            input_data: Dados da avaliação de elegibilidade.

        Returns:
            Dicionário contendo a pontuação geral e subcritérios.
        """
        # Inicializar subcritérios
        urgency_score = 0.0
        impracticality_score = 0.0
        benefits_score = 0.0
        
        # 1. Avaliar urgência da contribuição
        # Analisar descrição do trabalho proposto
        national_importance = input_data.us_plans.national_importance.lower() if hasattr(input_data.us_plans, 'national_importance') else ""
        
        # Palavras-chave indicando urgência
        high_urgency_keywords = [
            "urgent", "critical", "immediate", "crisis", 
            "emergency", "pressing", "vital", "severe shortage",
            "national security", "pandemic", "epidemic", "disaster"
        ]
        
        medium_urgency_keywords = [
            "important", "significant", "needed", "necessary", 
            "shortage", "gap", "advancing", "competitive advantage"
        ]
        
        # Avaliar urgência
        if any(keyword in national_importance for keyword in high_urgency_keywords):
            urgency_score = 1.0
        elif any(keyword in national_importance for keyword in medium_urgency_keywords):
            urgency_score = 0.7
        else:
            urgency_score = 0.5
        
        # 2. Avaliar impraticabilidade do processo padrão
        impracticality_reasons = input_data.us_plans.standard_process_impracticality.lower() if hasattr(input_data.us_plans, 'standard_process_impracticality') else ""
        
        # Palavras-chave indicando impraticabilidade
        high_impracticality_keywords = [
            "impossible", "cannot", "unable to", "no employer",
            "self-employed", "entrepreneur", "founder", "startup",
            "multiple employers", "consulting", "freelance"
        ]
        
        medium_impracticality_keywords = [
            "difficult", "challenging", "burden", "time-consuming",
            "delay", "competitive", "limited opportunities"
        ]
        
        # Avaliar impraticabilidade
        if any(keyword in impracticality_reasons for keyword in high_impracticality_keywords):
            impracticality_score = 1.0
        elif any(keyword in impracticality_reasons for keyword in medium_impracticality_keywords):
            impracticality_score = 0.7
        elif impracticality_reasons:  # Se há alguma explicação, mesmo que fraca
            impracticality_score = 0.4
        else:
            impracticality_score = 0.2
        
        # 3. Avaliar benefícios vs. requisitos
        # Combinar diferentes elementos para avaliar este critério
        proposed_work = input_data.us_plans.proposed_work.lower() if hasattr(input_data.us_plans, 'proposed_work') else ""
        beneficiaries = input_data.us_plans.potential_beneficiaries.lower() if hasattr(input_data.us_plans, 'potential_beneficiaries') else ""
        
        combined_text = f"{proposed_work} {beneficiaries} {national_importance}"
        
        # Palavras-chave indicando benefícios claros
        high_benefit_keywords = [
            "substantial benefit", "significant benefit", "greatly benefit",
            "national interest", "economic growth", "job creation",
            "innovation", "competitive edge", "leadership", "pioneer"
        ]
        
        medium_benefit_keywords = [
            "benefit", "improve", "enhance", "advance", "contribute",
            "support", "help", "useful", "valuable"
        ]
        
        # Avaliar benefícios
        if any(keyword in combined_text for keyword in high_benefit_keywords):
            benefits_score = 1.0
        elif any(keyword in combined_text for keyword in medium_benefit_keywords):
            benefits_score = 0.7
        elif combined_text:  # Se há alguma descrição, mesmo que fraca
            benefits_score = 0.4
        else:
            benefits_score = 0.2
        
        # Calcular pontuação final com pesos
        final_score = (
            urgency_score * 0.4 +          # 40%
            impracticality_score * 0.3 +   # 30%
            benefits_score * 0.3           # 30%
        )
        
        # Montar resultado
        return {
            "score": final_score,
            "subcriteria": {
                "urgency": urgency_score,
                "impracticality": impracticality_score,
                "benefits": benefits_score
            }
        }

    def calculate_niw_score(self, 
                          merit_importance_score: float, 
                          well_positioned_score: float, 
                          benefit_waiver_score: float) -> float:
        """
        Calcula o score NIW final com base nos três critérios principais
        e seus respectivos pesos.
        
        Args:
            merit_importance_score: Pontuação do critério de mérito e importância
            well_positioned_score: Pontuação do critério de bem posicionado
            benefit_waiver_score: Pontuação do critério de benefício de dispensa
            
        Returns:
            Pontuação NIW final (0.0 a 1.0)
        """
        # Implementação conforme seção 4.2.4 dos requisitos
        niw_score = (
            merit_importance_score * 0.35 +
            well_positioned_score * 0.35 +
            benefit_waiver_score * 0.30
        )
        
        return niw_score