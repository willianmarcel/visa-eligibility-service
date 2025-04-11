#!/usr/bin/env python3

import logging
import sys
from sqlalchemy import text
from app.db.session import engine, Base
from app.models.eligibility import QuickAssessment
import os
import time
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Número máximo de tentativas para conectar ao banco
MAX_ATTEMPTS = 5
WAIT_SECONDS = 5


@retry(stop=stop_after_attempt(MAX_ATTEMPTS), wait=wait_fixed(WAIT_SECONDS))
def init_db() -> None:
    try:
        logger.info("Tentando conectar ao SQL Server...")
        
        # Testa a conexão
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Conexão estabelecida com sucesso!")
        
        # Cria tabelas se não existirem
        logger.info("Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
        
        return True
    except Exception as e:
        logger.error(f"Falha ao conectar ao banco de dados: {e}")
        raise e


def main() -> None:
    logger.info("Inicializando banco de dados...")
    db_initialized = init_db()
    if db_initialized:
        logger.info("Banco de dados inicializado com sucesso!")
    else:
        logger.error("Falha ao inicializar o banco de dados")
        sys.exit(1)


if __name__ == "__main__":
    main() 