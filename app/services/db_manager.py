from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.eligibility import QuickAssessment
from app.core.logging import log_structured_data, eligibility_logger
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DBManager:
    """
    Gerencia operações de banco de dados para o serviço de elegibilidade.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de banco de dados."""
        self.session_factory = SessionLocal
    
    async def create_eligibility_assessment(self, assessment: QuickAssessment) -> QuickAssessment:
        """
        Persiste uma avaliação de elegibilidade no banco de dados.
        
        Args:
            assessment: Objeto QuickAssessment a ser criado
            
        Returns:
            O objeto QuickAssessment criado com seu ID
        """
        db = self.session_factory()
        try:
            log_structured_data(eligibility_logger, "info", 
                              f"Persistindo avaliação no banco de dados: {assessment.id}", 
                              {"user_id": assessment.user_id})
            
            # Se este for o último assessment para o usuário, atualizar os outros
            if assessment.is_latest and assessment.user_id:
                # Marcar assessments anteriores como não sendo os mais recentes
                db.query(QuickAssessment).filter(
                    QuickAssessment.user_id == assessment.user_id,
                    QuickAssessment.is_latest == True
                ).update({"is_latest": False})
            
            # Adicionar o novo assessment
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            
            log_structured_data(eligibility_logger, "info", 
                              f"Avaliação persistida com sucesso: {assessment.id}")
            
            return assessment
            
        except Exception as e:
            db.rollback()
            log_structured_data(eligibility_logger, "error", 
                              f"Erro ao persistir avaliação: {str(e)}", 
                              {"assessment_id": assessment.id})
            # Em ambiente de desenvolvimento, logar falha mas não falhar a operação
            logger.exception("Erro ao persistir avaliação de elegibilidade")
            return assessment
            
        finally:
            db.close()
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[QuickAssessment]:
        """
        Recupera uma avaliação pelo seu ID.
        
        Args:
            assessment_id: ID da avaliação
            
        Returns:
            O objeto QuickAssessment correspondente ou None se não encontrado
        """
        db = self.session_factory()
        try:
            assessment = db.query(QuickAssessment).filter(QuickAssessment.id == assessment_id).first()
            return assessment
        finally:
            db.close()
    
    async def get_latest_assessment_for_user(self, user_id: str) -> Optional[QuickAssessment]:
        """
        Recupera a avaliação mais recente para um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            O objeto QuickAssessment mais recente ou None se não houver
        """
        db = self.session_factory()
        try:
            assessment = db.query(QuickAssessment).filter(
                QuickAssessment.user_id == user_id,
                QuickAssessment.is_latest == True
            ).first()
            return assessment
        finally:
            db.close() 