"""
Schemas para Briefing
"""
from pydantic import BaseModel, Field, field_validator
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
    video_orientation: Optional[str] = Field("horizontal", description="Orientação do vídeo: 'horizontal' (16:9) ou 'vertical' (9:16 para stories/reels)")
    
    @field_validator('video_orientation')
    @classmethod
    def validate_orientation(cls, v):
        """Valida orientação do vídeo"""
        if v and v.lower() not in ['horizontal', 'vertical']:
            raise ValueError("video_orientation deve ser 'horizontal' ou 'vertical'")
        return v.lower() if v else 'horizontal'

class BriefingResponse(BaseModel):
    """Schema de resposta de briefing (IDs ofuscados para segurança)"""
    id: str  # Retorna hash em vez de ID numérico
    title: str
    description: str
    target_audience: Optional[str]
    subject_area: Optional[str]
    teacher_experience_level: Optional[str]
    training_goal: Optional[str]
    duration_minutes: Optional[int]
    tone: Optional[str]
    video_orientation: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    @field_validator('id', mode='before')
    @classmethod
    def hash_id(cls, v):
        """Converte ID numérico em hash ofuscado"""
        from src.utils.hashid import encode_id
        return encode_id(v) if isinstance(v, int) else v
    
    class Config:
        from_attributes = True
