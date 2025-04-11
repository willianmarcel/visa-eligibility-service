import pytest
import asyncio
from unittest.mock import MagicMock, patch
from app.services.eligibility_service import EligibilityService
from app.services.scoring_engine import ScoringEngine
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
def strong_candidate():
    """Candidato com perfil forte para EB2-NIW."""
    return EligibilityAssessmentInput(
        user_id="test_user_1",
        education=EducationInput(
            highest_degree="PHD",
            field_of_study="Computer Science",
            university_ranking=25,
            years_since_graduation=3,
            professional_license=False
        ),
        experience=ExperienceInput(
            years_of_experience=8,
            leadership_roles=True,
            specialized_experience=True,
            current_position="Senior Researcher"
        ),
        achievements=AchievementsInput(
            publications_count=15,
            patents_count=2,
            projects_led=3,
            citations_count=200
        ),
        recognition=RecognitionInput(
            awards_count=3,
            speaking_invitations=8,
            professional_memberships=2
        ),
        us_plans=USPlansInput(
            proposed_work="Advanced AI research for healthcare applications",
            field_of_work="Artificial Intelligence",
            national_importance="Improve healthcare outcomes with AI technology",
            potential_beneficiaries="Healthcare providers and patients across the US",
            standard_process_impracticality="Highly specialized AI expertise"
        )
    )

@pytest.fixture
def moderate_candidate():
    """Candidato com perfil moderado para EB2-NIW."""
    return EligibilityAssessmentInput(
        user_id="test_user_2",
        education=EducationInput(
            highest_degree="MASTERS",
            field_of_study="Civil Engineering",
            university_ranking=150,
            years_since_graduation=6,
            professional_license=True
        ),
        experience=ExperienceInput(
            years_of_experience=7,
            leadership_roles=True,
            specialized_experience=False,
            current_position="Project Manager"
        ),
        achievements=AchievementsInput(
            publications_count=2,
            patents_count=0,
            projects_led=5
        ),
        recognition=RecognitionInput(
            awards_count=1,
            speaking_invitations=3,
            professional_memberships=1
        ),
        us_plans=USPlansInput(
            proposed_work="Infrastructure development consulting",
            field_of_work="Civil Engineering",
            national_importance="Improving critical infrastructure",
            potential_beneficiaries="Communities needing infrastructure improvements",
            standard_process_impracticality="Specialized experience in large projects"
        )
    )

@pytest.fixture
def weak_candidate():
    """Candidato com perfil fraco para EB2-NIW."""
    return EligibilityAssessmentInput(
        user_id="test_user_3",
        education=EducationInput(
            highest_degree="BACHELORS",
            field_of_study="Business",
            university_ranking=None,
            years_since_graduation=2,
            professional_license=False
        ),
        experience=ExperienceInput(
            years_of_experience=3,
            leadership_roles=False,
            specialized_experience=False,
            current_position="Marketing Specialist"
        ),
        achievements=AchievementsInput(
            publications_count=0,
            patents_count=0,
            projects_led=1
        ),
        recognition=RecognitionInput(
            awards_count=0,
            speaking_invitations=1,
            professional_memberships=0
        ),
        us_plans=USPlansInput(
            proposed_work="General marketing services",
            field_of_work="Marketing",
            national_importance="Support for businesses",
            potential_beneficiaries="Small businesses",
            standard_process_impracticality="Personal preference"
        )
    )

@pytest.fixture
def mock_eligibility_service():
    """Mock para o serviço de elegibilidade."""
    with patch('app.services.eligibility_service.DBManager') as mock_db_manager, \
         patch('app.services.eligibility_service.AnalyticsService') as mock_analytics:
        # Configurar mocks
        mock_db_manager_instance = MagicMock()
        mock_db_manager.return_value = mock_db_manager_instance
        mock_db_manager_instance.create_assessment.return_value = None
        
        mock_analytics_instance = MagicMock()
        mock_analytics.return_value = mock_analytics_instance
        mock_analytics_instance.track_assessment_completed.return_value = None
        
        # Criar serviço
        service = EligibilityService()
        
        yield service


