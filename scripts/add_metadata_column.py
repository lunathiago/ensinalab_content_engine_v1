"""
Script de migração: Adiciona coluna extra_data na tabela options
"""
import os
from sqlalchemy import text
from src.config.database import engine

def add_extra_data_column():
    """Adiciona coluna extra_data (JSON) na tabela options"""
    
    print("🔄 Adicionando coluna extra_data na tabela options...")
    
    with engine.connect() as conn:
        # Verificar se coluna já existe
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='options' AND column_name='extra_data'
        """)
        
        result = conn.execute(check_query)
        exists = result.fetchone()
        
        if exists:
            print("ℹ️  Coluna extra_data já existe. Nada a fazer.")
            return
        
        # Adicionar coluna
        alter_query = text("""
            ALTER TABLE options 
            ADD COLUMN extra_data JSON
        """)
        
        conn.execute(alter_query)
        conn.commit()
        
        print("✅ Coluna extra_data adicionada com sucesso!")

if __name__ == "__main__":
    add_extra_data_column()
