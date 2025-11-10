"""
Script para criar as tabelas do banco de dados
"""
# IMPORTANTE: Importar todos os models ANTES de chamar init_db()
from src.models.user import User
from src.models.briefing import Briefing
from src.models.option import Option
from src.models.video import Video
from src.config.database import init_db

if __name__ == "__main__":
    print("🗄️  Criando tabelas no banco de dados...")
    init_db()
    print("✅ Tabelas criadas com sucesso!")
