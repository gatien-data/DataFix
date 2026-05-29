"""Page À propos - DATAFIX (style startup cinéma)."""

from base64 import b64encode
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="DATAFIX – À propos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────────
GOLD = "#F5C518"
BG_DEEP = "#0F0F12"
BG_SOFT = "#15161C"
TXT = "#FFFFFF"
MUTED = "#B8B8B8"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "df_film.csv"
LOGO = BASE_DIR / "asset" / "logo.png"

TMDB_BEARER = (
    "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5Y2IwZTY2ZDU4M2NlMjRlNzhkMWIyNzc2YmUxYTJiMCIs"
    "Im5iZiI6MTc3NzI5NjYzNS4wODksInN1YiI6IjY5ZWY2NGZiYTQ5YzYxY2QwNzE1MWFiNiIsInNj"
    "b3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.kcNXcdjcIvWsz84XKCFBrOopCYfR7g4yg-IMIV2YYbU"
)
TMDB_HEADERS = {"accept": "application/json", "Authorization": f"Bearer {TMDB_BEARER}"}


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=86400)
def tmdb_backdrop(movie_id: int) -> str:
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{int(movie_id)}",
            headers=TMDB_HEADERS, params={"language": "fr-FR"}, timeout=5,
        )
        if r.status_code == 200:
            p = r.json().get("backdrop_path")
            if p:
                return f"https://image.tmdb.org/t/p/original{p}"
    except Exception:
        pass
    return ""


def img_data_uri(path: Path) -> str:
    """Lit une image locale et la convertit en data URI base64 (garantie d'affichage)."""
    if not path.exists():
        return ""
    ext = path.suffix.lstrip(".").lower().replace("jpg", "jpeg")
    try:
        return f"data:image/{ext};base64,{b64encode(path.read_bytes()).decode()}"
    except Exception:
        return ""


@st.cache_data(ttl=3600)
def n_films() -> int:
    try:
        return len(pd.read_csv(DATA_PATH))
    except Exception:
        return 800


# Hero backdrop : Intouchables
hero_back = tmdb_backdrop(77338)

# Équipe (avec photos locales)
TEAM = [
    {
        "key": "salim",
        "name": "Salim Fillali",
        "role": "Product Owner",
        "desc": (
            "Définit la vision du projet, coordonne les fonctionnalités et veille "
            "à la cohérence globale entre expérience utilisateur, besoins métier "
            "et stratégie produit."
        ),
        "quote": "Transformer les données en expérience utilisateur.",
        "photo": "photo_salim.jpg",
    },
    {
        "key": "romain",
        "name": "Romain Lafforgue",
        "role": "Scrum Master",
        "desc": (
            "Supervise l'organisation agile du projet, facilite la collaboration "
            "de l'équipe et garantit le bon déroulement des cycles de développement."
        ),
        "quote": "Avancer en équipe, sprint après sprint.",
        "photo": "photo_romain.jpg",
    },
    {
        "key": "gatien",
        "name": "Gatien",
        "role": "Code Reviewer",
        "desc": (
            "Responsable de la qualité technique du code, de la validation "
            "des développements et des bonnes pratiques de programmation."
        ),
        "quote": "Du code propre, un produit solide.",
        "photo": "photo_gatien.jpg",
    },
    {
        "key": "liliana",
        "name": "Liliana",
        "role": "Data Analyst",
        "desc": (
            "Analyse les données utilisateurs et cinéma afin d'identifier "
            "les tendances et améliorer la pertinence des recommandations."
        ),
        "quote": "La donnée raconte des histoires — il faut savoir les écouter.",
        "photo": "photo_liliana.jpg",
    },
    {
        "key": "jade",
        "name": "Jade",
        "role": "Data Analyst",
        "desc": (
            "Participe à l'exploration des données, à la visualisation analytique "
            "et à l'optimisation des modèles de recommandation."
        ),
        "quote": "Voir clair dans les chiffres pour mieux choisir.",
        "photo": "photo_jade.jpg",
    },
]

