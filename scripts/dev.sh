#!/bin/bash
# Script para rodar todos os serviços em modo desenvolvimento

echo "🚀 Iniciando EnsinaLab Content Engine..."

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Copiando de .env.example..."
    cp .env.example .env
    echo "📝 Configure suas variáveis em .env antes de continuar!"
    exit 1
fi

# Verificar se venv está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Ambiente virtual não ativado!"
    echo "Execute: source venv/bin/activate"
    exit 1
fi

# Verificar se Redis está rodando
if ! redis-cli ping &> /dev/null; then
    echo "⚠️  Redis não está rodando!"
    echo "Inicie com: redis-server"
    exit 1
fi

# Função para cleanup ao sair
cleanup() {
    echo "🛑 Parando serviços..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Iniciar API
echo "🌐 Iniciando FastAPI..."
python -m src.main &
API_PID=$!

# Aguardar API iniciar
sleep 3

# Iniciar Celery Worker
echo "⚙️  Iniciando Celery Worker..."
celery -A src.workers.celery_config worker --loglevel=info &
CELERY_PID=$!

echo ""
echo "✅ Todos os serviços iniciados!"
echo ""
echo "📚 API Docs: http://localhost:8000/docs"
echo "💚 Health: http://localhost:8000/health"
echo ""
echo "Pressione Ctrl+C para parar todos os serviços"

# Aguardar
wait
