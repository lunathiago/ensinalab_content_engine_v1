"""
Schemas para Option
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime

class OptionResponse(BaseModel):
    """Schema de resposta de opção (IDs ofuscados para segurança)"""
    id: str  # Hash em vez de ID numérico
    briefing_id: str  # Hash em vez de ID numérico
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
    extra_data: Optional[Dict[str, Any]] = None  # Dados extras dos agentes
    created_at: datetime
    
    @field_validator('id', 'briefing_id', mode='before')
    @classmethod
    def hash_id(cls, v):
        """Converte IDs numéricos em hashes ofuscados"""
        from src.utils.hashid import encode_id
        return encode_id(v) if isinstance(v, int) else v
    
    class Config:
        from_attributes = True

class OptionSelect(BaseModel):
    """Schema para selecionar uma opção"""
    notes: Optional[str] = Field(None, description="Notas/ajustes do gestor")