# Logos technos (SVG simple-icons via cdn jsdelivr, fallback : aucun)
TECHS = [
    {"name": "Python",       "color": "#3776AB", "sub": "Langage core",      "logo": "https://cdn.simpleicons.org/python/FFFFFF"},
    {"name": "Streamlit",    "color": "#FF4B4B", "sub": "Interface web",     "logo": "https://cdn.simpleicons.org/streamlit/FFFFFF"},
    {"name": "Pandas",       "color": "#150458", "sub": "Manipulation data", "logo": "https://cdn.simpleicons.org/pandas/FFFFFF"},
    {"name": "scikit-learn", "color": "#F7931E", "sub": "Machine learning",  "logo": "https://cdn.simpleicons.org/scikitlearn/FFFFFF"},
    {"name": "TMDB",         "color": "#01B4E4", "sub": "API films",         "logo": "https://cdn.simpleicons.org/themoviedatabase/FFFFFF"},
    {"name": "Plotly",       "color": "#7A76FF", "sub": "Visualisation",     "logo": "https://cdn.simpleicons.org/plotly/FFFFFF"},
    {"name": "GitHub",       "color": "#FFFFFF", "sub": "Collaboration",     "logo": "https://cdn.simpleicons.org/github/FFFFFF"},
]


# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
:root {{
  --gold: {GOLD};
  --bg-deep: {BG_DEEP};
  --bg-soft: {BG_SOFT};
  --txt: {TXT};
  --muted: {MUTED};
}}
.stApp {{ background: var(--bg-deep); color: var(--txt); }}
[data-testid="stHeader"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
section.main > div {{ padding: 0 !important; }}
footer, #MainMenu {{ visibility: hidden; }}

/* NAVBAR custom (toujours visible) */
.topnav {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  background: rgba(15,15,18,0.78);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.topnav-inner {{
  max-width: 1400px; margin: 0 auto;
  padding: 0.85rem 2rem;
  display: flex; align-items: center; justify-content: space-between;
}}
.topnav-brand {{
  color: var(--gold) !important; font-weight: 900;
  letter-spacing: 0.18em; font-size: 1rem;
  text-decoration: none !important;
}}
.topnav-links {{ display: flex; gap: 2rem; }}
.topnav-links a {{
  color: #D8D8DC !important; text-decoration: none !important;
  font-weight: 600; font-size: 0.9rem;
  letter-spacing: 0.05em;
  padding: 0.4rem 0.8rem; border-radius: 8px;
  transition: all 0.2s ease;
}}
.topnav-links a:hover {{ color: var(--gold) !important; background: rgba(245,197,24,0.08); }}
.topnav-links a.active {{ color: var(--gold) !important; background: rgba(245,197,24,0.12); }}
.topnav-search input {{
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px;
  padding: 0.35rem 1rem;
  color: #fff;
  font-size: 0.85rem;
  width: 260px;
  outline: none;
  transition: border 0.2s;
}}
.topnav-search input:focus {{
  border-color: var(--gold);
}}
.topnav-search input::placeholder {{
  color: rgba(255,255,255,0.4);
}}

/* ============ HERO ============ */
.hero {{
  position: relative; min-height: 80vh;
  display: flex; align-items: center; justify-content: center;
  text-align: center; overflow: hidden; background: #000;
}}
.hero-bg {{
  position: absolute; inset: 0;
  background-image: url('{hero_back}');
  background-size: cover; background-position: center;
  filter: brightness(0.45) saturate(1.1) blur(3px);
  transform: scale(1.08);
  animation: heroIn 1.8s ease-out both;
}}
.hero-overlay {{
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at center, rgba(0,0,0,0.4) 0%, rgba(15,15,18,0.95) 80%),
    linear-gradient(180deg, rgba(15,15,18,0.5) 0%, rgba(15,15,18,1) 100%);
}}
.hero-content {{
  position: relative; z-index: 2; max-width: 1000px; padding: 0 2rem;
  animation: fadeUp 1.4s ease-out 0.3s both;
}}
.hero-eyebrow {{
  display: inline-block; letter-spacing: 0.42em; font-size: 0.78rem;
  font-weight: 700; color: var(--gold);
  border: 1px solid rgba(245,197,24,0.4);
  padding: 0.4rem 1rem; border-radius: 999px; margin-bottom: 1.8rem;
  text-transform: uppercase;
}}
.hero-brand {{
  font-size: clamp(3rem, 8vw, 6.5rem); font-weight: 900;
  letter-spacing: -0.04em; line-height: 1; margin: 0;
  background: linear-gradient(180deg, #FFFFFF 30%, {GOLD} 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.hero-tagline {{
  font-size: clamp(1.15rem, 1.8vw, 1.5rem);
  font-style: italic; color: var(--gold); font-weight: 500;
  margin: 1.4rem 0 1rem 0;
}}
.hero-subtitle {{
  color: var(--muted); font-size: clamp(0.95rem, 1.3vw, 1.1rem);
  line-height: 1.7; max-width: 720px; margin: 0 auto 2.6rem auto;
}}
.hero-ctas {{
  display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;
}}
.btn {{
  display: inline-block; padding: 0.95rem 2.1rem; border-radius: 999px;
  font-weight: 700; font-size: 0.98rem; text-decoration: none !important;
  transition: all 0.25s ease; border: none;
}}
.btn-primary {{
  background: {GOLD}; color: #0E0E10 !important;
  box-shadow: 0 10px 30px rgba(245,197,24,0.25);
}}
.btn-primary:hover {{
  transform: translateY(-2px);
  box-shadow: 0 14px 36px rgba(245,197,24,0.45);
}}
.btn-ghost {{
  background: rgba(255,255,255,0.06); color: var(--txt) !important;
  border: 1px solid rgba(255,255,255,0.18);
}}
.btn-ghost:hover {{
  background: rgba(255,255,255,0.12);
  border-color: rgba(245,197,24,0.5); transform: translateY(-2px);
}}

/* ============ SECTIONS GÉNÉRIQUES ============ */
.section {{
  max-width: 1300px; margin: 0 auto; padding: 6rem 2rem 2rem 2rem;
}}
.section-eyebrow {{
  color: var(--gold); font-size: 0.78rem; letter-spacing: 0.35em;
  font-weight: 700; text-transform: uppercase; margin-bottom: 0.8rem;
}}
.section-title {{
  font-size: clamp(2rem, 3.5vw, 3rem); font-weight: 900;
  letter-spacing: -0.02em; margin: 0 0 1.2rem 0;
}}
.section-lead {{
  color: var(--muted); font-size: 1.1rem; line-height: 1.75;
  max-width: 780px; margin: 0 0 3rem 0;
}}

/* ============ VISION (texte centré + stats) ============ */
.vision {{
  text-align: center;
  max-width: 900px; margin: 0 auto;
}}
.vision-quote {{
  font-size: clamp(1.5rem, 2.4vw, 2rem); font-weight: 700;
  line-height: 1.45; color: var(--txt);
  border-left: 0; padding: 0 1.5rem;
  margin: 0 auto 1.5rem auto;
}}
.vision-quote em {{
  color: var(--gold); font-style: normal;
}}
.vision-text {{
  color: var(--muted); font-size: 1.08rem; line-height: 1.75; margin-top: 1rem;
}}
.vision-stats {{
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 1rem; max-width: 800px; margin: 3rem auto 0 auto;
}}
.vstat {{
  padding: 1.6rem; background: var(--bg-soft);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 18px; text-align: center;
  transition: all 0.3s ease;
}}
.vstat:hover {{
  border-color: rgba(245,197,24,0.4);
  transform: translateY(-4px);
}}
.vstat-num {{
  font-size: clamp(1.8rem, 2.6vw, 2.4rem); font-weight: 900;
  color: var(--gold); line-height: 1;
}}
.vstat-lbl {{
  margin-top: 0.7rem; font-size: 0.78rem; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--muted);
}}

/* ============ HOW IT WORKS ============ */
.how-grid {{
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem; margin-top: 1rem;
}}
.how-card {{
  position: relative; padding: 2.4rem 1.8rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 22px;
  backdrop-filter: blur(20px);
  transition: all 0.4s ease;
  overflow: hidden;
}}
.how-card::before {{
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(245,197,24,0.12) 0%, transparent 60%);
  opacity: 0; transition: opacity 0.4s ease;
}}
.how-card:hover {{
  transform: translateY(-6px);
  border-color: rgba(245,197,24,0.4);
  box-shadow: 0 18px 50px rgba(245,197,24,0.12);
}}
.how-card:hover::before {{ opacity: 1; }}
.how-card > * {{ position: relative; z-index: 1; }}
.how-num {{
  font-size: 2.5rem; font-weight: 900; color: var(--gold);
  line-height: 1; margin-bottom: 1rem; opacity: 0.5;
}}
.how-title {{
  font-size: 1.25rem; font-weight: 800; margin: 0 0 0.8rem 0;
}}
.how-text {{
  color: var(--muted); font-size: 0.95rem; line-height: 1.65;
}}


