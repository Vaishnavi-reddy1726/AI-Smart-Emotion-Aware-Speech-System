from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import AUDIO_DIR, FRONTEND_DIR
from .emotion import detect_emotion
from .tts import generate_voice


class GenerateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2500)


class GenerateResponse(BaseModel):
    emotion: str
    intensity: float
    audio_url: str
    provider: str


app = FastAPI(
    title="The Empathy Engine API",
    description="Emotion-aware text-to-speech generation service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")


@app.post("/generate", response_model=GenerateResponse)
def generate(payload: GenerateRequest) -> GenerateResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    try:
        emotion, intensity, _ = detect_emotion(text)
        audio_url, provider = generate_voice(text=text, emotion=emotion, intensity=intensity)
    except requests.RequestException as exc:  # type: ignore[name-defined]
        raise HTTPException(
            status_code=502,
            detail=f"TTS provider error: {str(exc)}",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(exc)}") from exc

    return GenerateResponse(
        emotion=emotion,
        intensity=round(float(intensity), 4),
        audio_url=audio_url,
        provider=provider,
    )


# Import placed at end to keep fast startup path straightforward.
import requests  # noqa: E402


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
