#!/usr/bin/env python3
"""
Script de diagnóstico: Verifica configuração TTS
"""
import os
import sys

def check_tts_credentials():
    """Verifica todas as credenciais TTS disponíveis"""
    
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO: Credenciais TTS")
    print("="*60 + "\n")
    
    credentials = {
        'ElevenLabs': 'ELEVENLABS_API_KEY',
        'Google Cloud': 'GOOGLE_CLOUD_API_KEY',
        'Google ADC': 'GOOGLE_APPLICATION_CREDENTIALS',
        'AWS Polly': 'AWS_ACCESS_KEY_ID',
        'Azure Speech': 'AZURE_SPEECH_KEY'
    }
    
    found_any = False
    
    for service, env_var in credentials.items():
        value = os.getenv(env_var)
        
        if value:
            # Mascarar chave (mostrar só primeiros/últimos chars)
            if len(value) > 10:
                masked = f"{value[:8]}...{value[-4:]}"
            else:
                masked = "***"
            
            print(f"✅ {service:20} → {env_var}")
            print(f"   Valor: {masked}")
            print()
            found_any = True
        else:
            print(f"❌ {service:20} → {env_var} (não configurado)")
    
    print("\n" + "="*60)
    
    if not found_any:
        print("⚠️  NENHUMA CREDENCIAL TTS ENCONTRADA!")
        print("\nPara configurar ElevenLabs:")
        print("1. Acesse: https://dashboard.render.com")
        print("2. Selecione: ensinalab-worker")
        print("3. Vá em: Environment")
        print("4. Adicione: ELEVENLABS_API_KEY = sk_...")
        print("5. Salve (worker vai reiniciar automaticamente)")
        print("\nDocumentação: CONFIGURE_ELEVENLABS.md")
        return False
    else:
        print("✅ CONFIGURAÇÃO OK!")
        
        # Determinar qual será usado
        if os.getenv("ELEVENLABS_API_KEY"):
            print("\n🎤 Provider ativo: ElevenLabs (melhor qualidade)")
        elif os.getenv("GOOGLE_CLOUD_API_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            print("\n🎤 Provider ativo: Google Cloud TTS")
        elif os.getenv("AWS_ACCESS_KEY_ID"):
            print("\n🎤 Provider ativo: Amazon Polly")
        elif os.getenv("AZURE_SPEECH_KEY"):
            print("\n🎤 Provider ativo: Azure Speech")
        
        return True
    
    print("="*60 + "\n")

if __name__ == "__main__":
    success = check_tts_credentials()
    sys.exit(0 if success else 1)
