# 🚀 Guia Completo de Deploy no Render.com

## 📖 O que é o Render?

Render é uma plataforma que **hospeda sua aplicação na nuvem**. Pense nele como um computador sempre ligado na internet que roda seu código.

**Analogia:** É como alugar um espaço no shopping (Render) para sua loja (aplicação).

---

## 💰 Custos

| Período | Custo | O que está incluído |
|---------|-------|---------------------|
| **Meses 1-3** | **$0/mês** | API + Worker + PostgreSQL + Redis grátis |
| **Mês 4+** | **$7/mês** | Só PostgreSQL pago, resto continua grátis |
| **Produção** | **$21/mês** | Se precisar de mais recursos |

**Observação:** OpenAI API cobra separado (~$5-10/mês para 100 vídeos com GPT-3.5)

---

## 🎯 PASSO 1: Criar Conta no Render

### 1.1 Acessar o site
```
🌐 Abra: https://render.com
```

### 1.2 Clicar em "Get Started" ou "Sign Up"

### 1.3 Escolher "Sign up with GitHub"
- ✅ **IMPORTANTE:** Use a mesma conta do GitHub onde está seu código
- ✅ Isso permite deploy automático

### 1.4 Autorizar Render
- GitHub vai pedir permissão
- Clique em "Authorize Render"

**✅ Pronto! Conta criada.**

---

## 🎯 PASSO 2: Preparar o Código no GitHub

### 2.1 Verificar se o código está no GitHub

Você já deve ter o repositório, mas vamos confirmar:

```bash
# No seu terminal, dentro da pasta do projeto
git remote -v
```

**Deve aparecer algo como:**
```
origin  https://github.com/lunathiago/ensinalab_content_engine_v1.git (fetch)
origin  https://github.com/lunathiago/ensinalab_content_engine_v1.git (push)
```

### 2.2 Fazer commit do render.yaml

```bash
# Adicionar o arquivo de configuração
git add render.yaml

# Fazer commit
git commit -m "Add Render deploy configuration"

# Enviar para GitHub
git push origin main
```

**✅ Código está no GitHub com as configurações de deploy!**

---

## 🎯 PASSO 3: Criar os Serviços no Render

### 3.1 Acessar Dashboard do Render
```
🌐 https://dashboard.render.com
```

### 3.2 Conectar o Repositório

1. Clique em **"New +"** (botão azul no canto superior direito)
2. Escolha **"Blueprint"**
3. Clique em **"Connect a repository"**
4. Encontre seu repositório: `ensinalab_content_engine_v1`
5. Clique em **"Connect"**

**O que acontece:** Render lê o arquivo `render.yaml` e entende o que precisa criar.

### 3.3 Configurar Blueprint

Render vai mostrar uma tela com:
- ✅ `ensinalab-api` (Web Service)
- ✅ `ensinalab-worker` (Background Worker)
- ✅ `ensinalab-db` (PostgreSQL Database)

1. **Service Group Name:** Deixe como `ensinalab-content-engine`
2. **Branch:** Confirme que está `main`
3. Clique em **"Apply"**

**⏱️ Aguarde 2-3 minutos** enquanto Render cria os serviços.

---

## 🎯 PASSO 4: Criar Redis (Manual)

O Redis não pode ser criado via YAML no plano free, então vamos criar manualmente:

### 4.1 No Dashboard do Render

1. Clique em **"New +"**
2. Escolha **"Redis"**
3. Configure:
   - **Name:** `ensinalab-redis`
   - **Plan:** Free (25MB)
   - **Region:** Ohio (US East)
4. Clique em **"Create Redis"**

**⏱️ Aguarde 1-2 minutos**

### 4.2 Conectar Redis aos Serviços

1. Vá em **"ensinalab-api"** (na lista de serviços)
2. Clique na aba **"Environment"**
3. Clique em **"Add Environment Variable"**
4. Adicione:
   ```
   Key: REDIS_URL
   Value: (clique em "Select Redis" e escolha "ensinalab-redis")
   ```
5. Clique em **"Save Changes"**

6. **Repita o processo** para `ensinalab-worker`

**✅ Redis conectado!**

---

## 🎯 PASSO 5: Adicionar Chave da OpenAI

### 5.1 Conseguir sua API Key da OpenAI

