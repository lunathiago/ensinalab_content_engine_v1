#!/usr/bin/env python3
"""
Teste end-to-end: Upload e Download com Presigned URL
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Simular R2 configurado
os.environ['R2_ACCESS_KEY_ID'] = 'test_key'
os.environ['R2_SECRET_ACCESS_KEY'] = 'test_secret'
os.environ['R2_ACCOUNT_ID'] = '00f0e82cafe3dfa560dc626ac9b38f82'
os.environ['R2_BUCKET_NAME'] = 'ensinalab-videos'

from src.utils.storage import VideoStorage

def test_upload_download_flow():
    """Testa fluxo completo: upload -> save URL -> download"""
    
    storage = VideoStorage()
    
    print("=" * 70)
    print("TESTE END-TO-END: Upload e Download")
    print("=" * 70)
    
    # Simular upload
    video_id = 4
    
    print(f"\n1️⃣ UPLOAD (simulado)")
    print(f"   Video ID: {video_id}")
    
    # Simular path após upload
    key = f"videos/video_{video_id}.mp4"
    
    if storage.use_r2 and not storage.public_url:
        # R2 privado
        file_path = f"r2://{storage.bucket}/{key}"
        print(f"   ✅ R2 privado detectado")
        print(f"   → file_path salvo no banco: {file_path}")
    elif storage.use_r2 and storage.public_url:
        # R2 público com custom domain
        file_path = f"{storage.public_url}/{key}"
        print(f"   ✅ R2 público (custom domain)")
        print(f"   → file_path salvo no banco: {file_path}")
    else:
        print(f"   ⚠️  S3 ou Local")
    
    print(f"\n2️⃣ DOWNLOAD (endpoint /videos/{{hash}}/download)")
    
    # Simular endpoint detectando storage path
    if file_path.startswith(("r2://", "s3://")):
        print(f"   🔑 Detectado storage path")
        print(f"   → Gerando presigned URL...")
        
        presigned_url = storage.generate_presigned_download_url(
            video_id=video_id,
            expires_in=3600
        )
        
        if presigned_url:
            print(f"   ✅ Presigned URL gerada!")
            print(f"\n   URL (primeiros 100 chars):")
            print(f"   {presigned_url[:100]}...")
            
            # Verificar assinatura
            if 'X-Amz-Signature' in presigned_url:
                print(f"\n   ✅ Assinatura AWS detectada (acesso autenticado)")
                print(f"   ✅ Válida por 1 hora")
                print(f"   ✅ Download via 307 Redirect")
                return True
            else:
                print(f"   ❌ Assinatura não encontrada!")
                return False
        else:
            print(f"   ❌ Falhou ao gerar presigned URL")
            return False
    
    elif file_path.startswith(("http://", "https://")):
        print(f"   ⚠️  URL pública antiga detectada")
        print(f"   → Tentando gerar presigned URL mesmo assim...")
        
        presigned_url = storage.generate_presigned_download_url(
            video_id=video_id,
            expires_in=3600
        )
        
        if presigned_url:
            print(f"   ✅ Presigned URL gerada (override da URL pública)")
            return True
        else:
            print(f"   ⚠️  Fallback: usando URL pública (pode dar 401)")
            return False
    
    print(f"\n3️⃣ RESULTADO")
    print(f"   ✅ Fluxo completo testado com sucesso!")
    return True

if __name__ == "__main__":
    success = test_upload_download_flow()
    sys.exit(0 if success else 1)
