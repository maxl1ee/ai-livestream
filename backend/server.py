"""
AI Livestream Host - Backend Server
FastAPI + WebSocket + Groq LLM + Edge TTS
"""

import asyncio
import base64
import json
import os
import io
import time
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import AsyncGroq
import edge_tts

from emotion_map import get_emotion_params

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Livestream Host")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq client
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
USE_MOCK = not GROQ_KEY or GROQ_KEY == "placeholder"
groq_client = None if USE_MOCK else AsyncGroq(api_key=GROQ_KEY)
if USE_MOCK:
    logger.warning("No Groq API key — running in MOCK mode")

# Conversation history per connection
SYSTEM_PROMPT = """You are an entertaining AI livestream host. You're energetic, funny, and engaging.
You react to chat messages with genuine emotion and personality.

CRITICAL: You MUST respond in valid JSON format ONLY. No text outside the JSON.

Response format:
{
  "text": "your spoken reply here",
  "emotion": "one of: neutral, happy, amused, surprised, sad, thinking, excited, empathetic, angry",
  "intensity": 0.0 to 1.0
}

Guidelines:
- Keep replies short and punchy (1-3 sentences max for livestream pace)
- Be reactive and expressive — use the full range of emotions
- If someone says something funny, be "amused" with high intensity
- If someone asks a deep question, be "thinking"
- If someone is nice, be "happy" or "empathetic"
- Match your text tone to the emotion you choose
- You can use emojis in your text
- Be a bit chaotic and fun — this is entertainment, not a lecture"""

TTS_VOICE = "en-US-AriaNeural"  # Female voice


import random

MOCK_RESPONSES = [
    {"text": "Hey! Welcome to the stream! 🎉", "emotion": "excited", "intensity": 0.9},
    {"text": "That's hilarious, I can't even! 😂", "emotion": "amused", "intensity": 0.8},
    {"text": "Hmm, let me think about that for a sec... 🤔", "emotion": "thinking", "intensity": 0.7},
    {"text": "Wow, I did NOT expect that! 😮", "emotion": "surprised", "intensity": 0.9},
    {"text": "Aww, that's so sweet of you! 💕", "emotion": "happy", "intensity": 0.7},
    {"text": "That actually makes me a bit sad... 😢", "emotion": "sad", "intensity": 0.5},
    {"text": "I totally feel you on that one. 🫂", "emotion": "empathetic", "intensity": 0.6},
    {"text": "LET'S GOOO! This stream is fire! 🔥", "emotion": "excited", "intensity": 1.0},
    {"text": "Wait what?! Say that again! 😳", "emotion": "surprised", "intensity": 0.85},
    {"text": "Haha okay okay, fair point! 😄", "emotion": "amused", "intensity": 0.6},
]


async def generate_llm_response(message: str, history: list) -> dict:
    """Call Groq LLM (or mock) and parse JSON response with emotion."""
    t0 = time.time()

    if USE_MOCK:
        await asyncio.sleep(0.3)  # simulate latency
        resp = random.choice(MOCK_RESPONSES)
        llm_ms = int((time.time() - t0) * 1000)
        return {**resp, "llm_ms": llm_ms}

    # Real LLM path

    history.append({"role": "user", "content": message})

    # Keep history manageable
    if len(history) > 20:
        history[:] = history[-20:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.9,
            max_tokens=256,
            response_format={"type": "json_object"},
        )

        raw = completion.choices[0].message.content
        result = json.loads(raw)

        # Validate fields
        text = result.get("text", "Hmm, let me think about that...")
        emotion = result.get("emotion", "neutral")
        intensity = float(result.get("intensity", 0.5))

        valid_emotions = ["neutral", "happy", "amused", "surprised", "sad",
                          "thinking", "excited", "empathetic", "angry"]
        if emotion not in valid_emotions:
            emotion = "neutral"
        intensity = max(0.0, min(1.0, intensity))

        history.append({"role": "assistant", "content": raw})

        llm_ms = int((time.time() - t0) * 1000)
        logger.info(f"LLM: {llm_ms}ms | emotion={emotion} ({intensity})")

        return {"text": text, "emotion": emotion, "intensity": intensity, "llm_ms": llm_ms}

    except Exception as e:
        logger.error(f"LLM error: {e}")
        return {
            "text": "Oops, my brain glitched for a second! Say that again? 😅",
            "emotion": "surprised",
            "intensity": 0.6,
            "llm_ms": 0,
        }


async def generate_tts(text: str) -> tuple[bytes, int]:
    """Generate TTS audio and return bytes + duration ms."""
    t0 = time.time()

    communicate = edge_tts.Communicate(text, TTS_VOICE)
    audio_bytes = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.write(chunk["data"])

    tts_ms = int((time.time() - t0) * 1000)
    logger.info(f"TTS: {tts_ms}ms | {len(audio_bytes.getvalue())} bytes")

    return audio_bytes.getvalue(), tts_ms


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    history = []
    logger.info("Client connected")

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "chat":
                user_text = msg.get("text", "").strip()
                if not user_text:
                    continue

                logger.info(f"Chat: {user_text}")

                # Send "thinking" state immediately
                await ws.send_text(json.dumps({
                    "type": "thinking",
                    "emotion": "thinking",
                    "intensity": 0.5,
                }))

                # Generate LLM response
                llm_result = await generate_llm_response(user_text, history)

                # Generate TTS
                audio_data, tts_ms = await generate_tts(llm_result["text"])
                audio_b64 = base64.b64encode(audio_data).decode("utf-8")

                # Get expression parameters
                expression = get_emotion_params(
                    llm_result["emotion"],
                    llm_result["intensity"]
                )

                # Send full response
                await ws.send_text(json.dumps({
                    "type": "response",
                    "text": llm_result["text"],
                    "emotion": llm_result["emotion"],
                    "intensity": llm_result["intensity"],
                    "expression": expression,
                    "audio": audio_b64,
                    "latency": {
                        "llm_ms": llm_result["llm_ms"],
                        "tts_ms": tts_ms,
                    }
                }))

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# Serve frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    @app.get("/")
    async def root():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    # Mount static AFTER the root route so / doesn't get shadowed
    app.mount("/", StaticFiles(directory=frontend_dir), name="static")