/* ============ TEAM ============ */
.team-grid {{
  display: grid; grid-template-columns: repeat(5, 1fr);
  gap: 1.2rem; margin-top: 1rem;
}}
.tcard {{
  position: relative;
  background: var(--bg-soft);
  border-radius: 22px; padding: 2rem 1.2rem 1.5rem 1.2rem;
  border: 1px solid rgba(255,255,255,0.06);
  text-align: center;
  transition: all 0.4s ease;
  overflow: hidden;
}}
.tcard:hover {{
  transform: translateY(-8px);
  border-color: rgba(245,197,24,0.5);
  box-shadow: 0 22px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(245,197,24,0.2);
}}
.tcard-photo {{
  width: 120px; height: 120px; border-radius: 50%;
  margin: 0 auto 1.2rem auto;
  overflow: hidden;
  border: 3px solid rgba(245,197,24,0.25);
  position: relative;
  transition: all 0.4s ease;
}}
.tcard:hover .tcard-photo {{
  border-color: var(--gold);
  box-shadow: 0 0 0 6px rgba(245,197,24,0.12);
}}
.tcard-photo img {{
  width: 100%; height: 100%; object-fit: cover; display: block;
  filter: grayscale(60%) contrast(1.05);
  transition: filter 0.4s ease;
}}
.tcard:hover .tcard-photo img {{ filter: grayscale(0%) contrast(1.05); }}
.tcard-name {{
  font-size: 1.05rem; font-weight: 800; margin: 0 0 0.3rem 0;
}}
.tcard-role {{
  color: var(--gold); font-size: 0.72rem;
  font-weight: 700; letter-spacing: 0.18em;
  text-transform: uppercase; margin-bottom: 0.9rem;
}}
.tcard-desc {{
  color: var(--muted); font-size: 0.82rem;
  line-height: 1.55; min-height: 110px;
}}
.tcard-quote {{
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 1.2rem 1rem; color: var(--gold);
  font-style: italic; font-size: 0.85rem; line-height: 1.4;
  background: linear-gradient(180deg, transparent 0%, rgba(15,15,18,0.97) 35%);
  opacity: 0; transform: translateY(10px);
  transition: all 0.4s ease;
}}
.tcard:hover .tcard-quote {{
  opacity: 1; transform: translateY(0);
}}
.tcard-quote::before {{
  content: '\\201C'; font-size: 2.2rem; color: var(--gold);
  line-height: 0; vertical-align: -0.4em; margin-right: 0.2rem;
}}

