from fastapi import APIRouter, Depends, HTTPException, Request, Header
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
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json
import jwt
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
eligibility_service = EligibilityService()
limiter = Limiter(key_func=get_remote_address)

@router.post("/assess", response_model=EligibilityAssessmentOutput)
@limiter.limit("5/minute")
async def assess_eligibility(
    request: Request,
    assessment_input: EligibilityAssessmentInput,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Realiza uma avaliação de elegibilidade para visto EB2-NIW.
    
    Esta avaliação analisa vários critérios como educação, experiência profissional,
    conquistas acadêmicas e reconhecimento na área para determinar a viabilidade da petição.
    
    A resposta inclui pontuações detalhadas, pontos fortes, fracos e recomendações específicas.
    """
    try:
        # Tentar extrair o user_id do token de autorização
        if not assessment_input.user_id and authorization:
            try:
                # Verificar se está no modo de desenvolvimento
                is_dev_mode = settings.ENVIRONMENT.lower() == "dev"
                
                # Extrair o token do cabeçalho Authorization
                token = authorization.replace("Bearer ", "")
                
                # Decodificar o token e extrair o user_id
                decoded_token = jwt.decode(
                    token, 
                    settings.SECRET_KEY,
                    algorithms=["HS256"]
                )
                authenticated_user_id = decoded_token.get("sub")
                
                if authenticated_user_id:
                    logger.info(f"Usando ID de usuário do token: {authenticated_user_id}")
                    assessment_input.user_id = authenticated_user_id
            except jwt.PyJWTError as e:
                logger.warning(f"Não foi possível decodificar o token: {e}")
                # Não interrompe o fluxo se falhar ao decodificar o token
        
        # Se ainda não tiver um user_id, usar um ID anônimo temporário
        if not assessment_input.user_id:
            # Gerar um ID temporário para este usuário anônimo
            import uuid
            temp_user_id = f"anon_{uuid.uuid4()}"
            logger.info(f"Criando ID temporário para usuário anônimo: {temp_user_id}")
            assessment_input.user_id = temp_user_id
        
        logger.info(f"Recebida solicitação de avaliação para usuário: {assessment_input.user_id}")
        
        # Chamar o serviço para realizar a avaliação
        assessment_result = await eligibility_service.assess_eligibility(assessment_input)
        
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
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Busca o histórico de avaliações de elegibilidade de um usuário.
    
    Retorna uma lista de avaliações anteriores realizadas pelo usuário, ordenadas da mais recente para a mais antiga.
    A autenticação é obrigatória e o usuário só pode acessar seu próprio histórico.
    """
    try:
        logger.info(f"Buscando histórico de avaliações para usuário: {user_id}")
        
        # Verificar autenticação e autorização
        authenticated_user_id = None
        
        # Verificar se está no modo de desenvolvimento
        is_dev_mode = settings.ENVIRONMENT.lower() == "dev"
        logger.info(f"Modo de ambiente: {'desenvolvimento' if is_dev_mode else 'produção'}")
        
        # Se não estiver em modo de desenvolvimento, verificar a autenticação
        if not is_dev_mode:
            if not authorization:
                logger.error("Tentativa de acesso sem token de autenticação")
                raise HTTPException(status_code=401, detail="Autenticação obrigatória")
            
            try:
                # Extrair o token do cabeçalho Authorization
                token = authorization.replace("Bearer ", "")
                
                # Decodificar o token e extrair o user_id
                decoded_token = jwt.decode(
                    token, 
                    settings.SECRET_KEY,
                    algorithms=["HS256"]
                )
                authenticated_user_id = decoded_token.get("sub")
                
                # Verificar se o usuário está tentando acessar seu próprio histórico
                if authenticated_user_id != user_id:
                    logger.error(f"Usuário {authenticated_user_id} tentando acessar histórico de {user_id}")
                    raise HTTPException(
                        status_code=403, 
                        detail="Acesso negado: Você só pode acessar seu próprio histórico"
                    )
            except jwt.PyJWTError as e:
                logger.error(f"Erro ao decodificar token: {e}")
                raise HTTPException(status_code=401, detail="Token inválido ou expirado")
        else:
            logger.warning(f"Operando em modo de desenvolvimento - verificações de segurança reduzidas")
            # Em modo de desenvolvimento, verificamos apenas se o token está presente, sem validá-lo
            if authorization:
                logger.info("Token de autorização fornecido em modo de desenvolvimento")
            else:
                logger.warning("Sem token de autorização em modo de desenvolvimento")
        
        if not db:
            logger.error("Conexão com banco de dados não disponível")
            raise HTTPException(status_code=503, detail="Serviço de banco de dados indisponível")
        
        # Buscar todas as avaliações do usuário, ordenadas por data (mais recente primeiro)
        assessments = db.query(QuickAssessment).filter(
            QuickAssessment.user_id == user_id
        ).order_by(QuickAssessment.created_at.desc()).all()
        
        logger.info(f"Encontradas {len(assessments)} avaliações para o usuário {user_id}")
        
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

@router.get("/assessment/{assessment_id}", response_model=EligibilityAssessmentOutput)
@limiter.limit("20/minute")
async def get_assessment_by_id(
    request: Request,
    assessment_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Busca uma avaliação específica pelo seu ID.
    
    Retorna os detalhes de uma avaliação específica se ela existir.
    """
    try:
        logger.info(f"Buscando avaliação com ID: {assessment_id}")
        
        if not db:
            logger.error("Conexão com banco de dados não disponível")
            raise HTTPException(status_code=503, detail="Serviço de banco de dados indisponível")
        
        # Buscar a avaliação pelo ID
        assessment = db.query(QuickAssessment).filter(
            QuickAssessment.id == assessment_id
        ).first()
        
        if not assessment:
            logger.error(f"Avaliação específica não encontrada: {assessment_id}")
            raise HTTPException(
                status_code=404, 
                detail=f'Avaliação específica não encontrada: "{assessment_id}"'
            )
        
        logger.info(f"Avaliação encontrada: {assessment_id}")
        
        try:
            # Converter dados JSON armazenados
            strengths = assessment.strengths if isinstance(assessment.strengths, list) else json.loads(assessment.strengths) if assessment.strengths else []
            weaknesses = assessment.weaknesses if isinstance(assessment.weaknesses, list) else json.loads(assessment.weaknesses) if assessment.weaknesses else []
            recommendations = assessment.recommendations if isinstance(assessment.recommendations, list) else json.loads(assessment.recommendations) if assessment.recommendations else []
            detailed_recommendations = assessment.detailed_recommendations if isinstance(assessment.detailed_recommendations, list) else json.loads(assessment.detailed_recommendations) if assessment.detailed_recommendations else None
            next_steps = assessment.next_steps if isinstance(assessment.next_steps, list) else json.loads(assessment.next_steps) if assessment.next_steps else None
            
            # Processar avaliação de EB2 se existir
            eb2_route_data = None
            if assessment.eb2_route_evaluation:
                try:
                    eb2_data = assessment.eb2_route_evaluation if isinstance(assessment.eb2_route_evaluation, dict) else json.loads(assessment.eb2_route_evaluation)
                    eb2_route_data = EB2RouteEvaluation(
                        recommended_route=eb2_data.get("recommended_route", "ADVANCED_DEGREE"),
                        advanced_degree_score=eb2_data.get("advanced_degree_score", 0.0),
                        exceptional_ability_score=eb2_data.get("exceptional_ability_score", 0.0),
                        route_explanation=eb2_data.get("route_explanation", "")
                    )
                except Exception as e:
                    logger.warning(f"Erro ao processar dados EB2: {e}")
            
            # Processar avaliação NIW se existir
            niw_evaluation_data = None
            if assessment.niw_evaluation:
                try:
                    niw_data = assessment.niw_evaluation if isinstance(assessment.niw_evaluation, dict) else json.loads(assessment.niw_evaluation)
                    niw_evaluation_data = NIWEvaluation(
                        merit_importance_score=niw_data.get("merit_importance_score", 0.0),
                        well_positioned_score=niw_data.get("well_positioned_score", 0.0),
                        benefit_waiver_score=niw_data.get("benefit_waiver_score", 0.0),
                        niw_overall_score=niw_data.get("niw_overall_score", 0.0)
                    )
                except Exception as e:
                    logger.warning(f"Erro ao processar dados NIW: {e}")
        except Exception as e:
            logger.warning(f"Erro ao processar dados JSON da avaliação: {e}")
            strengths = []
            weaknesses = []
            recommendations = []
            detailed_recommendations = None
            next_steps = None
            eb2_route_data = None
            niw_evaluation_data = None
        
        # Criar objeto de resposta
        result = EligibilityAssessmentOutput(
            id=assessment.id,
            user_id=assessment.user_id,
            created_at=assessment.created_at,
            score=EligibilityScore(
                education=assessment.education_score or 0.0,
                experience=assessment.experience_score or 0.0,
                achievements=assessment.achievements_score or 0.0,
                recognition=assessment.recognition_score or 0.0,
                overall=assessment.overall_score or 0.0
            ),
            viability_level=assessment.viability_level or "INSUFFICIENT",
            viability=assessment.viability_level or "Low",  # Mantendo para compatibilidade
            probability=assessment.overall_score or 0.0,  # Usando o score como probabilidade
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            detailed_recommendations=detailed_recommendations,
            next_steps=next_steps,
            message=assessment.message,
            eb2_route=eb2_route_data,
            niw_evaluation=niw_evaluation_data,
            estimated_processing_time=assessment.estimated_processing_time or (
                90 if assessment.overall_score and assessment.overall_score > 0.8 
                else (120 if assessment.overall_score and assessment.overall_score > 0.65 else 180)
            )
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar avaliação: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar avaliação: {str(e)}"
        ) 