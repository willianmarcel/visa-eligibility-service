from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
from app.core.config import settings
from app.models.base import Base
import logging
from dotenv import load_dotenv, find_dotenv

# Configurar logging básico para diagnóstico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Diagnóstico: Imprimir o diretório atual de trabalho
logger.info(f"Diretório atual: {os.getcwd()}")

# Carregar variáveis de ambiente, forçando o carregamento explícito do arquivo .env
dotenv_path = find_dotenv()
logger.info(f"Arquivo .env encontrado em: {dotenv_path}")
load_dotenv(dotenv_path)

# Diagnóstico: Imprimir todas as variáveis de ambiente disponíveis
logger.info("Variáveis de ambiente disponíveis:")
for key, value in os.environ.items():
    if 'DATABASE' in key and 'URL' in key:
        # Mascarar senha se presente
        if 'postgres:' in str(value):
            masked = str(value).replace('postgres:postgres', 'postgres:********')
            logger.info(f"{key} = {masked}")
        else:
            logger.info(f"{key} = {value}")

# Verificar DATABASE_URL nas variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("DATABASE_URL não encontrada no ambiente após carregar .env")
    
    # Definir DATABASE_URL explicitamente
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/visadev"
    os.environ["DATABASE_URL"] = DATABASE_URL
    logger.info(f"DATABASE_URL definida explicitamente: {DATABASE_URL}")

# Log da URL que será usada
logger.info(f"Usando DATABASE_URL: {DATABASE_URL}")

# Verificar ambiente de execução
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
logger.info(f"Ambiente de execução: {ENVIRONMENT}")

# Criar engine de banco de dados
try:
    # Usar PostgreSQL
    logger.info(f"Conectando ao PostgreSQL usando {DATABASE_URL}...")
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        echo=ENVIRONMENT == "dev"
    )
    
    # Testar conexão
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexão com PostgreSQL estabelecida com sucesso.")
    except Exception as db_conn_error:
        logger.error(f"Erro ao conectar ao banco de dados: {db_conn_error}")
        raise
    
except Exception as e:
    logger.error(f"Falha ao configurar engine PostgreSQL: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency para injeção nas rotas do FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar banco de dados
def init_db():
    """Inicializa as tabelas do banco de dados."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas do banco de dados criadas com sucesso.")
    except Exception as init_error:
        logger.error(f"Erro ao criar tabelas do banco de dados: {init_error}")
        raise 