/* ============ TECHNOLOGIES ============ */
.tech-grid {{
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 1rem; margin-top: 2rem;
}}
.tech-chip {{
  position: relative;
  padding: 1.6rem 0.8rem; text-align: center;
  background: var(--bg-soft);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: default;
}}
.tech-chip:hover {{
  transform: translateY(-4px);
  border-color: rgba(255,255,255,0.2);
  box-shadow: 0 10px 26px rgba(0,0,0,0.4);
}}
.tech-dot {{
  display: block; width: 38px; height: 38px;
  border-radius: 10px; margin: 0 auto 0.8rem auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  position: relative;
}}
.tech-name {{
  font-weight: 800; font-size: 0.92rem; color: var(--txt);
  margin: 0 0 0.2rem 0;
}}
.tech-sub {{
  color: var(--muted); font-size: 0.72rem;
  letter-spacing: 0.08em; text-transform: uppercase;
}}

/* ============ WHY DATAFIX ============ */
.why {{
  max-width: 1100px; margin: 5rem auto;
  padding: 4rem 3rem;
  background:
    radial-gradient(ellipse at top right, rgba(245,197,24,0.10) 0%, transparent 55%),
    var(--bg-soft);
  border-radius: 28px;
  border: 1px solid rgba(245,197,24,0.18);
}}
.why h2 {{
  font-size: clamp(1.8rem, 2.8vw, 2.4rem);
  font-weight: 900; margin: 0 0 1.5rem 0;
}}
.why h2 em {{ color: var(--gold); font-style: normal; }}
.why p {{
  color: #D8D8DC; font-size: 1.08rem; line-height: 1.8; margin: 0.8rem 0;
}}

