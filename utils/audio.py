"""utils/audio.py — gTTS text-to-speech"""
from __future__ import annotations
import io

_REMAP = {"zh-cn":"zh-CN","zh-tw":"zh-TW","ceb":"en","hmn":"en","haw":"en"}

def text_to_speech(text: str, lang_code: str = "en") -> bytes | None:
    if not text.strip():
        return None
    lc = _REMAP.get(lang_code, lang_code)
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text[:3000], lang=lc, slow=False).write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        return None
    except Exception:
        try:
            from gtts import gTTS
            buf = io.BytesIO()
            gTTS(text=text[:3000], lang="en", slow=False).write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception:
            return None
