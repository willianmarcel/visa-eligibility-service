#!/usr/bin/env python3

"""
Script para iniciar o serviço de elegibilidade em ambiente de desenvolvimento
com banco de dados SQLite em memória para testes rápidos.
"""

import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Definir ambiente de desenvolvimento
os.environ['ENVIRONMENT'] = 'dev'

def setup_dev_environment():
    """Configurar o ambiente de desenvolvimento."""
    try:
        # Verificar se o banco de dados está configurado
        if not os.getenv('DATABASE_URL'):
            logger.warning("DATABASE_URL não está configurado. Usando SQLite em memória.")
            os.environ['USE_SQLITE'] = 'true'
        
        # Iniciar app em modo desenvolvimento
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8080,
            reload=True,
            log_level="debug"
        )
        
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Iniciando serviço de elegibilidade em modo de desenvolvimento...")
    setup_dev_environment() 