/* ============ KPI ============ */
.kpi-grid {{
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1.2rem; margin-top: 2.5rem;
}}
.kpi {{
  text-align: center; padding: 2.2rem 1rem;
  background: var(--bg-soft);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  transition: all 0.3s ease;
}}
.kpi:hover {{
  transform: translateY(-4px); border-color: rgba(245,197,24,0.4);
}}
.kpi-num {{
  font-size: clamp(2.2rem, 3.5vw, 3rem); font-weight: 900;
  color: var(--gold); line-height: 1;
}}
.kpi-lbl {{
  margin-top: 0.8rem; font-size: 0.82rem; letter-spacing: 0.15em;
  text-transform: uppercase; color: var(--muted);
}}

/* ============ FOOTER ============ */
.footer {{
  margin-top: 6rem; padding: 3rem 2rem 2rem 2rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  text-align: center; color: var(--muted);
}}
.footer-brand {{
  color: var(--gold); font-weight: 800; letter-spacing: 0.15em;
  font-size: 0.95rem; margin-bottom: 0.5rem;
}}
.footer-links {{
  margin-top: 1rem; display: flex; justify-content: center;
  gap: 2rem; flex-wrap: wrap; font-size: 0.85rem;
}}
.footer-links a {{
  color: var(--muted); text-decoration: none; transition: color 0.2s ease;
}}
.footer-links a:hover {{ color: var(--gold); }}
.footer-bottom {{
  margin-top: 1.5rem; font-size: 0.72rem; letter-spacing: 0.1em; opacity: 0.6;
}}

