from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.eligibility_service import EligibilityService
from app.schemas.eligibility import (
    EligibilityAssessmentInput,
    EligibilityAssessmentOutput,
    EligibilityScore
)
from app.models.eligibility import QuickAssessment
from typing import List, Dict, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = APIRouter()
eligibility_service = EligibilityService()
limiter = Limiter(key_func=get_remote_address)

@router.post("/assess", response_model=EligibilityAssessmentOutput)
@limiter.limit("5/minute")
async def assess_eligibility(
    request: Request,
    assessment_input: EligibilityAssessmentInput,
    db: Session = Depends(get_db)
):
    """
    Realiza uma avaliação de elegibilidade para visto EB2-NIW.
    
    Esta avaliação analisa vários critérios como educação, experiência profissional,
    conquistas acadêmicas e reconhecimento na área para determinar a viabilidade da petição.
    
    A resposta inclui pontuações detalhadas, pontos fortes, fracos e recomendações específicas.
    """
    try:
        logger.info(f"Recebida solicitação de avaliação para usuário: {assessment_input.user_id or 'anônimo'}")
        
        # Chamar o serviço para realizar a avaliação
        assessment_result = eligibility_service.assess_eligibility(assessment_input)
        
        # Salvar a avaliação no banco de dados
        if assessment_input.user_id:
            # Se for um usuário autenticado, salvar a avaliação
            try:
                # Marcar todas as avaliações anteriores como não sendo a mais recente
                if db:
                    db.query(QuickAssessment).filter(
                        QuickAssessment.user_id == assessment_input.user_id,
                        QuickAssessment.is_latest == True
                    ).update({"is_latest": False})
                    
                    # Criar nova avaliação
                    db_assessment = QuickAssessment(
                        id=assessment_result.id,
                        user_id=assessment_input.user_id,
                        created_at=assessment_result.created_at,
                        overall_score=assessment_result.score.overall,
                        viability_level=assessment_result.viability,
                        education_score=assessment_result.score.education,
                        experience_score=assessment_result.score.experience,
                        achievements_score=assessment_result.score.achievements,
                        recognition_score=assessment_result.score.recognition,
                        input_data=assessment_input.dict(),
                        strengths=assessment_result.strengths,
                        weaknesses=assessment_result.weaknesses,
                        recommendations=assessment_result.recommendations,
                        is_latest=True
                    )
                    
                    db.add(db_assessment)
                    db.commit()
                    logger.info(f"Avaliação salva para usuário {assessment_input.user_id}")
            except Exception as e:
                logger.error(f"Erro ao salvar avaliação no banco de dados: {e}")
                # Não interrompe o fluxo se falhar ao salvar
        
        return assessment_result
        
    except Exception as e:
        logger.error(f"Erro ao processar avaliação de elegibilidade: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar avaliação: {str(e)}"
        )

