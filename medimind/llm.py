"""Chat backend: OpenRouter API (OpenAI-compatible) with an offline fallback."""
import os
import re
from . import knowledge

LANGS = {"en": "English", "hi": "Hindi", "mr": "Marathi", "gu": "Gujarati", "bn": "Bengali",
         "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "pa": "Punjabi", "ml": "Malayalam"}

SYSTEM = """You are MediMind, a warm, patient health-information assistant talking BY VOICE with people who may not read or write and may have little medical knowledge.
Reply ONLY in {language}, in very simple everyday words and short sentences, as if speaking to a neighbour.
Your reply will be read aloud: no markdown, no bullet symbols, no emojis, no tables. Maximum 80 words.
You are not a doctor and never diagnose. Say what it could be only as a possibility, give simple home care, and say clearly when to see a doctor.
Ask at most ONE short follow-up question (age, how many days, how bad) when needed.
Do not give prescription medicine doses; for common medicines say to follow the label or ask a pharmacist or health worker.
If there is any emergency sign (chest pain, hard to breathe, stroke signs, heavy bleeding, fainting, fits, severe allergy, poison, thoughts of self-harm), your first sentence must say to call 112 or 108 right now or go to the nearest hospital.
For self-harm: be kind, urge them to talk to someone they trust, and mention Tele-MANAS 14416 (India).
Mention ASHA workers or the nearest PHC / government hospital when it helps."""


def clean(msgs):
    out = []
    for m in (msgs or [])[-12:]:
        if not isinstance(m, dict):
            continue
        role, text = m.get("role"), str(m.get("content", ""))[:1500].strip()
        if role in ("user", "assistant") and text:
            if out and out[-1]["role"] == role:
                out[-1]["content"] += "\n" + text
            else:
                out.append({"role": role, "content": text})
    while out and out[0]["role"] != "user":
        out.pop(0)
    return out


def fallback(text, flags):
    if flags:
        return ("This may be an emergency. Please call 112 or 108 right now, or go to the nearest hospital. "
                "यह आपात स्थिति हो सकती है। अभी 112 या 108 पर फोन करें या नजदीकी अस्पताल जाएं।")
    words = text.lower()
    sel = [s for s in knowledge.SYMPTOMS if s.split()[0] in words]
    res = knowledge.match(sel)["matches"]
    if res:
        top = res[0]
        return (f"This could possibly be {top['name']}. {top['advice']} This is not a diagnosis. "
                "If it gets worse or lasts more than a few days, please see a doctor.")
    return "I could not understand fully. Please tell me your problem, how many days, and your age. For anything serious, see a doctor."


def _normalize_model(model: str) -> str:
    if not model or model in ("claude-sonnet-5-5", "claude-3-5-sonnet", "anthropic/claude-3.5-sonnet"):
        return "anthropic/claude-haiku-5.5"
    if "/" not in model:
        if "claude" in model:
            return f"anthropic/{model}"
        if "gpt" in model:
            return f"openai/{model}"
        if "gemini" in model:
            return f"google/{model}"
    return model


def _call_openrouter(key: str, model: str, system: str, msgs: list) -> str:
    full_msgs = [{"role": "system", "content": system}] + msgs
    try:
        import openai
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "MediMind AI",
            },
        )
        r = client.chat.completions.create(
            model=model,
            messages=full_msgs,
            max_tokens=400,
        )
        return (r.choices[0].message.content or "").strip()
    except ImportError:
        import requests
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "MediMind AI",
        }
        payload = {
            "model": model,
            "messages": full_msgs,
            "max_tokens": 400,
        }
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if not res.ok:
            try:
                err_data = res.json().get("error", {})
                err_msg = err_data.get("message", res.text)
            except Exception:
                err_msg = res.text
            raise RuntimeError(f"OpenRouter API error ({res.status_code}): {err_msg}")
        data = res.json()
        return (data["choices"][0]["message"]["content"] or "").strip()


def reply(msgs, lang, flags):
    key = os.getenv("OPENROUTER_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    last = msgs[-1]["content"]
    if not key:
        return fallback(last, flags), False
    try:
        system = SYSTEM.format(language=LANGS.get((lang or "en")[:2], "English"))
        if flags:
            system += "\nEMERGENCY SIGNS DETECTED (" + ", ".join(flags) + "). Your first sentence must tell them to call 112 or 108 now."
        model = _normalize_model(os.getenv("MEDIMIND_MODEL", "anthropic/claude-haiku-5.5"))
        text = _call_openrouter(key=key, model=model, system=system, msgs=msgs)
        text = re.sub(r"[*#_`>]+", "", text)
        return text, False
    except Exception as e:  # network, quota, bad key...
        print("LLM error:", repr(e))
        return fallback(last, flags), False