class TestEligibilityIntegration:
    """Testes de integração para o fluxo completo de avaliação de elegibilidade."""
    
    @pytest.mark.asyncio
    async def test_assess_eligibility_strong_candidate(self, strong_candidate, mock_eligibility_service):
        """Testa o fluxo completo para um candidato forte."""
        # Executar avaliação
        result = await mock_eligibility_service.assess_eligibility(strong_candidate)
        
        # Verificar estrutura da resposta
        assert result.id is not None
        assert result.user_id == strong_candidate.user_id
        assert result.created_at is not None
        
        # Verificar pontuações - a escala real do sistema é 0.0-1.0 para cada categoria
        # e 0-100 para o score geral
        assert 70 <= result.score.overall <= 100  # Deve ter score alto
        assert 0.8 <= result.score.education <= 1.0  # PhD deve ter pontuação alta
        
        # Verificar avaliação EB2
        assert result.eb2_route is not None
        assert result.eb2_route.recommended_route in ["ADVANCED_DEGREE", "EXCEPTIONAL_ABILITY"]
        assert result.eb2_route.advanced_degree_score > 0.8  # PhD deve ter pontuação alta
        assert len(result.eb2_route.route_explanation) > 10
        
        # Verificar avaliação NIW
        assert result.niw_evaluation is not None
        assert 0.68 <= result.niw_evaluation.niw_overall_score <= 1.0  # Deve ter score NIW adequado
        assert 0.7 <= result.niw_evaluation.merit_importance_score <= 1.0
        
        # Verificar viabilidade
        assert result.viability_level in ["EXCELLENT", "STRONG"]
        
        # Verificar recomendações
        assert len(result.detailed_recommendations) > 0
        assert all(isinstance(rec.description, str) and len(rec.description) > 10 for rec in result.detailed_recommendations)
        assert all(rec.impact in ["LOW", "MEDIUM", "HIGH"] for rec in result.detailed_recommendations)
        assert all(1 <= rec.priority <= 5 for rec in result.detailed_recommendations)
        
        # Verificar próximos passos e mensagem
        assert len(result.next_steps) > 0
        assert result.message is not None
    
    @pytest.mark.asyncio
    async def test_assess_eligibility_moderate_candidate(self, moderate_candidate, mock_eligibility_service):
        """Testa o fluxo completo para um candidato com perfil moderado."""
        # Executar avaliação
        result = await mock_eligibility_service.assess_eligibility(moderate_candidate)
        
        # Verificar estrutura da resposta
        assert result.id is not None
        assert result.user_id == moderate_candidate.user_id
        
        # Verificar pontuações
        assert 50 <= result.score.overall <= 80  # Deve ter score moderado
        
        # Verificar viabilidade
        assert result.viability_level in ["PROMISING", "STRONG"]
        
        # Verificar recomendações - deve ter mais recomendações de alta prioridade
        high_priority_recs = [rec for rec in result.detailed_recommendations if rec.priority <= 2]
        assert len(high_priority_recs) >= 2
    
    @pytest.mark.asyncio
    async def test_assess_eligibility_weak_candidate(self, weak_candidate, mock_eligibility_service):
        """Testa o fluxo completo para um candidato com perfil fraco."""
        # Executar avaliação
        result = await mock_eligibility_service.assess_eligibility(weak_candidate)
        
        # Verificar estrutura da resposta
        assert result.id is not None
        assert result.user_id == weak_candidate.user_id
        
        # Verificar pontuações
        assert result.score.overall <= 50  # Deve ter score baixo
        
        # Verificar viabilidade
        assert result.viability_level in ["CHALLENGING", "INSUFFICIENT"]
        
        # Verificar recomendações - deve ter recomendações de alta prioridade
        high_priority_recs = [rec for rec in result.detailed_recommendations if rec.priority == 1]
        assert len(high_priority_recs) >= 2
        
        # Verificar que existem recomendações de educação (ponto fraco típico)
        education_recs = [rec for rec in result.detailed_recommendations if rec.category == "EDUCATION"]
        assert len(education_recs) > 0
    
    @pytest.mark.asyncio
    async def test_assess_eligibility_response_format(self, strong_candidate, mock_eligibility_service):
        """Testa se o formato da resposta segue o schema esperado."""
        # Executar avaliação
        result = await mock_eligibility_service.assess_eligibility(strong_candidate)
        
        # Verificar todos os campos obrigatórios do schema
        required_fields = [
            "id", "user_id", "created_at", "score", "eb2_route", "niw_evaluation",
            "viability_level", "viability", "probability", "strengths", "weaknesses",
            "recommendations", "detailed_recommendations", "next_steps", "message",
            "estimated_processing_time"
        ]
        
        # Verificar que todos os campos obrigatórios estão presentes
        for field in required_fields:
            assert hasattr(result, field), f"Campo obrigatório {field} não encontrado na resposta"
        
        # Verificar subcampos de score
        score_fields = ["education", "experience", "achievements", "recognition", "overall"]
        for field in score_fields:
            assert hasattr(result.score, field), f"Campo {field} não encontrado em score"
        
        # Verificar subcampos de eb2_route
        eb2_fields = ["recommended_route", "advanced_degree_score", "exceptional_ability_score", "route_explanation"]
        for field in eb2_fields:
            assert hasattr(result.eb2_route, field), f"Campo {field} não encontrado em eb2_route"
        
        # Verificar subcampos de niw_evaluation
        niw_fields = ["merit_importance_score", "well_positioned_score", "benefit_waiver_score", "niw_overall_score"]
        for field in niw_fields:
            assert hasattr(result.niw_evaluation, field), f"Campo {field} não encontrado em niw_evaluation" 