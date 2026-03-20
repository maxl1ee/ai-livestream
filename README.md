# AI Livestream Host with Facial Expressions

An AI-powered livestream host that can talk, express emotions, and interact with audiences in real-time.

## Architecture

```
User Chat Input
    ↓
Groq LLM (Llama 3.3 70B) → JSON {text, emotion, intensity}
    ↓
Edge TTS → Audio stream
    ↓
Frontend: Live2D Avatar + Expression Controller + Lip Sync
    ↓
Browser output (OBS-capturable for streaming)
```

## Quick Start

1. Get a free Groq API key at https://console.groq.com
2. Copy `.env.example` to `.env` and add your key:
   ```
   cp backend/.env.example backend/.env
   ```
3. Run:
   ```
   bash run.sh
   ```
4. Open http://localhost:8000

## Tech Stack

- **Backend**: Python FastAPI + WebSocket
- **LLM**: Groq (Llama 3.3 70B) — ~100ms TTFT
- **TTS**: Edge TTS (free, async)
- **Avatar**: Live2D (pixi-live2d-display)
- **Lip Sync**: Web Audio API amplitude analysis
- **Expressions**: LLM emotion → Live2D parameter mapping with smooth transitions

## No GPU Required

Everything runs on CPU. Live2D is 2D rendering, TTS is cloud-based.
