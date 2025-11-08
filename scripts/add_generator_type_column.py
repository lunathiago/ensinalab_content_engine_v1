#!/usr/bin/env python3
"""
Adiciona campo generator_type ao modelo Video
Para rastrear qual gerador foi usado
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.config.database import SessionLocal, engine


def add_generator_type_column():
    """Adiciona coluna generator_type na tabela videos"""
    
    print("🔧 Adicionando coluna 'generator_type' na tabela 'videos'...")
    
    try:
        with engine.connect() as conn:
            # Verificar se coluna já existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'videos' 
                AND column_name = 'generator_type'
            """))
            
            if result.fetchone():
                print("⚠️  Coluna 'generator_type' já existe. Nada a fazer.")
                return
            
            # Adicionar coluna
            conn.execute(text("""
                ALTER TABLE videos 
                ADD COLUMN generator_type VARCHAR(20) DEFAULT 'simple'
            """))
            
            conn.commit()
            
            print("✅ Coluna 'generator_type' adicionada com sucesso!")
            print("   Valores possíveis: 'simple', 'avatar', 'ai'")
            print("   Default: 'simple'")
            
            # Verificar
            result = conn.execute(text("""
                SELECT generator_type 
                FROM videos 
                LIMIT 1
            """))
            
            row = result.fetchone()
            if row:
                print(f"   Teste: generator_type = {row[0]}")
            
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    print("\n" + "="*60)
    print("🎬 VIDEO GENERATOR TYPE MIGRATION")
    print("="*60 + "\n")
    
    add_generator_type_column()
    
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO COMPLETA!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
