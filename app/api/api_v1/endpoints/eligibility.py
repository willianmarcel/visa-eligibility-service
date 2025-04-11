from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.eligibility import QuickAssessment
from app.schemas.eligibility import EligibilityAssessmentInput, EligibilityAssessmentOutput, AssessmentCreate, AssessmentResponse, EligibilityScore
from app.services.scoring_engine import ScoringEngine
from app.services.recommendation_engine import RecommendationEngine
from app.api.deps import get_current_user
from app.core.logging import api_logger, log_structured_data, log_metric

router = APIRouter()

@router.post("/assessment", response_model=EligibilityAssessmentOutput, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_input: EligibilityAssessmentInput,
    db: Session = Depends(get_db),
    user_id: Optional[str] = Depends(get_current_user)
):
    """
    Realiza uma avaliação rápida de elegibilidade para visto EB2-NIW.
    
    - Calcula scores para cada categoria com base nos dados fornecidos
    - Determina o nível de viabilidade geral da petição
    - Identifica pontos fortes e fracos
    - Gera recomendações personalizadas
    - Salva os resultados para referência futura
    
    Retorna os resultados detalhados da avaliação.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    log_structured_data(api_logger, "info", 
                        f"Iniciando nova avaliação de elegibilidade",
                        {"request_id": request_id, "user_id": user_id})
    
    try:
        # Inicializar motores de avaliação
        scoring_engine = ScoringEngine()
        recommendation_engine = RecommendationEngine()
        
        # Realizar avaliação
        assessment_results = scoring_engine.evaluate_eligibility(assessment_input)
        
        # Estruturar dados para persistência
        db_assessment = QuickAssessment(
            user_id=user_id,
            overall_score=assessment_results["overall_score"],
            viability_level=assessment_results["viability_level"],
            education_score=assessment_results["category_scores"]["education"] * 100, # Convertendo para percentual
            experience_score=assessment_results["category_scores"]["experience"] * 100,
            achievements_score=assessment_results["category_scores"]["achievements"] * 100,
            recognition_score=assessment_results["category_scores"]["recognition"] * 100,
            input_data=assessment_input.dict(),
            strengths=assessment_results["strengths"],
            weaknesses=assessment_results["weaknesses"],
            recommendations=[rec.dict() for rec in assessment_results["recommendations"]],
            is_latest=True
        )
        
        log_structured_data(api_logger, "info", 
                           f"Salvando resultados da avaliação",
                           {"request_id": request_id, 
                            "viability_level": assessment_results["viability_level"],
                            "overall_score": assessment_results["overall_score"]})
        
        # Atualizar flag de 'mais recente' para avaliações anteriores do mesmo usuário
        if user_id:
            previous_assessments = db.query(QuickAssessment).filter(
                QuickAssessment.user_id == user_id,
                QuickAssessment.is_latest == True
            ).all()
            
            for assessment in previous_assessments:
                assessment.is_latest = False
        
        # Salvar nova avaliação
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        
        # Preparar resposta
        response = EligibilityAssessmentOutput(
            id=db_assessment.id,
            user_id=user_id,
            created_at=db_assessment.created_at,
            score=EligibilityScore(
                education=assessment_results["category_scores"]["education"],
                experience=assessment_results["category_scores"]["experience"],
                achievements=assessment_results["category_scores"]["achievements"],
                recognition=assessment_results["category_scores"]["recognition"],
                overall=assessment_results["overall_score"]
            ),
            viability_level=assessment_results["viability_level"],
            viability=assessment_results["viability_level"],
            probability=assessment_results["overall_score"],
            strengths=assessment_results["strengths"],
            weaknesses=assessment_results["weaknesses"],
            recommendations=assessment_results["recommendations"],
            next_steps=assessment_results["next_steps"],
            message=assessment_results["message"]
        )
        
        # Registrar métricas
        processing_time = time.time() - start_time
        log_metric("api.assessment.processing_time", processing_time)
        log_metric("api.assessment.created", 1, {"viability_level": assessment_results["viability_level"]})
        
        log_structured_data(api_logger, "info", 
                           f"Avaliação de elegibilidade concluída com sucesso",
                           {"request_id": request_id, 
                            "processing_time_ms": int(processing_time * 1000)})
        
        return response
        
    except Exception as e:
        log_structured_data(api_logger, "error", 
                           f"Erro ao processar avaliação de elegibilidade: {str(e)}",
                           {"request_id": request_id, 
                            "error": str(e),
                            "processing_time_ms": int((time.time() - start_time) * 1000)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar avaliação: {str(e)}"
        )


@router.get("/assessment/latest", response_model=EligibilityAssessmentOutput)
async def get_latest_assessment(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Recupera a avaliação mais recente do usuário atual.
    Retorna erro 404 se nenhuma avaliação for encontrada.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    log_structured_data(api_logger, "info", 
                       f"Buscando avaliação mais recente",
                       {"request_id": request_id, "user_id": user_id})
    
    try:
        latest_assessment = db.query(QuickAssessment).filter(
            QuickAssessment.user_id == user_id,
            QuickAssessment.is_latest == True
        ).first()
        
        if not latest_assessment:
            log_structured_data(api_logger, "warn", 
                               f"Nenhuma avaliação encontrada para o usuário",
                               {"request_id": request_id, "user_id": user_id})
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma avaliação encontrada para este usuário"
            )
        
        # Converter recomendações armazenadas em JSON para objetos Recommendation
        recommendations = [
            RecommendationEngine.create_recommendation_from_dict(rec)
            for rec in latest_assessment.recommendations
        ]
        
        response = EligibilityAssessmentOutput(
            id=latest_assessment.id,
            user_id=user_id,
            created_at=latest_assessment.created_at,
            score=EligibilityScore(
                education=latest_assessment.education_score,
                experience=latest_assessment.experience_score,
                achievements=latest_assessment.achievements_score,
                recognition=latest_assessment.recognition_score,
                overall=latest_assessment.overall_score
            ),
            viability_level=latest_assessment.viability_level,
            viability=latest_assessment.viability_level,
            probability=latest_assessment.overall_score,
            strengths=latest_assessment.strengths,
            weaknesses=latest_assessment.weaknesses,
            recommendations=recommendations,
            next_steps=[],  # Precisaria ser regenerado ou armazenado
            message=""  # Precisaria ser regenerado ou armazenado
        )
        
        processing_time = time.time() - start_time
        log_metric("api.get_latest_assessment.processing_time", processing_time)
        
        log_structured_data(api_logger, "info", 
                           f"Avaliação recuperada com sucesso",
                           {"request_id": request_id, 
                            "assessment_id": latest_assessment.id,
                            "processing_time_ms": int(processing_time * 1000)})
        
        return response
        
    except HTTPException:
        # Repassar exceções HTTP conforme definidas
        raise
    except Exception as e:
        log_structured_data(api_logger, "error", 
                           f"Erro ao buscar avaliação mais recente: {str(e)}",
                           {"request_id": request_id, 
                            "error": str(e),
                            "processing_time_ms": int((time.time() - start_time) * 1000)})
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao recuperar avaliação: {str(e)}"
        )


@router.get("/assessment/history", response_model=List[EligibilityAssessmentOutput])
async def get_assessment_history(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Recupera o histórico de avaliações do usuário atual.
    Retorna uma lista vazia se nenhuma avaliação for encontrada.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    log_structured_data(api_logger, "info", 
                       f"Buscando histórico de avaliações",
                       {"request_id": request_id, "user_id": user_id})
    
    try:
        assessments = db.query(QuickAssessment).filter(
            QuickAssessment.user_id == user_id
        ).order_by(QuickAssessment.created_at.desc()).all()
        
        result = []
        for assessment in assessments:
            # Converter recomendações armazenadas em JSON para objetos Recommendation
            recommendations = [
                RecommendationEngine.create_recommendation_from_dict(rec)
                for rec in assessment.recommendations
            ]
            
            result.append(
                EligibilityAssessmentOutput(
                    id=assessment.id,
                    user_id=user_id,
                    created_at=assessment.created_at,
                    score=EligibilityScore(
                        education=assessment.education_score,
                        experience=assessment.experience_score,
                        achievements=assessment.achievements_score,
                        recognition=assessment.recognition_score,
                        overall=assessment.overall_score
                    ),
                    viability_level=assessment.viability_level,
                    viability=assessment.viability_level,
                    probability=assessment.overall_score,
                    strengths=assessment.strengths,
                    weaknesses=assessment.weaknesses,
                    recommendations=recommendations,
                    next_steps=[],  # Precisaria ser regenerado ou armazenado
                    message=""  # Precisaria ser regenerado ou armazenado
                )
            )
        
        processing_time = time.time() - start_time
        log_metric("api.get_assessment_history.processing_time", processing_time)
        log_metric("api.get_assessment_history.count", len(result))
        
        log_structured_data(api_logger, "info", 
                           f"Histórico de avaliações recuperado com sucesso",
                           {"request_id": request_id, 
                            "count": len(result),
                            "processing_time_ms": int(processing_time * 1000)})
        
        return result
        
    except Exception as e:
        log_structured_data(api_logger, "error", 
                           f"Erro ao buscar histórico de avaliações: {str(e)}",
                           {"request_id": request_id, 
                            "error": str(e),
                            "processing_time_ms": int((time.time() - start_time) * 1000)})
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao recuperar histórico de avaliações: {str(e)}"
        )

@router.post("/assess", response_model=AssessmentResponse)
def create_assessment(
    assessment: AssessmentCreate,
    db: Session = Depends(get_db)
):
    """Cria uma avaliação rápida de elegibilidade baseada nos dados fornecidos."""
    
    # Aqui seria implementada a lógica de avaliação completa
    # Por enquanto, apenas retornamos valores exemplo
    
    # Criar nova avaliação no banco
    db_assessment = QuickAssessment(
        id=str(uuid.uuid4()),
        user_id=assessment.user_id if assessment.user_id else "anonymous",
        created_at=datetime.utcnow(),
        
        # Scores (simulados)
        overall_score=0.75,
        viability_level="Promising",
        education_score=0.8,
        experience_score=0.7,
        achievements_score=0.6,
        recognition_score=0.9,
        
        # Dados
        input_data=assessment.model_dump(),
        strengths=["Strong educational background", "Impressive work experience"],
        weaknesses=["Limited publications", "Few citations"],
        recommendations=["Consider publishing more research", "Obtain additional letters of recommendation"]
    )
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    
    # Construir resposta
    return AssessmentResponse(
        id=db_assessment.id,
        overall_score=db_assessment.overall_score,
        viability_level=db_assessment.viability_level,
        education_score=db_assessment.education_score,
        experience_score=db_assessment.experience_score,
        achievements_score=db_assessment.achievements_score,
        recognition_score=db_assessment.recognition_score,
        strengths=db_assessment.strengths,
        weaknesses=db_assessment.weaknesses,
        recommendations=db_assessment.recommendations,
        created_at=db_assessment.created_at
    )

@router.get("/history/{user_id}", response_model=list[AssessmentResponse])
def get_assessment_history(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Obtém o histórico de avaliações para um usuário específico."""
    assessments = db.query(QuickAssessment).filter(
        QuickAssessment.user_id == user_id
    ).order_by(QuickAssessment.created_at.desc()).all()
    
    return assessments 