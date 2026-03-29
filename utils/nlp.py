"""
utils/nlp.py
• Summarisation  : facebook/bart-large-cnn  (direct model.generate, no pipeline)
• Simplification : deterministic synonym-replacement  (no hallucination)
• Spell-fix      : pyspellchecker (lightweight, pure-Python)
"""
from __future__ import annotations
import re
import streamlit as st
import torch

# ─── professional → simple synonym map ───────────────────────────────────────
_SYN: dict[str, str] = {
    "utilize":"use","utilise":"use","utilization":"use","utilisation":"use",
    "approximately":"about","approximately":"around","commence":"start",
    "commencement":"start","terminate":"end","termination":"end",
    "assistance":"help","endeavour":"try","endeavor":"try",
    "subsequently":"later","facilitate":"help","demonstrate":"show",
    "indicate":"show","indicates":"shows","indicated":"showed",
    "acquire":"get","acquires":"gets","acquired":"got",
    "significant":"important","significantly":"importantly",
    "sufficient":"enough","sufficiently":"well enough",
    "necessary":"needed","additional":"extra","numerous":"many",
    "individual":"person","individuals":"people",
    "currently":"now","previously":"before","regarding":"about",
    "concerning":"about","implement":"use","implemented":"used",
    "implementation":"use","constructed":"built","elevated":"raised",
    "diminished":"reduced","extraordinary":"amazing",
    "furthermore":"also","however":"but","therefore":"so",
    "consequently":"so","nevertheless":"still",
    "proficient":"skilled","administer":"manage","administered":"managed",
    "comprehend":"understand","elucidate":"explain","initiate":"begin",
    "initiated":"began","culminate":"end","unprecedented":"new",
    "accomplished":"done","substantial":"large","substantially":"greatly",
    "obtained":"got","appointed":"chosen","criticised":"blamed",
    "criticized":"blamed","conducted":"held","established":"set up",
    "associated":"linked","attributed":"credited","prominent":"well-known",
    "extensive":"wide","controversial":"debated","predominantly":"mostly",
    "nonetheless":"still","whereas":"while","whereby":"by which",
    "henceforth":"from now","heretofore":"until now","thereof":"of it",
    "therein":"in it","thereafter":"after that","thereby":"by that",
    "herein":"in this","aforementioned":"mentioned above",
    "aforementioned":"said","pertaining":"relating","pertain":"relate",
    "provisions":"rules","provision":"rule","legislation":"law",
    "legislative":"legal","jurisdiction":"authority","pursuant":"under",
    "notwithstanding":"despite","irrespective":"regardless",
    "ascertain":"find out","ascertained":"found out",
    "disseminate":"spread","disseminated":"spread",
    "proliferate":"spread","proliferation":"spread",
    "mitigate":"reduce","mitigation":"reduction","mitigated":"reduced",
    "exacerbate":"worsen","exacerbated":"worsened",
    "ameliorate":"improve","ameliorated":"improved",
    "perpetuate":"continue","perpetuated":"continued",
    "encompass":"include","encompasses":"includes","encompassed":"included",
    "predominantly":"mainly","predominantly":"mostly",
    "endeavoured":"tried","endeavored":"tried",
    "ramifications":"effects","ramification":"effect",
    "manifestation":"sign","manifestations":"signs",
    "corroborate":"confirm","corroborated":"confirmed",
    "substantiate":"prove","substantiated":"proved",
    "discrepancy":"difference","discrepancies":"differences",
    "anticipate":"expect","anticipated":"expected",
    "formulate":"create","formulated":"created",
    "delineate":"outline","delineated":"outlined",
    "collaborate":"work together","collaborated":"worked together",
    "collaboration":"teamwork","consolidate":"combine",
    "consolidated":"combined","consolidation":"combination",
    "ascertain":"find","multifaceted":"complex",
    "holistic":"complete","comprehensive":"complete",
    "paramount":"most important","pivotal":"key","crucial":"key",
    "imperative":"must","mandatory":"required","obligatory":"required",
    "voluntary":"optional","discretionary":"optional",
    "subsequent":"next","prior":"earlier","prior to":"before",
    "in order to":"to","in the event that":"if","with regard to":"about",
    "in relation to":"about","in accordance with":"following",
    "on account of":"because","for the purpose of":"to",
    "in the absence of":"without","in addition to":"besides",
    "in spite of":"despite","by means of":"by","as a result of":"because of",
    "with the exception of":"except","in the vicinity of":"near",
}

