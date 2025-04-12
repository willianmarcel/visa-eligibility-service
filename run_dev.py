#!/usr/bin/env python3

"""
Script para iniciar o serviço de elegibilidade em ambiente de desenvolvimento
"""

import os
import sys
import uvicorn
import logging
import argparse
from dotenv import load_dotenv
import subprocess

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Inicia o serviço de elegibilidade em modo de desenvolvimento")
    parser.add_argument("--force", action="store_true", help="Força a inicialização mesmo sem banco de dados (apenas para testes)")
    parser.add_argument("--setup-env", action="store_true", help="Configura variáveis de ambiente padrão se necessário")
    return parser.parse_args()

def check_postgres():
    """Verifica se o PostgreSQL está disponível."""
    try:
        # Verificar se o container do Docker está rodando
        process = subprocess.run(
            ["docker", "ps", "--filter", "name=eligibility-postgres", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if "eligibility-postgres" in process.stdout:
            logger.info("Container PostgreSQL encontrado e rodando.")
            return True
        else:
            logger.warning("Container PostgreSQL não encontrado ou não está rodando.")
            return False
    except Exception as e:
        logger.warning(f"Erro ao verificar status do PostgreSQL: {e}")
        return False

def setup_environment():
    """Configura variáveis de ambiente se necessário."""
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Verificar se DATABASE_URL está configurada
    if not os.getenv('DATABASE_URL'):
        # Configurar variável de ambiente padrão
        os.environ['DATABASE_URL'] = "postgresql://postgres:postgres@localhost:5432/visadev"
        logger.info("Configurada DATABASE_URL padrão: postgresql://postgres:postgres@localhost:5432/visadev")
    else:
        logger.info(f"DATABASE_URL já configurada: {os.getenv('DATABASE_URL')}")
    
    # Definir ambiente de desenvolvimento
    os.environ['ENVIRONMENT'] = 'dev'
    logger.info("Ambiente configurado como: dev")

def setup_dev_environment(force=False):
    """Configurar o ambiente de desenvolvimento."""
    try:
        # Verificar se o banco de dados está disponível
        postgres_available = check_postgres()
        
        if not postgres_available and not force:
            logger.error("PostgreSQL não está disponível. Inicie o contêiner ou use --force para continuar.")
            return False
        
        # Agora podemos importar init_db após as variáveis de ambiente estarem configuradas
        from app.db.session import init_db
        
        # Initialize database tables
        try:
            logger.info("Inicializando tabelas do banco de dados...")
            init_db()
            logger.info("Tabelas do banco de dados inicializadas com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            if not force:
                return False
            else:
                logger.warning("Continuando sem banco de dados (APENAS PARA TESTES)")
        
        # Iniciar app em modo desenvolvimento
        logger.info("Iniciando servidor FastAPI...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8080,
            reload=True,
            log_level="debug"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor: {e}")
        return False

if __name__ == "__main__":
    args = parse_args()
    logger.info("Iniciando serviço de elegibilidade em modo de desenvolvimento...")
    
    # Configurar ambiente
    setup_environment()
    
    # Iniciar servidor
    if not setup_dev_environment(force=args.force):
        logger.error("Falha ao iniciar serviço de elegibilidade.")
        sys.exit(1) 