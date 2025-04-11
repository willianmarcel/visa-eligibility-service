"""
Script para migração segura do banco de dados.
Este script adiciona as novas colunas ao modelo QuickAssessment sem perder dados existentes.
"""

#!/usr/bin/env python
import sys
import os

# Adicionar o diretório raiz ao path para facilitar imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
import logging
from app.db.session import DATABASE_URL
import traceback

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """
    Aplica migrações ao banco de dados para adicionar novas colunas necessárias.
    """
    logger.info("Iniciando migração do banco de dados...")
    
    try:
        # Conectar ao banco de dados
        engine = create_engine(DATABASE_URL)
        
        # Verificar se a conexão está funcionando
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Conexão com o banco de dados estabelecida com sucesso.")
            
            # Verificar se a tabela quick_assessments existe
            table_exists = connection.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'quick_assessments')"
            )).scalar()
            
            if not table_exists:
                logger.error("A tabela quick_assessments não existe. É necessário inicializar o banco de dados primeiro.")
                return False
            
            # Verificar se as colunas já existem
            columns = connection.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'quick_assessments'"
            )).scalars().all()
            
            # Colunas a serem adicionadas se não existirem
            columns_to_add = []
            
            if 'eb2_route_evaluation' not in columns:
                columns_to_add.append(('eb2_route_evaluation', 'JSONB'))
                logger.info("Coluna eb2_route_evaluation será adicionada.")
                
            if 'niw_evaluation' not in columns:
                columns_to_add.append(('niw_evaluation', 'JSONB'))
                logger.info("Coluna niw_evaluation será adicionada.")
                
            if 'detailed_recommendations' not in columns:
                columns_to_add.append(('detailed_recommendations', 'JSONB'))
                logger.info("Coluna detailed_recommendations será adicionada.")
                
            if 'next_steps' not in columns:
                columns_to_add.append(('next_steps', 'JSONB'))
                logger.info("Coluna next_steps será adicionada.")
                
            if 'message' not in columns:
                columns_to_add.append(('message', 'TEXT'))
                logger.info("Coluna message será adicionada.")
                
            if 'estimated_processing_time' not in columns:
                columns_to_add.append(('estimated_processing_time', 'INTEGER'))
                logger.info("Coluna estimated_processing_time será adicionada.")
                
            if 'processing_time_ms' not in columns:
                columns_to_add.append(('processing_time_ms', 'INTEGER'))
                logger.info("Coluna processing_time_ms será adicionada.")
            
            # Adicionar as colunas
            for column_name, column_type in columns_to_add:
                try:
                    connection.execute(text(
                        f"ALTER TABLE quick_assessments ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                    ))
                    # Commit explicitamente a alteração
                    connection.commit()
                    logger.info(f"Coluna {column_name} adicionada com sucesso.")
                except Exception as e:
                    logger.error(f"Erro ao adicionar coluna {column_name}: {e}")
                    return False
                    
            # Se chegou aqui é porque a migração foi bem sucedida
            logger.info("Migração do banco de dados concluída com sucesso!")
            return True
            
    except Exception as e:
        logger.error(f"Erro durante a migração do banco de dados: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if migrate_database():
        logger.info("Migração concluída com sucesso.")
        sys.exit(0)
    else:
        logger.error("A migração falhou.")
        sys.exit(1)
