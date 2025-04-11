#!/usr/bin/env python3

import logging
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text
from app.db.session import engine, SessionLocal

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()


def test_connection():
    """Testa a conexão com o banco de dados SQL Server."""
    try:
        logger.info("Testando conexão com SQL Server...")
        
        # Testa conexão básica
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS test_value"))
            row = result.fetchone()
            
            if row and row.test_value == 1:
                logger.info("✅ Conexão básica bem-sucedida")
            else:
                logger.error("❌ Falha na consulta de teste")
                return False
        
        # Testa sessão e transação
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT @@VERSION AS version"))
            version = result.fetchone().version
            logger.info(f"✅ Versão do SQL Server: {version}")
            
            # Testa isolamento de transação
            db.begin()
            db.execute(text("CREATE TABLE #temp_test (id INT)"))
            db.execute(text("INSERT INTO #temp_test VALUES (1)"))
            result = db.execute(text("SELECT COUNT(*) AS count FROM #temp_test"))
            count = result.fetchone().count
            
            if count == 1:
                logger.info("✅ Transação funcionando corretamente")
            else:
                logger.error("❌ Falha no teste de transação")
                return False
                
            # Rollback para limpar
            db.rollback()
            
            logger.info("✅ Todos os testes de conexão passaram com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante teste de sessão: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False


if __name__ == "__main__":
    logger.info("Iniciando teste de conexão com o banco de dados...")
    success = test_connection()
    
    if success:
        logger.info("✅ SUCESSO: Conexão com o banco de dados está funcionando corretamente!")
        sys.exit(0)
    else:
        logger.error("❌ FALHA: Problemas na conexão com o banco de dados!")
        sys.exit(1) 