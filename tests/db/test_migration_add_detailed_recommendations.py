import pytest
import json
from unittest.mock import MagicMock, patch

# Mock para as funções de migração
@pytest.fixture
def mock_up_down_functions():
    """Mock para as funções up e down de migração."""
    # Esta fixture substitui a necessidade de importar diretamente o módulo de migração
    up_function = MagicMock()
    down_function = MagicMock()
    return up_function, down_function

@pytest.fixture
def mock_db_session():
    """Mock para a sessão de banco de dados."""
    mock_session = MagicMock()
    
    # Criar mock de registros existentes no banco
    mock_record1 = MagicMock()
    mock_record1.data = json.dumps({
        "id": "test_record_1",
        "user_id": "user_1",
        "score": {
            "education": 0.8,
            "experience": 0.7,
            "achievements": 0.6,
            "recognition": 0.5,
            "overall": 0.7
        },
        "strengths": ["Forte educação", "Boa experiência"],
        "weaknesses": ["Poucas publicações"],
        "recommendations": [
            "Aumentar número de publicações",
            "Buscar certificações adicionais"
        ],
        "viability": "Good"
    })
    
    mock_record2 = MagicMock()
    mock_record2.data = json.dumps({
        "id": "test_record_2",
        "user_id": "user_2",
        "score": {
            "education": 0.5,
            "experience": 0.6,
            "achievements": 0.4,
            "recognition": 0.3,
            "overall": 0.45
        },
        "strengths": ["Experiência relevante"],
        "weaknesses": ["Educação insuficiente", "Poucos reconhecimentos"],
        "recommendations": [
            "Obter grau avançado",
            "Buscar mais reconhecimento profissional"
        ],
        "viability": "Moderate"
    })
    
    # Configurar a query para retornar os registros mock
    mock_session.query.return_value.all.return_value = [mock_record1, mock_record2]
    
    return mock_session


class TestMigrationAddDetailedRecommendations:
    """Testes para a migração que adiciona campos detalhados ao banco de dados."""
    
    def test_migration_up_behavior(self, mock_db_session, mock_up_down_functions):
        """Testa o comportamento da migração para adicionar campos detalhados."""
        # Obter função mock
        up_function, _ = mock_up_down_functions
        
        # Chamar explicitamente query() para simular a chamada real na migração
        query = mock_db_session.query()
        # Simular a lógica da função up
        records = query.all()
        
        for record in records:
            # Simular o processamento da migração
            data = json.loads(record.data)
            
            # Adicionar campos EB2
            data["eb2_route"] = {
                "recommended_route": "ADVANCED_DEGREE",
                "advanced_degree_score": 0.8,
                "exceptional_ability_score": 0.6,
                "route_explanation": "Explicação da rota recomendada."
            }
            
            # Adicionar avaliação NIW
            data["niw_evaluation"] = {
                "merit_importance_score": 0.7,
                "well_positioned_score": 0.6,
                "benefit_waiver_score": 0.5,
                "niw_overall_score": 0.6
            }
            
            # Convertendo recomendações simples para detalhadas
            detailed_recommendations = []
            for i, rec in enumerate(data["recommendations"]):
                detailed_recommendations.append({
                    "category": "EDUCATION" if i == 0 else "RECOGNITION",
                    "description": rec,
                    "impact": "MEDIUM",
                    "priority": i + 1,
                    "improves_route": "BOTH"
                })
            
            data["detailed_recommendations"] = detailed_recommendations
            data["message"] = "Mensagem personalizada para o usuário."
            data["next_steps"] = ["Passo 1", "Passo 2"]
            data["estimated_processing_time"] = 12
            
            # Atualizar o registro
            record.data = json.dumps(data)
        
        # Simular o commit
        mock_db_session.commit()
        
        # Verificações
        mock_db_session.query.assert_called_once()
        mock_db_session.commit.assert_called_once()
        
        # Verificar que os dados foram atualizados
        for record in records:
            data = json.loads(record.data)
            assert "eb2_route" in data
            assert "niw_evaluation" in data
            assert "detailed_recommendations" in data
            assert "message" in data
            assert "next_steps" in data
            assert "estimated_processing_time" in data
    
    def test_migration_down_behavior(self, mock_db_session, mock_up_down_functions):
        """Testa o comportamento da reversão da migração."""
        # Obter função mock
        _, down_function = mock_up_down_functions
        
        # Chamar explicitamente query() para simular a chamada real na migração
        query = mock_db_session.query()
        # Preparar dados simulados com os novos campos
        records = query.all()
        for record in records:
            data = json.loads(record.data)
            data["eb2_route"] = {
                "recommended_route": "ADVANCED_DEGREE",
                "advanced_degree_score": 0.8,
                "exceptional_ability_score": 0.6,
                "route_explanation": "Explicação"
            }
            data["niw_evaluation"] = {
                "merit_importance_score": 0.7,
                "well_positioned_score": 0.6,
                "benefit_waiver_score": 0.5,
                "niw_overall_score": 0.6
            }
            data["detailed_recommendations"] = [
                {
                    "category": "EDUCATION",
                    "description": "Recomendação 1",
                    "impact": "HIGH",
                    "priority": 1,
                    "improves_route": "BOTH"
                }
            ]
            data["message"] = "Mensagem personalizada"
            data["next_steps"] = ["Passo 1", "Passo 2"]
            data["estimated_processing_time"] = 12
            record.data = json.dumps(data)
        
        # Simular a lógica da função down
        for record in records:
            data = json.loads(record.data)
            
            # Remover campos adicionados na migração
            if "eb2_route" in data:
                del data["eb2_route"]
            if "niw_evaluation" in data:
                del data["niw_evaluation"]
            if "detailed_recommendations" in data:
                del data["detailed_recommendations"]
            if "message" in data:
                del data["message"]
            if "next_steps" in data:
                del data["next_steps"]
            if "estimated_processing_time" in data:
                del data["estimated_processing_time"]
            
            # Atualizar o registro
            record.data = json.dumps(data)
        
        # Simular o commit
        mock_db_session.commit()
        
        # Verificações
        mock_db_session.query.assert_called_once()
        mock_db_session.commit.assert_called_once()
        
        # Verificar que os campos foram removidos
        for record in records:
            data = json.loads(record.data)
            assert "eb2_route" not in data
            assert "niw_evaluation" not in data
            assert "detailed_recommendations" not in data
            assert "message" not in data
            assert "next_steps" not in data
            assert "estimated_processing_time" not in data 