/* ============ ANIMATIONS ============ */
@keyframes heroIn {{
  from {{ transform: scale(1.18); opacity: 0; }}
  to {{ transform: scale(1.08); opacity: 1; }}
}}
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(30px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

@media (max-width: 1100px) {{
  .team-grid {{ grid-template-columns: repeat(3, 1fr); }}
  .tech-grid {{ grid-template-columns: repeat(4, 1fr); }}
}}
@media (max-width: 700px) {{
  .vision-stats {{ grid-template-columns: 1fr; }}
  .how-grid {{ grid-template-columns: 1fr; }}
  .team-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .tech-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
    st.caption("v0.3 · Sprint 4 · 2026")


# ─────────────────────────────────────────────────────────────
# NAVBAR (toujours visible)
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="topnav">
  <div class="topnav-inner">
    <a href="/" target="_top" class="topnav-brand">DATAFIX</a>
    <form class="topnav-search" action="/Recommandation" method="get" target="_top">
      <input type="text" name="search" placeholder="Rechercher un film dans le catalogue…" autocomplete="off" />
    </form>
    <div class="topnav-links">
      <a href="/" target="_top">Accueil</a>
      <a href="/Recommandation" target="_top">Recommandation</a>
      <a href="/A_propos" target="_top" class="active">À propos</a>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 1. HERO
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
  <div class="hero-bg"></div>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-eyebrow">À propos de DATAFIX</div>
    <h1 class="hero-brand">DATAFIX</h1>
    <div class="hero-tagline">"L'intelligence des données au service du cinéma local."</div>
    <p class="hero-subtitle">
      DATAFIX est une plateforme de recommandation de films pensée pour
      accompagner la transformation digitale d'un cinéma indépendant de la Creuse.
      Notre mission : proposer une expérience moderne, immersive et personnalisée
      grâce à la data et à l'intelligence artificielle.
    </p>
    <div class="hero-ctas">
      <a href="/Recommandation" target="_top" class="btn btn-primary">Voir les recommandations</a>
      <a href="#vision" class="btn btn-ghost">Découvrir le projet</a>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 2. NOTRE VISION
# ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="section" id="vision">
  <div class="vision">
    <div class="section-eyebrow">Notre vision</div>
    <div class="vision-quote">
      Les petits cinémas méritent les <em>mêmes outils technologiques</em>
      que les grandes plateformes de streaming.
    </div>
    <p class="vision-text">
      DATAFIX combine analyse de données, expérience utilisateur et intelligence
      artificielle afin de reconnecter le public local avec le cinéma.
      Nous transformons la richesse du catalogue français en une expérience
      personnalisée, fluide et accessible à toutes les générations.
    </p>
    <div class="vision-stats">
      <div class="vstat">
        <div class="vstat-num">Large</div>
        <div class="vstat-lbl">Catalogue de films</div>
      </div>
      <div class="vstat">
        <div class="vstat-num">100%</div>
        <div class="vstat-lbl">Comédies françaises</div>
      </div>
      <div class="vstat">
        <div class="vstat-num">24/7</div>
        <div class="vstat-lbl">API temps réel</div>
      </div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 3. COMMENT ÇA MARCHE
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="section">
  <div class="section-eyebrow">Méthodologie</div>
  <h2 class="section-title">Comment ça marche</h2>
  <p class="section-lead">
    Trois piliers techniques au service d'une expérience cinéma sur mesure.
  </p>
  <div class="how-grid">
    <div class="how-card">
      <div class="how-num">01</div>
      <div class="how-title">Analyse des données</div>
    </div>
    <div class="how-card">
      <div class="how-num">02</div>
      <div class="how-title">Intelligence de recommandation</div>
    </div>
    <div class="how-card">
      <div class="how-num">03</div>
      <div class="how-title">Expérience immersive</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 4. NOTRE ÉQUIPE
# ─────────────────────────────────────────────────────────────
team_cards = []
for m in TEAM:
    photo_uri = img_data_uri(BASE_DIR / "asset" / m["photo"])
    img_html = (
        f'<img src="{photo_uri}" alt="{m["name"]}" loading="lazy"/>'
        if photo_uri
        else '<div style="width:100%;height:100%;background:linear-gradient(135deg,#3a3a44,#1a1a22);"></div>'
    )
    team_cards.append(
        f'<div class="tcard">'
        f'  <div class="tcard-photo">{img_html}</div>'
        f'  <div class="tcard-name">{m["name"]}</div>'
        f'  <div class="tcard-role">{m["role"]}</div>'
        f'  <div class="tcard-desc">{m["desc"]}</div>'
        f'  <div class="tcard-quote">{m["quote"]}</div>'
        f'</div>'
    )

st.markdown(
    f"""
<div class="section">
  <div class="section-eyebrow">L'équipe</div>
  <h2 class="section-title">Les visages de DATAFIX</h2>
  <p class="section-lead">
    Cinq profils complémentaires, une même conviction :
    la data peut sublimer l'expérience cinéma locale.
  </p>
  <div class="team-grid">
    {''.join(team_cards)}
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 5. TECHNOLOGIES
# ─────────────────────────────────────────────────────────────
tech_chips = "".join(
    (
        '<div class="tech-chip">'
        '<div class="tech-dot" style="background:' + t['color'] + ';display:flex;align-items:center;justify-content:center;">'
        '<img src="' + t['logo'] + '" alt="' + t['name'] + '" style="width:20px;height:20px;object-fit:contain;">'
        '</div>'
        '<div class="tech-name">' + t['name'] + '</div>'
        '<div class="tech-sub">' + t['sub'] + '</div>'
        '</div>'
    )
    for t in TECHS
)
st.markdown(
    f"""
<div class="section">
  <div class="section-eyebrow">Stack technique</div>
  <h2 class="section-title">Technologies</h2>
  <p class="section-lead">
    DATAFIX s'appuie sur des technologies modernes de data science et de
    développement web afin d'offrir une plateforme performante, évolutive
    et intuitive.
  </p>
  <div class="tech-grid">{tech_chips}</div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 6. POURQUOI DATAFIX
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="section">
  <div class="why">
    <div class="section-eyebrow">Pourquoi DATAFIX ?</div>
    <h2>Le streaming a transformé la consommation cinéma — <em>il est temps que le cinéma local en profite aussi.</em></h2>
    <p>
      Les plateformes de streaming utilisent la data pour fidéliser leurs utilisateurs,
      personnaliser les recommandations et créer des expériences immersives.
      Ces outils sont restés inaccessibles aux salles indépendantes — jusqu'à maintenant.
    </p>
    <p>
      DATAFIX applique cette même logique au cinéma local afin de proposer une
      expérience plus <strong>humaine</strong>, plus <strong>ciblée</strong>
      et plus <strong>moderne</strong>. Notre objectif : reconnecter les habitants
      de la Creuse avec leur cinéma, en donnant à chacun la séance qu'il mérite.
    </p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 7. NOS OBJECTIFS (KPI)
# ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="section">
  <div class="section-eyebrow">Nos objectifs</div>
  <h2 class="section-title">Ce que DATAFIX permet</h2>
  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-num">Large</div>
      <div class="kpi-lbl">Catalogue de films</div>
    </div>
    <div class="kpi">
      <div class="kpi-num">API</div>
      <div class="kpi-lbl">Temps réel TMDB</div>
    </div>
    <div class="kpi">
      <div class="kpi-num">ML</div>
      <div class="kpi-lbl">Reco intelligentes</div>
    </div>
    <div class="kpi">
      <div class="kpi-num">UX</div>
      <div class="kpi-lbl">Expérience premium</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── FOOTER ──────────────────────────────────────────────────
st.markdown(
    """
<div class="footer">
  <div class="footer-brand">DATAFIX</div>
  <div>© 2026 DATAFIX — Projet de recommandation cinématographique basé sur la data science.</div>
  <div class="footer-links">
    <a href="https://github.com/romainlafforgue-alt/datafix-application" target="_blank">GitHub</a>
    <a href="/" target="_top">Accueil</a>
    <a href="/Recommandation" target="_top">Recommandation</a>
    <a href="https://www.themoviedb.org/" target="_blank">TMDB</a>
  </div>
  <div class="footer-bottom">Wild Code School · Cinéma de la Creuse · Sprint 4 · 2026</div>
</div>
""",
    unsafe_allow_html=True,
)
