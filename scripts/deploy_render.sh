#!/bin/bash
# 🚀 Script para Deploy Rápido no Render

echo "🚀 Preparando Deploy no Render..."
echo ""

# 1. Verificar se está no diretório correto
if [ ! -f "render.yaml" ]; then
    echo "❌ Erro: render.yaml não encontrado!"
    echo "Execute este script na pasta do projeto."
    exit 1
fi

# 2. Verificar se Git está configurado
if ! command -v git &> /dev/null; then
    echo "❌ Git não está instalado!"
    echo "Instale com: sudo apt install git"
    exit 1
fi

# 3. Inicializar Git (se necessário)
if [ ! -d ".git" ]; then
    echo "📦 Inicializando Git..."
    git init
    git add .
    git commit -m "Initial commit - EnsinaLab Content Engine"
    echo "✅ Git inicializado"
else
    echo "✅ Git já está configurado"
fi

# 4. Verificar se tem remote
if ! git remote | grep -q "origin"; then
    echo ""
    echo "🔗 Configurar GitHub:"
    echo ""
    echo "1. Acesse: https://github.com/new"
    echo "2. Nome do repositório: ensinalab_content_engine_v1"
    echo "3. Deixe PRIVADO se preferir"
    echo "4. NÃO marque 'Initialize with README'"
    echo "5. Clique em 'Create repository'"
    echo ""
    read -p "Digite a URL do repositório (ex: https://github.com/seu-usuario/ensinalab_content_engine_v1.git): " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo "❌ URL não pode ser vazia!"
        exit 1
    fi
    
    git remote add origin "$REPO_URL"
    echo "✅ Remote configurado"
fi

# 5. Fazer push para o GitHub
echo ""
echo "📤 Enviando código para GitHub..."
git branch -M main

# Verificar se tem alterações para commitar
if ! git diff-index --quiet HEAD --; then
    git add .
    git commit -m "Update: preparando para deploy no Render"
fi

git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Código enviado para GitHub com sucesso!"
else
    echo "❌ Erro ao enviar código. Verifique suas credenciais do GitHub."
    exit 1
fi

# 6. Instruções finais
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Código pronto para deploy no Render!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Acesse: https://dashboard.render.com"
echo "2. Clique em 'New +' → 'Blueprint'"
echo "3. Conecte seu repositório: ensinalab_content_engine_v1"
echo "4. Render vai ler o render.yaml e criar tudo automaticamente"
echo "5. Aguarde ~5-10 minutos"
echo ""
echo "⚠️  IMPORTANTE: Adicionar variáveis de ambiente:"
echo ""
echo "   • ensinalab-api → Environment → Add:"
echo "     Nome: OPENAI_API_KEY"
echo "     Valor: sk-proj-xxxxxxxxxx (sua chave)"
echo ""
echo "   • ensinalab-worker → Environment → Add:"
echo "     Nome: OPENAI_API_KEY"
echo "     Valor: sk-proj-xxxxxxxxxx (mesma chave)"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentação completa: DEPLOY_RENDER.md"
echo ""
