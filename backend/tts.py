from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Dict, Tuple

import pyttsx3
import requests

from .config import (
    AUDIO_DIR,
    ELEVENLABS_API_KEY,
    ELEVENLABS_MODEL_ID,
    ELEVENLABS_VOICE_ID,
)


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _emotion_style(emotion: str, intensity: float) -> Dict[str, float]:
    i = _clamp(intensity, 0.0, 1.0)

    # These values are tuned to be noticeably expressive.
    if emotion == "joy":
        return {
            "rate": 185 + (i * 65),
            "volume": 0.86 + (i * 0.14),
            "pitch": 52 + (i * 26),
            "stability": 0.35 - (i * 0.20),
            "style": 0.45 + (i * 0.50),
            "similarity_boost": 0.75,
        }
    if emotion == "sadness":
        return {
            "rate": 160 - (i * 55),
            "volume": 0.78 - (i * 0.18),
            "pitch": 38 - (i * 12),
            "stability": 0.75 + (i * 0.20),
            "style": 0.20 + (i * 0.25),
            "similarity_boost": 0.78,
        }
    if emotion == "anger":
        return {
            "rate": 182 + (i * 45),
            "volume": 0.92 + (i * 0.08),
            "pitch": 48 + (i * 12),
            "stability": 0.40 - (i * 0.15),
            "style": 0.55 + (i * 0.40),
            "similarity_boost": 0.70,
        }
    if emotion == "surprise":
        return {
            "rate": 190 + (i * 55),
            "volume": 0.88 + (i * 0.12),
            "pitch": 56 + (i * 30),
            "stability": 0.30 - (i * 0.15),
            "style": 0.60 + (i * 0.35),
            "similarity_boost": 0.72,
        }

    # neutral
    return {
        "rate": 180 + (i * 15),
        "volume": 0.90,
        "pitch": 45 + (i * 6),
        "stability": 0.62,
        "style": 0.20 + (i * 0.15),
        "similarity_boost": 0.80,
    }


def _build_ssml(text: str, emotion: str, intensity: float) -> str:
    style = _emotion_style(emotion, intensity)
    rate_percent = int(style["rate"] - 180)
    pitch = int(style["pitch"])
    volume_pct = int(style["volume"] * 100)
    safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        "<speak>"
        f"<prosody rate='{rate_percent:+d}%' pitch='{pitch:+d}%' volume='{volume_pct}'>"
        f"{safe_text}"
        "</prosody>"
        "</speak>"
    )


def _generate_with_pyttsx3(text: str, emotion: str, intensity: float, output_path: Path) -> None:
    style = _emotion_style(emotion, intensity)
    engine = pyttsx3.init()
    engine.setProperty("rate", int(style["rate"]))
    engine.setProperty("volume", _clamp(style["volume"], 0.0, 1.0))

    # Some drivers ignore pitch; no-op on unsupported platforms.
    try:
        engine.setProperty("pitch", int(style["pitch"]))
    except Exception:
        pass

    if emotion == "sadness":
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)

    engine.save_to_file(text, str(output_path))
    engine.runAndWait()
    engine.stop()


def _generate_with_elevenlabs(text: str, emotion: str, intensity: float, output_path: Path) -> None:
    style = _emotion_style(emotion, intensity)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "model_id": ELEVENLABS_MODEL_ID,
        "text": text,
        "voice_settings": {
            "stability": _clamp(style["stability"], 0.0, 1.0),
            "similarity_boost": _clamp(style["similarity_boost"], 0.0, 1.0),
            "style": _clamp(style["style"], 0.0, 1.0),
            "use_speaker_boost": True,
        },
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def generate_voice(text: str, emotion: str, intensity: float) -> Tuple[str, str]:
    """
    Returns:
      (relative_url, provider_mode)
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    uid = uuid.uuid4().hex[:10]

    if ELEVENLABS_API_KEY:
        output_path = AUDIO_DIR / f"{uid}.mp3"
        _generate_with_elevenlabs(text, emotion, intensity, output_path)
        return f"/audio/{output_path.name}", "elevenlabs"

    output_path = AUDIO_DIR / f"{uid}.wav"
    _generate_with_pyttsx3(text, emotion, intensity, output_path)
    return f"/audio/{output_path.name}", "pyttsx3"
