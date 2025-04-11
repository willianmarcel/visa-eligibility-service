"""
Motor de recomendações para avaliações de elegibilidade EB2-NIW.
Implementa a lógica de recomendações detalhadas conforme a documentação.
"""

from typing import Dict, List, Any
from app.schemas.eligibility import RecommendationDetail, EligibilityAssessmentInput
from app.core.logging import scoring_logger, log_structured_data


class RecommendationEngine:
    """
    Motor de recomendações para gerar sugestões personalizadas com base no perfil do usuário.
    Implementa a lógica de recomendações conforme especificado na documentação.
    """
    
    def __init__(self):
        # Inicializar biblioteca de recomendações
        self._init_recommendation_libraries()
    
    def _init_recommendation_libraries(self):
        """Inicializa as várias bibliotecas de recomendações para diferentes categorias."""
        
        # Recomendações para Educação
        self.education_recommendations = {
            # Recomendações para melhorar qualificação por rota de grau avançado
            "advanced_degree": [
                {
                    "description": "Obtenha um mestrado em sua área para fortalecer sua qualificação pela rota de Grau Avançado",
                    "impact": "HIGH",
                    "priority": 1,
                    "for_degree": "BACHELORS"
                },
                {
                    "description": "Considere um programa de doutorado para maximizar sua qualificação pela rota de Grau Avançado",
                    "impact": "HIGH",
                    "priority": 1,
                    "for_degree": "MASTERS"
                },
                {
                    "description": "Obtenha certificações profissionais avançadas para complementar sua formação acadêmica",
                    "impact": "MEDIUM",
                    "priority": 2,
                    "for_degree": "ANY"
                },
                {
                    "description": "Participe de programas de educação continuada em universidades reconhecidas",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "for_degree": "ANY"
                }
            ],
            
            # Recomendações para melhorar qualificação por rota de habilidade excepcional
            "exceptional_ability": [
                {
                    "description": "Obtenha um grau acadêmico avançado relacionado à sua área de habilidade excepcional",
                    "impact": "HIGH",
                    "priority": 1,
                    "for_degree": "BACHELORS"
                },
                {
                    "description": "Obtenha licença profissional ou certificações reconhecidas em sua área de atuação",
                    "impact": "HIGH",
                    "priority": 2,
                    "for_degree": "ANY"
                },
                {
                    "description": "Documente seu conhecimento especializado através de cursos, workshops e seminários",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "for_degree": "ANY"
                }
            ]
        }
        
        # Recomendações para Experiência
        self.experience_recommendations = {
            # Recomendações gerais para experiência
            "general": [
                {
                    "description": "Acumule pelo menos 5 anos de experiência progressiva em sua especialidade",
                    "impact": "HIGH",
                    "priority": 1,
                    "min_years": 0,
                    "max_years": 5
                },
                {
                    "description": "Documentar como sua experiência evoluiu com responsabilidades crescentes ao longo do tempo",
                    "impact": "MEDIUM",
                    "priority": 2,
                    "min_years": 3,
                    "max_years": 15
                }
            ],
            
            # Recomendações para liderança
            "leadership": [
                {
                    "description": "Busque posições de liderança ou gerência para demonstrar reconhecimento profissional",
                    "impact": "HIGH",
                    "priority": 2,
                    "for_leadership": False
                },
                {
                    "description": "Documente quantitativamente o impacto de sua liderança (equipes gerenciadas, projetos liderados)",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "for_leadership": True
                }
            ],
            
            # Recomendações para experiência especializada
            "specialized": [
                {
                    "description": "Desenvolva maior especialização em um nicho específico de sua área",
                    "impact": "HIGH",
                    "priority": 2,
                    "for_specialized": False
                },
                {
                    "description": "Documente como sua especialização é rara ou altamente procurada no mercado",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "for_specialized": True
                }
            ],
            
            # Recomendações específicas para rota de habilidade excepcional
            "exceptional_ability": [
                {
                    "description": "Documente pelo menos 10 anos de experiência em tempo integral na sua área através de cartas e registros de emprego",
                    "impact": "HIGH",
                    "priority": 1,
                    "min_years": 0,
                    "max_years": 10
                },
                {
                    "description": "Obtenha cartas detalhadas de supervisores passados destacando suas contribuições únicas",
                    "impact": "MEDIUM",
                    "priority": 2,
                    "min_years": 5,
                    "max_years": 100
                },
                {
                    "description": "Documente salário acima da média para sua ocupação, demonstrando reconhecimento excepcional",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "min_years": 3,
                    "max_years": 100
                }
            ]
        }
        
        # Recomendações para Realizações
        self.achievements_recommendations = {
            # Recomendações para publicações
            "publications": [
                {
                    "description": "Publique artigos em journals reconhecidos na sua área de especialização",
                    "impact": "HIGH",
                    "priority": 1,
                    "min_count": 0,
                    "max_count": 5
                },
                {
                    "description": "Aumente seu número de publicações para pelo menos 10 artigos em journals de impacto",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_count": 5,
                    "max_count": 10
                },
                {
                    "description": "Busque coautorias com pesquisadores reconhecidos em sua área",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "min_count": 0,
                    "max_count": 100
                }
            ],
            
            # Recomendações para patentes
            "patents": [
                {
                    "description": "Registre patentes relacionadas ao seu trabalho para demonstrar inovação",
                    "impact": "HIGH",
                    "priority": 1,
                    "min_count": 0,
                    "max_count": 1
                },
                {
                    "description": "Aumente seu número de patentes para demonstrar consistência em inovação",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_count": 1,
                    "max_count": 3
                }
            ],
            
            # Recomendações para projetos
            "projects": [
                {
                    "description": "Lidere projetos significativos e documente seu papel de liderança e impacto",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_count": 0,
                    "max_count": 2
                },
                {
                    "description": "Quantifique o impacto de seus projetos (ex: economia gerada, usuários beneficiados)",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "min_count": 1,
                    "max_count": 100
                }
            ],
            
            # Recomendações para citações
            "citations": [
                {
                    "description": "Trabalhe para aumentar o número de citações de suas publicações acadêmicas",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "min_count": 0,
                    "max_count": 50
                },
                {
                    "description": "Promova seus trabalhos publicados em conferências e redes sociais acadêmicas",
                    "impact": "LOW",
                    "priority": 4,
                    "min_count": 0,
                    "max_count": 100
                }
            ]
        }
        
        # Recomendações para Reconhecimento
        self.recognition_recommendations = {
            # Recomendações para prêmios
            "awards": [
                {
                    "description": "Candidate-se a prêmios relevantes em sua área de atuação",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_count": 0,
                    "max_count": 2
                },
                {
                    "description": "Documente detalhadamente o prestígio e seletividade dos prêmios recebidos",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "min_count": 1,
                    "max_count": 100
                }
            ],
            
            # Recomendações para palestras
            "speaking": [
                {
                    "description": "Busque oportunidades para palestrar em conferências e eventos da sua área",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_count": 0,
                    "max_count": 3
                },
                {
                    "description": "Torne-se palestrante regular em eventos importantes da sua indústria",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "min_count": 2,
                    "max_count": 100
                }
            ],
            
            # Recomendações para afiliações profissionais
            "memberships": [
                {
                    "description": "Associe-se a organizações profissionais reconhecidas em sua área",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "min_count": 0,
                    "max_count": 2
                },
                {
                    "description": "Busque posições de liderança ou comitês em associações profissionais",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_count": 1,
                    "max_count": 100
                }
            ],
            
            # Recomendações específicas para rota de habilidade excepcional
            "exceptional_ability": [
                {
                    "description": "Obtenha cartas de recomendação de especialistas reconhecidos em seu campo",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_count": 0,
                    "max_count": 100
                },
                {
                    "description": "Documente reconhecimento formal por suas contribuições (certificados, menções)",
                    "impact": "MEDIUM",
                    "priority": 3,
                    "min_count": 0,
                    "max_count": 100
                }
            ]
        }
        
        # Recomendações para critérios NIW
        self.niw_recommendations = {
            # Recomendações para mérito e importância nacional
            "merit_importance": [
                {
                    "description": "Articule claramente como seu trabalho tem impacto substancial em uma área de importância para os EUA",
                    "impact": "HIGH",
                    "priority": 1,
                    "min_score": 0.0,
                    "max_score": 0.7
                },
                {
                    "description": "Desenvolva uma explicação detalhada do impacto nacional do seu trabalho, com dados e referências concretas",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_score": 0.0,
                    "max_score": 0.8
                },
                {
                    "description": "Vincule seu trabalho às prioridades nacionais atuais dos EUA (ex: segurança, saúde, economia)",
                    "impact": "MEDIUM",
                    "priority": 2,
                    "min_score": 0.5,
                    "max_score": 0.9
                }
            ],
            
            # Recomendações para bem posicionado
            "well_positioned": [
                {
                    "description": "Detalhe sua formação, experiência e recursos específicos que o qualificam excepcionalmente para avançar este trabalho",
                    "impact": "HIGH",
                    "priority": 1,
                    "min_score": 0.0,
                    "max_score": 0.7
                },
                {
                    "description": "Demonstre como seu histórico de sucesso passado prevê sucesso futuro no empreendimento proposto",
                    "impact": "MEDIUM",
                    "priority": 2,
                    "min_score": 0.0,
                    "max_score": 0.8
                }
            ],
            
            # Recomendações para benefício de dispensa
            "benefit_waiver": [
                {
                    "description": "Explique por que o processo padrão de certificação de trabalho seria impraticável no seu caso específico",
                    "impact": "HIGH",
                    "priority": 1,
                    "min_score": 0.0,
                    "max_score": 0.7
                },
                {
                    "description": "Articule razões específicas pelas quais exigir oferta de emprego seria prejudicial ao interesse nacional",
                    "impact": "HIGH",
                    "priority": 2,
                    "min_score": 0.0,
                    "max_score": 0.7
                },
                {
                    "description": "Explique como sua contribuição é urgente ou atende a uma necessidade imediata nos EUA",
                    "impact": "MEDIUM",
                    "priority": 2,
                    "min_score": 0.0,
                    "max_score": 0.8
                }
            ]
        }
    
    def generate_detailed_recommendations(self, 
                                    input_data: EligibilityAssessmentInput,
                                    category_scores: Dict[str, float],
                                    eb2_route_eval: Dict,
                                    niw_eval: Dict) -> List[RecommendationDetail]:
        """
        Gera recomendações detalhadas com categorização, priorização e impacto
        estimado conforme requisitos.
        
        Args:
            input_data: Dados da avaliação para personalização
            category_scores: Pontuações por categoria
            eb2_route_eval: Avaliação das rotas EB2
            niw_eval: Avaliação dos critérios NIW
            
        Returns:
            Lista de recomendações detalhadas
        """
        log_structured_data(scoring_logger, "info", 
                           "Gerando recomendações detalhadas")
        
        all_recommendations = []
        
        # Identificar categorias mais fracas (prioridade para melhoria)
        sorted_categories = sorted(
            category_scores.items(), 
            key=lambda x: x[1]
        )
        
        # Limite máximo de recomendações conforme documentação
        MAX_RECOMMENDATIONS = 10
        
        # 1. Recomendações para melhorar a rota EB2 recomendada
        recommended_route = eb2_route_eval["recommended_route"]
        
        # Se a rota recomendada for Advanced Degree
        if recommended_route == "ADVANCED_DEGREE":
            degree = input_data.education.highest_degree
            
            # Adicionar recomendações específicas para rota de grau avançado
            for rec in self.education_recommendations["advanced_degree"]:
                if rec["for_degree"] == degree or rec["for_degree"] == "ANY":
                    all_recommendations.append(
                        RecommendationDetail(
                            category="EDUCATION",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=rec["priority"],
                            improves_route="ADVANCED_DEGREE"
                        )
                    )
        
        # Se a rota recomendada for Exceptional Ability
        elif recommended_route == "EXCEPTIONAL_ABILITY":
            for rec in self.education_recommendations["exceptional_ability"]:
                if rec["for_degree"] == input_data.education.highest_degree or rec["for_degree"] == "ANY":
                    all_recommendations.append(
                        RecommendationDetail(
                            category="EDUCATION",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=rec["priority"],
                            improves_route="EXCEPTIONAL_ABILITY"
                        )
                    )
            
            # Adicionar recomendações específicas para experiência (critério importante para Exceptional Ability)
            years = input_data.experience.years_of_experience
            for rec in self.experience_recommendations["exceptional_ability"]:
                if years >= rec["min_years"] and years <= rec["max_years"]:
                    all_recommendations.append(
                        RecommendationDetail(
                            category="EXPERIENCE",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=rec["priority"],
                            improves_route="EXCEPTIONAL_ABILITY"
                        )
                    )
        
        # 2. Recomendações para melhorar os critérios NIW mais fracos
        niw_criteria_scores = {
            "merit_importance": niw_eval["subcriteria"]["merit_importance_score"],
            "well_positioned": niw_eval["subcriteria"]["well_positioned_score"],
            "benefit_waiver": niw_eval["subcriteria"]["benefit_waiver_score"]
        }
        
        # Ordenar critérios NIW do mais fraco para o mais forte
        sorted_niw_criteria = sorted(
            niw_criteria_scores.items(), 
            key=lambda x: x[1]
        )
        
        # Adicionar recomendações para o critério NIW mais fraco
        weakest_niw_criterion = sorted_niw_criteria[0][0]
        
        if weakest_niw_criterion == "merit_importance":
            # Recomendações para melhorar mérito e importância nacional
            if category_scores["achievements"] < 0.7:
                # Se publicações são fracas
                pub_count = input_data.achievements.publications_count
                for rec in self.achievements_recommendations["publications"]:
                    if pub_count >= rec["min_count"] and pub_count <= rec["max_count"]:
                        all_recommendations.append(
                            RecommendationDetail(
                                category="ACHIEVEMENTS",
                                description=rec["description"],
                                impact=rec["impact"],
                                priority=rec["priority"],
                                improves_route="NIW"
                            )
                        )
        
        elif weakest_niw_criterion == "well_positioned":
            # Recomendações para demonstrar que está bem posicionado
            if category_scores["experience"] < 0.7:
                years = input_data.experience.years_of_experience
                for rec in self.experience_recommendations["general"]:
                    if years >= rec["min_years"] and years <= rec["max_years"]:
                        all_recommendations.append(
                            RecommendationDetail(
                                category="EXPERIENCE",
                                description=rec["description"],
                                impact=rec["impact"],
                                priority=rec["priority"],
                                improves_route="NIW"
                            )
                        )
        
        # 3. Recomendações gerais para as categorias mais fracas
        weakest_category = sorted_categories[0][0]
        second_weakest_category = sorted_categories[1][0]
        
        # Adicionar recomendações para a categoria mais fraca
        if weakest_category == "education":
            degree = input_data.education.highest_degree
            for rec in self.education_recommendations["advanced_degree"]:
                if (rec["for_degree"] == degree or rec["for_degree"] == "ANY") and rec["impact"] == "HIGH":
                    all_recommendations.append(
                        RecommendationDetail(
                            category="EDUCATION",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=1,  # Alta prioridade por ser a categoria mais fraca
                            improves_route="BOTH"
                        )
                    )
        
        elif weakest_category == "experience":
            years = input_data.experience.years_of_experience
            leadership = input_data.experience.leadership_roles
            
            # Recomendações de experiência geral
            for rec in self.experience_recommendations["general"]:
                if years >= rec["min_years"] and years <= rec["max_years"]:
                    all_recommendations.append(
                        RecommendationDetail(
                            category="EXPERIENCE",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=1,  # Alta prioridade
                            improves_route="BOTH"
                        )
                    )
            
            # Recomendações para liderança
            for rec in self.experience_recommendations["leadership"]:
                if rec["for_leadership"] == leadership:
                    all_recommendations.append(
                        RecommendationDetail(
                            category="EXPERIENCE",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=2,
                            improves_route="BOTH"
                        )
                    )
        
        elif weakest_category == "achievements":
            pub_count = input_data.achievements.publications_count
            patent_count = input_data.achievements.patents_count
            
            # Recomendações para publicações
            for rec in self.achievements_recommendations["publications"]:
                if pub_count >= rec["min_count"] and pub_count <= rec["max_count"]:
                    all_recommendations.append(
                        RecommendationDetail(
                            category="ACHIEVEMENTS",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=1,
                            improves_route="BOTH"
                        )
                    )
            
            # Recomendações para patentes
            for rec in self.achievements_recommendations["patents"]:
                if patent_count >= rec["min_count"] and patent_count <= rec["max_count"]:
                    all_recommendations.append(
                        RecommendationDetail(
                            category="ACHIEVEMENTS",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=2,
                            improves_route="BOTH"
                        )
                    )
        
        elif weakest_category == "recognition":
            awards_count = input_data.recognition.awards_count
            
            # Recomendações para prêmios
            for rec in self.recognition_recommendations["awards"]:
                if awards_count >= rec["min_count"] and awards_count <= rec["max_count"]:
                    all_recommendations.append(
                        RecommendationDetail(
                            category="RECOGNITION",
                            description=rec["description"],
                            impact=rec["impact"],
                            priority=1,
                            improves_route="BOTH"
                        )
                    )
        
        # Adicionar algumas recomendações para a segunda categoria mais fraca
        if second_weakest_category == "recognition" and category_scores["recognition"] < 0.6:
            # Recomendações para palestras e afiliações profissionais
            speaking_count = input_data.recognition.speaking_invitations
            for rec in self.recognition_recommendations.get("speaking", []):
                if hasattr(rec, "min_count") and hasattr(rec, "max_count"):
                    if speaking_count >= rec["min_count"] and speaking_count <= rec["max_count"]:
                        all_recommendations.append(
                            RecommendationDetail(
                                category="RECOGNITION",
                                description=rec["description"],
                                impact=rec["impact"],
                                priority=3,  # Menor prioridade
                                improves_route="BOTH"
                            )
                        )
        
        # Limitar o número total de recomendações e ordenar por prioridade
        all_recommendations.sort(key=lambda x: (x.priority, -len(x.description)))
        final_recommendations = all_recommendations[:MAX_RECOMMENDATIONS]
        
        log_structured_data(scoring_logger, "info", 
                           f"Geradas {len(final_recommendations)} recomendações detalhadas")
        
        return final_recommendations
