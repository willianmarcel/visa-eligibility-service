"""
Arquivo de configuração centralizada para o sistema de avaliação de elegibilidade.
Contém todos os parâmetros e valores de threshold usados pelo sistema.
"""

from typing import Dict, List, Any

# Pesos das categorias principais
CATEGORY_WEIGHTS = {
    "education": 0.25,
    "experience": 0.30,
    "achievements": 0.30,
    "recognition": 0.15
}

# Critérios de pontuação para Educação
EDUCATION_CRITERIA = {
    "degree": {
        "weight": 0.50,
        "scores": {
            "PHD": 1.0,
            "MASTERS": 0.8,
            "BACHELORS": 0.5,
            "OTHER": 0.2
        }
    },
    "institution": {
        "weight": 0.20,
        "scores": {
            "TOP_50": 1.0,
            "TOP_200": 0.8,
            "NATIONAL": 0.6,
            "OTHER": 0.4
        }
    },
    "field_relevance": {
        "weight": 0.30,
        "scores": {
            "STEM_HIGH_DEMAND": 1.0,
            "STEM_GENERAL": 0.8,
            "ARTS_BUSINESS_HUMANITIES_NICHE": 0.7,
            "OTHER": 0.5
        }
    }
}

# Critérios de pontuação para Experiência
EXPERIENCE_CRITERIA = {
    "years": {
        "weight": 0.40,
        "thresholds": {
            "10+": {"min": 10, "score": 1.0},
            "7-9": {"min": 7, "max": 9, "score": 0.8},
            "4-6": {"min": 4, "max": 6, "score": 0.6},
            "1-3": {"min": 1, "max": 3, "score": 0.4},
            "<1": {"min": 0, "max": 1, "score": 0.2}
        }
    },
    "leadership": {
        "weight": 0.30,
        "bonus": 0.1
    },
    "specialization": {
        "weight": 0.30,
        "bonus": 0.1
    }
}

# Critérios de pontuação para Realizações
ACHIEVEMENTS_CRITERIA = {
    "publications": {
        "weight": 0.35,
        "thresholds": {
            "high": {"min": 10, "score": 1.0},
            "medium": {"min": 5, "max": 9, "score": 0.8},
            "low": {"min": 1, "max": 4, "score": 0.6},
            "none": {"min": 0, "max": 0, "score": 0.0}
        }
    },
    "patents": {
        "weight": 0.30,
        "thresholds": {
            "high": {"min": 3, "score": 1.0},
            "medium": {"min": 1, "max": 2, "score": 0.7},
            "none": {"min": 0, "max": 0, "score": 0.0}
        }
    },
    "projects": {
        "weight": 0.35,
        "thresholds": {
            "high": {"min": 3, "score": 1.0},
            "medium": {"min": 1, "max": 2, "score": 0.7},
            "none": {"min": 0, "max": 0, "score": 0.1}
        }
    },
    "citations": {
        "bonus_threshold": 100,
        "bonus_score": 0.1
    }
}

# Critérios de pontuação para Reconhecimento
RECOGNITION_CRITERIA = {
    "awards": {
        "weight": 0.40,
        "thresholds": {
            "high": {"min": 3, "score": 0.8},
            "medium": {"min": 1, "max": 2, "score": 0.5},
            "none": {"min": 0, "max": 0, "score": 0.0}
        }
    },
    "speaking": {
        "weight": 0.30,
        "thresholds": {
            "high": {"min": 5, "score": 0.8},
            "medium": {"min": 2, "max": 4, "score": 0.5},
            "low": {"min": 1, "max": 1, "score": 0.3},
            "none": {"min": 0, "max": 0, "score": 0.0}
        }
    },
    "memberships": {
        "weight": 0.30,
        "thresholds": {
            "high": {"min": 2, "score": 0.4},
            "low": {"min": 1, "max": 1, "score": 0.2},
            "none": {"min": 0, "max": 0, "score": 0.0}
        }
    }
}

# Limiares de pontuação para níveis de viabilidade
VIABILITY_THRESHOLDS = {
    "EXCELLENT": 85.0,
    "STRONG": 70.0,
    "PROMISING": 55.0,
    "CHALLENGING": 40.0,
    "INSUFFICIENT": 0.0
}

# Score mínimo considerado "forte" para uma categoria (usado para identificar pontos fortes)
STRENGTH_THRESHOLD = 0.7

