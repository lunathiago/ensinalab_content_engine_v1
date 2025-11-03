# 🚀 Quick Start Guide - EnsinaLab Content Engine

## Opção 1: Setup Local (Recomendado para desenvolvimento)

### 1. Pré-requisitos
```bash
# Verificar versões
python --version  # 3.9+
psql --version    # PostgreSQL
redis-cli --version
ffmpeg -version
```

### 2. Instalar dependências
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate no Windows

# Instalar pacotes
pip install -r requirements.txt
```

### 3. Configurar ambiente
```bash
# Copiar .env
cp .env.example .env

# EDITAR .env e adicionar:
# - OPENAI_API_KEY (obrigatório)
# - DB_PASSWORD (se necessário)
```

### 4. Inicializar banco
```bash
# Criar banco
createdb ensinalab_content

# Criar tabelas
python scripts/create_tables.py
```

### 5. Iniciar serviços

**Opção A - Script único (recomendado):**
```bash
./scripts/dev.sh
```

**Opção B - Manual (3 terminais):**

Terminal 1 - API:
```bash
python -m src.main
```

Terminal 2 - Worker:
```bash
celery -A src.workers.celery_config worker --loglevel=info
```

Terminal 3 - Redis (se não estiver como serviço):
```bash
redis-server
```

### 6. Testar
```bash
# Health check
curl http://localhost:8000/health

# Documentação interativa
open http://localhost:8000/docs
```

---

## Opção 2: Docker (Setup mais rápido)

### 1. Configurar .env
```bash
cp .env.example .env
# Adicionar OPENAI_API_KEY
```

### 2. Iniciar tudo
```bash
docker-compose up -d
```

### 3. Criar tabelas
```bash
docker-compose exec api python scripts/create_tables.py
```

### 4. Acessar
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Ver logs
```bash
docker-compose logs -f api
docker-compose logs -f worker
```

---

## 📝 Teste Rápido da API

### 1. Criar um briefing
```bash
curl -X POST "http://localhost:8000/api/v1/briefings" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fotossíntese para Crianças",
    "description": "Vídeo explicando fotossíntese de forma lúdica",
    "target_grade": "6º ano",
    "target_age_min": 11,
    "target_age_max": 12,
    "educational_goal": "Compreender como as plantas produzem energia",
    "duration_minutes": 3,
    "tone": "descontraído"
  }'
```

### 2. Listar briefings
```bash
curl http://localhost:8000/api/v1/briefings
```

### 3. Ver opções geradas (aguardar processamento)
```bash
curl http://localhost:8000/api/v1/briefings/1/options
```

### 4. Selecionar opção
```bash
curl -X POST "http://localhost:8000/api/v1/options/1/select" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Perfeito!"}'
```

### 5. Verificar status do vídeo
```bash
curl http://localhost:8000/api/v1/videos/1/status
```

### 6. Baixar vídeo (quando pronto)
```bash
curl -O http://localhost:8000/api/v1/videos/1/download
```

---

## 🐛 Troubleshooting

### Redis não conecta
```bash
# Verificar se está rodando
redis-cli ping  # Deve retornar PONG

# Iniciar manualmente
redis-server
```

### PostgreSQL não conecta
```bash
# Verificar status
pg_isready

# Criar banco manualmente
createdb ensinalab_content
```

### Erro de import
```bash
# Verificar ambiente virtual ativado
which python  # Deve apontar para venv/

# Reinstalar dependências
pip install -r requirements.txt --upgrade
```

### Worker não processa tasks
```bash
# Verificar se worker está rodando
ps aux | grep celery

# Verificar logs do worker
# Procurar erros de conexão com Redis ou banco
```

---

## 📚 Próximos Passos

1. Configurar TTS real (ElevenLabs/Polly)
2. Implementar RAG com base de conhecimento
3. Customizar templates visuais dos vídeos
4. Adicionar autenticação JWT
5. Configurar CI/CD

---

**Problemas?** Abra uma issue ou consulte a documentação completa no README.md
