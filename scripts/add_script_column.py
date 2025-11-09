#!/usr/bin/env python3
"""
Adiciona coluna script na tabela videos
Para armazenar o roteiro completo do vídeo
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.config.database import SessionLocal, engine


def add_script_column():
    """Adiciona coluna script na tabela videos"""
    
    print("🔧 Adicionando coluna 'script' na tabela 'videos'...")
    
    try:
        with engine.connect() as conn:
            # Verificar se coluna já existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'videos' 
                AND column_name = 'script'
            """))
            
            if result.fetchone():
                print("⚠️  Coluna 'script' já existe. Nada a fazer.")
                return
            
            # Adicionar coluna
            conn.execute(text("""
                ALTER TABLE videos 
                ADD COLUMN script TEXT NOT NULL DEFAULT ''
            """))
            
            conn.commit()
            
            print("✅ Coluna 'script' adicionada com sucesso!")
            print("   Tipo: TEXT (roteiro completo do vídeo)")
            
            # Verificar
            result = conn.execute(text("""
                SELECT script 
                FROM videos 
                LIMIT 1
            """))
            
            row = result.fetchone()
            if row is not None:
                print(f"   Teste: script existe (valor: '{row[0][:50]}...' se houver dados)")
            else:
                print("   Teste: coluna script criada (sem dados ainda)")
            
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    print("\n" + "="*60)
    print("🎬 VIDEO SCRIPT COLUMN MIGRATION")
    print("="*60 + "\n")
    
    add_script_column()
    
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO COMPLETA!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
