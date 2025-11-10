"""
Configuração do banco de dados com SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings

# Engine do SQLAlchemy
engine = create_engine(
    settings.get_database_url(),
    pool_pre_ping=True,
    echo=settings.DEBUG  # Log SQL queries em modo debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models
Base = declarative_base()

def get_db():
    """
    Dependency para obter sessão do banco de dados
    Uso: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def import_all_models():
    """
    Importa todos os models para garantir que o SQLAlchemy os registre
    Deve ser chamado antes de qualquer operação de DB
    """
    from src.models.user import User
    from src.models.briefing import Briefing
    from src.models.option import Option
    from src.models.video import Video
    # Retorna os models para evitar warning de "unused import"
    return User, Briefing, Option, Video

def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    import_all_models()  # Garantir que todos os models estão registrados
    Base.metadata.create_all(bind=engine)
