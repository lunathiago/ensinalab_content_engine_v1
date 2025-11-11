#!/usr/bin/env python3
"""
Script de diagnóstico: Verifica configuração de Storage
"""
import os
import sys


def check_storage_config():
    """Verifica configuração de storage (R2, S3, ou Local)"""
    
    print("\n" + "="*60)
    print("🗄️  DIAGNÓSTICO: Storage Configuration")
    print("="*60 + "\n")
    
    # Verificar Cloudflare R2
    r2_configured = all([
        os.getenv("R2_ACCESS_KEY_ID"),
        os.getenv("R2_SECRET_ACCESS_KEY"),
        os.getenv("R2_BUCKET_NAME")
    ])
    
    # Verificar AWS S3
    s3_configured = all([
        os.getenv("AWS_ACCESS_KEY_ID"),
        os.getenv("AWS_SECRET_ACCESS_KEY"),
        os.getenv("AWS_S3_BUCKET_NAME")
    ])
    
    if r2_configured:
        print("✅ CLOUDFLARE R2 CONFIGURADO")
        print(f"   Bucket: {os.getenv('R2_BUCKET_NAME')}")
        
        account_id = os.getenv("R2_ACCOUNT_ID")
        if account_id:
            print(f"   Account ID: {account_id}")
        
        public_url = os.getenv("R2_PUBLIC_URL")
        if public_url:
            print(f"   Public URL: {public_url}")
        else:
            print(f"   ⚠️  R2_PUBLIC_URL não configurado (opcional)")
            if account_id:
                print(f"   URLs usarão: https://pub-{account_id}.r2.dev/")
        
        access_key = os.getenv("R2_ACCESS_KEY_ID")
        if len(access_key) > 8:
            masked = f"{access_key[:8]}...{access_key[-4:]}"
        else:
            masked = "***"
        print(f"   Access Key: {masked}")
        
        print("\n🎯 Storage ativo: Cloudflare R2")
        print("   → Vídeos serão armazenados no R2")
        print("   → Bandwidth GRÁTIS (sem custo de saída)")
        print("   → CDN integrado para baixa latência")
        
        # Testar conexão
        print("\n🔍 Testando conexão...")
        try:
            from src.utils.storage import get_storage
            storage = get_storage()
            
            if storage.check_bucket_exists():
                print("   ✅ Bucket acessível!")
            else:
                print("   ❌ Bucket não encontrado ou sem permissões")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao conectar: {e}")
            return False
        
        return True
    
    elif s3_configured:
        print("✅ AWS S3 CONFIGURADO")
        print(f"   Bucket: {os.getenv('AWS_S3_BUCKET_NAME')}")
        print(f"   Region: {os.getenv('AWS_S3_REGION', 'us-east-1')}")
        
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        if len(access_key) > 8:
            masked = f"{access_key[:8]}...{access_key[-4:]}"
        else:
            masked = "***"
        print(f"   Access Key: {masked}")
        
        print("\n🎯 Storage ativo: AWS S3")
        print("   → Vídeos serão armazenados no S3")
        print("   ⚠️  Bandwidth cobrado ($0.09/GB)")
        
        return True
    
    else:
        print("❌ NENHUM STORAGE CONFIGURADO")
        print("\n⚠️  Vídeos serão salvos localmente (não funciona no Render!)")
        print("\n" + "="*60)
        print("📋 CONFIGURE CLOUDFLARE R2 (Recomendado)")
        print("="*60)
        print("\n1. Criar bucket no Cloudflare:")
        print("   https://dash.cloudflare.com/ → R2 → Create Bucket")
        print("   Nome sugerido: ensinalab-videos")
        
        print("\n2. Criar API Token:")
        print("   R2 → Manage R2 API Tokens → Create API Token")
        print("   Permissões: Object Read & Write")
        
        print("\n3. Adicionar no Render Dashboard:")
        print("   https://dashboard.render.com")
        print("   ensinalab-worker → Environment")
        print("   ensinalab-api → Environment")
        
        print("\n   Variáveis obrigatórias:")
        print("   ┌──────────────────────────────────────────────┐")
        print("   │ R2_ACCESS_KEY_ID        = <access_key>       │")
        print("   │ R2_SECRET_ACCESS_KEY    = <secret_key>       │")
        print("   │ R2_BUCKET_NAME          = ensinalab-videos   │")
        print("   │ R2_ACCOUNT_ID           = <account_id>       │")
        print("   └──────────────────────────────────────────────┘")
        
        print("\n   Opcional (custom domain):")
        print("   ┌──────────────────────────────────────────────┐")
        print("   │ R2_PUBLIC_URL           = https://videos.... │")
        print("   └──────────────────────────────────────────────┘")
        
        print("\n4. Salvar e aguardar restart dos serviços")
        
        print("\n💰 CUSTOS:")
        print("   - Storage: $0.015/GB/mês (após 10GB grátis)")
        print("   - Bandwidth: GRÁTIS (sem limite)")
        print("   - Operações: $0.36/milhão requests")
        print("   - Estimativa: ~$2-5/mês para 100GB")
        
        print("\n📖 Documentação: STORAGE_CONFIGURATION.md")
        print("="*60 + "\n")
        
        return False


if __name__ == "__main__":
    success = check_storage_config()
    sys.exit(0 if success else 1)
