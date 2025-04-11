"""
Configurações para o algoritmo de scoring de elegibilidade.
Este arquivo centraliza todos os parâmetros do algoritmo para facilitar ajustes.
"""

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
        "scores": {
            "10+": 1.0,
            "7-9": 0.8,
            "4-6": 0.6,
            "1-3": 0.4,
            "<1": 0.2
        }
    },
    "leadership": {
        "weight": 0.30,
        "scores": {
            "EXECUTIVE": 1.0,
            "SENIOR_MANAGER": 0.8,
            "MANAGER": 0.6,
            "SENIOR_INDIVIDUAL": 0.4,
            "NONE": 0.2
        }
    },
    "specialization": {
        "weight": 0.30,
        "scores": {
            "NICHE_SPECIALIST": 1.0,
            "GENERAL_SPECIALIST": 0.7,
            "GENERALIST_SOME_SPECIALIZATION": 0.5,
            "GENERALIST": 0.3
        }
    }
}

# Critérios de pontuação para Realizações
ACHIEVEMENTS_CRITERIA = {
    "publications": {
        "weight": 0.35,
        "scores": {
            "10+": 1.0,
            "5-9": 0.8,
            "1-4": 0.6,
            "0": 0.0
        }
    },
    "patents": {
        "weight": 0.30,
        "scores": {
            "3+": 1.0,
            "1-2": 0.7,
            "PENDING": 0.4,
            "0": 0.0
        }
    },
    "projects": {
        "weight": 0.35,
        "scores": {
            "HIGH_IMPACT_3+": 1.0,
            "SIGNIFICANT_1-2": 0.7,
            "CONTRIBUTOR": 0.4,
            "NONE": 0.1
        }
    }
}

# Critérios de pontuação para Reconhecimento
RECOGNITION_CRITERIA = {
    "awards": {
        "weight": 0.40,
        "scores": {
            "INTERNATIONAL": 1.0,
            "NATIONAL": 0.8,
            "REGIONAL": 0.6,
            "INTERNAL": 0.3,
            "NONE": 0.0
        }
    },
    "speaking": {
        "weight": 0.30,
        "scores": {
            "KEYNOTE_INTERNATIONAL": 1.0,
            "SPEAKER_INTERNATIONAL": 0.8,
            "SPEAKER_NATIONAL": 0.6,
            "SPEAKER_LOCAL": 0.3,
            "NONE": 0.0
        }
    },
    "memberships": {
        "weight": 0.30,
        "scores": {
            "BOARD_MEMBER": 1.0,
            "ACTIVE_MEMBER": 0.7,
            "BASIC_MEMBER": 0.4,
            "NONE": 0.0
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

# Limite de recomendações por avaliação
MAX_RECOMMENDATIONS = 5 