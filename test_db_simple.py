#!/usr/bin/env python3

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

# Formato correto para SQL Server: mssql+pymssql://username:password@server:port/database
raw_url = os.getenv("DATABASE_URL", "")
logger.info(f"URL original: {raw_url}")

# Converter para formato SQLAlchemy
if raw_url.startswith("sqlserver://"):
    # Extrair componentes da URL
    try:
        conn_parts = raw_url.replace("sqlserver://", "").split(";")
        params = {}
        
        for part in conn_parts:
            if "=" in part:
                key, value = part.split("=", 1)
                params[key.strip()] = value.strip()
        
        # Extrair os componentes necessários
        server = params.get("server", "").split(":")[0]  # remove port if present
        port = "1433"  # default SQL Server port
        if ":" in params.get("server", ""):
            port = params.get("server", "").split(":")[1]
            
        database = params.get("database", "")
        user = params.get("user", "")
        password = params.get("password", "")
        
        # Construir URL SQLAlchemy
        DATABASE_URL = f"mssql+pymssql://{user}:{password}@{server}:{port}/{database}"
        logger.info(f"URL convertida: {DATABASE_URL.replace(password, '********')}")
    except Exception as e:
        logger.error(f"Erro ao converter URL: {e}")
        DATABASE_URL = raw_url
else:
    DATABASE_URL = raw_url

def test_connection():
    """Testa a conexão com o SQL Server usando SQLAlchemy."""
    
    logger.info("=== TESTE DE CONEXÃO COM SQL SERVER ===")
    
    try:
        logger.info("Criando engine SQLAlchemy...")
        engine = create_engine(DATABASE_URL)
        
        logger.info("Tentando conectar...")
        with engine.connect() as conn:
            logger.info("Executando consulta de teste...")
            result = conn.execute(text("SELECT 1 AS test_value"))
            row = result.fetchone()
            
            if row and row.test_value == 1:
                logger.info("✅ Conexão SQLAlchemy bem-sucedida!")
                return True
            else:
                logger.error("❌ Falha na consulta SQLAlchemy")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("\n✅ SUCESSO: Conexão com o banco de dados está funcionando corretamente!")
    else:
        print("\n❌ FALHA: Problemas na conexão com o banco de dados!") 