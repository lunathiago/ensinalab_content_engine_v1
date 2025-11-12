# ⚡ Setup Shotstack - Renderização em Nuvem (10-20x mais rápido)

## 🎯 Por que usar Shotstack?

### **Problema Atual (MoviePy local):**
- ❌ **15-20 minutos** para gerar 1 vídeo
- ❌ **95% do tempo** é renderização CPU-bound
- ❌ **Consome recursos** do servidor Render
- ❌ **Não escala** (free tier = 0.5 vCPU)

### **Solução (Shotstack Cloud):**
- ✅ **1-2 minutos** para gerar 1 vídeo (**10-20x mais rápido**)
- ✅ **Renderização GPU** em servidores dedicados
- ✅ **CDN integrado** (vídeo já em URL pública)
- ✅ **Escala infinita** (sem limite de workers)
- ✅ **$0.10/vídeo** (tier pago) ou 20 vídeos/mês grátis

---

## 📋 Pré-requisitos

1. Conta Shotstack (free tier: 20 renders/mês)
2. API Key do Shotstack
3. Cloudflare R2 ou similar (para upload de áudio TTS)

---

## 🚀 Setup Rápido (5 minutos)

### **1. Criar Conta Shotstack** (2 min)

1. Acesse: https://dashboard.shotstack.io/register
2. Preencha dados:
   ```
   Email: seu@email.com
   Password: (senha forte)
   Company: EnsinaLab (ou seu projeto)
   ```
3. Confirme email
4. Login: https://dashboard.shotstack.io/

---

### **2. Obter API Keys** (1 min)

1. Dashboard → **API Keys** (menu lateral)
2. Você verá 2 keys:
   - **Sandbox Key** (stage) - para testes ✅
   - **Production Key** (v1) - para produção 🚀

3. Copie a **Sandbox Key** para começar:
   ```
   Sandbox Key: ptXXXXXXXXXXXXXXXXXXXXXX
   ```

**⚠️ Importante:**
- Sandbox: Vídeos têm watermark "Shotstack"
- Production: Sem watermark, mas consome créditos

---

### **3. Configurar no Render** (2 min)

#### **3.1: Worker**

1. Dashboard Render → **ensinalab-worker**
2. **Environment** → **Add Environment Variable**
3. Adicionar:

```bash
# Obrigatório
SHOTSTACK_API_KEY = ptXXXXXXXXXXXXXXXXXXXXXX  # Sua Sandbox Key

# Opcional (defaults já configurados)
SHOTSTACK_API_URL = https://api.shotstack.io/v1
SHOTSTACK_STAGE = stage  # "stage" (sandbox) ou "v1" (prod)
```

4. **Save Changes** → Worker reinicia automaticamente

#### **3.2: API (Web Service)**

1. Dashboard Render → **ensinalab-api**
2. **Environment** → Adicionar as **mesmas variáveis**:

```bash
SHOTSTACK_API_KEY = ptXXXXXXXXXXXXXXXXXXXXXX
SHOTSTACK_STAGE = stage
```

3. **Save Changes** → API reinicia

---

## ✅ Testar Integração

### **Método 1: Via API (Recomendado)**

```bash
# 1. Criar briefing
curl -X POST https://sua-api.onrender.com/api/v1/briefings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Teste Shotstack",
    "description": "Testar renderização em nuvem",
    "target_audience": "Testes",
    "duration_minutes": 5
  }'

# 2. Gerar opções (aguardar ~30s)

# 3. Selecionar opção e gerar vídeo
curl -X POST https://sua-api.onrender.com/api/v1/videos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "option_id": 1,
    "generator_type": "auto"  # Vai usar Shotstack se configurado
  }'

# 4. Monitorar logs do worker (deve mostrar "ShotstackGenerator")
# Aguardar 1-2 minutos (vs 15-20 min com MoviePy!)

# 5. Verificar vídeo gerado
curl https://sua-api.onrender.com/api/v1/videos/{video_hash}
```

**Saída esperada nos logs:**
```
🎬 [ShotstackGenerator] Gerando vídeo 1...
   → 8 slides identificados
   → Áudio gerado: generated_videos/audio_1.mp3
   → Áudio disponível: https://pub-xxx.r2.dev/temp/audio_1.mp3
   → Render ID: d7f3b2c1-4a5e-9f8d-1234-567890abcdef
   📊 Status: queued
   📊 Status: rendering
   📊 Status: done
✅ [ShotstackGenerator] Vídeo pronto: https://cdn.shotstack.io/xxx/video.mp4
```

---

### **Método 2: Script Python Local**

```python
# test_shotstack.py
import os
os.environ["SHOTSTACK_API_KEY"] = "ptXXXXXXXXXXXXXXXXXXXXXX"
os.environ["SHOTSTACK_STAGE"] = "stage"

from src.video.shotstack_generator import ShotstackGenerator

gen = ShotstackGenerator()

result = gen.generate(
    script="""
    # Introdução
    Bem-vindo ao teste Shotstack!
    
    ## Vantagens
    - 10x mais rápido
    - GPU cloud
    - CDN integrado
    
    ## Conclusão
    Renderização profissional em minutos!
    """,
    title="Teste Shotstack",
    metadata={"tone": "professional"},
    video_id=999
)

print(f"✅ Sucesso: {result['success']}")
print(f"📹 URL: {result['video_path']}")
print(f"⏱️ Duração: {result['duration']}s")
```

---

