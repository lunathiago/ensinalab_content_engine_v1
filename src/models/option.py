"""
Model Option - representa uma opção de conteúdo gerada pelo motor
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.config.database import Base

class Option(Base):
    """
    Tabela de opções de conteúdo
    
    O motor gera várias opções para cada briefing
    O gestor escolhe a que melhor se adequa
    """
    __tablename__ = "options"
    
    id = Column(Integer, primary_key=True, index=True)
    briefing_id = Column(Integer, ForeignKey("briefings.id"), nullable=False)
    
    # Conteúdo da opção
    title = Column(String(255), nullable=False)
    summary = Column(Text)  # Resumo da proposta
    script_outline = Column(Text)  # Esboço do roteiro
    key_points = Column(Text)  # Pontos-chave (JSON ou texto)
    
    # Detalhes técnicos
    estimated_duration = Column(Integer)  # Duração estimada em segundos
    tone = Column(String(100))
    approach = Column(String(255))  # Abordagem pedagógica
    
    # Scoring (gerado pelo filtro/classificador)
    relevance_score = Column(Float)  # Score de relevância (0-1)
    quality_score = Column(Float)  # Score de qualidade (0-1)
    
    # Seleção
    is_selected = Column(Boolean, default=False)
    selection_notes = Column(Text)  # Notas do gestor ao selecionar
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    briefing = relationship("Briefing", back_populates="options")
    video = relationship("Video", back_populates="option", uselist=False)
    
    def __repr__(self):
        return f"<Option(id={self.id}, briefing_id={self.briefing_id}, title='{self.title}')>"
