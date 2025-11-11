# ⚡ Setup Rápido: Cloudflare R2

## 🎯 O que você precisa fazer

### **1. Criar Bucket no Cloudflare (3 minutos)**

1. Acesse: https://dash.cloudflare.com/
2. Menu lateral → **R2**
3. Clique em **"Create Bucket"**
4. Configure:
   ```
   Bucket name: ensinalab-videos
   Location: Automatic (ou escolha região mais próxima)
   ```
5. Clique em **"Create bucket"**

---

### **2. Criar API Token (2 minutos)**

1. Na página do R2, clique em **"Manage R2 API Tokens"**
2. Clique em **"Create API Token"**
3. Configure:
   ```
   Token name: EnsaiaLab Video Storage
   
   Permissions:
   ✅ Object Read & Write
   
   Bucket scope:
   ○ Apply to specific buckets only
   ✅ ensinalab-videos
   
   TTL: Forever (ou escolha validade)
   ```
4. Clique em **"Create API Token"**
5. **IMPORTANTE:** Copie e salve as credenciais:
   ```
   Access Key ID: <copiar>
   Secret Access Key: <copiar>
   Account ID: <copiar>
   ```
   ⚠️ Você só verá o Secret Access Key UMA VEZ!

---

### **3. Configurar no Render (2 minutos)**

#### **3.1: Configurar Worker**

1. Acesse: https://dashboard.render.com
2. Selecione: **ensinalab-worker**
3. Menu lateral → **Environment**
4. Clique em **"Add Environment Variable"**
5. Adicione as seguintes variáveis (uma por vez):

```bash
# Obrigatórias
R2_ACCESS_KEY_ID = <cole o Access Key ID copiado>
R2_SECRET_ACCESS_KEY = <cole o Secret Access Key copiado>
R2_BUCKET_NAME = ensinalab-videos
R2_ACCOUNT_ID = <cole o Account ID copiado>

# Opcional (deixe em branco por enquanto)
R2_PUBLIC_URL = 
```

6. Clique em **"Save Changes"**
7. ⏳ Worker vai reiniciar automaticamente (30-60s)

#### **3.2: Configurar Web Service (API)**

1. Volte ao dashboard: https://dashboard.render.com
2. Selecione: **ensinalab-api** (ou nome do seu Web Service)
3. Menu lateral → **Environment**
4. Adicione as **MESMAS** variáveis:

```bash
R2_ACCESS_KEY_ID = <mesmo valor do worker>
R2_SECRET_ACCESS_KEY = <mesmo valor do worker>
R2_BUCKET_NAME = ensinalab-videos
R2_ACCOUNT_ID = <mesmo valor do worker>
```

5. Clique em **"Save Changes"**
6. ⏳ API vai reiniciar automaticamente (30-60s)

---

### **4. Testar Configuração (1 minuto)**

#### **Via Script (Recomendado)**

```bash
python scripts/check_storage_config.py
```

**Saída esperada:**
```
============================================================
🗄️  DIAGNÓSTICO: Storage Configuration
============================================================

✅ CLOUDFLARE R2 CONFIGURADO
   Bucket: ensinalab-videos
   Account ID: abc123...
   Access Key: 12345678...wxyz

🎯 Storage ativo: Cloudflare R2
   → Vídeos serão armazenados no R2
   → Bandwidth GRÁTIS (sem custo de saída)
   → CDN integrado para baixa latência

🔍 Testando conexão...
   ✅ Bucket acessível!
```

#### **Via Geração de Vídeo**

1. Crie um novo briefing na API
2. Gere um vídeo
3. Aguarde conclusão
4. Verifique os logs do worker:

```
📦 Storage configurado: R2
   ✓ R2 Bucket: ensinalab-videos
📤 Uploading para ensinalab-videos/videos/video_8.mp4...
✅ Upload concluído: https://pub-abc123.r2.dev/videos/video_8.mp4
🗑️  Arquivo local deletado: generated_videos/video_8_simple.mp4
```

