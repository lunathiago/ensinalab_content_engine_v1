"""
Schemas para autenticação
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema para criar novo usuário"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema para resposta de token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # segundos


class TokenData(BaseModel):
    """Schema para dados extraídos do token"""
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    """Schema para retornar informações do usuário"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    daily_video_limit: int
    monthly_video_limit: int
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
