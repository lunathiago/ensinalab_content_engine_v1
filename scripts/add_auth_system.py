"""
Migration Script: Adicionar Sistema de Autenticação

Este script:
1. Cria a tabela users
2. Cria usuário admin padrão
3. Adiciona coluna user_id em briefings
4. Associa briefings existentes ao admin
5. Torna user_id NOT NULL após backfill

Executar: python scripts/add_auth_system.py
"""
import os
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.services.auth_service import get_password_hash
from src.config.settings import settings

def run_migration():
    """Executa a migração do sistema de autenticação"""
    
    # Conectar ao banco
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🔄 Iniciando migração do sistema de autenticação...\n")
    
    try:
        # 1. Criar tabela users
        print("1️⃣ Criando tabela users...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE NOT NULL,
                daily_video_limit INTEGER DEFAULT 10 NOT NULL,
                monthly_video_limit INTEGER DEFAULT 100 NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """))
        session.commit()
        print("✅ Tabela users criada\n")
        
        # 2. Criar usuário admin padrão
        print("2️⃣ Criando usuário admin padrão...")
        
        # Verificar se admin já existe
        result = session.execute(text("SELECT id FROM users WHERE email = 'admin@ensinalab.com'"))
        admin_exists = result.fetchone()
        
        if not admin_exists:
            admin_password = get_password_hash("admin123")
            session.execute(text("""
                INSERT INTO users (email, username, hashed_password, full_name, is_active, is_admin)
                VALUES (:email, :username, :password, :full_name, :is_active, :is_admin)
            """), {
                'email': 'admin@ensinalab.com',
                'username': 'admin',
                'password': admin_password,
                'full_name': 'Administrador',
                'is_active': True,
                'is_admin': True
            })
            session.commit()
            print("✅ Usuário admin criado (email: admin@ensinalab.com, senha: admin123)\n")
        else:
            print("ℹ️  Usuário admin já existe\n")
        
        # 3. Obter ID do admin
        result = session.execute(text("SELECT id FROM users WHERE email = 'admin@ensinalab.com'"))
        admin_id = result.fetchone()[0]
        print(f"📝 Admin ID: {admin_id}\n")
        
        # 4. Adicionar coluna user_id em briefings (nullable temporariamente)
        print("3️⃣ Adicionando coluna user_id em briefings...")
        try:
            session.execute(text("""
                ALTER TABLE briefings 
                ADD COLUMN IF NOT EXISTS user_id INTEGER
            """))
            session.commit()
            print("✅ Coluna user_id adicionada\n")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️  Coluna user_id já existe\n")
                session.rollback()
            else:
                raise
        
        # 5. Associar briefings existentes ao admin
        print("4️⃣ Associando briefings existentes ao admin...")
        result = session.execute(text("""
            UPDATE briefings 
            SET user_id = :admin_id 
            WHERE user_id IS NULL
        """), {'admin_id': admin_id})
        session.commit()
        updated_count = result.rowcount
        print(f"✅ {updated_count} briefing(s) associado(s) ao admin\n")
        
        # 6. Tornar user_id NOT NULL
        print("5️⃣ Tornando user_id obrigatório...")
        try:
            session.execute(text("""
                ALTER TABLE briefings 
                ALTER COLUMN user_id SET NOT NULL
            """))
            session.commit()
            print("✅ user_id agora é obrigatório\n")
        except Exception as e:
            if "not null constraint" in str(e).lower():
                print("ℹ️  user_id já é NOT NULL\n")
                session.rollback()
            else:
                raise
        
        # 7. Adicionar foreign key constraint
        print("6️⃣ Adicionando foreign key constraint...")
        try:
            session.execute(text("""
                ALTER TABLE briefings 
                ADD CONSTRAINT fk_briefings_user 
                FOREIGN KEY (user_id) REFERENCES users(id)
            """))
            session.commit()
            print("✅ Foreign key adicionada\n")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️  Foreign key já existe\n")
                session.rollback()
            else:
                raise
        
        # 8. Criar índice para melhor performance
        print("7️⃣ Criando índice em user_id...")
        try:
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_briefings_user_id 
                ON briefings(user_id)
            """))
            session.commit()
            print("✅ Índice criado\n")
        except Exception as e:
            print(f"⚠️  Aviso ao criar índice: {e}\n")
            session.rollback()
        
        print("=" * 60)
        print("✅ Migração concluída com sucesso!")
        print("=" * 60)
        print("\n📋 Resumo:")
        print(f"  • Tabela users criada")
        print(f"  • Admin criado: admin@ensinalab.com (senha: admin123)")
        print(f"  • Coluna user_id adicionada em briefings")
        print(f"  • {updated_count} briefing(s) associado(s) ao admin")
        print(f"  • Constraints e índices criados")
        print("\n🔐 Credenciais de Teste:")
        print("  Email: admin@ensinalab.com")
        print("  Senha: admin123")
        print("\n⚠️  IMPORTANTE: Altere a senha do admin em produção!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()
