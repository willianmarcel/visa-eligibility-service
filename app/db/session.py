from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from app.core.config import settings
from app.models.base import Base
import logging

logger = logging.getLogger(__name__)

# Usar DATABASE_URL diretamente se estiver configurada no ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

# Verificar ambiente de execução
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
USE_SQLITE_FALLBACK = os.getenv("USE_SQLITE_FALLBACK", "false").lower() == "true"

# Criar engine de banco de dados
try:
    if ENVIRONMENT == "dev" and USE_SQLITE_FALLBACK:
        # Usar SQLite em memória para desenvolvimento/testes
        logger.info("Usando SQLite em memória para desenvolvimento.")
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            echo=True
        )
    else:
        # Usar PostgreSQL
        logger.info(f"Conectando ao PostgreSQL em ambiente {ENVIRONMENT}...")
        try:
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
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Conexão com PostgreSQL estabelecida com sucesso.")
        except Exception as e:
            if ENVIRONMENT == "dev":
                logger.warning(f"Não foi possível conectar ao PostgreSQL: {e}")
                logger.info("Usando SQLite em memória como fallback para desenvolvimento.")
                
                # Fallback para SQLite em memória
                engine = create_engine(
                    "sqlite:///:memory:",
                    connect_args={"check_same_thread": False},
                    echo=True
                )
            else:
                # Em produção, falhar se não conectar ao PostgreSQL
                logger.error(f"Falha ao conectar ao PostgreSQL: {e}")
                raise
except Exception as e:
    logger.error(f"Erro ao configurar conexão com banco de dados: {e}")
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
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas do banco de dados criadas com sucesso.") 