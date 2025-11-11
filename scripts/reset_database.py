#!/usr/bin/env python3
"""
Script de Reset: Limpa TODAS as tabelas do banco de dados
CUIDADO: Isso apaga TODOS OS DADOS permanentemente!
"""
import os
import sys
from sqlalchemy import create_engine, text


def confirm_reset():
    """Pede confirmação ao usuário"""
    print("\n" + "="*60)
    print("⚠️  AVISO: OPERAÇÃO DESTRUTIVA")
    print("="*60)
    print("\nEste script vai:")
    print("  🗑️  Deletar TODAS as tabelas")
    print("  🗑️  Apagar TODOS os dados (usuários, briefings, vídeos)")
    print("  🗑️  Resetar o banco para estado inicial")
    print("\n❌ ESTA AÇÃO É IRREVERSÍVEL!")
    print("\nDigite 'RESET' para confirmar (maiúsculas): ", end="")
    
    confirmation = input()
    
    if confirmation != "RESET":
        print("\n✅ Operação cancelada. Nenhum dado foi alterado.")
        return False
    
    print("\n⚠️  Última chance! Digite 'SIM' para prosseguir: ", end="")
    final = input()
    
    if final != "SIM":
        print("\n✅ Operação cancelada. Nenhum dado foi alterado.")
        return False
    
    return True


def reset_database():
    """Reseta o banco de dados completamente"""
    
    # Obter DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("\n❌ Erro: DATABASE_URL não encontrado no ambiente")
        print("Configure a variável de ambiente ou rode no Render Shell")
        return False
    
    # Ajustar URL se necessário (Render às vezes usa postgres://, SQLAlchemy usa postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"\n🔗 Conectando ao banco: {database_url[:40]}...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            print("\n✅ Conectado ao banco de dados")
            
            # Listar tabelas antes
            print("\n📋 Tabelas existentes:")
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            
            tables = [row[0] for row in result]
            
            if not tables:
                print("   (nenhuma tabela encontrada)")
            else:
                for table in tables:
                    print(f"   - {table}")
            
            # Confirmar novamente
            print(f"\n⚠️  {len(tables)} tabela(s) será(ão) deletada(s)")
            print("Digite 'DELETAR' para confirmar: ", end="")
            
            if input() != "DELETAR":
                print("\n✅ Operação cancelada")
                return False
            
            print("\n🗑️  Deletando todas as tabelas...")
            
            # Dropar schema public e recriar (mais seguro que dropar tabelas individualmente)
            conn.execute(text("DROP SCHEMA public CASCADE"))
            print("   ✓ Schema 'public' deletado")
            
            conn.execute(text("CREATE SCHEMA public"))
            print("   ✓ Schema 'public' recriado")
            
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            print("   ✓ Permissões restauradas")
            
            conn.commit()
            
            # Verificar se ficou limpo
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            
            remaining = [row[0] for row in result]
            
            if remaining:
                print(f"\n⚠️  Ainda há {len(remaining)} tabela(s):")
                for table in remaining:
                    print(f"   - {table}")
            else:
                print("\n✅ Banco completamente limpo!")
            
            print("\n" + "="*60)
            print("✅ RESET CONCLUÍDO COM SUCESSO")
            print("="*60)
            print("\nPróximos passos:")
            print("1. Recriar tabelas: python scripts/create_tables.py")
            print("2. Ou rodar migrations: alembic upgrade head")
            print("3. Retomar serviços no Render")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Erro ao resetar banco: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("🔥 SCRIPT DE RESET TOTAL DO BANCO DE DADOS")
    print("="*60)
    
    if not confirm_reset():
        return 0
    
    print("\n🚀 Iniciando reset...")
    
    success = reset_database()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
