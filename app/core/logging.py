import logging
import os
import json
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Dict, Any

# Context variable to track request IDs across asyncio context switches
request_id_context = ContextVar('request_id', default=None)

def get_request_id() -> str:
    """
    Returns the current request ID from the context, or generates a new one if not set.
    
    Returns:
        String UUID for the current request
    """
    current_id = request_id_context.get()
    if current_id is None:
        current_id = str(uuid.uuid4())
        request_id_context.set(current_id)
    return current_id

# Configurar o logger base
def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configura um logger com o nível especificado.
    
    Args:
        name: Nome do logger
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Um objeto logger configurado
    """
    logger = logging.getLogger(name)
    
    # Converter string de nível para constante de logging
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Nível de log inválido: {log_level}')
    
    logger.setLevel(numeric_level)
    
    # Adicionar handler para console se não existir
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Se estamos em produção, também adicionar log para arquivo
        if os.environ.get("ENVIRONMENT", "dev") == "prod":
            log_dir = os.environ.get("LOG_DIR", "/app/logs")
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(
                f"{log_dir}/eligibility-{datetime.now().strftime('%Y-%m-%d')}.log"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger

# Logger para eventos de assessement
assessment_logger = setup_logger("eligibility.assessment", os.environ.get("LOG_LEVEL", "INFO"))

# Logger para eventos de algoritmo de scoring
scoring_logger = setup_logger("eligibility.scoring", os.environ.get("LOG_LEVEL", "INFO"))

# Logger para eventos de recomendação
recommendation_logger = setup_logger("eligibility.recommendation", os.environ.get("LOG_LEVEL", "INFO"))

# Logger para eventos de API
api_logger = setup_logger("eligibility.api", os.environ.get("LOG_LEVEL", "INFO"))

# Logger for eligibility service
eligibility_logger = setup_logger("eligibility.service", os.environ.get("LOG_LEVEL", "INFO"))

# Função helper para serializar logs com informações estruturadas
def log_structured_data(logger: logging.Logger, level: str, message: str, data: Dict[str, Any] = None):
    """
    Loga uma mensagem com dados estruturados adicionais em formato JSON.
    
    Args:
        logger: O logger a ser usado
        level: Nível de log (debug, info, warning, error, critical)
        message: Mensagem de log
        data: Dados estruturados adicionais para incluir no log
    """
    json_data = ""
    if data:
        # Converter data para string JSON
        try:
            json_data = " - " + json.dumps(data, default=str)
        except Exception as e:
            json_data = f" - ERROR serializing data: {str(e)}"
    
    log_method = getattr(logger, level.lower())
    log_method(f"{message}{json_data}")

# Função para log de métricas para monitoramento
def log_metric(name: str, value: float, dimensions: Dict[str, str] = None):
    """
    Loga uma métrica para monitoramento.
    Em produção, esta função enviaria a métrica para Azure Application Insights.
    
    Args:
        name: Nome da métrica
        value: Valor da métrica
        dimensions: Dimensões adicionais da métrica
    """
    # Em ambiente de produção, integrar com Azure App Insights
    if os.environ.get("ENVIRONMENT", "dev") == "prod":
        # TODO: Implementar integração com Azure App Insights
        pass
    
    # Log local para desenvolvimento
    metrics_logger = setup_logger("eligibility.metrics")
    dimension_str = json.dumps(dimensions) if dimensions else "{}"
    metrics_logger.info(f"METRIC: {name}={value} {dimension_str}") 