5. Tente baixar o vídeo pela API:

```bash
GET /api/v1/videos/{video_hash}/download
```

Deve retornar **HTTP 307 Redirect** para URL do R2.

---

## ✅ Checklist Final

- [ ] Bucket criado no Cloudflare R2
- [ ] API Token criado com permissões corretas
- [ ] Credenciais copiadas e salvas em local seguro
- [ ] Variáveis configuradas no Worker (Render)
- [ ] Variáveis configuradas no Web Service (Render)
- [ ] Ambos os serviços reiniciados
- [ ] Script de diagnóstico executado com sucesso
- [ ] Vídeo de teste gerado e armazenado no R2
- [ ] Download funcionando via API

---

## 🎉 Pronto!

Agora seus vídeos são automaticamente:
1. ✅ Gerados pelo worker
2. ✅ Enviados para Cloudflare R2
3. ✅ Acessíveis via API (redirect para R2)
4. ✅ Servidos com CDN global (baixa latência)
5. ✅ Sem custo de bandwidth!

---

## 🔧 Troubleshooting

### **Erro: "Bucket não acessível"**

**Causa:** Permissões incorretas ou credenciais erradas

**Solução:**
1. Verifique se copiou as credenciais corretas
2. Verifique se o token tem permissão "Object Read & Write"
3. Verifique se o bucket name está exato: `ensinalab-videos`

### **Erro: "Upload falhou"**

**Causa:** Token expirado ou bucket cheio

**Solução:**
1. Verifique validade do token no Cloudflare
2. Verifique uso do storage: R2 → ensinalab-videos → Usage
3. Verifique logs completos do worker

### **Vídeo ainda retorna 503**

**Causa:** Variáveis não foram aplicadas ou serviços não reiniciaram

**Solução:**
1. Force restart manual:
   - Worker: Settings → "Manual Deploy" → "Clear build cache & deploy"
   - API: Settings → "Manual Deploy" → "Clear build cache & deploy"
2. Aguarde 2-3 minutos
3. Execute script de diagnóstico novamente

### **URL do vídeo não funciona**

**Causa:** Bucket não está público (R2 sem custom domain)

**Solução:**
1. Cloudflare R2 → ensinalab-videos → Settings
2. Habilitar **"Public Access"** (se quiser URLs públicas)
   
   OU
   
3. Usar presigned URLs (já implementado no código)

---

## 📊 Monitoramento

### **Ver uploads no Cloudflare**

1. https://dash.cloudflare.com/ → R2
2. Clique em **ensinalab-videos**
3. Veja lista de arquivos:
   - `videos/video_1.mp4`
   - `videos/video_2.mp4`
   - `thumbnails/video_1.jpg`

### **Verificar custos**

1. R2 Dashboard → **Usage**
2. Métricas:
   - Storage usado (GB)
   - Bandwidth (sempre $0 no R2!)
   - Operações (Class A/B requests)

**Estimativa mensal:**
- 100 vídeos × 20MB = 2GB storage
- Custo: **$0** (dentro do free tier de 10GB)
- Bandwidth: **$0** (sempre grátis no R2)
- **Total: $0/mês** 🎉

---

## 🚀 Próximos Passos (Opcional)

### **Custom Domain (para URLs bonitas)**

Em vez de: `https://pub-abc123.r2.dev/videos/video_1.mp4`  
Ter: `https://videos.ensinalab.com/videos/video_1.mp4`

**Setup:**
1. R2 → ensinalab-videos → Settings → Custom Domains
2. Adicionar: `videos.ensinalab.com`
3. Copiar CNAME record
4. Adicionar DNS no Cloudflare
5. Adicionar env var: `R2_PUBLIC_URL=https://videos.ensinalab.com`

### **Migrar vídeos antigos**

Se você tem vídeos gerados antes do R2:

```bash
python scripts/migrate_videos_to_r2.py
```

(Script a ser criado se necessário)

---

**Dúvidas?** Verifique `STORAGE_CONFIGURATION.md` para mais detalhes.
