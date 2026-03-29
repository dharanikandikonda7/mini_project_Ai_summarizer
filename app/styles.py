STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap');

/* ═════════════════ VARIABLES ═════════════════ */
:root {
  --bg:#050816;
  --card:rgba(13,21,55,0.7);
  --border:rgba(124,58,237,0.25);
  --purple:#7c3aed;
  --plite:#a78bfa;
  --teal:#06b6d4;
  --tlite:#67e8f9;
  --pink:#ec4899;
  --text:#e2e8f0;
  --muted:#64748b;
}

/* ═════════════════ BASE ═════════════════ */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* 🔥 Animated background glow */
[data-testid="stAppViewContainer"]::before {
  content:"";
  position:fixed;
  inset:0;
  z-index:0;
  background:
    radial-gradient(circle at 20% 20%, rgba(124,58,237,.2), transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(6,182,212,.15), transparent 50%);
  animation: moveBg 12s infinite alternate;
}

@keyframes moveBg {
  0% { transform: translateY(0px); }
  100% { transform: translateY(-40px); }
}

[data-testid="stMainBlockContainer"]{
  position:relative;
  z-index:1;
}

/* ═════════════════ HERO ═════════════════ */

.hero {
  text-align:center;
  padding:2.5rem 0;
  animation: fadeInUp 1s ease;
}
/* 🔥 TOP CENTER LOGO */
.hero-logo-top {
  display: block;
  margin: 0 auto 12px auto;
  width: 120px;
  filter: drop-shadow(0 0 25px rgba(124,58,237,0.7));
  transition: transform 0.4s ease;
}

/* HOVER EFFECT */
.hero-logo-top:hover {
  transform: scale(1.1) rotate(2deg);
}

.hero h1 {
  font-family:'Orbitron',sans-serif;
  font-size:3rem;
  font-weight:900;
  background:linear-gradient(135deg,#a78bfa,#06b6d4,#ec4899);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
}

.hero-sub {
  color:var(--muted);
}

/* ═════════════════ GLASS CARD ═════════════════ */
.gc {
  background: var(--card);
  border:1px solid var(--border);
  border-radius:18px;
  padding:1.5rem;
  margin-bottom:1.2rem;
  backdrop-filter: blur(20px);
  box-shadow: 0 10px 40px rgba(0,0,0,.5);
  transition: all .3s ease;
}

.gc:hover {
  transform: translateY(-4px) scale(1.01);
}

/* ═════════════════ OUTPUT BOX ═════════════════ */
.ob {
  border-radius:14px;
  padding:1.3rem;
  line-height:1.8;
}

.ob-p {
  background: rgba(124,58,237,.15);
  border:1px solid rgba(124,58,237,.4);
}

.ob-s {
  background: rgba(6,182,212,.15);
  border:1px solid rgba(6,182,212,.4);
}

/* ═════════════════ METRIC CARDS ═════════════════ */
.mc {
  background: rgba(255,255,255,.04);
  border:1px solid var(--border);
  border-radius:12px;
  padding:1rem;
  text-align:center;
  transition: all .3s ease;
}

.mc:hover {
  transform: translateY(-6px);
  box-shadow:0 10px 30px rgba(124,58,237,.4);
}

/* ═════════════════ VERTICAL TABS ═════════════════ */
[data-testid="stTabs"] {
  display:flex !important;
  flex-direction:row !important;
}

/* LEFT PANEL */
[data-testid="stTabs"] > div:first-child {
  display:flex !important;
  flex-direction:column !important;
  gap:10px;
  min-width:220px;
  position:sticky;
  top:100px;
}

/* TAB BUTTON */
[data-testid="stTabs"] button {
  text-align:left !important;
  padding:0.7rem !important;
  border-radius:10px !important;
  background: rgba(255,255,255,.03) !important;
  border:1px solid var(--border) !important;
  transition:all .3s ease !important;
}

/* HOVER */
[data-testid="stTabs"] button:hover {
  transform: translateX(6px);
  background: rgba(124,58,237,.2) !important;
}

/* ACTIVE */
[data-testid="stTabs"] button[aria-selected="true"] {
  background: linear-gradient(135deg,#7c3aed,#06b6d4) !important;
  color:white !important;
  box-shadow:0 0 20px rgba(124,58,237,.5);
}

/* CONTENT */
[data-testid="stTabs"] > div:last-child {
  flex:1;
  padding-left:20px;
  animation: fadeInUp .6s ease;
}


/* ═════════════════ BUTTONS ═════════════════ */
.stButton > button {
  background: linear-gradient(135deg,#7c3aed,#06b6d4) !important;
  border-radius:12px !important;
  color:white !important;
  transition:all .3s ease;
}

.stButton > button:hover {
  transform: scale(1.05);
  box-shadow:0 8px 30px rgba(124,58,237,.6);
}

/* ═════════════════ INPUTS ═════════════════ */
textarea, input {
  background: rgba(10,15,40,.8) !important;
  border:1px solid var(--border) !important;
  border-radius:10px !important;
  color:var(--text) !important;
}

/* ═════════════════ SCROLLBAR ═════════════════ */
::-webkit-scrollbar { width:5px }
::-webkit-scrollbar-thumb {
  background:linear-gradient(var(--purple),var(--teal));
}

/* ═════════════════ ANIMATION ═════════════════ */
@keyframes fadeInUp {
  from { opacity:0; transform:translateY(20px); }
  to { opacity:1; transform:translateY(0); }
}

/* ═════════════════ SMOOTH SCROLL ═════════════════ */
html {
  scroll-behavior: smooth;
}
</style>
"""