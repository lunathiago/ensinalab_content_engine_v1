#!/usr/bin/env python3
"""
Teste de autenticação ElevenLabs
Simula exatamente o que o worker faz
"""
import os
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_env_variable():
    """Testa se a variável de ambiente está configurada"""
    print("=" * 60)
    print("🔍 Testando Variável de Ambiente")
    print("=" * 60)
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if api_key:
        print(f"✅ ELEVENLABS_API_KEY encontrada")
        print(f"   → Começa com: {api_key[:10]}...")
        print(f"   → Termina com: ...{api_key[-10:]}")
        print(f"   → Tamanho: {len(api_key)} caracteres")
        return api_key
    else:
        print("❌ ELEVENLABS_API_KEY NÃO ENCONTRADA!")
        print("\n💡 Para configurar:")
        print("   export ELEVENLABS_API_KEY='sk_54364c35ae693d27d455eb535c70158fa60b0aa9e21fe0d1'")
        return None

def test_tts_service():
    """Testa o TTSService"""
    print("\n" + "=" * 60)
    print("🔍 Testando TTSService")
    print("=" * 60)
    
    from src.video.tts import TTSService
    
    tts = TTSService(provider="auto")
    
    print(f"\n   Provider detectado: {tts.provider}")
    print(f"   API Key carregada: {'✅ Sim' if tts.api_key else '❌ Não'}")
    
    if tts.api_key:
        print(f"   → Começa com: {tts.api_key[:10]}...")
        print(f"   → Tamanho: {len(tts.api_key)} caracteres")

def test_api_call():
    """Testa chamada real à API"""
    print("\n" + "=" * 60)
    print("🔍 Testando Chamada à API")
    print("=" * 60)
    
    import requests
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ Não pode testar: API Key não encontrada")
        return
    
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": "Teste de autenticação",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    print(f"\n   URL: {url}")
    print(f"   Headers: xi-api-key: {api_key[:10]}...")
    print(f"   Text: {data['text']}")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"\n   ✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Sucesso! Áudio recebido ({len(response.content)} bytes)")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

if __name__ == "__main__":
    print("🚀 Teste de Autenticação ElevenLabs\n")
    
    # 1. Verificar variável de ambiente
    api_key = test_env_variable()
    
    # 2. Testar TTSService
    test_tts_service()
    
    # 3. Testar chamada real
    if api_key:
        test_api_call()
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
    print("=" * 60)
