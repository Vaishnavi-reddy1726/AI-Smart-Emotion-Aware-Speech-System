const input = document.getElementById("inputText");
const button = document.getElementById("generateBtn");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");
const results = document.getElementById("results");
const emotionBadge = document.getElementById("emotionBadge");
const intensityValue = document.getElementById("intensityValue");
const intensityFill = document.getElementById("intensityFill");
const providerBadge = document.getElementById("providerBadge");
const audioPlayer = document.getElementById("audioPlayer");

function setLoading(isLoading) {
  button.disabled = isLoading;
  loading.classList.toggle("hidden", !isLoading);
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function updateEmotionStyle(emotion) {
  const map = {
    joy: { bg: "rgba(97, 239, 176, 0.16)", border: "rgba(97, 239, 176, 0.55)", text: "#adffd8" },
    sadness: { bg: "rgba(133, 166, 255, 0.16)", border: "rgba(133, 166, 255, 0.55)", text: "#d5deff" },
    anger: { bg: "rgba(255, 113, 133, 0.16)", border: "rgba(255, 113, 133, 0.55)", text: "#ffc4d0" },
    neutral: { bg: "rgba(172, 184, 210, 0.16)", border: "rgba(172, 184, 210, 0.55)", text: "#e5ecff" },
    surprise: { bg: "rgba(170, 129, 255, 0.16)", border: "rgba(170, 129, 255, 0.55)", text: "#e9dbff" },
  };
  const style = map[emotion] || map.neutral;
  emotionBadge.style.background = style.bg;
  emotionBadge.style.borderColor = style.border;
  emotionBadge.style.color = style.text;
}

async function generateVoice() {
  clearError();
  const text = input.value.trim();
  if (!text) {
    showError("Please enter some text before generating voice.");
    return;
  }

  setLoading(true);
  results.classList.add("hidden");

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || "Failed to generate voice.");
    }

    const emotion = (data.emotion || "neutral").toLowerCase();
    const intensity = Number(data.intensity || 0);
    const percent = Math.round(Math.max(0, Math.min(1, intensity)) * 100);
    const audioUrl = data.audio_url;

    emotionBadge.textContent = emotion;
    updateEmotionStyle(emotion);
    intensityValue.textContent = `${percent}%`;
    intensityFill.style.width = `${percent}%`;
    providerBadge.textContent = data.provider || "pyttsx3";

    audioPlayer.src = `${audioUrl}?t=${Date.now()}`;
    results.classList.remove("hidden");

    await audioPlayer.play().catch(() => {
      // Autoplay can fail due to browser policy; controls remain available.
    });
  } catch (error) {
    showError(error.message || "Unexpected error occurred.");
  } finally {
    setLoading(false);
  }
}

button.addEventListener("click", generateVoice);

input.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    generateVoice();
  }
});
