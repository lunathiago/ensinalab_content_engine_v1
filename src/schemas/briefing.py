"""
Schemas para Briefing
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BriefingCreate(BaseModel):
    """Schema para criar um briefing"""
    title: str = Field(..., min_length=3, max_length=255, description="Título/tema do treinamento")
    description: str = Field(..., min_length=10, description="Descrição detalhada do conteúdo de capacitação")
    target_audience: Optional[str] = Field(None, description="Público-alvo: 'Professores Iniciantes', 'Coordenadores', 'Todos os Professores'")
    subject_area: Optional[str] = Field(None, description="Área/disciplina: 'Matemática', 'Língua Portuguesa', 'Gestão de Sala', 'Geral'")
    teacher_experience_level: Optional[str] = Field(None, description="Nível de experiência: 'Iniciante', 'Intermediário', 'Avançado', 'Todos'")
    training_goal: Optional[str] = Field(None, description="Objetivo do treinamento: ex. 'Melhorar gestão de sala', 'Técnicas de avaliação'")
    duration_minutes: Optional[int] = Field(None, ge=1, le=30, description="Duração desejada (1-30 min)")
    tone: Optional[str] = Field(None, description="Tom: 'formal', 'prático', 'inspiracional', 'técnico'")

class BriefingResponse(BaseModel):
    """Schema de resposta de briefing"""
    id: int
    title: str
    description: str
    target_audience: Optional[str]
    subject_area: Optional[str]
    teacher_experience_level: Optional[str]
    training_goal: Optional[str]
    duration_minutes: Optional[int]
    tone: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