1. Acesse: https://platform.openai.com/api-keys
2. Faça login
3. Clique em **"Create new secret key"**
4. Copie a chave (algo como `sk-proj-abc123...`)
5. **⚠️ IMPORTANTE:** Guarde em local seguro, só aparece uma vez!

### 5.2 Adicionar no Render

**Para o serviço API:**
1. Vá em **"ensinalab-api"**
2. Clique na aba **"Environment"**
3. Encontre **"OPENAI_API_KEY"**
4. Clique em **"Edit"**
5. Cole sua chave da OpenAI
6. Clique em **"Save Changes"**

**Para o Worker:**
1. Vá em **"ensinalab-worker"**
2. Repita o processo acima

**✅ API Key configurada!**

---

## 🎯 PASSO 6: Criar as Tabelas do Banco de Dados

Agora precisamos criar as tabelas no PostgreSQL.

### 6.1 Acessar Shell do Serviço

1. Vá em **"ensinalab-api"**
2. Clique na aba **"Shell"** (no menu lateral)
3. Aguarde abrir o terminal

### 6.2 Executar Script de Criação

No terminal que abriu, digite:

```bash
python scripts/create_tables.py
```

**Você deve ver:**
```
✅ Tabelas criadas com sucesso!
   - briefings
   - options
   - videos
```

**✅ Banco de dados pronto!**

---

## 🎯 PASSO 7: Verificar se Está Funcionando

### 7.1 Pegar a URL da API

1. Vá em **"ensinalab-api"**
2. No topo, você verá uma URL tipo:
   ```
   https://ensinalab-api.onrender.com
   ```
3. Copie essa URL

### 7.2 Testar Health Check

Abra no navegador ou use curl:

```bash
curl https://ensinalab-api.onrender.com/health
```

**Deve retornar:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T..."
}
```

### 7.3 Testar Documentação Interativa

Abra no navegador:
```
https://ensinalab-api.onrender.com/docs
```

**Deve abrir a interface Swagger** com todos os endpoints! 🎉

### 7.4 Testar Criação de Briefing

Na interface Swagger:

1. Expanda **"POST /api/v1/briefings"**
2. Clique em **"Try it out"**
3. Cole este JSON:

```json
{
  "title": "Teste de Deploy",
  "description": "Testando se o sistema está funcionando após deploy",
  "target_audience": "Professores",
  "subject_area": "Teste",
  "teacher_experience_level": "iniciante",
  "training_goal": "Testar o sistema",
  "duration_minutes": 5,
  "tone": "objetivo"
}
```

4. Clique em **"Execute"**

**Deve retornar Status 201** com o briefing criado!

### 7.5 Verificar Worker Processando

1. Aguarde 30-60 segundos
2. Vá em **"ensinalab-worker"**
3. Clique na aba **"Logs"**
4. Você deve ver:
   ```
   🔄 Gerando opções com LangGraph para briefing 1...
   🤖 Iniciando análise de briefing...
   ✅ 5 opções geradas...
   ```

**✅ TUDO FUNCIONANDO!** 🎉

---

## 🎯 PASSO 8: Configurar Deploy Automático (Opcional mas Recomendado)

Agora, toda vez que você fizer `git push`, o Render faz deploy automático!

### 8.1 Verificar Auto-Deploy

1. Vá em **"ensinalab-api"**
2. Clique na aba **"Settings"**
3. Role até **"Build & Deploy"**
4. Confirme que **"Auto-Deploy"** está **Yes**

### 8.2 Testar

```bash
# Faça uma mudança qualquer
echo "# Deploy automático funcionando!" >> README.md

# Commit e push
git add README.md
git commit -m "Test auto-deploy"
git push origin main
```

**No Render:**
1. Vá em **"ensinalab-api"**
2. Clique na aba **"Events"**
3. Você verá **"Deploy triggered"**
4. Aguarde 2-3 minutos
5. **Deploy concluído!**

**✅ Deploy automático configurado!**

---

## 📊 Monitoramento e Logs

### Ver Logs da API

1. Vá em **"ensinalab-api"**
2. Clique em **"Logs"**
3. Você verá em tempo real:
   ```
   INFO: Uvicorn running on http://0.0.0.0:10000
   INFO: Application startup complete
   POST /api/v1/briefings 201
   ```

### Ver Logs do Worker

1. Vá em **"ensinalab-worker"**
2. Clique em **"Logs"**
3. Você verá:
   ```
   [celery@worker] Task received: generate_options
   [celery@worker] Task completed: generate_options
   ```

### Métricas

1. Vá em qualquer serviço
2. Clique em **"Metrics"**
3. Veja:
   - CPU usage
   - Memory usage
   - Request count
   - Response time

---

## 🔧 Troubleshooting (Resolver Problemas)

### ❌ Problema: "Build Failed"

**Causa:** Erro ao instalar dependências

**Solução:**
1. Vá em **"Logs"** da build
2. Procure a linha com `ERROR`
3. Geralmente é uma dependência faltando

**Corrigir:**
```bash
# Adicione a dependência que faltou
pip install <pacote-faltando>
pip freeze > requirements.txt

