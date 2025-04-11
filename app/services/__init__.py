"""
Módulo de serviços para a avaliação de elegibilidade de vistos EB2-NIW.
Exporta os principais serviços utilizados pela aplicação.
"""

from app.services.eligibility_service import EligibilityService
from app.services.eligibility_evaluator import EligibilityEvaluator
from app.services.eb2_route_evaluator import EB2RouteEvaluator
from app.services.niw_evaluator import NIWEvaluator
from app.services.recommendation_engine import RecommendationEngine
from app.services.db_manager import DBManager
from app.services.analytics_service import AnalyticsService

__all__ = [
    'EligibilityService',
    'EligibilityEvaluator',
    'EB2RouteEvaluator',
    'NIWEvaluator',
    'RecommendationEngine',
    'DBManager',
    'AnalyticsService'
]
