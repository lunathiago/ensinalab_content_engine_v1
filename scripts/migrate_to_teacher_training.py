"""
Script de migração: Atualizar tabela briefings para contexto de treinamento de professores

Este script renomeia as colunas antigas para o novo contexto:
- target_grade → target_audience
- target_age_min, target_age_max → removidos
- educational_goal → training_goal
- Adiciona: subject_area, teacher_experience_level
"""

from sqlalchemy import text
from src.config.database import engine

def migrate():
    """Executa a migração do banco de dados"""
    
    with engine.connect() as conn:
        print("🔄 Iniciando migração...")
        
        try:
            # 1. Verificar se tabela existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'briefings'
                );
            """))
            
            if not result.fetchone()[0]:
                print("⚠️  Tabela 'briefings' não existe. Execute create_tables.py primeiro.")
                return
            
            # 2. Verificar se já foi migrada
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'briefings' AND column_name = 'target_audience';
            """))
            
            if result.fetchone():
                print("✅ Migração já foi aplicada anteriormente.")
                return
            
            # 3. Renomear colunas
            print("📝 Renomeando colunas...")
            
            conn.execute(text("""
                ALTER TABLE briefings 
                RENAME COLUMN target_grade TO target_audience;
            """))
            
            conn.execute(text("""
                ALTER TABLE briefings 
                RENAME COLUMN educational_goal TO training_goal;
            """))
            
            # 4. Remover colunas antigas
            print("🗑️  Removendo colunas antigas...")
            
            conn.execute(text("""
                ALTER TABLE briefings 
                DROP COLUMN IF EXISTS target_age_min,
                DROP COLUMN IF EXISTS target_age_max;
            """))
            
            # 5. Adicionar novas colunas
            print("➕ Adicionando novas colunas...")
            
            conn.execute(text("""
                ALTER TABLE briefings 
                ADD COLUMN IF NOT EXISTS subject_area VARCHAR(100),
                ADD COLUMN IF NOT EXISTS teacher_experience_level VARCHAR(50);
            """))
            
            conn.commit()
            
            print("✅ Migração concluída com sucesso!")
            print("")
            print("Mudanças aplicadas:")
            print("  ✓ target_grade → target_audience")
            print("  ✓ educational_goal → training_goal")
            print("  ✓ Removido: target_age_min, target_age_max")
            print("  ✓ Adicionado: subject_area, teacher_experience_level")
            
        except Exception as e:
            print(f"❌ Erro na migração: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
