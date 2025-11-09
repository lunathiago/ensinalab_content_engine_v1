"""
Schemas para Video
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class VideoResponse(BaseModel):
    """Schema de resposta de vídeo (IDs ofuscados para segurança)"""
    id: str  # Hash em vez de ID numérico
    option_id: str  # Hash em vez de ID numérico
    title: str
    description: Optional[str]
    duration_seconds: Optional[int]
    file_path: Optional[str]
    file_size_bytes: Optional[int]
    thumbnail_path: Optional[str]
    status: str
    progress: float
    error_message: Optional[str]
    task_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    @field_validator('id', 'option_id', mode='before')
    @classmethod
    def hash_id(cls, v):
        """Converte IDs numéricos em hashes ofuscados"""
        from src.utils.hashid import encode_id
        return encode_id(v) if isinstance(v, int) else v
    
    class Config:
        from_attributes = True