# ─── model loader ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_models():
    from transformers import BartTokenizer, BartForConditionalGeneration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    name = "facebook/bart-large-cnn"
    tok   = BartTokenizer.from_pretrained(name)
    model = BartForConditionalGeneration.from_pretrained(name).to(device)
    model.eval()
    return tok, model, device

# ─── BART summarise ───────────────────────────────────────────────────────────
def _bart(text: str, tok, model, device, min_l: int, max_l: int) -> str:
    enc = tok(text, return_tensors="pt", max_length=1024, truncation=True).to(device)
    with torch.no_grad():
        ids = model.generate(
            **enc,
            min_length=min_l, max_length=max_l,
            num_beams=4, early_stopping=True,
            no_repeat_ngram_size=3, length_penalty=1.2,
            forced_bos_token_id=tok.bos_token_id,
        )
    return tok.decode(ids[0], skip_special_tokens=True).strip()

# ─── chunking ─────────────────────────────────────────────────────────────────
def _chunks(text: str, max_chars: int = 900) -> list[str]:
    words = text.split()
    out, cur, n = [], [], 0
    for w in words:
        if n + len(w) + 1 <= max_chars:
            cur.append(w); n += len(w) + 1
        else:
            if cur: out.append(" ".join(cur))
            cur, n = [w], len(w)
    if cur: out.append(" ".join(cur))
    return [c for c in out if len(c.split()) >= 20]

# ─── spell correction (pyspellchecker only on clear errors) ───────────────────
def _spell_fix(text: str) -> str:
    """
    Only corrects clearly misspelled common words.
    Skips proper nouns (capitalised), short words, and names.
    """
    try:
        from spellchecker import SpellChecker
        spell = SpellChecker()
        tokens = text.split()
        fixed  = []
        for tok in tokens:
            # skip proper nouns, URLs, numbers, short words
            core = re.sub(r"[^a-zA-Z]", "", tok)
            if (not core or len(core) < 5 or core[0].isupper()
                    or core.lower() == core.lower()):
                # only fix all-lowercase tokens that look wrong
                if core and core.islower() and len(core) >= 5:
                    if spell.unknown([core]):
                        candidate = spell.correction(core)
                        if candidate and candidate != core:
                            tok = tok.replace(core, candidate)
            fixed.append(tok)
        return " ".join(fixed)
    except Exception:
        return text

