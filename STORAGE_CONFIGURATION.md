# 🗄️ Configuração de Storage para Vídeos

## Problema Atual

No Render, **Worker** e **Web Service** rodam em **containers separados**:

```
Worker Container                 Web Service Container
├─ Gera vídeo                   ├─ Recebe requisições API
├─ Salva em generated_videos/   ├─ Tenta servir arquivo
└─ ❌ Filesystem efêmero         └─ ❌ Arquivo não existe!
```

**Erro típico:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'generated_videos/video_5_simple.mp4'
```

---

## 🎯 Soluções

### **Opção 1: Cloudflare R2 (Recomendado)** ✅

**Por quê?**
- ✅ **Sem custo de saída** (bandwidth gratuito)
- ✅ Compatível com API S3
- ✅ CDN integrado
- ✅ 10GB grátis/mês
- ✅ Melhor custo-benefício para vídeos

**Custo:** $0.015/GB storage (após 10GB grátis)

#### Setup Cloudflare R2

1. **Criar bucket**:
   ```bash
   # No dashboard Cloudflare
   R2 → Create Bucket → "ensinalab-videos"
   ```

2. **Obter credenciais**:
   ```
   R2 → Manage R2 API Tokens → Create API Token
   
   Permissões:
   - Object Read & Write
   - Bucket: ensinalab-videos
   ```

3. **Configurar variáveis no Render**:
   ```bash
   # Worker + Web Service
   R2_ACCOUNT_ID=your_account_id
   R2_ACCESS_KEY_ID=your_access_key
   R2_SECRET_ACCESS_KEY=your_secret_key
   R2_BUCKET_NAME=ensinalab-videos
   R2_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
   R2_PUBLIC_URL=https://videos.ensinalab.com  # Opcional: custom domain
   ```

4. **Instalar dependências**:
   ```bash
   # Já incluído em requirements.txt
   boto3>=1.28.0
   ```

5. **Habilitar no código**:
   ```python
   # src/config/settings.py
   USE_R2_STORAGE = True  # ou via env var
   ```

---

### **Opção 2: AWS S3**

**Por quê?**
- ✅ Mais robusto
- ✅ Ecossistema maduro
- ⚠️ Custo de bandwidth (saída de dados)

**Custo:** $0.023/GB storage + $0.09/GB transfer

#### Setup AWS S3

1. **Criar bucket**:
   ```bash
   aws s3 mb s3://ensinalab-videos --region us-east-1
   ```

2. **Configurar CORS**:
   ```json
   {
     "CORSRules": [{
       "AllowedOrigins": ["*"],
       "AllowedMethods": ["GET", "HEAD"],
       "AllowedHeaders": ["*"],
       "MaxAgeSeconds": 3600
     }]
   }
   ```

3. **Obter credenciais IAM**:
   ```
   Permissões: s3:PutObject, s3:GetObject, s3:DeleteObject
   ```

4. **Configurar no Render**:
   ```bash
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_S3_BUCKET_NAME=ensinalab-videos
   AWS_S3_REGION=us-east-1
   USE_S3_STORAGE=True
   ```

---

### **Opção 3: Render Persistent Disk** (Temporário)

**Por quê?**
- ✅ Simples de configurar
- ✅ Sem dependências externas
- ⚠️ Limitado a 1 região
- ⚠️ Backup manual

**Custo:** $1/GB/mês

#### Setup Render Disk

1. **Criar Disk no Dashboard**:
   ```
   Dashboard → New → Persistent Disk
   Name: ensinalab-videos-disk
   Size: 10GB
   Region: Oregon (mesma do worker)
   ```

2. **Montar no Worker**:
   ```yaml
   # render.yaml
   services:
     - type: worker
       name: ensinalab-worker
       disk:
         name: ensinalab-videos-disk
         mountPath: /opt/render/project/src/generated_videos
         sizeGB: 10
   ```

3. **Montar no Web Service**:
   ```yaml
   services:
     - type: web
       name: ensinalab-api
       disk:
         name: ensinalab-videos-disk
         mountPath: /opt/render/project/src/generated_videos
         sizeGB: 10
   ```

4. **Deploy**:
   ```bash
   git push origin main  # Render auto-deploya
   ```

**Limitações:**
- Disk precisa estar na mesma região que ambos os serviços
- Não tem CDN (vídeos servidos diretamente)
- Latência pode ser alta para usuários distantes

---

## 🚀 Implementação no Código

### Storage Abstraction Layer

```python
# src/utils/storage.py (criar)
import os
import boto3
from typing import Optional

