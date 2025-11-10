# ⚡ Configurar ElevenLabs TTS no Render

## Problema Atual

O sistema está usando **Google TTS** (que falha) porque a variável `ELEVENLABS_API_KEY` não está configurada no Render.

**Log evidência:**
```
[2025-11-10 23:10:52,695: WARNING/MainProcess]    🎤 TTS Provider selecionado: google
```

## Solução: Adicionar ELEVENLABS_API_KEY

### Passo 1: Obter API Key da ElevenLabs

1. Acesse: https://elevenlabs.io/
2. Faça login ou crie conta
3. Vá em **Profile → API Keys**
4. Copie sua API key (formato: `sk_...`)

**Free Tier**: 10.000 caracteres/mês (suficiente para testes)

### Passo 2: Adicionar no Render Dashboard

#### Para o **Worker** (onde os vídeos são gerados):

1. Acesse: https://dashboard.render.com/
2. Selecione seu serviço: **`ensinalab-worker`**
3. Vá em **Environment**
4. Clique em **Add Environment Variable**
5. Adicione:
   - **Key**: `ELEVENLABS_API_KEY`
   - **Value**: `sk_your_actual_key_here`
6. Clique em **Save Changes**
7. O worker vai reiniciar automaticamente

#### Para a **API** (opcional, mas recomendado):

Repita o processo acima para **`ensinalab-api`** (para manter sincronizado).

### Passo 3: Verificar nos Logs

Após o restart, você verá nos logs do worker:

```
✅ ANTES (errado):
   🎤 TTS Provider selecionado: google

✅ DEPOIS (correto):
   🎤 TTS Provider selecionado: elevenlabs
   🎤 Gerando áudio com ElevenLabs (voz: pNInz6obpgDQGcFmaJgB)...
   ✅ ElevenLabs TTS: generated_videos/audio_X.mp3
```

## Benefícios da ElevenLabs

| Aspecto | Google TTS | ElevenLabs |
|---------|-----------|------------|
| **Qualidade** | Robótica | Natural, humana |
| **Português BR** | Aceitável | Excelente |
| **Custo** | Grátis (com credenciais) | ~$0.30/1000 chars |
| **Setup** | Credenciais GCP complexas | API key simples |
| **Confiabilidade** | Requer auth complexa | Plug-and-play |

## Configuração Adicional (Opcional)

### Escolher Voz Específica

No arquivo `.env` ou Render Environment:

```bash
# Vozes disponíveis (português BR):
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB  # Adam (masculina, versátil)
# ou
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (feminina)
```

### Monitorar Uso

Acesse: https://elevenlabs.io/usage

- Veja caracteres consumidos
- Acompanhe gastos
- Configure alertas de limite

## Troubleshooting

### ❌ "TTS Provider selecionado: google"

**Causa**: API key não configurada ou não carregada

**Solução**:
1. Verifique se a variável foi salva no Render
2. Confirme que o worker foi reiniciado
3. Veja os logs de startup para erros

### ❌ "ElevenLabs falhou: 401 Unauthorized"

**Causa**: API key inválida ou expirada

**Solução**:
1. Gere nova API key no ElevenLabs
2. Atualize no Render
3. Reinicie o worker

### ❌ "ElevenLabs falhou: 429 Too Many Requests"

**Causa**: Limite de free tier excedido (10k chars/mês)

**Solução**:
1. Upgrade para plano pago (~$5/mês)
2. Ou aguarde reset mensal
3. Ou configure fallback para Google TTS temporariamente

## Tempo de Geração Esperado

Com ElevenLabs configurado:

| Componente | Tempo | Observação |
|------------|-------|------------|
| **Análise de briefing** | ~15s | LangGraph multi-agent |
| **Geração de opções** | ~15s | 4 opções criadas |
| **Aprimoramento de script** | ~5s | OpenAI GPT |
| **TTS (ElevenLabs)** | ~10-20s | Depende do tamanho |
| **Geração de slides** | ~5s | PIL/Pillow |
| **Renderização final** | ~30-60s | MoviePy |
| **TOTAL** | **~1-2 min** | ✅ Muito mais rápido! |

## Próximos Passos

1. ✅ Adicionar `ELEVENLABS_API_KEY` no Render
2. ✅ Aguardar worker reiniciar
3. ✅ Criar novo briefing de teste
4. ✅ Verificar logs para confirmar ElevenLabs sendo usado
5. ✅ Testar qualidade do áudio gerado

---

**Dúvidas?** Verifique: https://docs.elevenlabs.io/api-reference/
