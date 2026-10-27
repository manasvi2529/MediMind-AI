"""Voice in / voice out, pure Python.
Speech-to-text: SpeechRecognition (Google web recognizer, needs internet).
Text-to-speech: gTTS (returns MP3 bytes).
"""
import io
import re

import speech_recognition as sr
from gtts import gTTS

# label shown to user -> (speech-recognition code, gTTS code)
LANGUAGES = {
    "हिन्दी (Hindi)": ("hi-IN", "hi"),
    "English (India)": ("en-IN", "en"),
    "मराठी (Marathi)": ("mr-IN", "mr"),
    "ગુજરાતી (Gujarati)": ("gu-IN", "gu"),
    "বাংলা (Bengali)": ("bn-IN", "bn"),
    "தமிழ் (Tamil)": ("ta-IN", "ta"),
    "తెలుగు (Telugu)": ("te-IN", "te"),
    "ಕನ್ನಡ (Kannada)": ("kn-IN", "kn"),
    "ਪੰਜਾਬੀ (Punjabi)": ("pa-IN", "pa"),
    "മലയാളം (Malayalam)": ("ml-IN", "ml"),
}

GREETING = {
    "en": "Hello! I am MediMind. Tap the microphone, tell me your health problem, then tap stop. I will answer by voice.",
    "hi": "नमस्ते! मैं मेडीमाइंड हूँ। माइक का बटन दबाइए, अपनी तकलीफ बताइए, फिर रोकने का बटन दबाइए। मैं आवाज़ में जवाब दूँगा।",
    "mr": "नमस्कार! मी मेडीमाइंड आहे. माईकचे बटण दाबा, तुमचा त्रास सांगा, मग थांबवा. मी आवाजात उत्तर देईन.",
    "bn": "নমস্কার! আমি মেডিমাইন্ড। মাইক্রোফোনের বোতাম চাপুন, আপনার সমস্যা বলুন, তারপর থামান। আমি কথায় উত্তর দেব।",
    "ta": "வணக்கம்! நான் மெடிமைண்ட். மைக் பொத்தானை அழுத்தி உங்கள் பிரச்சனையைச் சொல்லுங்கள், பிறகு நிறுத்துங்கள். நான் குரலில் பதில் சொல்வேன்.",
    "te": "నమస్కారం! నేను మెడిమైండ్. మైక్ బటన్ నొక్కి మీ సమస్య చెప్పండి, తర్వాత ఆపండి. నేను గొంతుతో సమాధానం ఇస్తాను.",
}

NOT_HEARD = {
    "en": "I could not hear you. Please speak again, a little louder.",
    "hi": "मुझे सुनाई नहीं दिया। कृपया थोड़ा ज़ोर से फिर से बोलिए।",
    "mr": "मला ऐकू आले नाही. कृपया थोडे मोठ्याने पुन्हा बोला.",
    "bn": "আমি শুনতে পাইনি। একটু জোরে আবার বলুন।",
    "ta": "எனக்குக் கேட்கவில்லை. கொஞ்சம் சத்தமாக மீண்டும் சொல்லுங்கள்.",
    "te": "నాకు వినిపించలేదు. దయచేసి కొంచెం గట్టిగా మళ్ళీ చెప్పండి.",
}


class VoiceError(RuntimeError):
    """Speech service unreachable (usually no internet)."""


def transcribe(wav_bytes: bytes, sr_code: str):
    """Return recognised text, or None if nothing intelligible was heard."""
    rec = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav_bytes)) as src:
        audio = rec.record(src)
    try:
        return rec.recognize_google(audio, language=sr_code).strip() or None
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        raise VoiceError(str(e)) from e


def _speakable(text: str) -> str:
    text = re.sub(r"[*#_`>~|]+", " ", text)
    text = re.sub(r"https?://\S+", "", text)
    return re.sub(r"\s+", " ", text).strip()[:1500]


def speak(text: str, gtts_code: str):
    """Return MP3 bytes of `text` spoken in the language, or None on failure."""
    text = _speakable(text)
    if not text:
        return None
    buf = io.BytesIO()
    try:
        gTTS(text=text, lang=gtts_code, tld="co.in" if gtts_code == "en" else "com").write_to_fp(buf)
    except Exception as e:  # offline or unsupported language
        print("TTS error:", repr(e))
        return None
    return buf.getvalue()
