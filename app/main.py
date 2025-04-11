from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging
from app.db.session import init_db, engine
import os
from app.api.v1.api import api_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Eligibility Assessment API",
    description="API para avaliação de elegibilidade de vistos EB2-NIW",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Adicionar limiter ao app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS - Em desenvolvimento permitimos todas as origens
origins = [
    "http://localhost:3001",  # Frontend Next.js
    "http://localhost:3000",  # Frontend Next.js
    "http://localhost:8080",  # API
    "https://visa-platform.example.com",  # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verificar se estamos usando SQLite
using_sqlite = str(engine.url).startswith('sqlite')

@app.on_event("startup")
async def startup_db_client():
    """Inicializa o banco de dados no startup da aplicação."""
    try:
        init_db()
        logger.info("Banco de dados inicializado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")

# Incluir rotas da API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

# API Routes
@app.get("/", tags=["root"])
async def root():
    return {"message": "Eligibility Assessment API"}

@app.get("/api/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "PostgreSQL" if not using_sqlite else "SQLite (Dev Mode)"
    }

@app.get("/api/diagnose", tags=["diagnostics"])
async def diagnose():
    """Endpoint para diagnóstico da aplicação."""
    return {
        "environment": os.environ.get("ENVIRONMENT", "unknown"),
        "database": {
            "type": "SQLite (Development)" if using_sqlite else "PostgreSQL",
            "connection_string": str(engine.url).replace(":memory:", "<memory>") if using_sqlite else "**REDACTED**",
        },
        "settings": {
            "api_version": settings.API_V1_STR,
            "debug_enabled": settings.DEBUG,
            "cors_origins": settings.BACKEND_CORS_ORIGINS
        }
    } 