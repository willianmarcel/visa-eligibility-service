from datetime import datetime
import uuid
import logging
from app.schemas.eligibility import (
    EligibilityAssessmentInput,
    EligibilityAssessmentOutput,
    EligibilityScore,
    EB2RouteEvaluation,
    NIWEvaluation,
    RecommendationDetail
)
from app.models.eligibility import QuickAssessment as EligibilityAssessment
from typing import Dict
import time
from fastapi.encoders import jsonable_encoder
from app.services.eligibility_evaluator import EligibilityEvaluator
from app.services.db_manager import DBManager
from app.services.analytics_service import AnalyticsService
from app.core.logging import get_request_id, log_structured_data, log_metric, eligibility_logger, scoring_logger
from app.services.scoring_engine import ScoringEngine
import json

logger = logging.getLogger(__name__)

class EligibilityService:
    """Serviço para avaliação de elegibilidade de vistos EB2-NIW."""
    
    def __init__(self):
        # Inicializar componentes principais
        self.evaluator = EligibilityEvaluator()
        self.db_manager = DBManager()
        self.analytics_service = AnalyticsService()
        
        eligibility_logger.info("EligibilityService inicializado")
    
    async def assess_eligibility(self, input_data: EligibilityAssessmentInput) -> EligibilityAssessmentOutput:
        """
        Avalia a elegibilidade de um candidato e retorna uma análise detalhada.
        
        Args:
            input_data: Dados de entrada para a avaliação
            
        Returns:
            Resultado detalhado da avaliação de elegibilidade
        """
        scoring_logger.info("Iniciando avaliação de elegibilidade detalhada")
        
        # Processar avaliação usando o motor de scoring
        scoring_engine = ScoringEngine()
        result = scoring_engine.process_assessment(input_data)
        
        # Salvar na base de dados
        await self.save_assessment_result(result)
        
        # Converter para o formato de saída esperado
        return EligibilityAssessmentOutput(
            id=result["id"],
            user_id=result["user_id"],
            created_at=result["created_at"],
            
            # Pontuações
            score=EligibilityScore(**result["score"]),
            
            # Avaliação EB2
            eb2_route=EB2RouteEvaluation(**result["eb2_route"]),
            
            # Avaliação NIW
            niw_evaluation=NIWEvaluation(**result["niw_evaluation"]),
            
            # Classificação
            viability_level=result["viability_level"],
            viability=result["viability"],
            probability=result["probability"],
            
            # Feedback
            strengths=result["strengths"],
            weaknesses=result["weaknesses"],
            recommendations=result["recommendations"],
            
            # Recomendações detalhadas
            detailed_recommendations=[RecommendationDetail(**rec) for rec in result["detailed_recommendations"]],
            
            # Próximos passos e mensagem
            next_steps=result["next_steps"],
            message=result["message"],
            
            # Dados adicionais
            estimated_processing_time=result["estimated_processing_time"]
        )
    
    def _map_viability_level(self, viability_level: str) -> str:
        """
        Mapeia o novo formato de viabilidade para o formato legado.
        
        Args:
            viability_level: Nível de viabilidade (EXCELLENT, STRONG, PROMISING, CHALLENGING, INSUFFICIENT)
            
        Returns:
            Nível de viabilidade no formato legado (Strong, Good, Moderate, Low)
        """
        mapping = {
            "EXCELLENT": "Strong",
            "STRONG": "Strong",
            "PROMISING": "Good",
            "CHALLENGING": "Moderate",
            "INSUFFICIENT": "Low"
        }
        
        return mapping.get(viability_level, "Moderate")
    
    async def process_assessment(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Processa uma avaliação completa de elegibilidade EB2-NIW.
        Mantido para compatibilidade com a API atual.
        
        Args:
            input_data: Dados de entrada para avaliação
            
        Returns:
            Resultados detalhados da avaliação
        """
        try:
            # Utilizar o novo avaliador para processar a avaliação
            assessment_results = await self.evaluator.evaluate(input_data)
            
            return assessment_results
            
        except Exception as e:
            log_structured_data(eligibility_logger, "error", 
                              f"Erro ao processar avaliação: {str(e)}", 
                              {"user_id": input_data.user_id})
            raise

    async def save_assessment_result(self, result: Dict) -> None:
        """
        Salva o resultado da avaliação no banco de dados.
        
        Args:
            result: Resultado da avaliação de elegibilidade
        """
        try:
            # Criar nova entrada no banco de dados
            assessment = EligibilityAssessment(
                id=result["id"],
                user_id=result["user_id"],
                overall_score=result["score"]["overall"],
                viability_level=result["viability_level"],
                viability=result["viability"],
                # Armazenar todos os dados completos para referência futura
                data=json.dumps(result)
            )
            
            # Salvar no banco de dados
            await self.db_manager.create_assessment(assessment)
            
            # Registrar evento na análise do usuário, se houver um user_id
            if result["user_id"]:
                await self.analytics_service.track_assessment_completed(
                    user_id=result["user_id"], 
                    assessment_id=result["id"],
                    score=result["score"]["overall"],
                    viability=result["viability_level"]
                )
            
            scoring_logger.info(f"Avaliação salva no banco de dados: {result['id']}")
            
        except Exception as e:
            scoring_logger.error(f"Erro ao salvar avaliação no banco de dados: {str(e)}")
            # Continuar mesmo com erro de persistência para não impactar a resposta ao usuário
