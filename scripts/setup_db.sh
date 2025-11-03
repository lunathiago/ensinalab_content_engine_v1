#!/bin/bash
# Script para inicializar o banco de dados

echo "🗄️  Iniciando setup do banco de dados..."

# Verificar se PostgreSQL está rodando
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL não encontrado. Instale antes de continuar."
    exit 1
fi

# Criar banco de dados
echo "📦 Criando banco de dados 'ensinalab_content'..."
createdb ensinalab_content 2>/dev/null || echo "⚠️  Banco já existe ou erro ao criar"

# Criar tabelas (usando SQLAlchemy)
echo "📋 Criando tabelas..."
python -c "
from src.config.database import init_db
init_db()
print('✅ Tabelas criadas com sucesso!')
"

echo "🎉 Setup do banco concluído!"
