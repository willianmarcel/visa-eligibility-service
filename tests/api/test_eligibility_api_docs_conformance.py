import pytest
import json
from fastapi import status
from app.schemas.eligibility import EligibilityAssessmentOutput

class TestEligibilityAPIDocsConformance:
    """
    Testes para validar a conformidade da API de elegibilidade
    com os requisitos especificados na documentação.
    """
    
    def test_assessment_endpoint_response_format(self, client, mock_auth, sample_assessment_input):
        """
        Teste para verificar se o formato de resposta da avaliação de elegibilidade
        está de acordo com o schema especificado na documentação.
        """
        response = client.post(
            "/api/v1/eligibility/assessment",
            json=sample_assessment_input.dict()
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        
        # Verificar campos obrigatórios conforme a documentação
        assert "id" in data, "Resposta deve ter campo 'id'"
        assert "created_at" in data, "Resposta deve ter campo 'created_at'"
        assert "score" in data, "Resposta deve ter campo 'score'"
        assert "viability_level" in data, "Resposta deve ter campo 'viability_level'"
        assert "strengths" in data, "Resposta deve ter campo 'strengths'"
        assert "weaknesses" in data, "Resposta deve ter campo 'weaknesses'"
        assert "recommendations" in data, "Resposta deve ter campo 'recommendations'"
        
        # Verificar estrutura do campo 'score'
        assert "education" in data["score"], "Score deve incluir 'education'"
        assert "experience" in data["score"], "Score deve incluir 'experience'"
        assert "achievements" in data["score"], "Score deve incluir 'achievements'"
        assert "recognition" in data["score"], "Score deve incluir 'recognition'"
        assert "overall" in data["score"], "Score deve incluir 'overall'"
        
        # Verificar se o nível de viabilidade está entre os valores esperados
        assert data["viability_level"] in ["EXCELLENT", "STRONG", "PROMISING", "CHALLENGING", "INSUFFICIENT"], \
            f"Nível de viabilidade deve ser um dos valores esperados, mas foi '{data['viability_level']}'"
    
    def test_detailed_eb2_route_evaluation(self, client, mock_auth):
        """
        Teste para verificar se a resposta inclui a avaliação detalhada das rotas EB2
        conforme especificado na documentação.
        """
        # Criar perfil forte para rota de grau avançado
        advanced_degree_profile = {
            "education": {
                "highest_degree": "PHD",
                "field_of_study": "Computer Science",
                "university_ranking": 30,
                "years_since_graduation": 3,
                "professional_license": False
            },
            "experience": {
                "years_of_experience": 7,
                "leadership_roles": True,
                "specialized_experience": True,
                "current_position": "Senior Researcher"
            },
            "achievements": {
                "publications_count": 10,
                "patents_count": 1,
                "projects_led": 3
            },
            "recognition": {
                "awards_count": 2,
                "speaking_invitations": 5,
                "professional_memberships": 2
            },
            "us_plans": {
                "proposed_work": "Advanced research in AI algorithms",
                "field_of_work": "Artificial Intelligence",
                "national_importance": "Enhancing national security through AI advances",
                "potential_beneficiaries": "Defense sector, technology companies",
                "standard_process_impracticality": "Unique expertise in specialized AI techniques"
            }
        }
        
        response = client.post(
            "/api/v1/eligibility/assessment",
            json=advanced_degree_profile
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        
        # Verificar se a resposta inclui a avaliação de rotas EB2
        assert "eb2_route" in data, "Resposta deve incluir avaliação de rotas EB2"
        if "eb2_route" in data:
            eb2_route = data["eb2_route"]
            assert "recommended_route" in eb2_route, "Deve incluir rota recomendada"
            assert "advanced_degree_score" in eb2_route, "Deve incluir pontuação para rota de grau avançado"
            assert "exceptional_ability_score" in eb2_route, "Deve incluir pontuação para rota de habilidade excepcional"
            assert "route_explanation" in eb2_route, "Deve incluir explicação para a rota recomendada"
            
            # Verificar se neste caso a rota recomendada é ADVANCED_DEGREE
            assert eb2_route["recommended_route"] == "ADVANCED_DEGREE", \
                f"Para PhD, a rota recomendada deve ser ADVANCED_DEGREE, mas foi {eb2_route['recommended_route']}"
    
    def test_niw_criteria_evaluation(self, client, mock_auth):
        """
        Teste para verificar se a resposta inclui a avaliação dos critérios NIW
        conforme especificado na documentação.
        """
        # Criar perfil com forte justificativa para NIW
        niw_profile = {
            "education": {
                "highest_degree": "MASTERS",
                "field_of_study": "Cybersecurity",
                "university_ranking": 50,
                "years_since_graduation": 4,
                "professional_license": True,
                "license_details": "CISSP Certification"
            },
            "experience": {
                "years_of_experience": 9,
                "leadership_roles": True,
                "specialized_experience": True,
                "current_position": "Security Architect"
            },
            "achievements": {
                "publications_count": 5,
                "patents_count": 1,
                "projects_led": 4
            },
            "recognition": {
                "awards_count": 1,
                "speaking_invitations": 6,
                "professional_memberships": 3
            },
            "us_plans": {
                "proposed_work": "Critical infrastructure cybersecurity research",
                "field_of_work": "Critical Infrastructure Protection",
                "national_importance": "Protecting national utilities and infrastructure from cyber attacks",
                "potential_beneficiaries": "Government agencies, utility companies, American public",
                "standard_process_impracticality": "Specialized expertise in a national security field"
            }
        }
        
        response = client.post(
            "/api/v1/eligibility/assessment",
            json=niw_profile
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        
        # Verificar se a resposta inclui a avaliação de critérios NIW
        assert "niw_evaluation" in data, "Resposta deve incluir avaliação de critérios NIW"
        if "niw_evaluation" in data:
            niw_eval = data["niw_evaluation"]
            assert "merit_importance_score" in niw_eval, "Deve incluir pontuação para mérito e importância"
            assert "well_positioned_score" in niw_eval, "Deve incluir pontuação para 'bem posicionado'"
            assert "benefit_waiver_score" in niw_eval, "Deve incluir pontuação para benefício da dispensa"
            assert "niw_overall_score" in niw_eval, "Deve incluir pontuação geral NIW"
            
            # Para este perfil focado em segurança cibernética de infraestrutura crítica, verificar se o score de mérito/importância é alto
            assert niw_eval["merit_importance_score"] >= 0.7, \
                f"Para área de segurança nacional, o score de mérito/importância deve ser alto, mas foi {niw_eval['merit_importance_score']}"
    
    def test_recommendations_follow_documentation_structure(self, client, mock_auth):
        """
        Teste para verificar se as recomendações detalhadas seguem a estrutura
        especificada na documentação.
        """
        # Usar um perfil com pontos fracos óbvios para gerar recomendações
        profile_with_weaknesses = {
            "education": {
                "highest_degree": "BACHELORS",
                "field_of_study": "Computer Science",
                "university_ranking": 150,
                "years_since_graduation": 4
            },
            "experience": {
                "years_of_experience": 4,
                "leadership_roles": False,
                "specialized_experience": True,
                "current_position": "Software Developer"
            },
            "achievements": {
                "publications_count": 0,
                "patents_count": 0,
                "projects_led": 1
            },
            "recognition": {
                "awards_count": 0,
                "speaking_invitations": 0,
                "professional_memberships": 1
            },
            "us_plans": {
                "proposed_work": "Software development for healthcare applications",
                "field_of_work": "Healthcare Technology",
                "national_importance": "Improving healthcare efficiency and outcomes",
                "potential_beneficiaries": "Hospitals, patients, healthcare providers",
                "standard_process_impracticality": "Specialized technical expertise"
            }
        }
        
        response = client.post(
            "/api/v1/eligibility/assessment",
            json=profile_with_weaknesses
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        
        # Verificar se há recomendações detalhadas
        assert "detailed_recommendations" in data, "Resposta deve incluir recomendações detalhadas"
        if "detailed_recommendations" in data and data["detailed_recommendations"]:
            recommendation = data["detailed_recommendations"][0]  # Pegar a primeira recomendação
            
            # Verificar estrutura conforme documentação
            assert "category" in recommendation, "Recomendação deve incluir categoria"
            assert "description" in recommendation, "Recomendação deve incluir descrição"
            assert "impact" in recommendation, "Recomendação deve incluir impacto"
            assert "priority" in recommendation, "Recomendação deve incluir prioridade"
            assert "improves_route" in recommendation, "Recomendação deve incluir rota melhorada"
            
            # Verificar formatos conforme documentação
            assert recommendation["impact"] in ["LOW", "MEDIUM", "HIGH"], \
                f"Impacto deve ser LOW, MEDIUM ou HIGH, mas foi {recommendation['impact']}"
            assert 1 <= recommendation["priority"] <= 5, \
                f"Prioridade deve estar entre 1-5, mas foi {recommendation['priority']}"
            assert recommendation["improves_route"] in ["ADVANCED_DEGREE", "EXCEPTIONAL_ABILITY", "BOTH", "NIW"], \
                f"Rota melhorada deve ser uma das opções válidas, mas foi {recommendation['improves_route']}"
    
    def test_info_endpoint_provides_criteria_description(self, client):
        """
        Teste para verificar se o endpoint /info retorna as informações sobre
        critérios de elegibilidade conforme especificado na documentação.
        """
        response = client.get("/api/v1/eligibility/info")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Verificar a estrutura da resposta conforme documentação
        assert "criteria" in data, "Resposta deve incluir descrição dos critérios"
        assert "weights" in data, "Resposta deve incluir pesos dos critérios"
        assert "viability_levels" in data, "Resposta deve incluir descrição dos níveis de viabilidade"
        
        # Verificar categorias
        criteria = data["criteria"]
        assert "education" in criteria, "Critérios devem incluir educação"
        assert "experience" in criteria, "Critérios devem incluir experiência"
        assert "achievements" in criteria, "Critérios devem incluir realizações"
        assert "recognition" in criteria, "Critérios devem incluir reconhecimento"
        
        # Verificar níveis de viabilidade
        viability_levels = data["viability_levels"]
        assert "Strong" in viability_levels, "Níveis de viabilidade devem incluir 'Strong'"
        assert "Good" in viability_levels, "Níveis de viabilidade devem incluir 'Good'"
        assert "Moderate" in viability_levels, "Níveis de viabilidade devem incluir 'Moderate'"
        assert "Low" in viability_levels, "Níveis de viabilidade devem incluir 'Low'"
    
    def test_assessment_history_endpoint(self, client, mock_auth, sample_assessment_input):
        """
        Teste para verificar se o endpoint de histórico de avaliações
        funciona conforme especificado na documentação.
        """
        # Primeiro, criar algumas avaliações
        client.post(
            "/api/v1/eligibility/assessment",
            json=sample_assessment_input.dict()
        )
        
        # Modificar um pouco o input para criar outra avaliação
        modified_input = sample_assessment_input.dict()
        modified_input["education"]["highest_degree"] = "PHD"
        
        client.post(
            "/api/v1/eligibility/assessment",
            json=modified_input
        )
        
        # Buscar o histórico de avaliações
        response = client.get("/api/v1/eligibility/assessment/history")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Verificar se é uma lista
        assert isinstance(data, list), "Resposta deve ser uma lista"
        assert len(data) == 2, "Deve haver 2 avaliações no histórico"
        
        # Verificar se as avaliações estão ordenadas por data (mais recente primeiro)
        assert data[0]["created_at"] > data[1]["created_at"], "Avaliações devem estar ordenadas por data (decrescente)"
        
        # Verificar se cada avaliação tem a estrutura esperada
        for assessment in data:
            assert "id" in assessment, "Cada avaliação deve ter um ID"
            assert "created_at" in assessment, "Cada avaliação deve ter data de criação"
            assert "score" in assessment, "Cada avaliação deve ter pontuações"
            assert "viability_level" in assessment, "Cada avaliação deve ter nível de viabilidade"
    
    def test_latest_assessment_endpoint(self, client, mock_auth, sample_assessment_input):
        """
        Teste para verificar se o endpoint de avaliação mais recente
        funciona conforme especificado na documentação.
        """
        # Primeiro, criar duas avaliações
        client.post(
            "/api/v1/eligibility/assessment",
            json=sample_assessment_input.dict()
        )
        
        # Modificar o input para criar uma segunda avaliação (que deve ser a mais recente)
        modified_input = sample_assessment_input.dict()
        modified_input["education"]["highest_degree"] = "PHD"
        modified_input["experience"]["years_of_experience"] = 10
        
        client.post(
            "/api/v1/eligibility/assessment",
            json=modified_input
        )
        
        # Buscar a avaliação mais recente
        response = client.get("/api/v1/eligibility/assessment/latest")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Verificar se é a avaliação mais recente (modificada)
        assert data["score"]["education"] > 0.8, "A avaliação mais recente deve ter pontuação alta em educação (PhD)"
        
        # Verificar a estrutura da resposta
        assert "id" in data, "Resposta deve incluir ID"
        assert "created_at" in data, "Resposta deve incluir data de criação"
        assert "score" in data, "Resposta deve incluir pontuações"
        assert "viability_level" in data, "Resposta deve incluir nível de viabilidade"
        assert "strengths" in data, "Resposta deve incluir pontos fortes"
        assert "weaknesses" in data, "Resposta deve incluir pontos fracos"
        assert "recommendations" in data, "Resposta deve incluir recomendações" 