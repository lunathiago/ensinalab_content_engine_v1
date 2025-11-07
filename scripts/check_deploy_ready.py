#!/usr/bin/env python3
"""
Script para verificar se o projeto está pronto para deploy no Render
"""
import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_file_exists(filepath, required=True):
    """Verifica se arquivo existe"""
    if Path(filepath).exists():
        print(f"✅ {filepath}")
        return True
    else:
        status = "❌" if required else "⚠️"
        print(f"{status} {filepath} {'(OBRIGATÓRIO)' if required else '(opcional)'}")
        return not required

def check_env_var(var_name, required=True):
    """Verifica se variável de ambiente está configurada"""
    if os.getenv(var_name):
        print(f"✅ {var_name} configurada")
        return True
    else:
        status = "❌" if required else "⚠️"
        print(f"{status} {var_name} não configurada {'(OBRIGATÓRIO)' if required else '(opcional)'}")
        return not required

def check_requirements():
    """Verifica dependências no requirements.txt"""
    print("\n📦 Verificando dependências...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'celery',
        'redis',
        'openai',
        'langgraph',
        'moviepy'
    ]
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read().lower()
            
        all_present = True
        for package in required_packages:
            if package in content:
                print(f"✅ {package}")
            else:
                print(f"❌ {package} não encontrado")
                all_present = False
        
        return all_present
    except FileNotFoundError:
        print("❌ requirements.txt não encontrado!")
        return False

def check_git_status():
    """Verifica status do git"""
    print("\n🔍 Verificando Git...")
    
    # Verificar se é repositório git
    if not Path('.git').exists():
        print("❌ Não é um repositório Git")
        print("   Execute: git init")
        return False
    
    print("✅ Repositório Git inicializado")
    
    # Verificar se tem remote
    result = os.popen('git remote -v').read()
    if 'origin' in result and 'github.com' in result:
        print("✅ Remote GitHub configurado")
        print(f"   {result.split()[1]}")
        return True
    else:
        print("❌ Remote GitHub não configurado")
        print("   Execute: git remote add origin <url-do-github>")
        return False

def main():
    print_header("VERIFICAÇÃO PRÉ-DEPLOY - RENDER.COM")
    
    print("\n🎯 Este script verifica se seu projeto está pronto para deploy")
    
    checks_passed = []
    
    # 1. Verificar arquivos essenciais
    print_header("1. ARQUIVOS ESSENCIAIS")
    checks_passed.append(check_file_exists('render.yaml', required=True))
    checks_passed.append(check_file_exists('requirements.txt', required=True))
    checks_passed.append(check_file_exists('src/main.py', required=True))
    checks_passed.append(check_file_exists('src/app.py', required=True))
    checks_passed.append(check_file_exists('scripts/create_tables.py', required=True))
    
    # 2. Verificar estrutura do projeto
    print_header("2. ESTRUTURA DO PROJETO")
    checks_passed.append(check_file_exists('src/api', required=True))
    checks_passed.append(check_file_exists('src/models', required=True))
    checks_passed.append(check_file_exists('src/services', required=True))
    checks_passed.append(check_file_exists('src/workers', required=True))
    checks_passed.append(check_file_exists('src/workflows', required=True))
    
    # 3. Verificar dependências
    print_header("3. DEPENDÊNCIAS")
    checks_passed.append(check_requirements())
    
    # 4. Verificar Git
    print_header("4. CONFIGURAÇÃO GIT/GITHUB")
    checks_passed.append(check_git_status())
    
    # 5. Verificar variáveis de ambiente (localmente)
    print_header("5. VARIÁVEIS DE AMBIENTE (local)")
    print("ℹ️  Estas serão configuradas no Render Dashboard:")
    check_env_var('OPENAI_API_KEY', required=False)
    check_env_var('DATABASE_URL', required=False)
    check_env_var('REDIS_URL', required=False)
    
    # 6. Verificar arquivos de documentação
    print_header("6. DOCUMENTAÇÃO")
    check_file_exists('README.md', required=False)
    check_file_exists('DEPLOY_RENDER.md', required=False)
    check_file_exists('QUICKSTART.md', required=False)
    
    # Resumo final
    print_header("RESUMO")
    
    total_checks = len(checks_passed)
    passed_checks = sum(checks_passed)
    
    print(f"\n📊 Verificações: {passed_checks}/{total_checks} passaram")
    
    if passed_checks == total_checks:
        print("\n🎉 TUDO PRONTO PARA DEPLOY!")
        print("\n📝 Próximos passos:")
        print("   1. Commit e push para GitHub:")
        print("      git add .")
        print("      git commit -m 'Ready for Render deploy'")
        print("      git push origin main")
        print("\n   2. Acesse: https://dashboard.render.com")
        print("   3. Siga o guia: DEPLOY_RENDER.md")
        print("\n✨ Boa sorte com o deploy!")
        return 0
    else:
        print("\n⚠️  ATENÇÃO: Alguns itens precisam de correção")
        print("\n📝 Corrija os itens marcados com ❌ antes do deploy")
        print("   Execute este script novamente após as correções:")
        print("   python scripts/check_deploy_ready.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
