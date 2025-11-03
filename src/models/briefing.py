"""
Model Briefing - representa um briefing enviado pelo gestor
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from src.config.database import Base

class BriefingStatus(str, enum.Enum):
    """Status do briefing"""
    PENDING = "pending"  # Aguardando processamento
    PROCESSING = "processing"  # Gerando opções
    OPTIONS_READY = "options_ready"  # Opções prontas para escolha
    COMPLETED = "completed"  # Vídeo gerado
    FAILED = "failed"  # Erro

class Briefing(Base):
    """
    Tabela de briefings
    
    Armazena os briefings simplificados enviados pelos gestores
    """
    __tablename__ = "briefings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Público-alvo
    target_grade = Column(String(50))  # Ex: "5º ano", "Ensino Médio"
    target_age_min = Column(Integer)
    target_age_max = Column(Integer)
    
    # Detalhes do conteúdo
    educational_goal = Column(Text)  # Objetivo pedagógico
    duration_minutes = Column(Integer)  # Duração desejada em minutos
    tone = Column(String(100))  # Ex: "formal", "descontraído", "motivacional"
    
    # Metadata
    status = Column(SQLEnum(BriefingStatus), default=BriefingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    options = relationship("Option", back_populates="briefing", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Briefing(id={self.id}, title='{self.title}', status='{self.status}')>"
