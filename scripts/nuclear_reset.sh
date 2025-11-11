#!/bin/bash
################################################################################
# 🔥 NUCLEAR RESET - Apaga TUDO e recria do zero
################################################################################
# ATENÇÃO: Este script é DESTRUTIVO e IRREVERSÍVEL!
# Ele vai:
#   - Dropar todas as tabelas do PostgreSQL
#   - Limpar todas as keys do Redis (filas de tasks)
#   - Recriar tabelas do zero
#
# USO:
#   1. Via Render Shell (Worker ou API):
#      bash scripts/nuclear_reset.sh
#
#   2. Com confirmação automática (PERIGOSO!):
#      bash scripts/nuclear_reset.sh --force
#
################################################################################

set -e  # Para no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🔥 NUCLEAR RESET - Destruição Total do Sistema"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Verificar se está no modo --force
FORCE=0
if [[ "$1" == "--force" ]]; then
    FORCE=1
    echo -e "${YELLOW}⚠️  MODO FORCE ATIVADO - Sem confirmações!${NC}"
    echo ""
fi

# Função de confirmação
confirm() {
    if [[ $FORCE -eq 1 ]]; then
        return 0
    fi
    
    local message=$1
    local confirmation=$2
    
    echo -e "${RED}${message}${NC}"
    echo -en "${YELLOW}Digite '${confirmation}' para confirmar: ${NC}"
    read -r response
    
    if [[ "$response" != "$confirmation" ]]; then
        echo -e "${GREEN}✅ Operação cancelada. Nenhum dado foi alterado.${NC}"
        exit 0
    fi
}

# Primeira confirmação
confirm "⚠️  ATENÇÃO: Esta operação vai DELETAR TUDO!" "RESET"

# Segunda confirmação
confirm "⚠️  ÚLTIMA CHANCE! Tem certeza absoluta?" "SIM"

echo ""
echo -e "${BLUE}🚀 Iniciando destruição nuclear...${NC}"
echo ""

################################################################################
# PASSO 1: Limpar Redis
################################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  PASSO 1/3: Limpando Redis (filas de tasks)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ -z "$REDIS_URL" ]]; then
    echo -e "${YELLOW}⚠️  REDIS_URL não configurado. Pulando limpeza do Redis.${NC}"
else
    echo "Conectando ao Redis..."
    
    # Contar keys antes
    KEY_COUNT=$(redis-cli -u "$REDIS_URL" DBSIZE 2>/dev/null | grep -oP '\d+' || echo "0")
    echo "   📊 Keys encontradas: $KEY_COUNT"
    
    if [[ "$KEY_COUNT" -gt 0 ]]; then
        echo "   🗑️  Executando FLUSHALL..."
        redis-cli -u "$REDIS_URL" FLUSHALL >/dev/null 2>&1
        echo -e "   ${GREEN}✅ Redis limpo!${NC}"
    else
        echo "   ℹ️  Redis já estava vazio"
    fi
fi

echo ""

################################################################################
# PASSO 2: Dropar PostgreSQL
################################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  PASSO 2/3: Dropando PostgreSQL (todas as tabelas)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ -z "$DATABASE_URL" ]]; then
    echo -e "${RED}❌ Erro: DATABASE_URL não configurado!${NC}"
    exit 1
fi

echo "Conectando ao PostgreSQL..."

# Ajustar URL se necessário (postgres:// → postgresql://)
DB_URL="${DATABASE_URL/postgres:\/\//postgresql:\/\/}"

# Contar tabelas antes
TABLE_COUNT=$(psql "$DB_URL" -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | xargs || echo "0")
echo "   📊 Tabelas encontradas: $TABLE_COUNT"

if [[ "$TABLE_COUNT" -gt 0 ]]; then
    echo "   🗑️  Dropando schema 'public'..."
    psql "$DB_URL" -c "DROP SCHEMA public CASCADE;" >/dev/null 2>&1
    echo "   ✓ Schema deletado"
    
    echo "   🔧 Recriando schema 'public'..."
    psql "$DB_URL" -c "CREATE SCHEMA public;" >/dev/null 2>&1
    echo "   ✓ Schema criado"
    
    echo "   🔐 Restaurando permissões..."
    psql "$DB_URL" -c "GRANT ALL ON SCHEMA public TO postgres;" >/dev/null 2>&1
    psql "$DB_URL" -c "GRANT ALL ON SCHEMA public TO public;" >/dev/null 2>&1
    echo -e "   ${GREEN}✅ PostgreSQL limpo!${NC}"
else
    echo "   ℹ️  PostgreSQL já estava vazio"
fi

echo ""

################################################################################
# PASSO 3: Recriar Tabelas
################################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 PASSO 3/3: Recriando tabelas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ -f "scripts/create_tables.py" ]]; then
    echo "Executando create_tables.py..."
    python scripts/create_tables.py
    echo -e "${GREEN}✅ Tabelas recriadas!${NC}"
else
    echo -e "${YELLOW}⚠️  scripts/create_tables.py não encontrado${NC}"
    echo "   Execute manualmente: python scripts/create_tables.py"
fi

echo ""

################################################################################
# RESUMO FINAL
################################################################################
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ NUCLEAR RESET CONCLUÍDO COM SUCESSO!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 RESUMO:"
echo "   ✓ Redis limpo (todas as tasks removidas)"
echo "   ✓ PostgreSQL limpo (todas as tabelas recriadas)"
echo "   ✓ Sistema resetado para estado inicial"
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo "   1. Sistema está limpo e pronto para uso"
echo "   2. Registre um novo usuário via /api/v1/auth/register"
echo "   3. Teste criação de briefing"
echo "   4. Monitore logs do worker para validar"
echo ""
echo "📝 VALIDAÇÃO RÁPIDA:"
echo "   curl https://sua-api.onrender.com/api/v1/health"
echo ""
echo -e "${BLUE}Sistema online e operacional! 🎉${NC}"
echo ""
