from typing import Dict, List, Tuple, Optional
from app.schemas.eligibility import EligibilityAssessmentInput
from app.services.eb2_route_evaluator import EB2RouteEvaluator
from app.services.niw_evaluator import NIWEvaluator

class EligibilityEvaluator:
    """
    Avaliador principal de elegibilidade para vistos EB2-NIW.
    
    Esta classe coordena a avaliação completa de elegibilidade, combinando
    a avaliação das rotas EB2 (Grau Avançado e Habilidade Excepcional)
    com os critérios NIW (National Interest Waiver).
    """
    
    def __init__(self):
        """Inicializa os avaliadores de EB2 e NIW."""
        self.eb2_evaluator = EB2RouteEvaluator()
        self.niw_evaluator = NIWEvaluator()
    
    def evaluate(self, input_data: EligibilityAssessmentInput) -> Dict:
        """
        Realiza uma avaliação completa de elegibilidade para EB2-NIW.
        
        Args:
            input_data: Dados da avaliação de elegibilidade.
            
        Returns:
            Dicionário com resultados detalhados da avaliação.
        """
        # Avaliar rotas EB2
        eb2_evaluation = self.eb2_evaluator.evaluate(input_data)
        
        # Avaliar critérios NIW
        niw_evaluation = self.niw_evaluator.evaluate(input_data)
        
        # Calcular score final combinando EB2 e NIW
        final_score = self.calculate_final_score(
            eb2_score=eb2_evaluation["eligibility_score"],
            niw_score=niw_evaluation["niw_score"]
        )
        
        # Determinar nível de viabilidade
        viability_level = self.determine_viability_level(final_score)
        
        # Construir resultado completo
        result = {
            "score": final_score * 100,  # Convertido para escala 0-100
            "viability_level": viability_level,
            "eb2_route": {
                "recommended_route": eb2_evaluation["recommended_route"],
                "advanced_degree_score": eb2_evaluation["advanced_degree_score"],
                "exceptional_ability_score": eb2_evaluation["exceptional_ability_score"],
                "route_explanation": eb2_evaluation["route_explanation"]
            },
            "niw_evaluation": {
                "merit_importance_score": niw_evaluation["merit_importance_score"],
                "well_positioned_score": niw_evaluation["well_positioned_score"],
                "benefit_waiver_score": niw_evaluation["benefit_waiver_score"],
                "niw_score": niw_evaluation["niw_score"]
            }
        }
        
        return result
    
    def calculate_final_score(self, eb2_score: float, niw_score: float) -> float:
        """
        Calcula o score final combinando a qualificação base EB2 e a qualificação NIW.
        
        Args:
            eb2_score: Pontuação da rota EB2 recomendada (0.0-1.0)
            niw_score: Pontuação da avaliação NIW (0.0-1.0)
            
        Returns:
            Score final (0.0-1.0)
        """
        # Implementação conforme seção 4.3 do documento
        # Pesos: EB2 (40%) e NIW (60%)
        return (eb2_score * 0.4) + (niw_score * 0.6)
    
    def determine_viability_level(self, score: float) -> str:
        """
        Determina o nível de viabilidade com base no score final.
        
        Args:
            score: Score final (0.0-1.0)
            
        Returns:
            Nível de viabilidade (EXCELLENT, STRONG, PROMISING, CHALLENGING, INSUFFICIENT)
        """
        # Converter para escala 0-100 para comparação
        score_100 = score * 100
        
        if score_100 >= 85:
            return "EXCELLENT"
        elif score_100 >= 70:
            return "STRONG"
        elif score_100 >= 55:
            return "PROMISING"
        elif score_100 >= 40:
            return "CHALLENGING"
        else:
            return "INSUFFICIENT"