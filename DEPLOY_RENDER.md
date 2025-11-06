# 🚀 Guia Completo de Deploy no Render

## 📝 Pré-requisitos (coisas que você precisa ter)

1. ✅ Conta no GitHub (gratuita)
2. ✅ Conta no Render (gratuita)
3. ✅ API Key da OpenAI (você precisa pagar conforme usar)
4. ✅ Git instalado no seu computador

---

## 🎬 Passo a Passo Completo

### **PASSO 1: Criar conta no Render** ⏱️ 2 minutos

1. Acesse: https://render.com
2. Clique em **"Get Started for Free"**
3. Escolha **"Sign up with GitHub"** (mais fácil)
4. Autorize o Render a acessar seus repositórios

**O que acontece:** O Render vai se conectar ao seu GitHub para poder pegar o código.

---

### **PASSO 2: Subir código para o GitHub** ⏱️ 5 minutos

Se você **ainda não tem** o código no GitHub:

```bash
# 1. Abrir terminal na pasta do projeto
cd /workspaces/ensinalab_content_engine_v1

# 2. Inicializar Git (se ainda não fez)
git init

# 3. Adicionar todos os arquivos
git add .

# 4. Fazer primeiro commit
git commit -m "Initial commit - EnsinaLab Content Engine"

# 5. Criar repositório no GitHub
# Acesse: https://github.com/new
# Nome: ensinalab_content_engine_v1
# Deixe privado se preferir
# NÃO marque "Initialize with README"

# 6. Conectar seu código local ao GitHub
git remote add origin https://github.com/SEU_USUARIO/ensinalab_content_engine_v1.git

# 7. Enviar código para o GitHub
git branch -M main
git push -u origin main
```

**O que acontece:** Seu código sai do seu computador e vai para o GitHub (como uma cópia de segurança).

---

### **PASSO 3: Conectar Render ao GitHub** ⏱️ 2 minutos

