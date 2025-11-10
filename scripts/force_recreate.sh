#!/bin/bash
# Script para forçar recriação de tabelas via Render Shell
# Execute no terminal do Render: bash scripts/force_recreate.sh

echo "🚀 Forçando recriação de tabelas..."
cd /opt/render/project/src || exit 1
python -m scripts.recreate_tables
echo "✅ Concluído!"