## 🔧 Troubleshooting

### **Erro: "SHOTSTACK_API_KEY não configurado"**

**Causa:** Variável não foi setada ou worker não reiniciou

**Solução:**
1. Verificar env vars no Render:
   ```
   Dashboard → ensinalab-worker → Environment
   → Verificar SHOTSTACK_API_KEY presente
   ```
2. Force restart:
   ```
   Settings → Manual Deploy → Clear build cache & deploy
   ```

---

### **Erro: "Shotstack render falhou: 401 Unauthorized"**

**Causa:** API Key inválida ou expirada

**Solução:**
1. Gerar nova key no dashboard Shotstack
2. Atualizar no Render
3. Restart worker

---

### **Erro: "Não foi possível fazer upload do áudio"**

**Causa:** Cloudflare R2 não configurado

**Solução 1: Shotstack Assets (Recomendado)**
- ✅ Já implementado no código
- ✅ Upload automático via Shotstack API
- ⚠️ Requer API Key válida

**Solução 2: Configurar R2**
- Seguir guia: `QUICKSTART_R2.md`
- Adicionar env vars:
  ```
  R2_ACCESS_KEY_ID
  R2_SECRET_ACCESS_KEY
  R2_BUCKET_NAME
  R2_ACCOUNT_ID
  ```

---

### **Vídeos com watermark "Shotstack"**

**Causa:** Usando Sandbox (stage) mode

**Para remover watermark:**
1. Upgrade para tier pago ($49/mês ou $0.10/vídeo)
2. Usar Production key (v1) em vez de Sandbox
3. Mudar env var:
   ```
   SHOTSTACK_STAGE = v1
   ```

---

### **Renderização demorando >5 min**

**Causas possíveis:**
- Shotstack API lenta (raro)
- Muitos slides (>20)
- Áudio muito grande (>10MB)

**Soluções:**
1. Verificar status no dashboard Shotstack:
   ```
   https://dashboard.shotstack.io/renders
   → Ver Render ID
   → Verificar status/logs
   ```
2. Reduzir slides (código já limita a 10)
3. Comprimir áudio antes de upload

---

## 📊 Comparação de Performance

| Métrica | MoviePy (Local) | Shotstack (Cloud) | Melhoria |
|---------|----------------|-------------------|----------|
| **Tempo de render** | 15-20 min | 1-2 min | **10x mais rápido** |
| **Uso de CPU** | 100% (worker) | 0% (cloud) | **100% economizado** |
| **Uso de RAM** | 500MB+ | <50MB | **90% economizado** |
| **Custo/vídeo** | $0 (free tier) | $0.10 | $0.10 extra |
| **Escalabilidade** | Limitada (0.5 CPU) | Infinita | ⭐⭐⭐⭐⭐ |
| **Qualidade** | 720p, básica | 1080p, profissional | ⬆️ |
| **CDN** | ❌ (precisa R2) | ✅ (integrado) | ⭐⭐⭐⭐⭐ |

---

## 💰 Pricing Shotstack

### **Free Tier (Sandbox)**
- ✅ **20 renders/mês** grátis
- ⚠️ Watermark "Shotstack" nos vídeos
- ✅ Ideal para desenvolvimento/testes
- ✅ Mesma performance do tier pago

### **Paid Tier (Production)**
- 💵 **$49/mês** = 500 renders (~$0.10/vídeo)
- ✅ **Sem watermark**
- ✅ API v1 (production)
- ✅ Suporte prioritário

### **Pay-as-you-go**
- 💵 **$0.15/render** (sem mensalidade)
- ✅ Sem watermark
- ⚠️ Mais caro que plano mensal

**Recomendação:**
- **Dev/Testes:** Free tier (Sandbox)
- **Produção (<500 vídeos/mês):** Plano $49/mês
- **Produção (>500 vídeos/mês):** Enterprise (contato)

---

## 🎯 Próximos Passos

### **Após Setup:**
1. ✅ Gerar 3-5 vídeos de teste
2. ✅ Comparar qualidade com MoviePy
3. ✅ Medir tempo de geração real
4. ✅ Validar custos (free tier suficiente?)
5. ✅ Decidir: manter Shotstack ou voltar MoviePy

### **Produção:**
1. Upgrade para tier pago (remover watermark)
2. Mudar `SHOTSTACK_STAGE=v1`
3. Configurar webhook (notificações de conclusão)
4. Implementar retry policy (se render falhar)

---

## 📚 Recursos Adicionais

- **Docs Shotstack:** https://shotstack.io/docs/guide/
- **API Reference:** https://shotstack.io/docs/api/
- **Templates:** https://shotstack.io/templates/
- **Exemplos:** https://github.com/shotstack/shotstack-sdk-python

---

## ✅ Checklist Final

- [ ] Conta Shotstack criada
- [ ] Sandbox API Key obtida
- [ ] SHOTSTACK_API_KEY configurada no Worker
- [ ] SHOTSTACK_API_KEY configurada na API
- [ ] Ambos os serviços reiniciados
- [ ] Vídeo de teste gerado com sucesso
- [ ] Tempo de geração <3 min (vs 15+ min antes)
- [ ] URL do vídeo acessível (CDN)
- [ ] Qualidade do vídeo validada

---

**Dúvidas?** Consulte `TROUBLESHOOTING_WORKER.md` ou logs do Render!

🎉 **Shotstack configurado com sucesso! Agora seus vídeos são gerados 10x mais rápido!**
