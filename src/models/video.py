"""
Model Video - representa um vídeo gerado
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from src.config.database import Base

class VideoStatus(str, enum.Enum):
    """Status da geração do vídeo"""
    QUEUED = "queued"  # Na fila
    PROCESSING = "processing"  # Sendo gerado
    COMPLETED = "completed"  # Pronto
    FAILED = "failed"  # Erro
    CANCELLED = "cancelled"  # Cancelado pelo usuário

class Video(Base):
    """
    Tabela de vídeos
    
    Armazena informações sobre vídeos gerados
    """
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, ForeignKey("options.id"), nullable=False, unique=True)
    
    # Informações do vídeo
    title = Column(String(255), nullable=False)
    description = Column(Text)
    script = Column(Text, nullable=False)  # Roteiro completo do vídeo
    duration_seconds = Column(Integer)
    
    # Arquivo
    file_path = Column(String(500))  # Caminho do arquivo MP4
    file_size_bytes = Column(Integer)
    thumbnail_path = Column(String(500))
    
    # Generator usado
    generator_type = Column(String(20), default='simple')  # simple, avatar, ai
    
    # Status de geração
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.QUEUED)
    progress = Column(Float, default=0.0)  # 0.0 a 1.0
    error_message = Column(Text)
    
    # Celery task
    task_id = Column(String(255))  # ID da task Celery
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relacionamentos
    option = relationship("Option", back_populates="video")
    
    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}', status='{self.status}')>"
