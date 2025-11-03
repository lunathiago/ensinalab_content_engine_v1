"""
Service para Options
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from src.models.option import Option
from src.models.video import Video, VideoStatus

class OptionService:
    """Serviço de gerenciamento de opções"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_options_by_briefing(self, briefing_id: int) -> List[Option]:
        """Obtém todas as opções de um briefing"""
        return self.db.query(Option).filter(
            Option.briefing_id == briefing_id
        ).order_by(
            Option.relevance_score.desc()
        ).all()
    
    def get_option(self, option_id: int) -> Optional[Option]:
        """Obtém uma opção por ID"""
        return self.db.query(Option).filter(Option.id == option_id).first()
    
    def select_option(self, option_id: int, notes: Optional[str] = None) -> Optional[Dict]:
        """
        Marca uma opção como selecionada e dispara geração de vídeo
        """
        option = self.get_option(option_id)
        if not option:
            return None
        
        # Marca como selecionada
        option.is_selected = True
        option.selection_notes = notes
        
        # Cria registro de vídeo
        video = Video(
            option_id=option.id,
            title=option.title,
            description=option.summary,
            status=VideoStatus.QUEUED,
            progress=0.0
        )
        
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        
        # TODO: Disparar task Celery para gerar vídeo
        # from src.workers.tasks import generate_video
        # task = generate_video.delay(video.id)
        # video.task_id = task.id
        # self.db.commit()
        
        return {
            "video_id": video.id,
            "option_id": option.id
        }
    
    def create_option(self, option_data: dict) -> Option:
        """Cria uma nova opção (usado pelo motor de geração)"""
        option = Option(**option_data)
        self.db.add(option)
        self.db.commit()
        self.db.refresh(option)
        return option
