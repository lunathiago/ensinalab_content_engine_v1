"""
Script para DROPAR e RECRIAR todas as tabelas do banco de dados
⚠️  ATENÇÃO: Isso vai DELETAR TODOS OS DADOS!
Use apenas em desenvolvimento/testes
"""
# IMPORTANTE: Importar todos os models ANTES de chamar drop/create
from src.models.user import User
from src.models.briefing import Briefing
from src.models.option import Option
from src.models.video import Video
from src.config.database import Base, engine

if __name__ == "__main__":
    print("⚠️  ATENÇÃO: Este script vai DELETAR TODOS OS DADOS do banco!")
    print("🗄️  Dropando todas as tabelas...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tabelas dropadas!")
    
    print("🗄️  Criando tabelas novamente...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    
    print("\n📋 Tabelas recriadas:")
    print("  - users")
    print("  - briefings")
    print("  - options")
    print("  - videos")
