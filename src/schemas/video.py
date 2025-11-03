"""
Schemas para Video
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoResponse(BaseModel):
    """Schema de resposta de vídeo"""
    id: int
    option_id: int
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
    
    class Config:
        from_attributes = True