# ─── PUBLIC: professional summary ─────────────────────────────────────────────
def generate_professional(text: str, tok, model, device,
                           min_len: int, max_len: int) -> str:
    cks = _chunks(text)
    if not cks:
        return text[:600]

    n = max(len(cks), 1)
    parts = [_bart(c, tok, model, device,
                   max(10, min_len // n),
                   max(40, max_len // n + 40))
             for c in cks]
    combined = " ".join(parts)
    if len(combined.split()) > max_len:
        combined = _bart(combined, tok, model, device, min_len, max_len)
    return combined          # ← no spell fix on professional (names intact)

# ─── PUBLIC: simplified summary (deterministic, English-only) ─────────────────
def generate_simplified(professional: str) -> str:
    """
    Replace complex words with simple synonyms.
    Keeps names, numbers, and sentence structure intact.
    No ML model → zero hallucination.
    """
    result = professional

    # Replace multi-word phrases first (longest match first)
    phrases = sorted(_SYN.keys(), key=len, reverse=True)
    for phrase in phrases:
        simple = _SYN[phrase]
        # case-insensitive whole-word replacement
        result = re.sub(
            r'\b' + re.escape(phrase) + r'\b',
            simple, result, flags=re.IGNORECASE
        )

    # Fix capitalisation that may have been broken at sentence start
    result = re.sub(
        r'(?<=[.!?]\s)([a-z])',
        lambda m: m.group(1).upper(),
        result
    )
    # Fix first letter of whole text
    if result:
        result = result[0].upper() + result[1:]

    return result

# ─── Word-change map ──────────────────────────────────────────────────────────
def compute_word_changes(professional: str, simplified: str) -> list[dict]:
    pro_lower = professional.lower()
    changes   = []
    seen      = set()
    for phrase in sorted(_SYN.keys(), key=len, reverse=True):
        if phrase in seen:
            continue
        if re.search(r'\b' + re.escape(phrase) + r'\b', pro_lower):
            simple = _SYN[phrase]
            changes.append({
                "professional": phrase,
                "simplified":   simple,
                "meaning":      _meaning(phrase, simple),
            })
            seen.add(phrase)
        if len(changes) >= 30:
            break
    return changes

def _meaning(pro: str, sim: str) -> str:
    M = {
        "utilize":"to make use of something","approximately":"close to a number",
        "commence":"to begin or start","terminate":"to bring to an end",
        "assistance":"support or help given","endeavour":"an attempt or effort",
        "subsequently":"happening after something","facilitate":"to make easier",
        "demonstrate":"to show clearly","indicate":"to point out or signal",
        "acquire":"to get or obtain","significant":"very important or large",
        "sufficient":"as much as is needed","necessary":"something required",
        "additional":"something added on top","numerous":"a large number of",
        "individual":"a single person","currently":"at this present time",
        "previously":"at an earlier time","regarding":"on the subject of",
        "implement":"to put a plan into action","comprehensive":"covering everything",
        "paramount":"of greatest importance","pivotal":"very important, central",
        "crucial":"extremely important","collaborate":"to work together",
        "consolidate":"to combine into one","mitigate":"to reduce harm or severity",
        "exacerbate":"to make something worse","proliferate":"to spread rapidly",
        "disseminate":"to share information widely","ascertain":"to find out for sure",
        "corroborate":"to confirm something is true","substantial":"large in size or amount",
        "prominent":"well known and respected","controversial":"causing strong disagreement",
        "unprecedented":"never happened before","multifaceted":"having many aspects",
    }
    return M.get(pro, f"simpler word for '{pro}'")

# ─── Metrics ─────────────────────────────────────────────────────────────────
def compute_metrics(original: str, professional: str, simplified: str) -> dict:
    from difflib import SequenceMatcher
    def _sim(a, b):
        return SequenceMatcher(None, a.lower()[:3000], b.lower()[:3000]).ratio()

    ow = len(original.split())
    pw = len(professional.split())
    sw = len(simplified.split())
    compression  = round((1 - pw / max(ow, 1)) * 100, 1)
    retention    = round(_sim(original, professional) * 100, 1)
    # simplicity = % of words that changed
    pro_words = set(re.findall(r'\b[a-z]{4,}\b', professional.lower()))
    sim_words = set(re.findall(r'\b[a-z]{4,}\b', simplified.lower()))
    changed   = len(pro_words - sim_words)
    simplicity = round(min(changed / max(len(pro_words), 1) * 100, 100), 1)
    readability = _flesch(simplified)
    overall = round(retention * 0.4 + simplicity * 0.3 + min(compression, 80) * 0.3, 1)
    return dict(
        compression_pct=compression, retention_score=retention,
        simplicity_score=simplicity, readability=readability,
        overall_accuracy=min(overall, 99.0),
        orig_words=ow, pro_words=pw, sim_words=sw,
        pro_read_time=max(1, round(pw / 200)),
        sim_read_time=max(1, round(sw / 200)),
        words_changed=changed,
    )

def _flesch(text: str) -> float:
    sents = max(1, len(re.findall(r'[.!?]+', text)))
    words = text.split(); nw = max(1, len(words))
    sylls = sum(max(1, len(re.findall(r'[aeiou]+', w.lower()))) for w in words)
    return round(max(0, min(100, 206.835 - 1.015*(nw/sents) - 84.6*(sylls/nw))), 1)
