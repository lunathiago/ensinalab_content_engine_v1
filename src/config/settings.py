"""
Configurações da aplicação usando Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Configurações globais da aplicação"""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database - pode ser URL completa ou componentes individuais
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "ensinalab_content"
    
    def get_database_url(self) -> str:
        """Retorna DATABASE_URL se disponível, senão constrói a partir dos componentes"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Redis (para Celery) - pode ser URL completa ou componentes individuais
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    def get_redis_url(self) -> str:
        """Retorna REDIS_URL se disponível, senão constrói a partir dos componentes"""
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Storage
    UPLOAD_DIR: str = "/tmp/ensinalab_uploads"
    VIDEO_OUTPUT_DIR: str = "/tmp/ensinalab_videos"
    
    # Celery
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    
    @property
    def CELERY_CONFIG(self):
        redis_url = self.get_redis_url()
        return {
            "broker_url": redis_url,
            "result_backend": redis_url,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "America/Sao_Paulo",
            "enable_utc": True,
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
