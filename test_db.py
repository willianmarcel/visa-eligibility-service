#!/usr/bin/env python3

import pytest
# Skip all tests in this file since pymssql is not available
pytestmark = pytest.mark.skip("Skipping tests due to pymssql not being available")

import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def test_connection():
    """Testa a conexão direta com o SQL Server usando pymssql e SQLAlchemy."""
    
    logger.info("=== TESTE DE CONEXÃO COM SQL SERVER ===")
    
    # 1. Teste com SQLAlchemy
    try:
        logger.info("Testando conexão via SQLAlchemy...")
        
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS test_value"))
            row = result.fetchone()
            
            if row and row.test_value == 1:
                logger.info("✅ Conexão SQLAlchemy bem-sucedida!")
                
                # Obter informações do servidor
                version_info = conn.execute(text("SELECT @@VERSION AS version")).fetchone()
                logger.info(f"Versão do SQL Server: {version_info.version.split('on')[0]}")
                
                # Verificar tabelas disponíveis (se houver)
                try:
                    tables = conn.execute(text(
                        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
                    )).fetchall()
                    if tables:
                        logger.info(f"Tabelas disponíveis: {', '.join([t[0] for t in tables])}")
                    else:
                        logger.info("Não há tabelas disponíveis no banco de dados.")
                except Exception as e:
                    logger.warning(f"Não foi possível listar tabelas: {e}")
                
            else:
                logger.error("❌ Falha na consulta SQLAlchemy")
                return False
                
        return True
    
    except Exception as e:
        logger.error(f"❌ Erro na conexão SQLAlchemy: {e}")
        
        # Tentar diretamente com pymssql para diagnosticar
        try:
            logger.info("Tentando conexão direta via pymssql...")
            # Extrair parâmetros da URL
            conn_params = DATABASE_URL.replace('sqlserver://', '')
            parts = conn_params.split(';')
            
            server = None
            database = None
            user = None
            password = None
            
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    if key == 'server' or key == 'host':
                        server = value
                    elif key == 'database':
                        database = value
                    elif key == 'user':
                        user = value
                    elif key == 'password':
                        password = value
            
            # Conectar diretamente
            conn = pymssql.connect(
                server=server, 
                user=user,
                password=password, 
                database=database
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                logger.info("✅ Conexão pymssql bem-sucedida!")
            else:
                logger.error("❌ Falha na consulta pymssql")
            conn.close()
        except Exception as pymssql_error:
            logger.error(f"❌ Erro também na conexão pymssql: {pymssql_error}")
        
        return False

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        logger.info("✅ SUCESSO: Conexão com o banco de dados está funcionando corretamente!")
    else:
        logger.error("❌ FALHA: Problemas na conexão com o banco de dados!")