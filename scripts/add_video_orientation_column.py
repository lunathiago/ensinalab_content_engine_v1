#!/usr/bin/env python3
"""
Migração: Adiciona coluna video_orientation à tabela briefings

Execução:
    python scripts/add_video_orientation_column.py
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from src.config.database import engine

def add_video_orientation_column():
    """Adiciona coluna video_orientation à tabela briefings"""
    
    print("=" * 70)
    print("MIGRAÇÃO: Adicionar coluna video_orientation")
    print("=" * 70)
    
    with engine.connect() as conn:
        # Verificar se coluna já existe
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='briefings' 
            AND column_name='video_orientation'
        """))
        
        if result.fetchone():
            print("✅ Coluna 'video_orientation' já existe. Nada a fazer.")
            return True
        
        print("\n📝 Adicionando coluna 'video_orientation'...")
        
        try:
            # Adicionar coluna com valor padrão
            conn.execute(text("""
                ALTER TABLE briefings 
                ADD COLUMN video_orientation VARCHAR(20) DEFAULT 'horizontal'
            """))
            
            # Atualizar registros existentes
            conn.execute(text("""
                UPDATE briefings 
                SET video_orientation = 'horizontal' 
                WHERE video_orientation IS NULL
            """))
            
            conn.commit()
            
            print("✅ Coluna adicionada com sucesso!")
            print("\nDetalhes:")
            print("  - Nome: video_orientation")
            print("  - Tipo: VARCHAR(20)")
            print("  - Default: 'horizontal'")
            print("  - Valores aceitos: 'horizontal' (16:9) ou 'vertical' (9:16)")
            print("\n📊 Registros existentes atualizados para 'horizontal'")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar coluna: {e}")
            conn.rollback()
            return False

if __name__ == "__main__":
    success = add_video_orientation_column()
    sys.exit(0 if success else 1)
