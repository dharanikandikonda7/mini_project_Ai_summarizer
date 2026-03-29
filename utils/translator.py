"""utils/translator.py — deep-translator, no API key"""
from __future__ import annotations
import re

LANGUAGES: dict[str, str] = {
    "af":"Afrikaans","sq":"Albanian","am":"Amharic","ar":"Arabic",
    "hy":"Armenian","az":"Azerbaijani","eu":"Basque","be":"Belarusian",
    "bn":"Bengali","bs":"Bosnian","bg":"Bulgarian","ca":"Catalan",
    "ceb":"Cebuano","ny":"Chichewa","zh-cn":"Chinese (Simplified)",
    "zh-tw":"Chinese (Traditional)","co":"Corsican","hr":"Croatian",
    "cs":"Czech","da":"Danish","nl":"Dutch","en":"English",
    "eo":"Esperanto","et":"Estonian","tl":"Filipino","fi":"Finnish",
    "fr":"French","fy":"Frisian","gl":"Galician","ka":"Georgian",
    "de":"German","el":"Greek","gu":"Gujarati","ht":"Haitian Creole",
    "ha":"Hausa","haw":"Hawaiian","iw":"Hebrew","hi":"Hindi",
    "hmn":"Hmong","hu":"Hungarian","is":"Icelandic","ig":"Igbo",
    "id":"Indonesian","ga":"Irish","it":"Italian","ja":"Japanese",
    "jw":"Javanese","kn":"Kannada","kk":"Kazakh","km":"Khmer",
    "ko":"Korean","ku":"Kurdish","ky":"Kyrgyz","lo":"Lao","la":"Latin",
    "lv":"Latvian","lt":"Lithuanian","lb":"Luxembourgish","mk":"Macedonian",
    "mg":"Malagasy","ms":"Malay","ml":"Malayalam","mt":"Maltese",
    "mi":"Maori","mr":"Marathi","mn":"Mongolian","my":"Myanmar",
    "ne":"Nepali","no":"Norwegian","ps":"Pashto","fa":"Persian",
    "pl":"Polish","pt":"Portuguese","pa":"Punjabi","ro":"Romanian",
    "ru":"Russian","sm":"Samoan","gd":"Scots Gaelic","sr":"Serbian",
    "st":"Sesotho","sn":"Shona","sd":"Sindhi","si":"Sinhala",
    "sk":"Slovak","sl":"Slovenian","so":"Somali","es":"Spanish",
    "su":"Sundanese","sw":"Swahili","sv":"Swedish","tg":"Tajik",
    "ta":"Tamil","te":"Telugu","th":"Thai","tr":"Turkish",
    "uk":"Ukrainian","ur":"Urdu","uz":"Uzbek","vi":"Vietnamese",
    "cy":"Welsh","xh":"Xhosa","yi":"Yiddish","yo":"Yoruba","zu":"Zulu",
}

_NAME_TO_CODE: dict[str, str] = {v: k for k, v in LANGUAGES.items()}
DISPLAY_NAMES: list[str] = ["— Select language —"] + sorted(LANGUAGES.values())


def translate_text(text: str, target_lang_name: str) -> str:
    if not text.strip() or target_lang_name.startswith("—"):
        return text
    code = _NAME_TO_CODE.get(target_lang_name, "en")
    if code == "en":
        return text
    try:
        from deep_translator import GoogleTranslator
        MAX = 4500
        if len(text) <= MAX:
            return GoogleTranslator(source="auto", target=code).translate(text) or text
        sentences = re.split(r"(?<=[.!?])\s+", text)
        parts, cur = [], ""
        for s in sentences:
            if len(cur) + len(s) + 1 <= MAX:
                cur = (cur + " " + s).strip()
            else:
                if cur:
                    parts.append(GoogleTranslator(source="auto", target=code).translate(cur) or cur)
                cur = s
        if cur:
            parts.append(GoogleTranslator(source="auto", target=code).translate(cur) or cur)
        return " ".join(parts)
    except ImportError:
        return "[Install deep-translator: pip install deep-translator]"
    except Exception as e:
        return f"[Translation error: {e}]"

def lang_code(name: str) -> str:
    return _NAME_TO_CODE.get(name, "en")
