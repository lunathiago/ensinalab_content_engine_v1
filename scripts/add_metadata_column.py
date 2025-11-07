"""
Script de migração: Adiciona coluna metadata na tabela options
"""
import os
from sqlalchemy import text
from src.config.database import engine

def add_metadata_column():
    """Adiciona coluna metadata (JSON) na tabela options"""
    
    print("🔄 Adicionando coluna metadata na tabela options...")
    
    with engine.connect() as conn:
        # Verificar se coluna já existe
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='options' AND column_name='metadata'
        """)
        
        result = conn.execute(check_query)
        exists = result.fetchone()
        
        if exists:
            print("ℹ️  Coluna metadata já existe. Nada a fazer.")
            return
        
        # Adicionar coluna
        alter_query = text("""
            ALTER TABLE options 
            ADD COLUMN metadata JSON
        """)
        
        conn.execute(alter_query)
        conn.commit()
        
        print("✅ Coluna metadata adicionada com sucesso!")

if __name__ == "__main__":
    add_metadata_column()
