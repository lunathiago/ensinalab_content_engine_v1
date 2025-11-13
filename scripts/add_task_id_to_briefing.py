#!/usr/bin/env python3
"""
Migration: Adicionar task_id ao modelo Briefing

Adiciona campo task_id para armazenar ID da task Celery de geração de opções
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.config.database import engine

def add_task_id_column():
    """Adiciona coluna task_id à tabela briefings"""
    
    with engine.connect() as conn:
        # Verificar se coluna já existe
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='briefings' AND column_name='task_id'
        """))
        
        if result.fetchone():
            print("✓ Coluna task_id já existe em briefings")
            return
        
        # Adicionar coluna
        print("📝 Adicionando task_id a briefings...")
        conn.execute(text("""
            ALTER TABLE briefings 
            ADD COLUMN task_id VARCHAR(255)
        """))
        conn.commit()
        
        print("✓ Migration concluída com sucesso!")
        print("\nColuna adicionada:")
        print("  - briefings.task_id (VARCHAR(255))")

if __name__ == "__main__":
    print("🚀 Iniciando migration: add_task_id_to_briefing")
    print("=" * 60)
    
    try:
        add_task_id_column()
        print("\n✅ Migration executada com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
