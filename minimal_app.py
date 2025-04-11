#!/usr/bin/env python3

"""
Versão mínima da API de avaliação de elegibilidade usando SQLite para testes
"""

import logging
import os
import sqlite3
from datetime import datetime
import uuid
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Eligibility Assessment API (Minimal)",
    description="Versão mínima da API para avaliação de elegibilidade",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens em desenvolvimento
    allow_credentials=False,  # Importante para evitar problemas com cookies
    allow_methods=["*"],  # Permitir todos os métodos
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

# Adicionar prefixos às rotas para corresponder às expectativas do frontend
prefix = "/api/v1/eligibility"

# Inicializar banco SQLite em memória
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Criar tabela para avaliações
cursor.execute('''
CREATE TABLE assessments (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    created_at TEXT,
    overall_score REAL,
    viability_level TEXT,
    education_score REAL,
    experience_score REAL,
    achievements_score REAL,
    recognition_score REAL,
    input_data TEXT,
    strengths TEXT,
    weaknesses TEXT,
    recommendations TEXT
)
''')
conn.commit()

# Definição dos modelos
class AssessmentCreate(BaseModel):
    """Schema para criação de uma avaliação de elegibilidade."""
    user_id: Optional[str] = None
    education_level: str = Field(..., description="Nível de educação")
    field_of_study: str = Field(..., description="Área de estudo")
    years_of_experience: int = Field(..., description="Anos de experiência")
    
    def dict(self):
        return {
            "user_id": self.user_id,
            "education_level": self.education_level,
            "field_of_study": self.field_of_study,
            "years_of_experience": self.years_of_experience
        }

class AssessmentResponse(BaseModel):
    """Schema para resposta de uma avaliação."""
    id: str
    overall_score: float
    viability_level: str
    education_score: float
    experience_score: float
    achievements_score: float
    recognition_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    created_at: str

@app.get(f"{prefix}/")
async def root():
    return {"message": "Eligibility Assessment API (Minimal Version)"}

@app.get(f"{prefix}/health")
async def health_check():
    return {"status": "healthy", "database": "SQLite (in-memory)"}

@app.post(f"{prefix}/assess", response_model=AssessmentResponse)
async def create_assessment(assessment: AssessmentCreate):
    """Cria uma avaliação rápida de elegibilidade."""
    
    # Gerar ID e timestamp
    assessment_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    # AVISO: Esta é uma versão mínima para testes
    # Em produção, estes valores seriam calculados através de um algoritmo real
    # Usando apenas valores padrão para fins de desenvolvimento
    overall_score = 0.5
    viability_level = "TEST_MODE" 
    education_score = 0.5
    experience_score = 0.5
    achievements_score = 0.5
    recognition_score = 0.5
    
    # Mensagens genéricas
    strengths = ["Esta é uma versão mínima para testes. Os dados não são representativos."]
    weaknesses = ["Esta é uma versão mínima para testes. Os dados não são representativos."] 
    recommendations = ["Esta é uma versão mínima para testes. Os dados não são representativos."]
    
    # Processamento básico dos dados de entrada para mostrar alguma variação
    if assessment.education_level == "PHD":
        education_score = 0.8
        overall_score += 0.1
    
    if assessment.years_of_experience > 5:
        experience_score = 0.7
        overall_score += 0.05
    
    # Normalizar o score final
    overall_score = min(1.0, overall_score)
    
    # Salvar no banco
    cursor.execute(
        '''INSERT INTO assessments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            assessment_id,
            assessment.user_id or "anonymous",
            created_at,
            overall_score,
            viability_level,
            education_score,
            experience_score,
            achievements_score,
            recognition_score,
            json.dumps(assessment.dict()),
            json.dumps(strengths),
            json.dumps(weaknesses),
            json.dumps(recommendations)
        )
    )
    conn.commit()
    
    # Retornar resposta
    return AssessmentResponse(
        id=assessment_id,
        overall_score=overall_score,
        viability_level=viability_level,
        education_score=education_score,
        experience_score=experience_score,
        achievements_score=achievements_score,
        recognition_score=recognition_score,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        created_at=created_at
    )

@app.get(f"{prefix}/history/{{user_id}}", response_model=List[AssessmentResponse])
async def get_user_assessments(user_id: str):
    """Obtém todas as avaliações de um usuário."""
    
    cursor.execute(
        "SELECT * FROM assessments WHERE user_id = ?",
        (user_id,)
    )
    
    results = cursor.fetchall()
    
    if not results:
        return []
    
    assessments = []
    for row in results:
        assessments.append(AssessmentResponse(
            id=row[0],
            overall_score=row[3],
            viability_level=row[4],
            education_score=row[5],
            experience_score=row[6],
            achievements_score=row[7],
            recognition_score=row[8],
            strengths=json.loads(row[10]),
            weaknesses=json.loads(row[11]),
            recommendations=json.loads(row[12]),
            created_at=row[2]
        ))
    
    return assessments

if __name__ == "__main__":
    logger.info("Iniciando versão mínima da API de elegibilidade...")
    uvicorn.run(app, host="0.0.0.0", port=8080) 