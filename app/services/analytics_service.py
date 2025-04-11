from datetime import datetime
from app.core.logging import log_structured_data, log_metric, eligibility_logger
import logging
import os

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Serviço para registrar eventos de analytics do usuário e métricas do sistema.
    Em produção, integraria com Azure Application Insights ou outro serviço.
    """
    
    def __init__(self):
        """Inicializa o serviço de analytics."""
        self.environment = os.environ.get("ENVIRONMENT", "dev")
    
    async def track_assessment_completed(self, user_id: str, assessment_id: str, score: float, viability: str):
        """
        Registra evento de conclusão de avaliação.
        
        Args:
            user_id: ID do usuário
            assessment_id: ID da avaliação
            score: Pontuação final da avaliação
            viability: Viabilidade calculada
        """
        log_structured_data(eligibility_logger, "info", 
                          f"Registrando evento de avaliação concluída", 
                          {
                              "event": "assessment_completed",
                              "user_id": user_id,
                              "assessment_id": assessment_id,
                              "score": score,
                              "viability": viability,
                              "timestamp": datetime.utcnow().isoformat()
                          })
        
        # Registrar métricas
        log_metric("eligibility.assessments.completed", 1)
        log_metric("eligibility.assessments.score", score)
        
        # Em produção, enviar para Azure Application Insights
        if self.environment == "prod":
            # TODO: Implementar integração com Azure App Insights
            pass
    
    async def track_user_action(self, user_id: str, action: str, metadata: dict = None):
        """
        Registra ação do usuário para análise de comportamento.
        
        Args:
            user_id: ID do usuário
            action: Tipo de ação realizada
            metadata: Metadados adicionais sobre a ação
        """
        event_data = {
            "event": f"user_action_{action}",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            event_data.update(metadata)
        
        log_structured_data(eligibility_logger, "info", 
                          f"Registrando ação do usuário: {action}",
                          event_data)
        
        # Em produção, enviar para Azure Application Insights
        if self.environment == "prod":
            # TODO: Implementar integração com Azure App Insights
            pass 