1. No painel do Render (https://dashboard.render.com)
2. Clique em **"New +"** (canto superior direito)
3. Escolha **"Blueprint"**
4. Clique em **"Connect a repository"**
5. Procure por **"ensinalab_content_engine_v1"**
6. Clique em **"Connect"**

**O que acontece:** O Render vai ler o arquivo `render.yaml` e entender o que precisa criar.

---

### **PASSO 4: Configurar Variáveis de Ambiente** ⏱️ 3 minutos

O Render vai criar automaticamente:
- ✅ API (ensinalab-api)
- ✅ Worker (ensinalab-worker)
- ✅ PostgreSQL (ensinalab-db)
- ✅ Redis (ensinalab-redis)

**MAS** você precisa adicionar manualmente:

1. No painel, clique em **"ensinalab-api"**
2. No menu lateral, clique em **"Environment"**
3. Clique em **"Add Environment Variable"**
4. Adicione:

```
Nome: OPENAI_API_KEY
Valor: sk-proj-xxxxxxxxxxxxxxxxxx (sua chave da OpenAI)
```

5. Repita o processo para **"ensinalab-worker"**

**O que acontece:** Essas são configurações secretas que o código precisa (como senhas).

---

### **PASSO 5: Aguardar Deploy** ⏱️ 5-10 minutos

O Render vai automaticamente:

1. ✅ Baixar seu código do GitHub
2. ✅ Instalar Python 3.9
3. ✅ Instalar todas as dependências (requirements.txt)
4. ✅ Criar banco de dados PostgreSQL
5. ✅ Criar Redis
6. ✅ Criar tabelas no banco
7. ✅ Iniciar API
8. ✅ Iniciar Worker

Você pode acompanhar em **"Logs"** no painel.

**O que acontece:** O Render está configurando tudo automaticamente.

---

### **PASSO 6: Testar a API** ⏱️ 2 minutos

Quando o deploy terminar:

1. No painel, clique em **"ensinalab-api"**
2. No topo, você verá a URL: `https://ensinalab-api.onrender.com`
3. Clique nela
4. Adicione `/docs` no final: `https://ensinalab-api.onrender.com/docs`

Você verá a documentação interativa da API! 🎉

**Teste:**
```bash
# Verificar se está funcionando
curl https://ensinalab-api.onrender.com/health

# Deve retornar:
# {"status": "healthy"}
```

---

## 🎯 O que foi Criado?

```
┌─────────────────────────────────────┐
│         Render Dashboard            │
└─────────────────────────────────────┘
              │
    ┌─────────┼─────────┬─────────┐
    │         │         │         │
┌───▼───┐ ┌──▼──┐ ┌───▼───┐ ┌──▼───┐
│  API  │ │Worker│ │  DB   │ │Redis │
│ (Web) │ │(Task)│ │(Pgsql)│ │(Cache)│
└───────┘ └──────┘ └───────┘ └──────┘
   │         │         │         │
   └─────────┴─────────┴─────────┘
              │
         [Internet]
              │
         [Usuários]
```

### **1. API (ensinalab-api)**
- **O que faz:** Recebe requisições HTTP
- **URL:** `https://ensinalab-api.onrender.com`
- **Custo:** Grátis (750h/mês)

### **2. Worker (ensinalab-worker)**
- **O que faz:** Processa vídeos em background
- **Sem URL pública** (só a API se comunica com ele)
- **Custo:** Grátis (750h/mês)

### **3. PostgreSQL (ensinalab-db)**
- **O que faz:** Armazena dados (briefings, vídeos, etc.)
- **Conexão interna** (só seus serviços acessam)
- **Custo:** Grátis por 90 dias, depois $7/mês

### **4. Redis (ensinalab-redis)**
- **O que faz:** Fila de mensagens entre API e Worker
- **Conexão interna**
- **Custo:** Grátis (25MB)

---

## 🧪 Como Usar a API Agora

### Exemplo 1: Criar um Briefing

```bash
curl -X POST "https://ensinalab-api.onrender.com/api/v1/briefings" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Gestão de Sala de Aula",
    "description": "Técnicas para manter ordem e engajamento",
    "target_audience": "Professores Iniciantes",
    "subject_area": "Gestão",
    "teacher_experience_level": "iniciante",
    "training_goal": "Melhorar controle da sala",
    "duration_minutes": 10,
    "tone": "prático"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "title": "Gestão de Sala de Aula",
  "status": "pending",
  "created_at": "2025-11-04T..."
}
```

### Exemplo 2: Listar Briefings

```bash
curl https://ensinalab-api.onrender.com/api/v1/briefings
```

### Exemplo 3: Ver Opções Geradas

```bash
# Aguardar 30-60s após criar briefing
curl https://ensinalab-api.onrender.com/api/v1/briefings/1/options
```

---

## 🔄 Como Fazer Updates no Código

```bash
# 1. Fazer alterações no código localmente
nano src/main.py  # ou qualquer arquivo

# 2. Commitar mudanças
git add .
git commit -m "Atualização: melhorias na API"

# 3. Enviar para GitHub
git push origin main

# 4. RENDER FAZ DEPLOY AUTOMÁTICO! 🎉
# Você vai ver no dashboard:
# "Building..." → "Deploying..." → "Live"
```

**O que acontece:** Toda vez que você faz `git push`, o Render detecta e faz novo deploy automaticamente (em ~5 minutos).

---

## 📊 Monitoramento

### Ver Logs em Tempo Real:

1. Dashboard → **ensinalab-api** → **Logs**
2. Você verá tudo que acontece:

```
[INFO] Application startup complete
[INFO] Uvicorn running on http://0.0.0.0:10000
POST /api/v1/briefings 201 Created
[INFO] Briefing created: id=1
```

### Ver Métricas:

1. Dashboard → **ensinalab-api** → **Metrics**
2. Você verá:
   - CPU usage
   - Memory usage
   - Request count
   - Response time

---

## 💰 Custos Reais

### **Primeiros 3 Meses:**
```
API (Web):        $0/mês (grátis)
Worker:           $0/mês (grátis)
PostgreSQL:       $0/mês (90 dias grátis)
Redis:            $0/mês (grátis)
─────────────────────────
Total:            $0/mês 🎉
```

### **Após 3 Meses:**
```
API (Web):        $0/mês (ainda grátis, 750h)
Worker:           $0/mês (ainda grátis, 750h)
PostgreSQL:       $7/mês (após trial)
Redis:            $0/mês (ainda grátis)
─────────────────────────
Total:            $7/mês
```

### **Se precisar escalar:**
```
API (Pro):        $7/mês (mais recursos)
Worker (Pro):     $7/mês (mais recursos)
PostgreSQL:       $7/mês
Redis:            $3/mês (100MB)
─────────────────────────
Total:            $24/mês
```

---

## 🆘 Troubleshooting (Problemas Comuns)

### **1. Deploy falhou com "Build failed"**

**Causa:** Erro nas dependências

**Solução:**
```bash
# Testar localmente primeiro
pip install -r requirements.txt

# Se funcionar localmente, verificar logs no Render
```

### **2. API retorna "Application startup failed"**

**Causa:** Variável de ambiente faltando

**Solução:**
1. Dashboard → ensinalab-api → Environment
2. Verificar se `OPENAI_API_KEY` está configurada
3. Adicionar se necessário
4. Clicar em "Manual Deploy" → "Deploy latest commit"

### **3. Worker não processa vídeos**

**Causa:** Redis não conectado

**Solução:**
1. Dashboard → ensinalab-worker → Logs
2. Procurar erro de conexão
3. Verificar se Redis está rodando (deve estar verde)

### **4. "Database connection failed"**

**Causa:** PostgreSQL ainda está criando

**Solução:**
- Aguardar 5-10 minutos
- PostgreSQL leva tempo para inicializar primeira vez

---

## 🔐 Segurança

### O que o Render faz automaticamente:

✅ **SSL/HTTPS:** Certificado grátis
✅ **Backups:** PostgreSQL tem backup diário
✅ **Isolamento:** Cada serviço roda isolado
✅ **DDoS Protection:** Proteção básica incluída
✅ **Logs:** Mantidos por 7 dias

### O que você deve fazer:

❗ **NUNCA** commitar `OPENAI_API_KEY` no código
❗ **SEMPRE** usar variáveis de ambiente
❗ **VERIFICAR** logs regularmente
❗ **ATUALIZAR** dependências periodicamente

---

## 📞 Suporte

- **Documentação:** https://render.com/docs
- **Status:** https://status.render.com
- **Comunidade:** https://community.render.com
- **Email:** support@render.com (inglês)

---

## ✅ Checklist Final

Antes de considerar deploy completo:

- [ ] Código no GitHub
- [ ] Render conectado ao GitHub
- [ ] `render.yaml` no repositório
- [ ] API rodando (status verde)
- [ ] Worker rodando (status verde)
- [ ] PostgreSQL criado
- [ ] Redis criado
- [ ] `OPENAI_API_KEY` configurada
- [ ] Endpoint `/health` respondendo
- [ ] Endpoint `/docs` acessível
- [ ] Teste de criação de briefing OK
- [ ] Logs sem erros

---

## 🎉 Parabéns!

Sua aplicação está **rodando na nuvem** e acessível para qualquer pessoa na internet!

**URL da API:** https://ensinalab-api.onrender.com
**Documentação:** https://ensinalab-api.onrender.com/docs

---

## 📚 Próximos Passos (Opcional)

1. **Domínio Personalizado:**
   - Dashboard → ensinalab-api → Settings → Custom Domain
   - Adicionar: `api.seudominio.com`

2. **Webhooks:**
   - Notificações quando deploy terminar
   - Integrar com Discord/Slack

3. **Monitoramento Avançado:**
   - Integrar com Sentry (erros)
   - Integrar com LogTail (logs)

4. **CI/CD:**
   - Adicionar testes automáticos
   - Deploy só se testes passarem

---

**Dúvidas?** Estou aqui para ajudar! 🚀
