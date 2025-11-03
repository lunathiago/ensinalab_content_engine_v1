"""
Schemas para Briefing
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BriefingCreate(BaseModel):
    """Schema para criar um briefing"""
    title: str = Field(..., min_length=3, max_length=255, description="Título/tema do conteúdo")
    description: str = Field(..., min_length=10, description="Descrição detalhada do que é necessário")
    target_grade: Optional[str] = Field(None, description="Ex: '5º ano', 'Ensino Médio'")
    target_age_min: Optional[int] = Field(None, ge=3, le=18, description="Idade mínima do público")
    target_age_max: Optional[int] = Field(None, ge=3, le=18, description="Idade máxima do público")
    educational_goal: Optional[str] = Field(None, description="Objetivo pedagógico")
    duration_minutes: Optional[int] = Field(None, ge=1, le=30, description="Duração desejada (1-30 min)")
    tone: Optional[str] = Field(None, description="Tom: 'formal', 'descontraído', 'motivacional'")

class BriefingResponse(BaseModel):
    """Schema de resposta de briefing"""
    id: int
    title: str
    description: str
    target_grade: Optional[str]
    target_age_min: Optional[int]
    target_age_max: Optional[int]
    educational_goal: Optional[str]
    duration_minutes: Optional[int]
    tone: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
