"""
Migração para adicionar campos detalhados de avaliação EB2, NIW e recomendações detalhadas.
"""

from datetime import datetime
import json
from app.db.session import SessionLocal
from app.models.eligibility import QuickAssessment
from app.core.logging import api_logger


def up():
    """
    Adiciona novos campos aos registros existentes e atualiza o esquema da tabela.
    """
    api_logger.info("Iniciando migração para adicionar campos detalhados")
    
    # Criar sessão
    db_session = SessionLocal()
    
    try:
        # Obter todos os registros
        assessments = db_session.query(QuickAssessment).all()
        count = 0
        
        for assessment in assessments:
            # Adicionar campo de rota EB2 se não existir
            if not hasattr(assessment, 'eb2_route') or assessment.eb2_route is None:
                # Valores padrão se não existirem
                if hasattr(assessment, 'data') and assessment.data:
                    data = json.loads(assessment.data) if isinstance(assessment.data, str) else assessment.data
                    
                    # Tentar determinar uma rota recomendada com base nos dados existentes
                    recommended_route = "ADVANCED_DEGREE"  # padrão
                    
                    # Adicionar eb2_route
                    eb2_route = {
                        "recommended_route": recommended_route,
                        "advanced_degree_score": 0.0,
                        "exceptional_ability_score": 0.0,
                        "route_explanation": "Migração de dados: dados originais insuficientes para análise completa."
                    }
                    
                    # Adicionar niw_evaluation
                    niw_evaluation = {
                        "merit_importance_score": 0.0,
                        "well_positioned_score": 0.0,
                        "benefit_waiver_score": 0.0,
                        "niw_overall_score": 0.0
                    }
                    
                    # Adicionar recomendações detalhadas
                    detailed_recommendations = []
                    
                    # Se já existirem recomendações simples, convertê-las para o formato detalhado
                    if "recommendations" in data and data["recommendations"]:
                        for i, rec in enumerate(data["recommendations"]):
                            priority = i + 1
                            detailed_recommendations.append({
                                "category": "GENERAL",
                                "description": rec,
                                "impact": "MEDIUM",
                                "priority": priority,
                                "improves_route": "BOTH"
                            })
                    
                    # Mensagem personalizada e próximos passos
                    message = "Sua avaliação foi atualizada com mais detalhes."
                    next_steps = [
                        "Revise as recomendações detalhadas",
                        "Avalie a rota EB2 sugerida",
                        "Considere os critérios NIW detalhados"
                    ]
                    
                    # Atualizar campos no registro
                    data["eb2_route"] = eb2_route
                    data["niw_evaluation"] = niw_evaluation
                    data["detailed_recommendations"] = detailed_recommendations
                    data["message"] = message
                    data["next_steps"] = next_steps
                    
                    # Estimar tempo de processamento se não existir
                    if "estimated_processing_time" not in data:
                        viability = data.get("viability", "Moderate")
                        if viability == "Strong":
                            data["estimated_processing_time"] = 12
                        elif viability == "Good":
                            data["estimated_processing_time"] = 14
                        elif viability == "Moderate":
                            data["estimated_processing_time"] = 16
                        else:  # Low
                            data["estimated_processing_time"] = 20
                    
                    # Atualizar o campo data serializado
                    assessment.data = json.dumps(data)
                    count += 1
        
        # Commit das alterações
        db_session.commit()
        api_logger.info(f"Migração concluída. {count} registros atualizados.")
    
    except Exception as e:
        db_session.rollback()
        api_logger.error(f"Erro na migração: {e}")
        raise
    finally:
        db_session.close()


def down():
    """
    Reverte as alterações, removendo os campos adicionados.
    """
    api_logger.info("Iniciando reversão da migração")
    
    # Criar sessão
    db_session = SessionLocal()
    
    try:
        # Obter todos os registros
        assessments = db_session.query(QuickAssessment).all()
        count = 0
        
        for assessment in assessments:
            if hasattr(assessment, 'data') and assessment.data:
                data = json.loads(assessment.data) if isinstance(assessment.data, str) else assessment.data
                
                # Remover campos adicionados
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
                
                # Atualizar o campo data serializado
                assessment.data = json.dumps(data)
                count += 1
        
        # Commit das alterações
        db_session.commit()
        api_logger.info(f"Reversão concluída. {count} registros revertidos.")
    
    except Exception as e:
        db_session.rollback()
        api_logger.error(f"Erro na reversão: {e}")
        raise
    finally:
        db_session.close()


if __name__ == "__main__":
    # Executar a migração quando este script for executado diretamente
    up() 