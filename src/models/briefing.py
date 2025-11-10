"""
Model Briefing - representa um briefing enviado pelo gestor
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
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
    
    Armazena os briefings simplificados enviados pelos gestores escolares
    para gerar conteúdo de treinamento/capacitação de professores
    """
    __tablename__ = "briefings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Owner do briefing
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Público-alvo (professores)
    target_audience = Column(String(100))  # Ex: "Professores Iniciantes", "Coordenadores"
    subject_area = Column(String(100))  # Ex: "Matemática", "Gestão de Sala", "Geral"
    teacher_experience_level = Column(String(50))  # Ex: "Iniciante", "Intermediário", "Avançado"
    
    # Detalhes do treinamento
    training_goal = Column(Text)  # Objetivo do treinamento/capacitação
    duration_minutes = Column(Integer)  # Duração desejada em minutos
    tone = Column(String(100))  # Ex: "formal", "prático", "inspiracional", "técnico"
    
    # Metadata
    status = Column(SQLEnum(BriefingStatus), default=BriefingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="briefings", lazy="select")  # Lazy loading
    options = relationship("Option", back_populates="briefing", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        return f"<Briefing(id={self.id}, title='{self.title}', status='{self.status}')>"