# Score máximo considerado "fraco" para uma categoria (usado para identificar pontos fracos)
WEAKNESS_THRESHOLD = 0.5

# Lista de campos STEM para categorização
STEM_HIGH_DEMAND_FIELDS = [
    "computer", "software", "data", "artificial intelligence", 
    "machine learning", "engineer", "quantum", "robotics"
]

STEM_GENERAL_FIELDS = [
    "math", "physics", "chemistry", "biology", "medicine", 
    "technology", "science", "engineering"
]

# Configurações para EB2 Route Evaluator
EB2_CONFIG = {
    "advanced_degree": {
        "education_scores": {
            "PHD": 1.0,
            "MASTERS": 0.9,
            "BACHELORS": {
                "base": 0.4,
                "experience_bonus": {
                    "7+": 0.45,
                    "5-6": 0.4
                }
            }
        },
        "university_ranking_bonus": {
            "TOP_50": 0.1,
            "TOP_100": 0.05
        },
        "stem_field_bonus": 0.05
    },
    "exceptional_ability": {
        "criteria_scores": {
            "5+": 1.0,
            "4": 0.9,
            "3": 0.8,
            "2": 0.5,
            "1": 0.3,
            "0": 0.0
        },
        "score_diff_thresholds": {
            "significant": 0.2,
            "moderate": 0.1,
            "slight": 0.0
        }
    }
}