@router.get("/history/{user_id}", response_model=List[EligibilityAssessmentOutput])
@limiter.limit("10/minute")
async def get_user_assessment_history(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Busca o histórico de avaliações de elegibilidade de um usuário.
    
    Retorna uma lista de avaliações anteriores realizadas pelo usuário, ordenadas da mais recente para a mais antiga.
    """
    try:
        logger.info(f"Buscando histórico de avaliações para usuário: {user_id}")
        
        if not db:
            logger.error("Conexão com banco de dados não disponível")
            raise HTTPException(status_code=503, detail="Serviço de banco de dados indisponível")
        
        # Buscar todas as avaliações do usuário, ordenadas por data (mais recente primeiro)
        assessments = db.query(QuickAssessment).filter(
            QuickAssessment.user_id == user_id
        ).order_by(QuickAssessment.created_at.desc()).all()
        
        if not assessments:
            logger.info(f"Nenhuma avaliação encontrada para o usuário {user_id}")
            return []
        
        # Converter os resultados do banco de dados para o formato de saída
        result = []
        for assessment in assessments:
            try:
                # Converter dados JSON armazenados
                strengths = assessment.strengths if isinstance(assessment.strengths, list) else json.loads(assessment.strengths)
                weaknesses = assessment.weaknesses if isinstance(assessment.weaknesses, list) else json.loads(assessment.weaknesses)
                recommendations = assessment.recommendations if isinstance(assessment.recommendations, list) else json.loads(assessment.recommendations)
                
                # Criar objeto de resposta
                result.append(EligibilityAssessmentOutput(
                    id=assessment.id,
                    user_id=assessment.user_id,
                    created_at=assessment.created_at,
                    score=EligibilityScore(
                        education=assessment.education_score,
                        experience=assessment.experience_score,
                        achievements=assessment.achievements_score,
                        recognition=assessment.recognition_score,
                        overall=assessment.overall_score
                    ),
                    viability_level=assessment.viability_level,
                    viability=assessment.viability_level,  # Mantendo para compatibilidade
                    probability=assessment.overall_score,  # Usando o score como probabilidade
                    strengths=strengths,
                    weaknesses=weaknesses,
                    recommendations=recommendations,
                    estimated_processing_time=90 if assessment.overall_score > 0.8 else (
                        120 if assessment.overall_score > 0.65 else 180
                    )
                ))
            except Exception as e:
                logger.error(f"Erro ao processar avaliação {assessment.id}: {e}")
                # Continua para a próxima avaliação
        
        logger.info(f"Retornando {len(result)} avaliações para o usuário {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de avaliações: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )

@router.get("/info")
@limiter.limit("20/minute")
async def get_eligibility_criteria(request: Request):
    """
    Retorna informações sobre os critérios considerados na avaliação de elegibilidade.
    """
    return {
        "criteria": {
            "education": "Avaliação do nível educacional, instituição e área de estudo",
            "experience": "Avaliação da experiência profissional, cargos ocupados e anos de trabalho",
            "achievements": "Avaliação de publicações, citações e contribuições para a área",
            "recognition": "Avaliação de prêmios, cartas de recomendação e reconhecimento por pares"
        },
        "weights": eligibility_service.weights,
        "viability_levels": {
            "Strong": "Alta probabilidade de aprovação (80%+)",
            "Good": "Boa probabilidade de aprovação (65-80%)",
            "Moderate": "Probabilidade moderada de aprovação (50-65%)",
            "Low": "Baixa probabilidade de aprovação (<50%)"
        }
    }

@router.get("/config", response_model=Dict[str, Any])
async def get_eligibility_config():
    """
    Retorna a configuração utilizada pelo sistema de avaliação de elegibilidade.
    
    Esta configuração inclui todos os pesos, thresholds e parâmetros utilizados 
    pelo algoritmo para calcular as pontuações e gerar recomendações.
    """
    from app.core.eligibility_config import (
        CATEGORY_WEIGHTS,
        EDUCATION_CRITERIA,
        EXPERIENCE_CRITERIA,
        ACHIEVEMENTS_CRITERIA,
        RECOGNITION_CRITERIA,
        VIABILITY_THRESHOLDS,
        STRENGTH_THRESHOLD,
        WEAKNESS_THRESHOLD,
        EB2_CONFIG,
        NIW_CONFIG,
        MAX_RECOMMENDATIONS
    )
    
    return {
        "category_weights": CATEGORY_WEIGHTS,
        "education_criteria": EDUCATION_CRITERIA,
        "experience_criteria": EXPERIENCE_CRITERIA,
        "achievements_criteria": ACHIEVEMENTS_CRITERIA,
        "recognition_criteria": RECOGNITION_CRITERIA,
        "viability_thresholds": VIABILITY_THRESHOLDS,
        "strength_threshold": STRENGTH_THRESHOLD,
        "weakness_threshold": WEAKNESS_THRESHOLD,
        "eb2_config": EB2_CONFIG,
        "niw_config": NIW_CONFIG,
        "max_recommendations": MAX_RECOMMENDATIONS
    } 