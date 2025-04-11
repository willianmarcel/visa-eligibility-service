"""
Script para migração segura do banco de dados.
Este script adiciona as novas colunas ao modelo QuickAssessment sem perder dados existentes.
"""

import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar engine de conexão
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

# Criar fábrica de sessões
AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def check_if_column_exists(session, table_name, column_name):
    """Verifica se uma coluna existe na tabela."""
    query = text(f"""
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        AND column_name = '{column_name}'
    );
    """)
    
    result = await session.execute(query)
    return result.scalar()

async def add_column_if_not_exists(session, table_name, column_name, column_type):
    """Adiciona uma coluna se ela não existir."""
    exists = await check_if_column_exists(session, table_name, column_name)
    
    if not exists:
        logger.info(f"Adicionando coluna {column_name} à tabela {table_name}")
        
        query = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
        await session.execute(query)
        
        logger.info(f"Coluna {column_name} adicionada com sucesso")
    else:
        logger.info(f"Coluna {column_name} já existe na tabela {table_name}")

async def migrate_database():
    """Executa a migração do banco de dados."""
    logger.info("Iniciando migração do banco de dados")
    
    async with AsyncSessionLocal() as session:
        # Iniciar transação
        async with session.begin():
            logger.info("Verificando e adicionando novas colunas à tabela quick_assessments")
            
            # Novas colunas para avaliação EB2 e NIW
            await add_column_if_not_exists(session, "quick_assessments", "eb2_route_evaluation", "JSONB")
            await add_column_if_not_exists(session, "quick_assessments", "niw_evaluation", "JSONB")
            
            # Colunas para resultados expandidos
            await add_column_if_not_exists(session, "quick_assessments", "detailed_recommendations", "JSONB")
            await add_column_if_not_exists(session, "quick_assessments", "next_steps", "JSONB")
            await add_column_if_not_exists(session, "quick_assessments", "message", "TEXT")
            
            # Colunas para metadados adicionais
            await add_column_if_not_exists(session, "quick_assessments", "estimated_processing_time", "INTEGER")
            await add_column_if_not_exists(session, "quick_assessments", "processing_time_ms", "INTEGER")
            
            # Commit das alterações
            await session.commit()
            
    logger.info("Migração do banco de dados concluída com sucesso")

if __name__ == "__main__":
    # Executar migração
    loop = asyncio.get_event_loop()
    loop.run_until_complete(migrate_database())