# Configurações para NIW Evaluator
NIW_CONFIG = {
    "merit_importance": {
        "weights": {
            "relevance": 0.4,
            "impact": 0.4,
            "evidence": 0.2
        },
        "high_importance_keywords": [
            "saúde", "medicina", "cibersegurança", "energia renovável", 
            "inteligência artificial", "segurança", "defesa", "biotecnologia",
            "health", "medicine", "cybersecurity", "renewable energy",
            "artificial intelligence", "security", "defense", "biotechnology",
            "climate", "clima", "pandemic", "pandemia", "cancer", "câncer"
        ],
        "significant_importance_keywords": [
            "education", "educação", "technology", "tecnologia", 
            "innovation", "inovação", "agriculture", "agricultura",
            "infrastructure", "infraestrutura", "economy", "economia"
        ],
        "relevance_scores": {
            "high_importance": 1.0,
            "significant_importance": 0.8,
            "detailed_explanation": 0.7,
            "moderate_explanation": 0.6,
            "limited_explanation": 0.5,
            "minimal_explanation": 0.3
        },
        "impact_weights": {
            "scope": 0.6,
            "clarity": 0.4
        },
        "scope_terms": {
            "broad": ["national", "nationwide", "all americans", "country", "united states", 
                    "population", "millions", "todos", "nacionales", "país"],
            "significant": ["industry", "sector", "community", "communities", "many", 
                          "significant", "substantial", "indústria", "setor", "comunidade", "significativo"]
        },
        "scope_scores": {
            "broad": 1.0,
            "significant": 0.8,
            "limited": 0.6
        },
        "clarity_thresholds": {
            "detailed": {"min_length": 300, "score": 1.0},
            "moderate": {"min_length": 150, "score": 0.8},
            "limited": {"score": 0.6}
        },
        "evidence_thresholds": {
            "strong": {"publications": 10, "patents": 3, "awards": 3, "score": 1.0},
            "moderate": {"publications": 5, "patents": 1, "awards": 1, "score": 0.7},
            "weak": {"score": 0.4}
        }
    },
    "well_positioned": {
        "weights": {
            "qualification": 0.35,
            "success": 0.35,
            "plan": 0.30
        },
        "qualification_scores": {
            "education": {
                "PHD": 1.0,
                "MASTERS": 0.8,
                "BACHELORS": 0.6,
                "OTHER": 0.3
            },
            "experience_bonus": {
                "10+": 0.2,
                "7-9": 0.1
            },
            "specialization_bonus": 0.1
        },
        "success_thresholds": {
            "publications": {
                "high": {"min": 10, "score": 0.4},
                "medium": {"min": 5, "score": 0.3},
                "low": {"min": 1, "score": 0.2}
            },
            "patents": {
                "high": {"min": 3, "score": 0.3},
                "low": {"min": 1, "score": 0.2}
            },
            "projects": {
                "high": {"min": 3, "score": 0.3},
                "low": {"min": 1, "score": 0.2}
            },
            "recognition": {
                "high": {"awards": 3, "speaking": 5, "score": 0.3},
                "low": {"awards": 1, "speaking": 2, "score": 0.2}
            }
        },
        "plan_thresholds": {
            "detailed": {"min_length": 400, "score": 0.7},
            "moderate": {"min_length": 200, "score": 0.5},
            "basic": {"min_length": 100, "score": 0.3},
            "minimal": {"score": 0.1}
        },
        "leadership_bonus": 0.3,
        "experience_bonus": 0.2
    },
    "benefit_waiver": {
        "weights": {
            "urgency": 0.35,
            "impracticality": 0.30,
            "benefit": 0.35
        },
        "urgency_terms": [
            "urgent", "critical", "immediate", "pressing", "crucial", "vital", 
            "urgente", "crítico", "imediato", "urgência", "crucial", "vital",
            "emergency", "crisis", "pandemic", "epidemic", "shortage", "deficit",
            "emergência", "crise", "pandemia", "epidemia", "escassez", "déficit"
        ],
        "urgency_thresholds": {
            "high": {"term_count": 3, "score": 1.0},
            "medium": {"term_count": 2, "score": 0.8},
            "low": {"term_count": 1, "score": 0.7},
            "detailed": {"min_length": 300, "score": 0.6},
            "moderate": {"min_length": 150, "score": 0.5},
            "minimal": {"score": 0.3}
        },
        "impractical_terms": [
            "impractical", "difficult", "challenging", "impossible", "barrier", "obstacle",
            "impraticável", "difícil", "desafiador", "impossível", "barreira", "obstáculo",
            "unique", "singular", "rare", "scarce", "único", "singular", "raro", "escasso",
            "self-employed", "entrepreneur", "autônomo", "empreendedor", "freelance"
        ],
        "impractical_thresholds": {
            "high": {"term_count": 3, "score": 1.0},
            "medium": {"term_count": 2, "score": 0.8},
            "low": {"term_count": 1, "score": 0.7},
            "detailed": {"min_length": 300, "score": 0.6},
            "moderate": {"min_length": 150, "score": 0.5},
            "minimal": {"score": 0.3}
        },
        "profile_strength": {
            "education": {
                "PHD": 0.4,
                "MASTERS": 0.3,
                "BACHELORS": 0.2
            },
            "experience": {
                "10+": 0.3,
                "7-9": 0.2,
                "4-6": 0.1
            },
            "achievements": {
                "publications": {"threshold": 10, "score": 0.2},
                "patents": {"threshold": 2, "score": 0.2},
                "projects": {"threshold": 3, "score": 0.1}
            },
            "recognition": {
                "awards": {"threshold": 2, "score": 0.1},
                "speaking": {"threshold": 5, "score": 0.1}
            }
        }
    },
    "criteria_weights": {
        "merit_importance": 0.35,
        "well_positioned": 0.35,
        "benefit_waiver": 0.30
    }
}

# Configurações para mensagens personalizadas
PERSONAL_MESSAGES = {
    "EXCELLENT": "Seu perfil é excepcionalmente forte para uma petição EB2-NIW. Você tem excelentes chances de sucesso.",
    "STRONG": "Seu perfil mostra forte potencial para uma petição EB2-NIW. Com algumas melhorias direcionadas, você poderia fortalecer seu caso ainda mais.",
    "PROMISING": "Seu perfil tem potencial para uma petição EB2-NIW, mas há áreas que precisam ser fortalecidas para maximizar suas chances.",
    "CHALLENGING": "Sua petição EB2-NIW pode enfrentar desafios. Recomendamos fortalecer significativamente seu perfil antes de prosseguir.",
    "INSUFFICIENT": "Seu perfil atual não parece ser ideal para uma petição EB2-NIW. Considere fortalecer suas qualificações ou explorar outras opções de imigração."
}

# Tempo estimado de processamento em meses
PROCESSING_TIME_ESTIMATES = {
    "EXCELLENT": 6,
    "STRONG": 8,
    "PROMISING": 10,
    "CHALLENGING": 12,
    "INSUFFICIENT": 12
}

# Limite máximo de recomendações
MAX_RECOMMENDATIONS = 7
MIN_RECOMMENDATIONS = 3 