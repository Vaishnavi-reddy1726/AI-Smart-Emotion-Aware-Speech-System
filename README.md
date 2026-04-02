AI-Smart-Emotion-Aware-Speech-System

Project Overview

I built this as a full-stack web app that converts plain text into expressive, emotion-aware speech.  
The app detects emotion and intensity from text, maps those signals to voice behavior, generates audio, and plays it instantly in the browser.

Main Features

- Emotion-aware text-to-speech from a clean web interface
- Transformer model for emotion detection: `j-hartmann/emotion-english-distilroberta-base`
- Target emotions:
  - `joy`
  - `anger`
  - `sadness`
  - `neutral`
  - `surprise`
- Intensity score from normalized probabilities in the range `0.0` to `1.0`
- Two TTS modes:
  - Default offline mode with `pyttsx3`
  - Optional premium mode with ElevenLabs API
- Auto-play generated audio in browser
- Frontend includes textarea, loading state, emotion badge, intensity meter, and audio player
- Modular FastAPI backend with static audio serving

Project Structure

```text
empathy-engine/
|
|- backend/
|  |- main.py
|  |- emotion.py
|  |- tts.py
|  |- config.py
|  |- requirements.txt
|  |- .env.example
|  |- audio/               generated audio files
|
|- frontend/
|  |- index.html
|  |- style.css
|  |- script.js
|
|- README.md
```

How It Works

1. User enters text in the web app.
2. Frontend sends `POST /generate`.
3. Backend runs transformer inference to detect emotion and intensity.
4. Voice engine maps emotion plus intensity to expressive synthesis settings.
5. Audio is generated with ElevenLabs if API key exists, otherwise with pyttsx3.
6. API returns emotion, intensity, provider, and audio URL.
7. Frontend updates UI and starts playback.

Emotion to Voice Mapping

- Joy
  - faster speaking rate
  - higher pitch
  - energetic style
- Sadness
  - slower rate
  - lower pitch
  - softer volume
- Anger
  - slightly faster rate
  - sharper style
  - higher volume
- Neutral
  - balanced delivery
- Surprise
  - dynamic style with stronger pitch lift

Intensity scaling makes output more expressive for stronger emotional confidence.

API Usage

Endpoint: `POST /generate`

Request body
```json
{
  "text": "I cannot believe we finally did it!"
}
```

Response body
```json
{
  "emotion": "joy",
  "intensity": 0.8731,
  "audio_url": "/audio/abc123def4.wav",
  "provider": "pyttsx3"
}
```

Notes
- `audio_url` is `.wav` in offline mode
- `audio_url` is `.mp3` in ElevenLabs mode
- `provider` shows which TTS engine produced the file

Installation and Run

1) Clone and enter project
```bash
git clone <your-repo-url>
cd empathy-engine
```

2) Create virtual environment
```bash
python -m venv .venv
```

3) Activate virtual environment

Windows PowerShell
```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux
```bash
source .venv/bin/activate
```

4) Install backend dependencies
```bash
pip install -r backend/requirements.txt
```

5) Create environment file
```bash
copy backend\.env.example backend\.env
```

6) Start FastAPI server
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

7) Open in browser

[http://localhost:8000](http://localhost:8000)

Enable ElevenLabs Premium Mode
------------------------------
Set this in `backend/.env`:
```env
ELEVENLABS_API_KEY=your_api_key_here
```

Optional custom voice settings:
```env
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```

When API key is present, backend uses ElevenLabs automatically.  
When API key is missing, backend falls back to offline pyttsx3 automatically.

Demo Flow
---------
1. Open `http://localhost:8000`
2. Test sample lines for joy, sadness, anger, neutral, and surprise
3. Click Generate Voice
4. Observe emotion badge and intensity meter
5. Listen to voice variation by emotion and intensity

Deployment Notes
----------------
- Deploy on any Python-compatible platform such as Render, Railway, Fly.io, Azure, AWS, or GCP
- Configure environment variables in deployment settings
- Use ElevenLabs key in production for best voice quality
- Persist `backend/audio` if generated files should survive restarts

Tech Stack
----------
- Backend: Python, FastAPI
- NLP: Hugging Face Transformers
- TTS: pyttsx3 offline, ElevenLabs optional
- Frontend: HTML, CSS, Vanilla JavaScript

