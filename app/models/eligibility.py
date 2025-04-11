from sqlalchemy import Column, String, Float, Boolean, JSON, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.models.base import Base

class QuickAssessment(Base):
    __tablename__ = "quick_assessments"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Scores básicos
    overall_score = Column(Float)
    viability_level = Column(String)
    education_score = Column(Float)
    experience_score = Column(Float)
    achievements_score = Column(Float)
    recognition_score = Column(Float)
    
    # Novas colunas para avaliação das rotas EB2 e NIW
    eb2_route_evaluation = Column(JSON)  # Armazena recommended_route, scores, explanation
    niw_evaluation = Column(JSON)  # Armazena scores para os 3 critérios NIW
    
    # Dados de entrada e resultados expandidos
    input_data = Column(JSON)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    recommendations = Column(JSON)  # Mantido para compatibilidade
    detailed_recommendations = Column(JSON)  # Nova estrutura com categorias, impacto e prioridade
    next_steps = Column(JSON)  # Lista de próximos passos recomendados
    message = Column(String)  # Mensagem personalizada
    
    # Estimativas e metadados adicionais
    estimated_processing_time = Column(Integer)  # Tempo estimado em meses
    processing_time_ms = Column(Integer)  # Tempo de processamento da avaliação
    
    # Flag para a avaliação mais recente
    is_latest = Column(Boolean, default=True)
