"""
Gerador de áudio (TTS - Text-to-Speech)
Suporta múltiplos providers: Google Cloud TTS, ElevenLabs, Amazon Polly
"""
import os
from typing import Optional
from pathlib import Path


class TTSService:
    """Serviço de conversão de texto para fala"""
    
    def __init__(self, provider: str = "auto"):
        """
        Inicializa serviço TTS
        
        Args:
            provider: Provider a usar ('auto', 'elevenlabs', 'google', 'amazon', 'azure')
                     'auto' = detecta automaticamente baseado nas credenciais
        """
        self.provider = self._detect_provider(provider)
        self.output_dir = Path("generated_videos/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verificar credenciais
        self.api_key = self._get_api_key(self.provider)
        
        print(f"   🎤 TTS Provider selecionado: {self.provider}")
    
    def _detect_provider(self, requested_provider: str) -> str:
        """
        Detecta o melhor provider baseado nas credenciais disponíveis
        
        Prioridade: ElevenLabs > Fallback
        (Google TTS removido - usar apenas ElevenLabs)
        """
        if requested_provider.lower() != "auto":
            return requested_provider.lower()
        
        # 🔧 FIX: Apenas ElevenLabs ou fallback
        # Google Cloud TTS removido da detecção automática
        if os.getenv("ELEVENLABS_API_KEY"):
            return "elevenlabs"
        else:
            print("   ⚠️ ELEVENLABS_API_KEY não encontrada, usando fallback (silêncio)")
            return "fallback"
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Obtém a chave API para o provider"""
        key_map = {
            "google": "GOOGLE_CLOUD_API_KEY",
            "elevenlabs": "ELEVENLABS_API_KEY",
            "azure": "AZURE_SPEECH_KEY"
        }
        env_var = key_map.get(provider)
        return os.getenv(env_var) if env_var else None
    
    def generate(
        self, 
        text: str, 
        output_path: str,
        voice: str = "pt-BR-FranciscaNeural",
        speed: float = 1.0
    ) -> str:
        """
        Gera áudio a partir de texto
        
        Args:
            text: Texto para converter
            output_path: Caminho de saída
            voice: ID da voz
            speed: Velocidade (0.5 - 2.0)
        
        Returns:
            Caminho do arquivo de áudio gerado
        """
        
        # 🔧 FIX: Avisar se Google TTS for chamado
        if self.provider == "google":
            print("   ⚠️ Google TTS não está configurado. Use ElevenLabs.")
            print("   → Gerando fallback (silêncio)...")
            return self._generate_fallback_audio(output_path, len(text))
        
        if self.provider == "elevenlabs":
            return self._generate_elevenlabs(text, output_path, voice)
        elif self.provider == "amazon":
            return self._generate_amazon(text, output_path, voice)
        elif self.provider == "azure":
            return self._generate_azure(text, output_path, voice, speed)
        else:
            # Fallback: gerar silêncio
            return self._generate_fallback(text, output_path)
    
    def _generate_google(self, text: str, output_path: str, voice: str, speed: float) -> str:
        """
        Google TTS foi desabilitado.
        Use ElevenLabs configurando ELEVENLABS_API_KEY.
        """
        print(f"   ❌ Google TTS não está mais suportado neste projeto")
        print(f"   → Configure ELEVENLABS_API_KEY para usar ElevenLabs")
        print(f"   → Gerando fallback (silêncio)...")
        return self._generate_fallback(text, output_path)
    
    def _generate_elevenlabs(self, text: str, output_path: str, voice: str) -> str:
        """Gera com ElevenLabs (melhor qualidade para português)"""
        try:
            import requests
            
            # Vozes ElevenLabs com suporte a português
            voice_map = {
                'pt-BR-FranciscaNeural': 'pNInz6obpgDQGcFmaJgB',  # Adam (versátil)
                'pt-BR-AntonioNeural': '21m00Tcm4TlvDq8ikWAM',     # Rachel (feminina)
                'default': 'pNInz6obpgDQGcFmaJgB'
            }
            
            voice_id = voice_map.get(voice, voice_map['default'])
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Melhor para português
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            print(f"   🎤 Gerando áudio com ElevenLabs (voz: {voice_id})...")
            
            response = requests.post(url, json=data, headers=headers, timeout=300)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"   ✅ ElevenLabs TTS: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"   ❌ ElevenLabs falhou: {e}")
            print(f"   → Gerando fallback (silêncio)...")
            return self._generate_fallback(text, output_path)
    
    def _generate_amazon(self, text: str, output_path: str, voice: str) -> str:
        """Gera com Amazon Polly"""
        try:
            import boto3
            
            polly = boto3.client('polly')
            
            # Mapear voz
            voice_map = {
                'pt-BR-FranciscaNeural': 'Camila',
                'pt-BR-AntonioNeural': 'Ricardo'
            }
            
            polly_voice = voice_map.get(voice, 'Camila')
            
            response = polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=polly_voice,
                Engine='neural'
            )
            
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            print(f"   ✓ Amazon Polly: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"   ⚠️ Amazon Polly falhou: {e}, usando fallback")
            return self._generate_fallback(text, output_path)
    
    def _generate_azure(self, text: str, output_path: str, voice: str, speed: float) -> str:
        """Gera com Azure Speech"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_key = os.getenv("AZURE_SPEECH_KEY")
            service_region = os.getenv("AZURE_SPEECH_REGION", "brazilsouth")
            
            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=service_region
            )
            
            speech_config.speech_synthesis_voice_name = voice
            speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
            )
            
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # SSML para controlar velocidade
            ssml = f"""
            <speak version='1.0' xml:lang='pt-BR'>
                <voice name='{voice}'>
                    <prosody rate='{speed}'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"   ✓ Azure TTS: {output_path}")
                return output_path
            else:
                raise Exception(f"Azure falhou: {result.reason}")
            
        except Exception as e:
            print(f"   ⚠️ Azure TTS falhou: {e}, usando fallback")
            return self._generate_fallback(text, output_path)
    
    def _generate_fallback(self, text: str, output_path: str) -> str:
        """Fallback: gera áudio de silêncio com duração estimada"""
        print(f"   ⚠️ Gerando áudio fallback (silêncio)")
        
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine
            
            # Estimar duração
            duration_ms = self.estimate_duration(text) * 1000
            
            # Gerar tom baixo (simula fala)
            audio = Sine(200).to_audio_segment(duration=duration_ms, volume=-30)
            
            # Salvar
            audio.export(output_path, format="mp3")
            
            print(f"   → Fallback gerado: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"   ⚠️ Fallback também falhou: {e}")
            # Criar arquivo vazio
            open(output_path, 'a').close()
            return output_path
    
    def estimate_duration(self, text: str, words_per_minute: int = 150) -> float:
        """
        Estima duração do áudio em segundos
        
        Args:
            text: Texto
            words_per_minute: Palavras por minuto (velocidade de fala)
        
        Returns:
            Duração estimada em segundos
        """
        word_count = len(text.split())
        duration_minutes = word_count / words_per_minute
        return max(duration_minutes * 60, 1.0)  # Mínimo 1 segundo