class VideoStorage:
    """Abstração para upload de vídeos"""
    
    def __init__(self):
        self.use_r2 = os.getenv("USE_R2_STORAGE") == "true"
        self.use_s3 = os.getenv("USE_S3_STORAGE") == "true"
        
        if self.use_r2:
            self.client = boto3.client(
                's3',
                endpoint_url=os.getenv("R2_ENDPOINT_URL"),
                aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
            )
            self.bucket = os.getenv("R2_BUCKET_NAME")
            self.public_url = os.getenv("R2_PUBLIC_URL")
            
        elif self.use_s3:
            self.client = boto3.client('s3')
            self.bucket = os.getenv("AWS_S3_BUCKET_NAME")
            self.public_url = None  # S3 gera URL automaticamente
    
    def upload_video(self, local_path: str, video_id: int) -> str:
        """
        Faz upload do vídeo para storage
        
        Returns:
            URL pública do vídeo
        """
        if not (self.use_r2 or self.use_s3):
            # Sem storage externo, retornar path local
            return local_path
        
        key = f"videos/video_{video_id}.mp4"
        
        self.client.upload_file(
            local_path,
            self.bucket,
            key,
            ExtraArgs={'ContentType': 'video/mp4'}
        )
        
        if self.public_url:
            return f"{self.public_url}/{key}"
        else:
            # Gerar presigned URL (S3)
            return self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=86400  # 24h
            )
    
    def delete_video(self, video_id: int):
        """Remove vídeo do storage"""
        if not (self.use_r2 or self.use_s3):
            return
        
        key = f"videos/video_{video_id}.mp4"
        self.client.delete_object(Bucket=self.bucket, Key=key)
```

### Integração no Worker

```python
# src/workers/tasks.py (modificar)
from src.utils.storage import VideoStorage

@celery_app.task
def generate_video(video_id: int, ...):
    # ... gerar vídeo ...
    
    # Upload para storage
    storage = VideoStorage()
    video_url = storage.upload_video(local_path, video_id)
    
    # Atualizar DB com URL
    video.file_path = video_url
    video.status = "completed"
    db.commit()
```

### Endpoint de Download

```python
# src/api/routes/videos.py (modificar)
from fastapi.responses import RedirectResponse

@router.get("/videos/{video_hash}/download")
async def download_video(...):
    # ...
    
    # Se URL externa, redirecionar
    if video.file_path.startswith("http"):
        return RedirectResponse(video.file_path)
    
    # Se local, servir arquivo
    return FileResponse(video.file_path, ...)
```

---

## 📊 Comparação

| Feature | R2 | S3 | Render Disk |
|---------|----|----|-------------|
| **Custo Storage** | $0.015/GB | $0.023/GB | $1/GB |
| **Custo Bandwidth** | Grátis ✅ | $0.09/GB | Incluído |
| **CDN** | Sim ✅ | Via CloudFront | Não ❌ |
| **Setup** | Médio | Médio | Fácil |
| **Escalabilidade** | Alta | Alta | Baixa |
| **Free Tier** | 10GB | 5GB | 0GB |
| **Recomendado para** | Produção | Enterprise | MVP/Dev |

---

## 🎯 Recomendação

Para EnsaiaLab:

1. **Curto prazo (1-2 semanas):** Render Persistent Disk
   - Rápido de configurar
   - Resolve o problema imediato
   - $10/mês para 10GB

2. **Médio prazo (1 mês):** Migrar para Cloudflare R2
   - Melhor custo-benefício
   - Bandwidth grátis
   - CDN integrado

3. **Longo prazo:** Considerar S3 se precisar de:
   - Análises avançadas (S3 Analytics)
   - Integração com AWS ML
   - Replicação cross-region

---

## 🔧 Migração Passo a Passo

### Fase 1: Setup Render Disk (1h)

1. Criar disk no dashboard
2. Atualizar `render.yaml`
3. Deploy
4. Testar download de vídeo

### Fase 2: Implementar Storage Layer (2h)

1. Criar `src/utils/storage.py`
2. Adicionar `boto3` ao `requirements.txt`
3. Modificar `tasks.py` para usar storage
4. Testar upload/download

### Fase 3: Setup R2 (1h)

1. Criar bucket Cloudflare
2. Configurar env vars
3. Habilitar `USE_R2_STORAGE=true`
4. Migrar vídeos existentes

### Fase 4: Limpeza (30min)

1. Remover vídeos locais antigos
2. Desmontar Render Disk
3. Cancelar cobrança do disk

---

## 📝 Checklist de Implementação

- [ ] Decidir storage (R2, S3, ou Disk)
- [ ] Criar bucket/disk
- [ ] Configurar credenciais no Render
- [ ] Implementar `VideoStorage` class
- [ ] Atualizar `generate_video` task
- [ ] Modificar endpoint `/download`
- [ ] Adicionar campo `file_url` ao model Video
- [ ] Testar upload + download
- [ ] Migrar vídeos existentes (se houver)
- [ ] Documentar no README
- [ ] Monitorar custos

---

## ❓ Dúvidas Comuns

**Q: Por que não usar Firebase Storage?**
A: Firebase é mais caro para vídeos e tem limites de largura de banda no free tier.

**Q: Posso usar ambos (R2 + Disk)?**
A: Sim! Disk para cache local, R2 para storage permanente.

**Q: E se o upload para R2 falhar?**
A: Implementar retry automático + fallback para storage local temporário.

**Q: Como proteger vídeos?**
A: Presigned URLs com expiração ou CloudFlare Access.

---

## 🆘 Troubleshooting

**Erro: "No such file or directory"**
```python
# Verificar se storage está configurado
python scripts/check_storage_config.py
```

**Upload lento para R2/S3**
```python
# Usar multipart upload para vídeos grandes
s3.upload_file(..., Config=TransferConfig(multipart_threshold=50*1024*1024))
```

**Custo muito alto**
- Verificar se bandwidth está sendo cobrado (R2 não cobra!)
- Implementar compressão de vídeos
- Usar resoluções menores (720p vs 1080p)

---

**Próximos passos:** Escolha uma opção e eu te ajudo a implementar! 🚀
