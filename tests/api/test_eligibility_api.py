import pytest
import json
from fastapi import status
from app.schemas.eligibility import EligibilityAssessmentOutput

class TestEligibilityAPI:
    """Testes de integração para a API de avaliação de elegibilidade."""
    
    def test_create_assessment(self, client, mock_auth, sample_assessment_input):
        """Teste para criar uma nova avaliação de elegibilidade."""
        response = client.post(
            "/api/v1/eligibility/assessment",
            json=sample_assessment_input.dict()
        )
        
        assert response.status_code == status.HTTP_201_CREATED, "Deve retornar status 201 Created"
        
        data = response.json()
        assert "assessment_id" in data, "Resposta deve incluir ID da avaliação"
        assert "created_at" in data, "Resposta deve incluir data de criação"
        assert "overall_score" in data, "Resposta deve incluir pontuação geral"
        assert "viability_level" in data, "Resposta deve incluir nível de viabilidade"
        
        # Validar se o modelo de saída é adequado
        assessment_output = EligibilityAssessmentOutput(**data)
        assert assessment_output.overall_score > 0, "Pontuação geral deve ser maior que zero"
    
    def test_get_latest_assessment_not_found(self, client, mock_auth):
        """Teste para buscar a avaliação mais recente quando não existe nenhuma."""
        # Não criar nenhuma avaliação primeiro
        
        response = client.get("/api/v1/eligibility/assessment/latest")
        assert response.status_code == status.HTTP_404_NOT_FOUND, "Deve retornar status 404 Not Found"
    
    def test_get_latest_assessment(self, client, mock_auth, sample_assessment_input):
        """Teste para buscar a avaliação mais recente após criar uma."""
        # Primeiro criar uma avaliação
        client.post(
            "/api/v1/eligibility/assessment",
            json=sample_assessment_input.dict()
        )
        
        # Depois buscar a mais recente
        response = client.get("/api/v1/eligibility/assessment/latest")
        
        assert response.status_code == status.HTTP_200_OK, "Deve retornar status 200 OK"
        
        data = response.json()
        assert "assessment_id" in data, "Resposta deve incluir ID da avaliação"
        assert "category_scores" in data, "Resposta deve incluir pontuações por categoria"
    
    def test_get_assessment_history_empty(self, client, mock_auth):
        """Teste para buscar histórico de avaliações quando não existe nenhuma."""
        response = client.get("/api/v1/eligibility/assessment/history")
        
        assert response.status_code == status.HTTP_200_OK, "Deve retornar status 200 OK"
        
        data = response.json()
        assert isinstance(data, list), "Resposta deve ser uma lista"
        assert len(data) == 0, "Lista deve estar vazia"
    
    def test_get_assessment_history(self, client, mock_auth, sample_assessment_input):
        """Teste para buscar histórico de avaliações após criar algumas."""
        # Criar duas avaliações
        client.post(
            "/api/v1/eligibility/assessment",
            json=sample_assessment_input.dict()
        )
        
        # Modificar um pouco os dados e criar outra
        modified_input = sample_assessment_input.copy()
        modified_input.education.highest_degree = "MASTERS"
        
        client.post(
            "/api/v1/eligibility/assessment",
            json=modified_input.dict()
        )
        
        # Buscar o histórico
        response = client.get("/api/v1/eligibility/assessment/history")
        
        assert response.status_code == status.HTTP_200_OK, "Deve retornar status 200 OK"
        
        data = response.json()
        assert isinstance(data, list), "Resposta deve ser uma lista"
        assert len(data) == 2, "Deve haver duas avaliações no histórico"
        
        # A mais recente deve vir primeiro (ordem decrescente por data)
        assert data[0]["created_at"] > data[1]["created_at"], "Avaliações devem estar ordenadas por data (decrescente)"
    
    def test_different_profiles_get_different_scores(self, client, mock_auth):
        """Teste para verificar se perfis diferentes recebem pontuações diferentes."""
        # Perfil forte
        strong_profile = {
            "education": {
                "highest_degree": "PHD",
                "field_of_study": "Computer Science",
                "university_ranking": 10,
                "years_since_graduation": 5
            },
            "experience": {
                "years_of_experience": 10,
                "leadership_roles": True,
                "specialized_experience": True
            },
            "achievements": {
                "publications_count": 15,
                "patents_count": 3,
                "projects_led": 5,
                "notable_contributions": "Led groundbreaking research"
            },
            "recognition": {
                "awards_count": 4,
                "speaking_invitations": 10,
                "professional_memberships": 3
            },
            "us_plans": "Continue research in AI"
        }
        
        # Perfil fraco
        weak_profile = {
            "education": {
                "highest_degree": "BACHELORS",
                "field_of_study": "Business",
                "university_ranking": 300,
                "years_since_graduation": 1
            },
            "experience": {
                "years_of_experience": 2,
                "leadership_roles": False,
                "specialized_experience": False
            },
            "achievements": {
                "publications_count": 0,
                "patents_count": 0,
                "projects_led": 1,
                "notable_contributions": ""
            },
            "recognition": {
                "awards_count": 0,
                "speaking_invitations": 1,
                "professional_memberships": 0
            },
            "us_plans": "Find a job in the US"
        }
        
        # Avaliar perfil forte
        strong_response = client.post(
            "/api/v1/eligibility/assessment",
            json=strong_profile
        )
        
        # Avaliar perfil fraco
        weak_response = client.post(
            "/api/v1/eligibility/assessment",
            json=weak_profile
        )
        
        strong_data = strong_response.json()
        weak_data = weak_response.json()
        
        assert strong_data["overall_score"] > weak_data["overall_score"], "Perfil forte deve ter pontuação maior que perfil fraco"
        assert strong_data["viability_level"] != weak_data["viability_level"], "Níveis de viabilidade devem ser diferentes"
        
        # O perfil forte deve ter mais pontos fortes
        assert len(strong_data["strengths"]) > len(weak_data["strengths"]), "Perfil forte deve ter mais pontos fortes"
        
        # O perfil fraco deve ter mais pontos fracos
        assert len(weak_data["weaknesses"]) > len(strong_data["weaknesses"]), "Perfil fraco deve ter mais pontos fracos" 