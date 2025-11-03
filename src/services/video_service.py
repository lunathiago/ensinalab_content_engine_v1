"""
Service para Videos
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.video import Video, VideoStatus

class VideoService:
    """Serviço de gerenciamento de vídeos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_video(self, video_id: int) -> Optional[Video]:
        """Obtém um vídeo por ID"""
        return self.db.query(Video).filter(Video.id == video_id).first()
    
    def list_videos(self, skip: int = 0, limit: int = 20) -> List[Video]:
        """Lista vídeos com paginação"""
        return self.db.query(Video).order_by(
            Video.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def update_status(
        self, 
        video_id: int, 
        status: VideoStatus, 
        progress: float = None,
        error_message: str = None
    ) -> Optional[Video]:
        """Atualiza o status de um vídeo (usado pelo worker)"""
        video = self.get_video(video_id)
        if not video:
            return None
        
        video.status = status
        if progress is not None:
            video.progress = progress
        if error_message:
            video.error_message = error_message
        
        self.db.commit()
        self.db.refresh(video)
        return video
    
    def complete_video(
        self, 
        video_id: int, 
        file_path: str, 
        file_size: int,
        duration: int,
        thumbnail_path: str = None
    ) -> Optional[Video]:
        """Marca vídeo como completo (chamado pelo worker)"""
        video = self.get_video(video_id)
        if not video:
            return None
        
        video.status = VideoStatus.COMPLETED
        video.progress = 1.0
        video.file_path = file_path
        video.file_size_bytes = file_size
        video.duration_seconds = duration
        video.thumbnail_path = thumbnail_path
        
        from datetime import datetime
        video.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(video)
        return video
