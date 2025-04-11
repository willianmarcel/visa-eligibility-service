import pytest
from app.services.eb2_route_evaluator import EB2RouteEvaluator
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
def masters_candidate():
    """Candidato com Mestrado e perfil misto acadêmico/profissional."""
    return EligibilityAssessmentInput(
        user_id="test_user_2",
        education=EducationInput(
            highest_degree="MASTERS",
            field_of_study="Mechanical Engineering",
            university_ranking=120,
            years_since_graduation=6,
            professional_license=True
        ),
        experience=ExperienceInput(
            years_of_experience=8,
            leadership_roles=True,
            specialized_experience=True,
            current_position="Engineering Manager"
        ),
        achievements=AchievementsInput(
            publications_count=3,
            patents_count=2,
            projects_led=4
        ),
        recognition=RecognitionInput(
            awards_count=1,
            speaking_invitations=3,
            professional_memberships=1
        ),
        us_plans=USPlansInput(
            proposed_work="Developing innovative clean energy solutions",
            field_of_work="Renewable Energy",
            national_importance="Reducing carbon emissions and energy independence",
            potential_beneficiaries="Energy sector and consumers",
            standard_process_impracticality="Specialized knowledge in emerging field"
        )
    )

@pytest.fixture
def bachelors_experienced_candidate():
    """Candidato com Bacharelado mas experiência profissional extensa."""
    return EligibilityAssessmentInput(
        user_id="test_user_3",
        education=EducationInput(
            highest_degree="BACHELORS",
            field_of_study="Software Engineering",
            university_ranking=200,
            years_since_graduation=12,
            professional_license=False
        ),
        experience=ExperienceInput(
            years_of_experience=12,
            leadership_roles=True,
            specialized_experience=True,
            current_position="Chief Technology Officer"
        ),
        achievements=AchievementsInput(
            publications_count=1,
            patents_count=3,
            projects_led=8
        ),
        recognition=RecognitionInput(
            awards_count=3,
            speaking_invitations=10,
            professional_memberships=3
        ),
        us_plans=USPlansInput(
            proposed_work="Scaling enterprise software solutions",
            field_of_work="Enterprise Software",
            national_importance="Improving business efficiency and competitiveness",
            potential_beneficiaries="US businesses across sectors",
            standard_process_impracticality="Unique combination of skills and experience"
        )
    )

@pytest.fixture
def exceptional_ability_candidate():
    """Candidato com perfil forte para Habilidade Excepcional."""
    return EligibilityAssessmentInput(
        user_id="test_user_4",
        education=EducationInput(
            highest_degree="BACHELORS",
            field_of_study="Marketing",
            university_ranking=None,
            years_since_graduation=15,
            professional_license=True
        ),
        experience=ExperienceInput(
            years_of_experience=15,
            leadership_roles=True,
            specialized_experience=True,
            current_position="Marketing Director",
            salary_level="ABOVE_AVERAGE"
        ),
        achievements=AchievementsInput(
            publications_count=2,
            patents_count=0,
            projects_led=10
        ),
        recognition=RecognitionInput(
            awards_count=5,
            speaking_invitations=15,
            professional_memberships=4,
            media_coverage=True,
            peer_recognition=True
        ),
        us_plans=USPlansInput(
            proposed_work="Innovative marketing strategies for emerging technologies",
            field_of_work="Digital Marketing",
            national_importance="Helping US companies compete globally",
            potential_beneficiaries="Technology sector and digital economy",
            standard_process_impracticality="Unique combination of expertise"
        )
    )

