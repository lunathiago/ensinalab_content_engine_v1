#!/usr/bin/env python3
"""
Teste de geração de presigned URL para R2
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.storage import get_storage

def test_presigned_url():
    """Testa geração de presigned URL"""
    
    storage = get_storage()
    
    print("=" * 70)
    print("TESTE: Geração de Presigned URL")
    print("=" * 70)
    
    print(f"\nStorage configurado: {'R2' if storage.use_r2 else 'S3' if storage.use_s3 else 'Local'}")
    
    if storage.use_local:
        print("⚠️  Storage local - presigned URL não necessária")
        return True
    
    # Testar com vídeo ID 4 (do log do usuário)
    video_id = 4
    
    print(f"\n1️⃣ Testando get_video_url() (URL padrão, 24h):")
    url = storage.get_video_url(video_id)
    
    if url:
        print(f"   ✅ URL gerada: {url[:80]}...")
        print(f"   → Tipo: {'Presigned' if 'X-Amz-Signature' in url or 'Signature' in url else 'Pública'}")
    else:
        print(f"   ❌ Falhou ao gerar URL")
    
    print(f"\n2️⃣ Testando generate_presigned_download_url() (1h, com Content-Disposition):")
    download_url = storage.generate_presigned_download_url(video_id, expires_in=3600)
    
    if download_url:
        print(f"   ✅ Presigned URL gerada: {download_url[:80]}...")
        
        # Verificar parâmetros da presigned URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(download_url)
        params = parse_qs(parsed.query)
        
        print(f"   → Host: {parsed.netloc}")
        print(f"   → Path: {parsed.path}")
        
        if 'X-Amz-Signature' in params or 'Signature' in params:
            print(f"   ✅ Assinatura detectada")
        
        if 'X-Amz-Expires' in params:
            print(f"   ✅ Expiração: {params['X-Amz-Expires'][0]}s")
        
        if 'response-content-disposition' in params:
            print(f"   ✅ Content-Disposition: {params['response-content-disposition'][0]}")
        
        return True
    else:
        print(f"   ❌ Falhou ao gerar presigned URL")
        return False

if __name__ == "__main__":
    success = test_presigned_url()
    sys.exit(0 if success else 1)
