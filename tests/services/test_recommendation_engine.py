import pytest
from app.services.recommendation_engine import RecommendationEngine
from app.schemas.eligibility import (
    EligibilityAssessmentInput, 
    EducationInput,
    ExperienceInput,
    AchievementsInput,
    RecognitionInput,
    USPlansInput
)

# Fixtures para criar dados de teste
@pytest.fixture
def phd_candidate():
    """Candidato com PhD e forte perfil acadêmico."""
    return EligibilityAssessmentInput(
        user_id="test_user_1",
        education=EducationInput(
            highest_degree="PHD",
            field_of_study="Computer Science",
            university_ranking=30,
            years_since_graduation=3,
            professional_license=False
        ),
        experience=ExperienceInput(
            years_of_experience=5,
            leadership_roles=True,
            specialized_experience=True,
            current_position="Senior Researcher"
        ),
        achievements=AchievementsInput(
            publications_count=12,
            patents_count=1,
            projects_led=2
        ),
        recognition=RecognitionInput(
            awards_count=2,
            speaking_invitations=5,
            professional_memberships=2
        ),
        us_plans=USPlansInput(
            proposed_work="Advanced research in AI for healthcare",
            field_of_work="Artificial Intelligence",
            national_importance="Improving healthcare outcomes with AI",
            potential_beneficiaries="Hospitals and patients across the US",
            standard_process_impracticality="Specialized expertise not readily available"
        )
    )

@pytest.fixture
def bachelors_candidate():
    """Candidato com Bacharelado e perfil mais fraco."""
    return EligibilityAssessmentInput(
        user_id="test_user_2",
        education=EducationInput(
            highest_degree="BACHELORS",
            field_of_study="Business Administration",
            university_ranking=None,
            years_since_graduation=4,
            professional_license=False
        ),
        experience=ExperienceInput(
            years_of_experience=5,
            leadership_roles=False,
            specialized_experience=False,
            current_position="Marketing Analyst"
        ),
        achievements=AchievementsInput(
            publications_count=0,
            patents_count=0,
            projects_led=1
        ),
        recognition=RecognitionInput(
            awards_count=0,
            speaking_invitations=1,
            professional_memberships=1
        ),
        us_plans=USPlansInput(
            proposed_work="Marketing consultancy",
            field_of_work="Marketing",
            national_importance="Helping businesses grow",
            potential_beneficiaries="SMEs in the US",
            standard_process_impracticality="Entrepreneurial aspirations"
        )
    )

