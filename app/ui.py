
"""app/ui.py — full Streamlit page"""
from __future__ import annotations
import math, streamlit as st

from app.styles import STYLES
from utils.extractor  import extract_from_url, extract_from_file, word_count
from utils.nlp        import (load_models, generate_professional,
                              generate_simplified, compute_word_changes,
                              compute_metrics)
from utils.translator import DISPLAY_NAMES, translate_text, lang_code
from utils.audio      import text_to_speech


# ── SVG ring ──────────────────────────────────────────────────────────────────
def _ring(val: float, c1: str, c2: str, lbl: str, sz: int = 92) -> str:
    r = (sz - 16) / 2; cx = cy = sz / 2
    circ = 2 * math.pi * r
    dash = circ * max(0, min(val, 100)) / 100; gap = circ - dash
    return f"""
<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="rg{lbl[:4].replace(' ','')}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
    stroke="rgba(255,255,255,0.06)" stroke-width="9"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
    stroke="url(#rg{lbl[:4].replace(' ','')})" stroke-width="9"
    stroke-linecap="round"
    stroke-dasharray="{dash:.2f} {gap:.2f}"
    transform="rotate(-90 {cx} {cy})"/>
  <text x="{cx}" y="{cy-3}" text-anchor="middle"
    font-family="Orbitron,sans-serif" font-size="13" font-weight="700"
    fill="{c2}">{val:.0f}%</text>
  <text x="{cx}" y="{cy+12}" text-anchor="middle"
    font-family="Inter,sans-serif" font-size="6.5" fill="#64748b">{lbl}</text>
</svg>"""


# ── metric card ───────────────────────────────────────────────────────────────
def _mc(val: str, lbl: str) -> str:
    return f'<div class="mc"><div class="mv">{val}</div><div class="ml">{lbl}</div></div>'


# ── word-change table ─────────────────────────────────────────────────────────
def _table(changes: list[dict]) -> str:
    if not changes:
        return "<p style='color:#64748b;font-size:.85rem'>No significant word changes detected.</p>"
    rows = "".join(f"""
      <tr>
        <td><span class="wp">{c['professional']}</span></td>
        <td class="wa">→</td>
        <td><span class="ws">{c['simplified']}</span></td>
        <td class="wm">{c['meaning']}</td>
      </tr>""" for c in changes)
    return f"""
<table class="wt">
  <thead><tr>
    <th>Professional Term</th><th></th>
    <th>Simplified Word</th><th>Plain Meaning</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>"""


