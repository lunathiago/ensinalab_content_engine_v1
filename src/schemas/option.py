"""
Schemas para Option
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class OptionResponse(BaseModel):
    """Schema de resposta de opção"""
    id: int
    briefing_id: int
    title: str
    summary: Optional[str]
    script_outline: Optional[str]
    key_points: Optional[str]
    estimated_duration: Optional[int]
    tone: Optional[str]
    approach: Optional[str]
    relevance_score: Optional[float]
    quality_score: Optional[float]
    is_selected: bool
    metadata: Optional[Dict[str, Any]] = None  # Dados extras dos agentes
    created_at: datetime
    
    class Config:
        from_attributes = True

class OptionSelect(BaseModel):
    """Schema para selecionar uma opção"""
    notes: Optional[str] = Field(None, description="Notas/ajustes do gestor")
