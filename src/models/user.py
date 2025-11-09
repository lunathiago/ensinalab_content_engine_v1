"""
Model User - representa um usuário do sistema
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.config.database import Base


class User(Base):
    """
    Tabela de usuários
    
    Gerencia autenticação e autorização
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Credenciais
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Permissions
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Limits (para controle de uso)
    daily_video_limit = Column(Integer, default=10)
    monthly_video_limit = Column(Integer, default=100)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relacionamentos
    briefings = relationship("Briefing", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
