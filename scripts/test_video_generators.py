#!/usr/bin/env python3
"""
Script de teste para os geradores de vídeo
Testa cada gerador individualmente antes do deploy
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.video.factory import VideoGeneratorFactory, create_simple_generator
from src.config.video_config import video_config


def test_simple_generator(provider='google'):
    """Testa Simple Generator com TTS"""
    print("\n" + "="*60)
    print("🧪 TESTE: Simple Generator")
    print("="*60)
    
    try:
        # Script de teste curto
        script = """
        Bem-vindo ao EnsinaLab Content Engine.
        
        Este é um teste do gerador de vídeos simples.
        
        O sistema combina text-to-speech com slides estáticos para criar
        vídeos educacionais de forma rápida e econômica.
        
        Este gerador é ideal para desenvolvimento e testes.
        """
        
        print(f"\n📝 Script: {len(script)} caracteres")
        print(f"🎤 TTS Provider: {provider}")
        
        # Criar gerador
        generator = create_simple_generator(provider=provider)
        
        print(f"💰 Custo estimado: ${generator.estimate_cost(1):.2f}")
        
        # Gerar vídeo
        print("\n🎬 Gerando vídeo...")
        result = generator.generate(
            script=script,
            title="Teste Simple Generator",
            metadata={
                'tone': 'casual',
                'target_audience': 'developers'
            },
            video_id=999
        )
        
        # Resultados
        print("\n✅ SUCESSO!")
        print(f"📁 Arquivo: {result['file_path']}")
        print(f"⏱️  Duração: {result['duration']:.2f}s")
        print(f"💾 Tamanho: {result['file_size'] / (1024*1024):.2f} MB")
        
        if result.get('thumbnail_path'):
            print(f"🖼️  Thumbnail: {result['thumbnail_path']}")
        
        print("\nℹ️  Metadata:")
        for key, value in result['metadata'].items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_avatar_generator(provider='did'):
    """Testa Avatar Generator"""
    print("\n" + "="*60)
    print("🧪 TESTE: Avatar Generator")
    print("="*60)
    
    # Verificar API key
    key_map = {
        'heygen': 'HEYGEN_API_KEY',
        'did': 'DID_API_KEY'
    }
    
    env_var = key_map.get(provider)
    if not os.getenv(env_var):
        print(f"⚠️  PULADO: {env_var} não configurado")
        print(f"   Configure: export {env_var}=your-key")
        return False
    
    try:
        script = """
        Olá, sou seu instrutor virtual.
        
        Hoje vamos aprender sobre gestão escolar moderna.
        
        Este é um teste do gerador de avatares.
        """
        
        print(f"\n📝 Script: {len(script)} caracteres")
        print(f"👤 Provider: {provider}")
        
        generator = VideoGeneratorFactory.create('avatar', provider=provider)
        
        print(f"💰 Custo estimado: ${generator.estimate_cost(0.5):.2f}")
        print("\n🎬 Gerando vídeo (pode demorar 5-15 min)...")
        
        result = generator.generate(
            script=script,
            title="Teste Avatar Generator",
            metadata={
                'tone': 'professional',
                'avatar_id': 'default'
            },
            video_id=998
        )
        
        print("\n✅ SUCESSO!")
        print(f"📁 Arquivo: {result['file_path']}")
        print(f"⏱️  Duração: {result['duration']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_generator(provider='kling'):
    """Testa AI Generator"""
    print("\n" + "="*60)
    print("🧪 TESTE: AI Generator")
    print("="*60)
    
    # Verificar API key
    key_map = {
        'kling': 'KLING_API_KEY',
        'runway': 'RUNWAY_API_KEY'
    }
    
    env_var = key_map.get(provider)
    if not os.getenv(env_var):
        print(f"⚠️  PULADO: {env_var} não configurado")
        print(f"   Configure: export {env_var}=your-key")
        return False
    
    # Avisar sobre custo
    print("\n⚠️  ATENÇÃO: Este teste é CARO (~$50-100)")
    response = input("   Deseja continuar? (yes/no): ")
    if response.lower() != 'yes':
        print("   Teste cancelado pelo usuário")
        return False
    
    try:
        script = """
        Uma escola moderna com tecnologia de ponta.
        
        Professores e alunos colaborando em projetos digitais.
        
        O futuro da educação está aqui.
        """
        
        print(f"\n📝 Script: {len(script)} caracteres")
        print(f"🎨 Provider: {provider}")
        
        generator = VideoGeneratorFactory.create('ai', provider=provider)
        
        print(f"💰 Custo estimado: ${generator.estimate_cost(0.5):.2f}")
        print("\n🎬 Gerando vídeo (pode demorar 20-60 min)...")
        
        result = generator.generate(
            script=script,
            title="Teste AI Generator",
            metadata={
                'quality': 'standard',
                'max_scenes': 3
            },
            video_id=997
        )
        
        print("\n✅ SUCESSO!")
        print(f"📁 Arquivo: {result['file_path']}")
        print(f"⏱️  Duração: {result['duration']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_factory_methods():
    """Testa métodos do factory"""
    print("\n" + "="*60)
    print("🧪 TESTE: Factory Methods")
    print("="*60)
    
    try:
        # Listar geradores disponíveis
        print("\n📋 Geradores disponíveis:")
        generators = VideoGeneratorFactory.get_available_generators()
        
        for gen in generators:
            print(f"\n   {gen['type'].upper()}")
            print(f"   • {gen['description']}")
            print(f"   • Custo: ${gen['cost_per_minute']:.2f}/min")
            print(f"   • Velocidade: {gen['generation_speed']}")
            print(f"   • Melhor para: {gen['best_for']}")
        
        # Testar recomendação
        print("\n🤖 Teste de recomendação:")
        
        scenarios = [
            {'budget_usd': 1.0, 'urgency': 'high', 'quality_level': 'standard'},
            {'budget_usd': 20.0, 'urgency': 'normal', 'quality_level': 'high'},
            {'budget_usd': 100.0, 'urgency': 'low', 'quality_level': 'premium'}
        ]
        
        for scenario in scenarios:
            rec = VideoGeneratorFactory.recommend_generator(**scenario)
            print(f"\n   Budget ${scenario['budget_usd']}, "
                  f"Urgency {scenario['urgency']}, "
                  f"Quality {scenario['quality_level']}")
            print(f"   → Recomendação: {rec['type']} ({rec['provider']})")
            print(f"   → Custo estimado: ${rec['estimated_cost']:.2f}")
        
        # Testar seleção por briefing
        print("\n📊 Teste de seleção por briefing:")
        
        briefings = [
            {'duration_minutes': 2, 'tone': 'casual', 'subject_area': 'tutorial'},
            {'duration_minutes': 5, 'tone': 'professional', 'subject_area': 'leadership'},
            {'duration_minutes': 3, 'tone': 'inspirational', 'subject_area': 'marketing'}
        ]
        
        for briefing in briefings:
            config = video_config.get_generator_for_briefing(briefing)
            cost = video_config.estimate_cost(
                config['generator_type'], 
                briefing['duration_minutes']
            )
            print(f"\n   {briefing['subject_area'].title()} "
                  f"({briefing['duration_minutes']} min, {briefing['tone']})")
            print(f"   → Gerador: {config['generator_type']} ({config.get('provider', 'default')})")
            print(f"   → Custo estimado: ${cost:.2f}")
        
        print("\n✅ Factory methods funcionando!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Testa geradores de vídeo')
    parser.add_argument(
        '--generator',
        choices=['simple', 'avatar', 'ai', 'factory', 'all'],
        default='factory',
        help='Qual gerador testar'
    )
    parser.add_argument(
        '--provider',
        help='Provider específico (google, elevenlabs, heygen, did, kling, runway)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🎬 ENSINALAB VIDEO GENERATOR TESTS")
    print("="*60)
    
    # Verificar diretórios
    output_dir = Path(os.getenv('VIDEO_OUTPUT_DIR', '/tmp/ensinalab_videos'))
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Output directory: {output_dir}")
    
    results = {}
    
    # Executar testes
    if args.generator in ['factory', 'all']:
        results['factory'] = test_factory_methods()
    
    if args.generator in ['simple', 'all']:
        provider = args.provider or 'google'
        results['simple'] = test_simple_generator(provider)
    
    if args.generator in ['avatar', 'all']:
        provider = args.provider or 'did'
        results['avatar'] = test_avatar_generator(provider)
    
    if args.generator in ['ai', 'all']:
        provider = args.provider or 'kling'
        results['ai'] = test_ai_generator(provider)
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{name.upper()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 Todos os testes passaram!")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