class TestRecommendationEngine:
    """Testes para o motor de recomendações."""
    
    def test_generate_detailed_recommendations(self, phd_candidate, bachelors_candidate):
        """Testa a geração de recomendações detalhadas com categorização e priorização."""
        recommendation_engine = RecommendationEngine()
        
        # Preparar dados de entrada
        category_scores = {
            "education": 0.9,
            "experience": 0.6,
            "achievements": 0.7,
            "recognition": 0.5
        }
        
        eb2_route_eval = {
            "recommended_route": "ADVANCED_DEGREE",
            "advanced_degree_score": 0.9,
            "exceptional_ability_score": 0.7,
            "route_explanation": "Seu doutorado proporciona uma base sólida para a rota de Grau Avançado."
        }
        
        niw_eval = {
            "niw_overall_score": 0.75,
            "subcriteria": {
                "merit_importance_score": 0.8,
                "well_positioned_score": 0.7,
                "benefit_waiver_score": 0.6
            },
            "details": {
                "merit_importance": {},
                "well_positioned": {},
                "benefit_waiver": {}
            }
        }
        
        # Testar para candidato com PhD
        recommendations_phd = recommendation_engine.generate_detailed_recommendations(
            phd_candidate,
            category_scores,
            eb2_route_eval,
            niw_eval
        )
        
        # Verificar estrutura das recomendações
        assert len(recommendations_phd) > 0
        assert len(recommendations_phd) <= 10  # Deve respeitar o limite máximo
        
        # Verificar campos das recomendações
        for rec in recommendations_phd:
            assert rec.category in ["EDUCATION", "EXPERIENCE", "ACHIEVEMENTS", "RECOGNITION"]
            assert rec.impact in ["LOW", "MEDIUM", "HIGH"]
            assert 1 <= rec.priority <= 5
            assert rec.improves_route in ["ADVANCED_DEGREE", "EXCEPTIONAL_ABILITY", "BOTH", "NIW"]
            assert len(rec.description) > 10
        
        # Testar ordenamento por prioridade
        priorities = [rec.priority for rec in recommendations_phd]
        assert priorities == sorted(priorities)  # Deve estar ordenado por prioridade
        
        # Testar para candidato com bacharelado
        category_scores_bachelors = {
            "education": 0.5,
            "experience": 0.6,
            "achievements": 0.4,
            "recognition": 0.3
        }
        
        eb2_route_eval_bachelors = {
            "recommended_route": "EXCEPTIONAL_ABILITY",
            "advanced_degree_score": 0.5,
            "exceptional_ability_score": 0.7,
            "route_explanation": "Sua combinação de experiência e habilidades indica maior vantagem pela rota de Habilidade Excepcional."
        }
        
        recommendations_bachelors = recommendation_engine.generate_detailed_recommendations(
            bachelors_candidate,
            category_scores_bachelors,
            eb2_route_eval_bachelors,
            niw_eval
        )
        
        # Deve haver recomendações específicas para melhorar educação
        education_recs = [rec for rec in recommendations_bachelors if rec.category == "EDUCATION"]
        assert len(education_recs) > 0
        
        # Deve haver recomendações para a rota de Habilidade Excepcional
        exceptional_recs = [rec for rec in recommendations_bachelors if rec.improves_route == "EXCEPTIONAL_ABILITY"]
        assert len(exceptional_recs) > 0
        
        # Recomendações de alta prioridade devem ter impacto alto para candidato fraco
        high_priority_recs = [rec for rec in recommendations_bachelors if rec.priority == 1]
        high_impact_high_priority = [rec for rec in high_priority_recs if rec.impact == "HIGH"]
        assert len(high_impact_high_priority) > 0
    
    def test_recommendations_for_weak_niw_criteria(self):
        """Testa que recomendações específicas são geradas para melhorar critério NIW mais fraco."""
        recommendation_engine = RecommendationEngine()
        
        # Criar candidato com perfil fraco em um critério NIW específico
        input_data = EligibilityAssessmentInput(
            user_id="test_user",
            education=EducationInput(
                highest_degree="MASTERS",
                field_of_study="Engineering",
                university_ranking=100,
                years_since_graduation=5,
                professional_license=False
            ),
            experience=ExperienceInput(
                years_of_experience=6,
                leadership_roles=False,
                specialized_experience=True,
                current_position="Engineer"
            ),
            achievements=AchievementsInput(
                publications_count=2,
                patents_count=0,
                projects_led=1
            ),
            recognition=RecognitionInput(
                awards_count=0,
                speaking_invitations=1,
                professional_memberships=1
            ),
            us_plans=USPlansInput(
                proposed_work="Engineering consultancy",
                field_of_work="Engineering",
                national_importance="Improving infrastructure",
                potential_beneficiaries="Engineering companies",
                standard_process_impracticality="Specialized knowledge"
            )
        )
        
        category_scores = {
            "education": 0.7,
            "experience": 0.6,
            "achievements": 0.4,
            "recognition": 0.3
        }
        
        eb2_route_eval = {
            "recommended_route": "ADVANCED_DEGREE",
            "advanced_degree_score": 0.7,
            "exceptional_ability_score": 0.5,
            "route_explanation": "Seu mestrado proporciona uma base para a rota de Grau Avançado."
        }
        
        # Critério de "benefit_waiver" propositalmente baixo
        niw_eval = {
            "niw_overall_score": 0.5,
            "subcriteria": {
                "merit_importance_score": 0.6,
                "well_positioned_score": 0.6,
                "benefit_waiver_score": 0.3  # Este é o critério mais fraco
            },
            "details": {
                "merit_importance": {},
                "well_positioned": {},
                "benefit_waiver": {}
            }
        }
        
        recommendations = recommendation_engine.generate_detailed_recommendations(
            input_data,
            category_scores,
            eb2_route_eval,
            niw_eval
        )
        
        # Deve haver recomendações para categorias de Reconhecimento e Conquistas, que são
        # áreas fracas e que indiretamente ajudam a melhorar o critério NIW de benefício de dispensa
        recognition_recs = [rec for rec in recommendations if rec.category == "RECOGNITION"]
        achievements_recs = [rec for rec in recommendations if rec.category == "ACHIEVEMENTS"]
        assert len(recognition_recs) > 0 or len(achievements_recs) > 0
        
        # Deve haver pelo menos uma recomendação de alta prioridade (1-2) para áreas fracas
        high_priority_recs = [rec for rec in recommendations if rec.priority <= 2]
        assert len(high_priority_recs) > 0 