class TestEB2RouteEvaluator:
    """Testes para o avaliador de rotas EB2."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.evaluator = EB2RouteEvaluator()
    
    def test_advanced_degree_phd(self, phd_candidate):
        """Testa avaliação de rota de Grau Avançado para candidato com PhD."""
        score = self.evaluator.evaluate_advanced_degree_route(phd_candidate)
        
        # Um PhD deve ter pontuação muito alta
        assert score > 0.9
        assert score <= 1.0
    
    def test_advanced_degree_masters(self, masters_candidate):
        """Testa avaliação de rota de Grau Avançado para candidato com Mestrado."""
        score = self.evaluator.evaluate_advanced_degree_route(masters_candidate)
        
        # Um Mestrado deve ter pontuação boa
        assert score >= 0.8
        assert score <= 1.0
    
    def test_advanced_degree_bachelors_experienced(self, bachelors_experienced_candidate):
        """Testa avaliação de rota de Grau Avançado para candidato com Bacharelado e muita experiência."""
        score = self.evaluator.evaluate_advanced_degree_route(bachelors_experienced_candidate)
        
        # Bacharelado com muita experiência deve ter pontuação moderada
        assert score >= 0.7
        assert score <= 0.9
    
    def test_exceptional_ability(self, exceptional_ability_candidate):
        """Testa avaliação de rota de Habilidade Excepcional para candidato com perfil adequado."""
        score = self.evaluator.evaluate_exceptional_ability_route(exceptional_ability_candidate)
        
        # Candidato com perfil forte para Habilidade Excepcional deve ter pontuação alta
        assert score >= 0.8
        assert score <= 1.0
    
    def test_exceptional_ability_phd(self, phd_candidate):
        """Testa avaliação de Habilidade Excepcional para candidato com PhD."""
        score = self.evaluator.evaluate_exceptional_ability_route(phd_candidate)
        
        # Candidato com PhD também deve se qualificar razoavelmente bem
        assert score >= 0.5
    
    def test_determine_recommended_route_phd(self, phd_candidate):
        """Testa determinação da rota recomendada para candidato com PhD."""
        advanced_degree_score = self.evaluator.evaluate_advanced_degree_route(phd_candidate)
        exceptional_ability_score = self.evaluator.evaluate_exceptional_ability_route(phd_candidate)
        
        result = self.evaluator.determine_recommended_route(
            advanced_degree_score,
            exceptional_ability_score,
            phd_candidate
        )
        
        # Para PhD, deve recomendar rota de Grau Avançado
        assert result["recommended_route"] == "ADVANCED_DEGREE"
        assert result["advanced_degree_score"] == advanced_degree_score
        assert result["exceptional_ability_score"] == exceptional_ability_score
        assert "doutorado" in result["route_explanation"].lower()
    
    def test_determine_recommended_route_exceptional(self, exceptional_ability_candidate):
        """Testa determinação da rota recomendada para candidato com perfil para Habilidade Excepcional."""
        advanced_degree_score = self.evaluator.evaluate_advanced_degree_route(exceptional_ability_candidate)
        exceptional_ability_score = self.evaluator.evaluate_exceptional_ability_route(exceptional_ability_candidate)
        
        result = self.evaluator.determine_recommended_route(
            advanced_degree_score,
            exceptional_ability_score,
            exceptional_ability_candidate
        )
        
        # Para este perfil, deve recomendar rota de Habilidade Excepcional
        assert result["recommended_route"] == "EXCEPTIONAL_ABILITY"
        assert result["advanced_degree_score"] == advanced_degree_score
        assert result["exceptional_ability_score"] == exceptional_ability_score
        assert "habilidade excepcional" in result["route_explanation"].lower()
    
    def test_edge_case_equal_scores(self, masters_candidate):
        """Testa caso onde as pontuações são muito próximas."""
        # Simular um cenário onde as pontuações são iguais
        advanced_degree_score = 0.75
        exceptional_ability_score = 0.75
        
        result = self.evaluator.determine_recommended_route(
            advanced_degree_score,
            exceptional_ability_score,
            masters_candidate
        )
        
        # Quando empatado, deve preferir a rota de Grau Avançado
        assert result["recommended_route"] == "ADVANCED_DEGREE"
        assert "ligeira" in result["route_explanation"].lower() or "pequena" in result["route_explanation"].lower() 