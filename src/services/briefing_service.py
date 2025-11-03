"""
Service para Briefings
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.briefing import Briefing, BriefingStatus
from src.schemas.briefing import BriefingCreate

class BriefingService:
    """Serviço de gerenciamento de briefings"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_briefing(self, briefing_data: BriefingCreate) -> Briefing:
        """Cria um novo briefing"""
        briefing = Briefing(
            title=briefing_data.title,
            description=briefing_data.description,
            target_audience=briefing_data.target_audience,
            subject_area=briefing_data.subject_area,
            teacher_experience_level=briefing_data.teacher_experience_level,
            training_goal=briefing_data.training_goal,
            duration_minutes=briefing_data.duration_minutes,
            tone=briefing_data.tone,
            status=BriefingStatus.PENDING
        )
        
        self.db.add(briefing)
        self.db.commit()
        self.db.refresh(briefing)
        
        # TODO: Disparar task Celery para gerar opções
        # from src.workers.tasks import generate_options
        # generate_options.delay(briefing.id)
        
        return briefing
    
    def get_briefing(self, briefing_id: int) -> Optional[Briefing]:
        """Obtém um briefing por ID"""
        return self.db.query(Briefing).filter(Briefing.id == briefing_id).first()
    
    def list_briefings(self, skip: int = 0, limit: int = 20) -> List[Briefing]:
        """Lista briefings com paginação"""
        return self.db.query(Briefing).offset(skip).limit(limit).all()
    
    def delete_briefing(self, briefing_id: int) -> bool:
        """Deleta um briefing"""
        briefing = self.get_briefing(briefing_id)
        if not briefing:
            return False
        
        self.db.delete(briefing)
        self.db.commit()
        return True
    
    def update_status(self, briefing_id: int, status: BriefingStatus) -> Optional[Briefing]:
        """Atualiza o status de um briefing"""
        briefing = self.get_briefing(briefing_id)
        if not briefing:
            return None
        
        briefing.status = status
        self.db.commit()
        self.db.refresh(briefing)
        return briefing
