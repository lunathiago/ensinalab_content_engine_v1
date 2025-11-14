"""
Script para DROPAR e RECRIAR todas as tabelas do banco de dados
⚠️  ATENÇÃO: Isso vai DELETAR TODOS OS DADOS!
Use apenas em desenvolvimento/testes
"""
import sys
print("=" * 60)
print("🚀 INICIANDO RECREATE_TABLES.PY")
print("=" * 60)

# IMPORTANTE: Importar todos os models ANTES de chamar drop/create
try:
    print("📦 Importando models...")
    from src.models.user import User
    from src.models.briefing import Briefing
    from src.models.option import Option
    from src.models.video import Video
    from src.config.database import Base, engine
    print("✅ Models importados com sucesso!")
except Exception as e:
    print(f"❌ ERRO ao importar models: {e}")
    sys.exit(1)

if __name__ == "__main__":
    try:
        print("\n⚠️  ATENÇÃO: Este script vai DELETAR TODOS OS DADOS do banco!")
        print("🗄️  Dropando todas as tabelas...")
        Base.metadata.drop_all(bind=engine)
        print("✅ Tabelas dropadas!")
        
        print("\n🗄️  Criando tabelas novamente...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        
        print("\n📋 Tabelas recriadas:")
        print("  - users (id, email, username, hashed_password, created_at)")
        print("  - briefings (id, user_id, title, description, video_orientation, etc)")
        print("  - options (id, briefing_id, title, summary, script_outline, etc)")
        print("  - videos (id, option_id, title, file_path, status, etc)")
        
        print("\n" + "=" * 60)
        print("✅ RECREATE_TABLES.PY CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERRO durante recreate_tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
