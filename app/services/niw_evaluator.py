"""
Módulo para avaliação dos critérios NIW (National Interest Waiver).
Implementa a avaliação dos três critérios do precedente Matter of Dhanasar.
"""

from typing import Dict, List, Tuple
from app.schemas.eligibility import EligibilityAssessmentInput
from app.core.logging import scoring_logger, log_structured_data
from app.core.eligibility_config import NIW_CONFIG


class NIWEvaluator:
    """
    Avaliador dos critérios de National Interest Waiver (NIW).
    
    Esta classe implementa a lógica de avaliação para os três critérios do NIW
    conforme o precedente Matter of Dhanasar:
    1. Mérito substancial e importância nacional
    2. Bem posicionado para avançar o empreendimento
    3. Benefício em dispensar os requisitos de oferta de emprego
    """
    
    def evaluate_merit_importance(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia o critério de 'mérito substancial e importância nacional' do NIW
        conforme o precedente Matter of Dhanasar.
        
        Args:
            input_data: Dados da avaliação
            
        Returns:
            Dicionário com pontuação geral e subcritérios
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando critério NIW: mérito e importância nacional")
        
        # Inicializar pontuações para os subcritérios com valores neutros
        relevance_score = 0.5  # Relevância da área
        impact_score = 0.5     # Impacto potencial
        evidence_score = 0.5   # Sustentação por evidências
        
        # Obter configurações
        config = NIW_CONFIG["merit_importance"]
        
        if hasattr(input_data, "us_plans") and input_data.us_plans:
            # 1. Avaliar relevância da área (config["weights"]["relevance"])
            field = input_data.us_plans.field_of_work.lower()
            proposed_work = input_data.us_plans.proposed_work.lower()
            
            # Verificar se a área é de alta importância nacional
            if any(keyword in field or keyword in proposed_work for keyword in config["high_importance_keywords"]):
                relevance_score = config["relevance_scores"]["high_importance"]
            elif any(keyword in field or keyword in proposed_work for keyword in config["significant_importance_keywords"]):
                relevance_score = config["relevance_scores"]["significant_importance"]
            else:
                # Outras áreas recebem pontuação baseada na descrição da importância
                if hasattr(input_data.us_plans, "national_importance") and input_data.us_plans.national_importance:
                    importance = input_data.us_plans.national_importance.lower()
                    # Análise da explicação da importância nacional
                    if len(importance) > 300:  # Explicação detalhada
                        relevance_score = config["relevance_scores"]["detailed_explanation"]
                    elif len(importance) > 150:  # Explicação moderada
                        relevance_score = config["relevance_scores"]["moderate_explanation"]
                    else:  # Explicação limitada
                        relevance_score = config["relevance_scores"]["limited_explanation"]
                else:
                    relevance_score = config["relevance_scores"]["minimal_explanation"]
            
            # 2. Avaliar impacto potencial (config["weights"]["impact"])
            # Analisar a descrição do trabalho proposto e beneficiários potenciais
            impact_scope = 0.0
            
            if hasattr(input_data.us_plans, "potential_beneficiaries") and input_data.us_plans.potential_beneficiaries:
                beneficiaries = input_data.us_plans.potential_beneficiaries.lower()
                
                # Avaliar escopo dos beneficiários
                if any(term in beneficiaries for term in config["scope_terms"]["broad"]):
                    impact_scope = config["scope_scores"]["broad"]
                elif any(term in beneficiaries for term in config["scope_terms"]["significant"]):
                    impact_scope = config["scope_scores"]["significant"]
                else:
                    impact_scope = config["scope_scores"]["limited"]
                    
            # Avaliar a claridade e especificidade do impacto
            impact_clarity = 0.0
            
            if hasattr(input_data.us_plans, "proposed_work") and input_data.us_plans.proposed_work:
                work = input_data.us_plans.proposed_work
                
                if len(work) > config["clarity_thresholds"]["detailed"]["min_length"]:
                    impact_clarity = config["clarity_thresholds"]["detailed"]["score"]
                elif len(work) > config["clarity_thresholds"]["moderate"]["min_length"]:
                    impact_clarity = config["clarity_thresholds"]["moderate"]["score"]
                else:
                    impact_clarity = config["clarity_thresholds"]["limited"]["score"]
                    
            # Combinar escopo e claridade para score de impacto
            impact_score = (impact_scope * config["impact_weights"]["scope"]) + (impact_clarity * config["impact_weights"]["clarity"])
            
            # 3. Avaliar sustentação por evidências (config["weights"]["evidence"])
            if hasattr(input_data, "achievements") and hasattr(input_data, "recognition"):
                # Calculando a força da evidência baseada em publicações, patentes, prêmios, etc.
                pub_count = getattr(input_data.achievements, "publications_count", 0)
                patent_count = getattr(input_data.achievements, "patents_count", 0)
                awards_count = getattr(input_data.recognition, "awards_count", 0)
                
                if (pub_count >= config["evidence_thresholds"]["strong"]["publications"] or 
                    patent_count >= config["evidence_thresholds"]["strong"]["patents"] or 
                    awards_count >= config["evidence_thresholds"]["strong"]["awards"]):
                    evidence_score = config["evidence_thresholds"]["strong"]["score"]
                elif (pub_count >= config["evidence_thresholds"]["moderate"]["publications"] or 
                      patent_count >= config["evidence_thresholds"]["moderate"]["patents"] or 
                      awards_count >= config["evidence_thresholds"]["moderate"]["awards"]):
                    evidence_score = config["evidence_thresholds"]["moderate"]["score"]
                else:
                    evidence_score = config["evidence_thresholds"]["weak"]["score"]
        
        # Calcular pontuação geral ponderada
        overall_score = (
            (relevance_score * config["weights"]["relevance"]) +
            (impact_score * config["weights"]["impact"]) +
            (evidence_score * config["weights"]["evidence"])
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score do critério NIW - mérito e importância: {overall_score}", 
                           {
                               "relevance_score": relevance_score,
                               "impact_score": impact_score,
                               "evidence_score": evidence_score
                           })
        
        return {
            "overall_score": overall_score,
            "subcriteria": {
                "relevance": relevance_score,
                "impact": impact_score,
                "evidence": evidence_score
            }
        }
    
    def evaluate_well_positioned(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia o critério 'bem posicionado para avançar o empreendimento proposto'
        conforme o precedente Matter of Dhanasar.
        
        Args:
            input_data: Dados da avaliação
            
        Returns:
            Dicionário com pontuação geral e subcritérios
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando critério NIW: bem posicionado")
        
        # Pontuações para os subcritérios (inicializadas com valores baixos)
        qualification_score = 0.0  # Qualificações do solicitante (35%)
        success_score = 0.0        # Histórico de sucesso (35%)
        plan_score = 0.0           # Plano e recursos (30%)
        
        # 1. Qualificações do solicitante (35%)
        # Considerar formação acadêmica e experiência
        
        # Avaliar grau acadêmico
        if input_data.education.highest_degree == "PHD":
            qualification_score += 1.0
        elif input_data.education.highest_degree == "MASTERS":
            qualification_score += 0.8
        elif input_data.education.highest_degree == "BACHELORS":
            qualification_score += 0.6
        else:
            qualification_score += 0.3
            
        # Avaliar experiência relevante
        if input_data.experience.years_of_experience >= 10:
            qualification_score = min(1.0, qualification_score + 0.2)  # Bônus, limitado a 1.0
        elif input_data.experience.years_of_experience >= 7:
            qualification_score = min(1.0, qualification_score + 0.1)
            
        # Avaliar especializações e certificações
        has_specialization = input_data.experience.specialized_experience
        has_certifications = (
            hasattr(input_data.education, "certifications") and 
            input_data.education.certifications and 
            len(input_data.education.certifications) > 0
        )
        
        if has_specialization or has_certifications:
            qualification_score = min(1.0, qualification_score + 0.1)
            
        # 2. Histórico de sucesso (35%)
        # Avaliar publicações, patentes, projetos, reconhecimentos
        
        # Avaliar publicações
        pub_count = getattr(input_data.achievements, "publications_count", 0)
        if pub_count >= 10:
            success_score += 0.4
        elif pub_count >= 5:
            success_score += 0.3
        elif pub_count >= 1:
            success_score += 0.2
            
        # Avaliar patentes
        patent_count = getattr(input_data.achievements, "patents_count", 0)
        if patent_count >= 3:
            success_score += 0.3
        elif patent_count >= 1:
            success_score += 0.2
            
        # Avaliar projetos liderados
        projects_led = getattr(input_data.achievements, "projects_led", 0)
        if projects_led >= 3:
            success_score += 0.3
        elif projects_led >= 1:
            success_score += 0.2
            
        # Avaliar prêmios e reconhecimentos
        awards_count = getattr(input_data.recognition, "awards_count", 0)
        speaking_invitations = getattr(input_data.recognition, "speaking_invitations", 0)
        
        if awards_count >= 3 or speaking_invitations >= 5:
            success_score += 0.3
        elif awards_count >= 1 or speaking_invitations >= 2:
            success_score += 0.2
            
        # Normalizar success_score para máximo de 1.0
        success_score = min(1.0, success_score)
            
        # 3. Plano e recursos (30%)
        # Avaliar a clareza do plano e acesso a recursos necessários
        
        if hasattr(input_data, "us_plans") and input_data.us_plans:
            # Avaliar clareza e detalhamento do plano
            proposed_work = getattr(input_data.us_plans, "proposed_work", "")
            
            if len(proposed_work) > 400:  # Plano muito detalhado
                plan_score += 0.7
            elif len(proposed_work) > 200:  # Plano detalhado
                plan_score += 0.5
            elif len(proposed_work) > 100:  # Plano básico
                plan_score += 0.3
            else:  # Plano vago
                plan_score += 0.1
                
            # Avaliar acesso a recursos (inferido indiretamente)
            # Podemos considerar a experiência atual, posição de liderança, etc.
            if input_data.experience.leadership_roles:
                plan_score = min(1.0, plan_score + 0.3)
            elif input_data.experience.years_of_experience >= 7:
                plan_score = min(1.0, plan_score + 0.2)
                
        # Calcular pontuação geral ponderada
        overall_score = (
            (qualification_score * 0.35) +  # Qualificações (35%)
            (success_score * 0.35) +        # Histórico de sucesso (35%)
            (plan_score * 0.30)             # Plano e recursos (30%)
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score do critério NIW - bem posicionado: {overall_score}", 
                           {
                               "qualification_score": qualification_score,
                               "success_score": success_score,
                               "plan_score": plan_score
                           })
        
        return {
            "overall_score": overall_score,
            "subcriteria": {
                "qualification": qualification_score,
                "success_history": success_score,
                "plan_resources": plan_score
            }
        }
    
    def evaluate_benefit_waiver(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia o critério 'seria benéfico dispensar os requisitos de oferta de emprego'
        conforme o precedente Matter of Dhanasar.
        
        Args:
            input_data: Dados da avaliação
            
        Returns:
            Dicionário com pontuação geral e subcritérios
        """
        log_structured_data(scoring_logger, "info", 
                           "Avaliando critério NIW: benefício de dispensa")
        
        # Pontuações para os subcritérios
        urgency_score = 0.5       # Urgência da contribuição (40%)
        impractical_score = 0.5   # Impraticabilidade do processo padrão (30%)
        benefit_score = 0.5       # Benefícios vs. Requisitos (30%)
        
        if hasattr(input_data, "us_plans") and input_data.us_plans:
            # 1. Urgência da contribuição (40%)
            
            # Verificar se há termos relacionados a urgência ou necessidade crítica
            urgency_terms = [
                "urgent", "critical", "immediate", "shortage", "gap", "needed", "essential",
                "urgente", "crítico", "imediato", "escassez", "lacuna", "necessário", "essencial",
                "priority", "prioridade", "demand", "demanda", "crisis", "crise"
            ]
            
            # Campos para verificar termos de urgência
            importance = getattr(input_data.us_plans, "national_importance", "").lower()
            proposed_work = getattr(input_data.us_plans, "proposed_work", "").lower()
            
            combined_text = importance + " " + proposed_work
            
            # Verificar presença de termos de urgência
            urgency_term_count = sum(1 for term in urgency_terms if term in combined_text)
            
            if urgency_term_count >= 3:
                urgency_score = 1.0
            elif urgency_term_count >= 2:
                urgency_score = 0.8
            elif urgency_term_count >= 1:
                urgency_score = 0.7
            else:
                # Se não há termos explícitos, verificar pelo menos o comprimento da explicação
                if len(importance) > 300:
                    urgency_score = 0.6
                elif len(importance) > 150:
                    urgency_score = 0.5
                else:
                    urgency_score = 0.3
            
            # 2. Impraticabilidade do processo padrão (30%)
            
            # Verificar a explicação para dispensa do processo padrão
            impracticality = getattr(input_data.us_plans, "standard_process_impracticality", "").lower()
            
            # Termos que indicam impraticabilidade do processo padrão
            impractical_terms = [
                "impractical", "difficult", "challenging", "impossible", "barrier", "obstacle",
                "impraticável", "difícil", "desafiador", "impossível", "barreira", "obstáculo",
                "unique", "singular", "rare", "scarce", "único", "singular", "raro", "escasso",
                "self-employed", "entrepreneur", "autônomo", "empreendedor", "freelance"
            ]
            
            # Verificar presença de termos de impraticabilidade
            impractical_term_count = sum(1 for term in impractical_terms if term in impracticality)
            
            if impractical_term_count >= 3:
                impractical_score = 1.0
            elif impractical_term_count >= 2:
                impractical_score = 0.8
            elif impractical_term_count >= 1:
                impractical_score = 0.7
            else:
                # Se não há termos explícitos, verificar pelo menos o comprimento da explicação
                if len(impracticality) > 300:
                    impractical_score = 0.6
                elif len(impracticality) > 150:
                    impractical_score = 0.5
                else:
                    impractical_score = 0.3
            
            # 3. Benefícios vs. Requisitos (30%)
            
            # Este critério é mais subjetivo e depende da força dos argumentos anteriores
            # e do perfil geral do candidato
            
            # Considerar o perfil geral do candidato
            profile_strength = 0.0
            
            # Educação avançada indica que o benefício pode superar requisitos
            if input_data.education.highest_degree == "PHD":
                profile_strength += 0.4
            elif input_data.education.highest_degree == "MASTERS":
                profile_strength += 0.3
            
            # Experiência substancial também indica benefício
            if input_data.experience.years_of_experience >= 10:
                profile_strength += 0.3
            elif input_data.experience.years_of_experience >= 7:
                profile_strength += 0.2
                
            # Realizações notáveis indicam benefício
            pub_count = getattr(input_data.achievements, "publications_count", 0)
            patent_count = getattr(input_data.achievements, "patents_count", 0)
            awards_count = getattr(input_data.recognition, "awards_count", 0)
            
            if pub_count >= 10 or patent_count >= 3 or awards_count >= 3:
                profile_strength += 0.3
            elif pub_count >= 5 or patent_count >= 1 or awards_count >= 1:
                profile_strength += 0.2
                
            # Normalizar profile_strength para máximo de 1.0
            profile_strength = min(1.0, profile_strength)
            
            # Combinar com os argumentos anteriores para determinar benefício
            benefit_score = (urgency_score * 0.4) + (impractical_score * 0.3) + (profile_strength * 0.3)
        
        # Calcular pontuação geral ponderada
        overall_score = (
            (urgency_score * 0.4) +      # Urgência da contribuição (40%)
            (impractical_score * 0.3) +  # Impraticabilidade do processo padrão (30%)
            (benefit_score * 0.3)        # Benefícios vs. Requisitos (30%)
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score do critério NIW - benefício de dispensa: {overall_score}", 
                           {
                               "urgency_score": urgency_score,
                               "impractical_score": impractical_score,
                               "benefit_score": benefit_score
                           })
        
        return {
            "overall_score": overall_score,
            "subcriteria": {
                "urgency": urgency_score,
                "impracticality": impractical_score,
                "benefit": benefit_score
            }
        }
    
    def calculate_niw_score(self, 
                          merit_importance_score: float, 
                          well_positioned_score: float, 
                          benefit_waiver_score: float) -> float:
        """
        Calcula a pontuação NIW combinando os três critérios com seus respectivos pesos.
        
        Args:
            merit_importance_score: Pontuação do critério de mérito e importância nacional
            well_positioned_score: Pontuação do critério bem posicionado
            benefit_waiver_score: Pontuação do critério benefício de dispensa
            
        Returns:
            Pontuação NIW (0 a 1)
        """
        # Pesos para cada critério NIW
        merit_weight = 0.35
        well_positioned_weight = 0.35
        waiver_benefit_weight = 0.30
        
        # Calcular pontuação ponderada
        niw_score = (
            (merit_importance_score * merit_weight) +
            (well_positioned_score * well_positioned_weight) +
            (benefit_waiver_score * waiver_benefit_weight)
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score NIW calculado: {niw_score}", 
                           {
                               "merit_importance_score": merit_importance_score,
                               "well_positioned_score": well_positioned_score,
                               "benefit_waiver_score": benefit_waiver_score
                           })
        
        return niw_score
    
    def evaluate_niw(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Avalia os três critérios NIW (Matter of Dhanasar) e calcula uma pontuação geral.
        
        Args:
            input_data: Dados da avaliação
            
        Returns:
            Dicionário com pontuação geral e subcritérios
        """
        log_structured_data(scoring_logger, "info", 
                           "Iniciando avaliação NIW completa")
        
        # Avaliar os três critérios
        merit_importance_eval = self.evaluate_merit_importance(input_data)
        well_positioned_eval = self.evaluate_well_positioned(input_data)
        benefit_waiver_eval = self.evaluate_benefit_waiver(input_data)
        
        # Extrair pontuações dos critérios
        merit_importance_score = merit_importance_eval["overall_score"]
        well_positioned_score = well_positioned_eval["overall_score"]
        benefit_waiver_score = benefit_waiver_eval["overall_score"]
        
        # Calcular score NIW geral
        niw_overall_score = self.calculate_niw_score(
            merit_importance_score,
            well_positioned_score,
            benefit_waiver_score
        )
        
        log_structured_data(scoring_logger, "info", 
                           f"Score NIW final: {niw_overall_score}", 
                           {
                               "merit_importance": merit_importance_score,
                               "well_positioned": well_positioned_score,
                               "benefit_waiver": benefit_waiver_score
                           })
        
        # Preparar resultado detalhado
        result = {
            "niw_overall_score": niw_overall_score,
            "subcriteria": {
                "merit_importance_score": merit_importance_score,
                "well_positioned_score": well_positioned_score,
                "benefit_waiver_score": benefit_waiver_score
            },
            "details": {
                "merit_importance": merit_importance_eval["subcriteria"],
                "well_positioned": well_positioned_eval["subcriteria"],
                "benefit_waiver": benefit_waiver_eval["subcriteria"]
            }
        }
        
        return result
