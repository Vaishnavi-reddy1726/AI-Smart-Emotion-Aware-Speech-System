from typing import Dict, Tuple

from transformers import pipeline

# Load once at startup for fast repeated inference.
_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True,
)

TARGET_EMOTIONS = ("joy", "anger", "sadness", "neutral", "surprise")
ALIASES = {
    "fear": "sadness",
    "disgust": "anger",
}


def _normalize_scores(raw_scores: Dict[str, float]) -> Dict[str, float]:
    normalized = {emotion: 0.0 for emotion in TARGET_EMOTIONS}

    for label, score in raw_scores.items():
        label_lower = label.lower()
        mapped = ALIASES.get(label_lower, label_lower)
        if mapped in normalized:
            normalized[mapped] += float(score)

    total = sum(normalized.values())
    if total <= 0:
        return normalized

    return {k: v / total for k, v in normalized.items()}


def detect_emotion(text: str) -> Tuple[str, float, Dict[str, float]]:
    """
    Returns:
      - dominant emotion among requested target emotions
      - intensity score (0..1)
      - normalized probability map for target emotions
    """
    results = _classifier(text, truncation=True, max_length=512)[0]
    score_map = {item["label"].lower(): float(item["score"]) for item in results}
    normalized = _normalize_scores(score_map)

    emotion = max(normalized, key=normalized.get)
    intensity = max(0.0, min(1.0, normalized[emotion]))
    return emotion, intensity, normalized