# Commit e push
git add requirements.txt
git commit -m "Fix dependencies"
git push
```

---

### ❌ Problema: "Service Unavailable"

**Causa:** Aplicação não iniciou corretamente

**Solução:**
1. Vá em **"Logs"**
2. Procure erros de Python
3. Geralmente é variável de ambiente faltando

**Corrigir:**
1. Vá em **"Environment"**
2. Adicione a variável que falta
3. Clique em **"Save Changes"**

---

### ❌ Problema: Worker não processa tarefas

**Causa:** Redis não conectado ou Worker não iniciou

**Solução:**
1. Verifique se `REDIS_URL` está configurado
2. Vá em **"ensinalab-worker"** → **"Logs"**
3. Procure erro de conexão com Redis
4. Se necessário, recrie a conexão com Redis

---

### ❌ Problema: "Out of Free Hours"

**Causa:** Free tier acabou (750h/mês dividido por serviços)

**Solução:**
- **Opção 1:** Upgrade para plano pago ($7/serviço)
- **Opção 2:** Pausar serviços quando não usar
- **Opção 3:** Migrar para Railway (tem crédito mensal)

---

## 🎨 Fluxo Completo (Resumo Visual)

```
┌─────────────────┐
│  SEU CÓDIGO     │
│  (local)        │
└────────┬────────┘
         │ git push
         ▼
┌─────────────────┐
│   GITHUB        │
│  (repositório)  │
└────────┬────────┘
         │ webhook
         ▼
┌─────────────────┐
│   RENDER        │
│  ┌───────────┐  │
│  │ BUILD     │  │ ← pip install
│  └─────┬─────┘  │
│        ▼        │
│  ┌───────────┐  │
│  │ DEPLOY    │  │ ← uvicorn start
│  └─────┬─────┘  │
│        ▼        │
│  ┌───────────┐  │
│  │ RUNNING   │  │ ← https://sua-url.onrender.com
│  └───────────┘  │
└─────────────────┘
```

---

## 📝 Checklist Final

Antes de considerar o deploy completo, verifique:

- [ ] Conta Render criada
- [ ] Repositório conectado
- [ ] `render.yaml` no repositório
- [ ] Blueprint aplicado
- [ ] Redis criado e conectado
- [ ] OPENAI_API_KEY configurada
- [ ] Tabelas do banco criadas
- [ ] `/health` retorna 200
- [ ] `/docs` abre documentação
- [ ] Briefing de teste criado
- [ ] Worker processando tarefas
- [ ] Logs sem erros
- [ ] Auto-deploy funcionando

**✅ Tudo marcado? Parabéns! Seu sistema está ONLINE!** 🎉

---

## 🚀 Próximos Passos

1. **Configurar domínio customizado** (opcional)
   - Render permite domínio próprio grátis
   - Ex: `api.ensinalab.com`

2. **Configurar alertas**
   - Render pode enviar email se algo der errado
   - Vá em Settings → Notifications

3. **Backup do banco**
   - Render faz backup automático
   - Pode baixar backup manual quando quiser

4. **Monitorar custos**
   - Acompanhe uso em Billing
   - Configure alertas de custo

5. **Documentar URL da API**
   - Compartilhe com equipe
   - Adicione no README do projeto

---

## 📞 Suporte

**Render:**
- Documentação: https://render.com/docs
- Community: https://community.render.com
- Support: support@render.com

**Problemas no código:**
- GitHub Issues: https://github.com/lunathiago/ensinalab_content_engine_v1/issues

---

**Dúvidas?** Entre em contato! 💬

**Deploy funcionando?** Compartilhe sua URL! 🌐