# ── main render ───────────────────────────────────────────────────────────────
def render_page() -> None:
    st.markdown(STYLES, unsafe_allow_html=True)
    

    # ── Hero ──────────────────────────────────────────────────────────────────
    import base64

    with open("logo.png", "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <div class="hero">
    
    <img src="data:image/png;base64,{logo_base64}" class="hero-logo-top"/>

    <div class="hero-pill">
        ✦ BART-large-CNN · Deterministic Simplifier · 10+ Languages
    </div>

    <h1>Ai text summarisation using NLP and transformer model</h1>

    <p class="hero-sub">
        Professional & plain-English summaries · Word simplification map ·
        Translation · Audio playback · Accuracy metrics
    </p>

    </div>
    """, unsafe_allow_html=True)

    # ── Input card ────────────────────────────────────────────────────────────
    st.markdown('<div class="gc">', unsafe_allow_html=True)

    mode = st.radio("src", ["✍️  Paste Text", "📄  Upload .txt", "🔗  Article URL"],
                    horizontal=True, label_visibility="collapsed")

    raw_text = ""
    if mode == "✍️  Paste Text":
        raw_text = st.text_area("txt", height=190, label_visibility="collapsed",
            placeholder="Paste any article, essay, research paper, or long text…")

    elif mode == "📄  Upload .txt":
        f = st.file_uploader("file", type=["txt"], label_visibility="collapsed")
        if f:
            raw_text = extract_from_file(f)
            st.success(f"✅ Loaded — {word_count(raw_text):,} words")

    else:
        url = st.text_input("url", label_visibility="collapsed",
            placeholder="https://en.wikipedia.org/wiki/Artificial_intelligence")
        if url.strip():
            with st.spinner("🌐 Fetching…"):
                try:
                    raw_text = extract_from_url(url.strip())
                    st.success(f"✅ Fetched — {word_count(raw_text):,} words")
                except Exception as e:
                    st.error(f"URL fetch failed: {e}")

    st.markdown('<div class="hdiv"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: min_len = st.slider("Min length (words)", 30, 120, 55)
    with c2: max_len = st.slider("Max length (words)", 80, 350, 160)
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("⚡  SUMMARIZE")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Session state init ────────────────────────────────────────────────────
    for k, v in [("pro",""),("sim",""),("raw",""),
                 ("metrics",{}),("changes",[]),
                 ("t_pro",""),("t_sim",""),("t_lang","— Select language —")]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Run ───────────────────────────────────────────────────────────────────
    if run:
        if not raw_text or word_count(raw_text) < 30:
            st.warning("⚠️  Please provide at least **30 words** of text.")
        else:
            with st.spinner("🔄  Loading BART model… (first run ~60 s)"):
                try:
                    tok, mdl, dev = load_models()
                except Exception as e:
                    st.error(f"❌ Model load error: {e}"); st.stop()

            with st.spinner("📋  Generating professional summary…"):
                try:
                    pro = generate_professional(raw_text, tok, mdl, dev, min_len, max_len)
                except Exception as e:
                    st.error(f"❌ Summarisation error: {e}"); st.stop()

            with st.spinner("💡  Building simplified version…"):
                sim = generate_simplified(pro)   # deterministic — no hallucination

            st.session_state.pro     = pro
            st.session_state.sim     = sim
            st.session_state.raw     = raw_text
            st.session_state.metrics = compute_metrics(raw_text, pro, sim)
            st.session_state.changes = compute_word_changes(pro, sim)
            st.session_state.t_pro   = ""
            st.session_state.t_sim   = ""
            st.success("✅  Summaries ready!")

    pro = st.session_state.pro
    sim = st.session_state.sim
    m   = st.session_state.metrics

    # ── Tabs ──────────────────────────────────────────────────────────────────
    t1, t2, t3, t4, t5 = st.tabs([
        "📄  Summaries",
        "🔤  Word Changes",
        "📊  Metrics",
        "🌍  Translate",
        "🔊  Audio",
    ])

    # ═══ TAB 1 — Summaries ═══════════════════════════════════════════════════
    with t1:
        lc1, lc2 = st.columns(2, gap="large")
        with lc1:
            st.markdown('<p class="sl sl-p">📋 Professional Summary</p>', unsafe_allow_html=True)
            if pro:
                st.markdown(f'<div class="ob ob-p">{pro}</div>', unsafe_allow_html=True)
                st.download_button("⬇ Download", pro, "professional_summary.txt", "text/plain")
            else:
                st.markdown('<div class="ob ob-p ob-empty">Professional summary will appear here…</div>',
                            unsafe_allow_html=True)
        with lc2:
            st.markdown('<p class="sl sl-s">💡 Simplified Summary</p>', unsafe_allow_html=True)
            if sim:
                st.markdown(f'<div class="ob ob-s">{sim}</div>', unsafe_allow_html=True)
                st.download_button("⬇ Download", sim, "simplified_summary.txt", "text/plain")
            else:
                st.markdown('<div class="ob ob-s ob-empty">Simplified summary will appear here…</div>',
                            unsafe_allow_html=True)

    # ═══ TAB 2 — Word Changes ════════════════════════════════════════════════
    with t2:
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        changes = st.session_state.changes
        n_changes = len(changes)
        st.markdown(
            f'<p class="sl sl-c">🔤 Word Simplification Map '
            f'<span style="color:#64748b;font-family:Inter;font-size:.75rem;font-weight:400">'
            f'— {n_changes} term{"s" if n_changes!=1 else ""} replaced</span></p>',
            unsafe_allow_html=True)
        st.markdown(_table(changes), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ TAB 3 — Metrics ═════════════════════════════════════════════════════
    with t3:
        if not m:
            st.info("Run a summarisation first to see metrics.")
        else:
            # Rings
            st.markdown('<div class="gc">', unsafe_allow_html=True)
            st.markdown('<p class="sl sl-m">📊 Accuracy & Quality Scores</p>', unsafe_allow_html=True)
            rings_html = (
                '<div class="rings">'
                + _ring(m["overall_accuracy"],  "#7c3aed","#a78bfa","Overall")
                + _ring(m["retention_score"],   "#4f46e5","#818cf8","Retention")
                + _ring(m["simplicity_score"],  "#0891b2","#67e8f9","Simplicity")
                + _ring(m["compression_pct"],   "#059669","#6ee7b7","Compression")
                + _ring(min(m["readability"],100),"#d97706","#fcd34d","Readability")
                + '</div>'
            )
            st.markdown(rings_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Stat cards
            st.markdown('<div class="gc">', unsafe_allow_html=True)
            st.markdown('<p class="sl sl-s">📈 Document Statistics</p>', unsafe_allow_html=True)
            cards = (
                '<div class="mgrid">'
                + _mc(f"{m['orig_words']:,}",    "Original Words")
                + _mc(str(m['pro_words']),        "Pro Words")
                + _mc(str(m['sim_words']),        "Simple Words")
                + _mc(str(m.get('words_changed',0)),"Words Simplified")
                + _mc(f"{m['compression_pct']}%", "Compression")
                + _mc(f"{m['pro_read_time']} min","Pro Read Time")
                + _mc(f"{m['sim_read_time']} min","Simple Read Time")
                + _mc(str(m['readability']),      "Flesch Score")
                + '</div>'
            )
            st.markdown(cards, unsafe_allow_html=True)
            st.markdown("""
<p style="font-size:.77rem;color:#475569;margin-top:.9rem;line-height:1.85">
  <strong style="color:#a78bfa">Overall Accuracy</strong> — weighted score combining retention, simplicity &amp; compression.<br>
  <strong style="color:#818cf8">Retention</strong> — how much key content from the original is preserved.<br>
  <strong style="color:#67e8f9">Simplicity</strong> — proportion of complex terms replaced with simpler alternatives.<br>
  <strong style="color:#6ee7b7">Compression</strong> — how much shorter the summary is vs the original.<br>
  <strong style="color:#fcd34d">Flesch Score</strong> — readability (90–100 very easy · 50–70 fairly easy · &lt;30 difficult).
</p>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ═══ TAB 4 — Translate ═══════════════════════════════════════════════════
    with t4:
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.markdown('<p class="sl sl-t">🌍 Translate Summaries</p>', unsafe_allow_html=True)

        if not pro:
            st.info("Generate summaries first, then translate them here.")
        else:
            tc1, tc2 = st.columns([4, 1])
            with tc1:
                tgt = st.selectbox("Language", DISPLAY_NAMES,
                                   index=0, label_visibility="collapsed")
            with tc2:
                do_tr = st.button("🌐  Translate")

            if do_tr:
                if tgt.startswith("—"):
                    st.warning("Please select a target language.")
                else:
                    with st.spinner(f"Translating to {tgt}…"):
                        st.session_state.t_pro  = translate_text(pro, tgt)
                        st.session_state.t_sim  = translate_text(sim, tgt)
                        st.session_state.t_lang = tgt

        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.t_pro:
            tl = st.session_state.t_lang
            oc1, oc2 = st.columns(2, gap="large")
            with oc1:
                st.markdown(f'<p class="sl sl-p">📋 Professional — {tl}</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="ob ob-p">{st.session_state.t_pro}</div>',
                            unsafe_allow_html=True)
                st.download_button("⬇ Download", st.session_state.t_pro,
                    f"professional_{tl.lower().replace(' ','_')}.txt", "text/plain")
            with oc2:
                st.markdown(f'<p class="sl sl-s">💡 Simplified — {tl}</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="ob ob-s">{st.session_state.t_sim}</div>',
                            unsafe_allow_html=True)
                st.download_button("⬇ Download", st.session_state.t_sim,
                    f"simplified_{tl.lower().replace(' ','_')}.txt", "text/plain")

    # ═══ TAB 5 — Audio ═══════════════════════════════════════════════════════
    with t5:
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.markdown('<p class="sl sl-a">🔊 Audio Playback</p>', unsafe_allow_html=True)

        if not pro:
            st.info("Generate summaries first, then listen to them here.")
        else:
            # Determine language for TTS
            t_lang_name = st.session_state.t_lang
            lc_code = lang_code(t_lang_name) if not t_lang_name.startswith("—") else "en"

            ac1, ac2 = st.columns(2, gap="large")

            with ac1:
                st.markdown('<p style="color:#a78bfa;font-size:.88rem;font-weight:600">📋 Professional</p>',
                            unsafe_allow_html=True)
                if st.button("▶  Play Professional"):
                    txt = st.session_state.t_pro or pro
                    with st.spinner("Generating audio…"):
                        ab = text_to_speech(txt, lc_code)
                    if ab:
                        st.audio(ab, format="audio/mp3")
                        st.download_button("⬇ Download MP3", ab,
                                           "professional_summary.mp3", "audio/mp3")
                    else:
                        st.warning("Install gTTS: `pip install gTTS`")

            with ac2:
                st.markdown('<p style="color:#67e8f9;font-size:.88rem;font-weight:600">💡 Simplified</p>',
                            unsafe_allow_html=True)
                if st.button("▶  Play Simplified"):
                    txt = st.session_state.t_sim or sim
                    with st.spinner("Generating audio…"):
                        ab = text_to_speech(txt, lc_code)
                    if ab:
                        st.audio(ab, format="audio/mp3")
                        st.download_button("⬇ Download MP3", ab,
                                           "simplified_summary.mp3", "audio/mp3")
                    else:
                        st.warning("Install gTTS: `pip install gTTS`")

            st.markdown("""
<p style="font-size:.77rem;color:#475569;margin-top:.85rem">
  💡 Audio uses the translated version if you translated first.
  Supports 60+ languages. Translate tab → then come back here.
</p>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown('<div class="hdiv"></div>', unsafe_allow_html=True)
    st.markdown("""
<p style="text-align:center;color:#1e293b;font-size:.72rem;letter-spacing:.09em">
  SUMMARIZEAI PRO &nbsp;·&nbsp; BART-large-CNN &nbsp;·&nbsp;
  Deterministic Simplifier &nbsp;·&nbsp; gTTS &nbsp;·&nbsp; deep-translator
</p>""", unsafe_allow_html=True)
