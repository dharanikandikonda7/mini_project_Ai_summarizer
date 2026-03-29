# 🧠 SummarizeAI Pro

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Features
- **Dual summaries**: Professional (BART) + Simplified (deterministic synonym replacement)
- **Zero hallucination**: Simplified version uses a curated synonym map — never invents words or mixes languages
- **Word Change Map**: Table showing every professional term → simple word + plain meaning
- **5 Accuracy Rings**: Overall, Retention, Simplicity, Compression, Flesch Readability
- **8 Stat Cards**: Word counts, read times, compression %, words simplified
- **100+ Language Translation**: Google Translate via deep-translator (no API key)
- **Audio Playback**: gTTS text-to-speech, uses translated text automatically
- **3D Glassmorphism UI**: Dark purple/teal theme, Orbitron font, animated gradient rings

## Project Structure
```
summarizer_pro/
├── app.py                    # Entry point
├── requirements.txt
├── .streamlit/config.toml    # Dark theme
├── app/
│   ├── ui.py                 # All 5 tabs
│   └── styles.py             # 3D CSS
└── utils/
    ├── nlp.py                # BART + synonym simplifier + metrics
    ├── extractor.py          # URL / file text extraction
    ├── translator.py         # 100+ languages
    └── audio.py              # gTTS TTS
```

## Why no T5 for simplification?
T5 was causing **hallucination** — generating random words, mixing languages,
and changing names (e.g. "Modi" → "Lodi"). The deterministic synonym-map approach
is 100% accurate: it only replaces known complex words with their simpler equivalents
while leaving names, numbers, and sentence structure intact.
