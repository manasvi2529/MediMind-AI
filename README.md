# MediMind AI

Voice-first health assistant in pure Python (Streamlit). People who cannot read or write can **speak** their problem
in 10 Indian languages and **hear** the answer. Also: symptom checker, vitals/BMI checker, first-aid guides,
interactive map for nearest hospitals and blood banks with live bed and blood vacancies, and automatic emergency detection (112 / 108).

## Run locally
```
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  (Linux/Mac: source .venv/bin/activate)
python -m pip install -r requirements.txt
set OPENROUTER_API_KEY=your-key   # PowerShell: $env:OPENROUTER_API_KEY="your-key"
python -m streamlit run app.py
```
Without an API key the app still works with a simple built-in answer engine.

## Deploy (free): Streamlit Community Cloud
Push to GitHub, create the app from `app.py`, and add `OPENROUTER_API_KEY` under Settings > Secrets.
The browser microphone needs HTTPS, which Streamlit Cloud provides (localhost also works).

## Notes
- Speech-to-text (`SpeechRecognition` + Google web recognizer) and text-to-speech (`gTTS`) need internet.
- Do not enter private patient data. Educational only, not a medical device.
- Your original CSV machine-learning app: keep it as `legacy_ml_app.py` and run it separately.
