"""Page Recommandation - DATAFIX (style plateforme cinéma).

"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import urllib.parse

import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


# =====================================================================
# Configuration
# =====================================================================
st.set_page_config(
    page_title="DATAFIX – Recommandation",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "df_film.csv"
PEOPLE_PATH = BASE_DIR / "data" / "df_people_details.csv"
LOGO = BASE_DIR / "asset" / "logo.png"

TMDB_BEARER = (
    "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5Y2IwZTY2ZDU4M2NlMjRlNzhkMWIyNzc2YmUxYTJiMCIs"
    "Im5iZiI6MTc3NzI5NjYzNS4wODksInN1YiI6IjY5ZWY2NGZiYTQ5YzYxY2QwNzE1MWFiNiIsInNj"
    "b3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.kcNXcdjcIvWsz84XKCFBrOopCYfR7g4yg-IMIV2YYbU"
)
TMDB_HEADERS = {"accept": "application/json", "Authorization": f"Bearer {TMDB_BEARER}"}

GOLD = "#F5C518"
BG_DEEP = "#0B0B0F"
BG_CARD = "rgba(255,255,255,0.04)"

DEFAULT_FILM = "Intouchables"
FALLBACK_FILMS = [
    "Intouchables",
    "Le Fabuleux Destin d'Amélie Poulain",
    "OSS 117 : Le Caire, nid d'espions",
    "La Grande Vadrouille",
]


# =====================================================================
# CSS — style plateforme streaming
# =====================================================================
st.markdown(
    f"""
<style>
/* ---------- Reset / fond global ---------- */
.stApp {{
    background: {BG_DEEP};
}}
/* on retire les éléments par défaut */
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stHeader"] {{ display: none !important; }}

/* NAVBAR custom (toujours visible) */
.topnav {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  background: rgba(11,11,15,0.78);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.topnav-inner {{
  max-width: 1400px; margin: 0 auto;
  padding: 0.85rem 2rem;
  display: flex; align-items: center; justify-content: space-between;
}}
.topnav-brand {{
  color: {GOLD} !important; font-weight: 900;
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
.topnav-links a:hover {{ color: {GOLD} !important; background: rgba(245,197,24,0.08); }}
.topnav-links a.active {{ color: {GOLD} !important; background: rgba(245,197,24,0.12); }}
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
.block-container {{
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 100% !important;
}}

/* ---------- Suppression du bleu par défaut Streamlit ---------- */
/* Texte général : blanc cassé */
body, .stApp, .stMarkdown, p, span, label, div {{
    color: #E8E8EA;
}}
/* Liens markdown courants : doré (sans toucher aux boutons custom ni aux cartes) */
.stMarkdown p a,
.stMarkdown li a,
.stMarkdown span a,
a.streamlit-link {{
    color: {GOLD};
    text-decoration: none;
    transition: opacity .2s ease;
}}
.stMarkdown p a:hover,
.stMarkdown li a:hover,
.stMarkdown span a:hover,
a.streamlit-link:hover {{
    opacity: 0.8;
    text-decoration: underline;
}}
/* Forcer la couleur du texte sur les boutons custom (priorité absolue) */
a.btn-primary, a.btn-primary:hover, a.btn-primary:visited {{
    color: #0E0E10 !important;
}}
a.btn-ghost, a.btn-ghost:hover, a.btn-ghost:visited {{
    color: #FFFFFF !important;
}}
/* Sélection texte : surlignage doré */
::selection {{
    background: rgba(245,197,24,0.35);
    color: #FFF;
}}
/* Caret / sélection des inputs */
input, textarea {{
    caret-color: {GOLD} !important;
}}
/* Boutons primaires Streamlit (st.button type="primary") */
.stButton > button[kind="primary"] {{
    background: {GOLD} !important;
    color: #0E0E10 !important;
    border: 0 !important;
    font-weight: 700;
}}
.stButton > button[kind="primary"]:hover {{
    background: #E5B815 !important;
    color: #0E0E10 !important;
}}
/* Boutons secondaires */
.stButton > button {{
    border-color: rgba(245,197,24,0.45) !important;
    color: #E8E8EA !important;
}}
.stButton > button:hover {{
    border-color: {GOLD} !important;
    color: {GOLD} !important;
}}
/* Spinner / progress en doré */
.stSpinner > div > div {{
    border-top-color: {GOLD} !important;
}}
[data-testid="stProgressBar"] > div > div > div {{
    background: {GOLD} !important;
}}
/* Info / Success / Warning : repeindre le bleu en sombre */
div[data-testid="stAlert"] {{
    background: rgba(245,197,24,0.07) !important;
    border-left: 4px solid {GOLD} !important;
    color: #E8E8EA !important;
}}
div[data-testid="stAlert"] svg {{
    fill: {GOLD} !important;
    color: {GOLD} !important;
}}
/* Slider : couleur or */
[data-testid="stSlider"] [role="slider"] {{
    background: {GOLD} !important;
    border-color: {GOLD} !important;
}}
[data-testid="stSlider"] > div > div > div > div {{
    background: {GOLD} !important;
}}
/* Selectbox / Combobox au focus */
[data-baseweb="select"] > div {{
    border-color: rgba(255,255,255,0.10) !important;
}}
[data-baseweb="select"] > div:focus-within {{
    border-color: {GOLD} !important;
    box-shadow: 0 0 0 3px rgba(245,197,24,0.15) !important;
}}
/* Navigation pages dans la sidebar : item actif en doré */
[data-testid="stSidebarNav"] a[aria-current="page"] {{
    color: {GOLD} !important;
    background: rgba(245,197,24,0.10) !important;
    border-radius: 8px;
}}
[data-testid="stSidebarNav"] a {{
    color: #C4C4CA !important;
}}
[data-testid="stSidebarNav"] a:hover {{
    color: {GOLD} !important;
}}

/* ---------- Sidebar premium ---------- */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0E0E12 0%, #050507 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}}
section[data-testid="stSidebar"] .stCaption {{
    color: #7a7a82;
}}

/* ---------- HERO plein écran ---------- */
.hero-wrap {{
    position: relative;
    width: calc(100% + 5rem);
    margin-left: -2.5rem;
    height: 78vh;
    min-height: 560px;
    overflow: hidden;
    margin-bottom: 2rem;
    /* fond de secours si aucune image ne charge */
    background:
      radial-gradient(ellipse at 30% 40%, #1a1a22 0%, {BG_DEEP} 70%);
}}
.hero-bg, .hero-bg-blur {{
    position: absolute; inset: 0;
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
}}
.hero-bg-blur {{
    /* image nette à gauche, douce à droite — beaucoup plus lisible */
    filter: blur(6px) brightness(0.85) saturate(1.05);
    transform: scale(1.08);
    z-index: 0;
}}
.hero-bg {{
    z-index: 1;
    opacity: 0;
}}
.hero-overlay {{
    position: absolute; inset: 0; z-index: 2;
    background:
      linear-gradient(180deg, rgba(11,11,15,0.05) 0%, rgba(11,11,15,0.55) 60%, {BG_DEEP} 100%),
      linear-gradient(90deg, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.45) 45%, rgba(0,0,0,0.05) 80%);
}}
.hero-content {{
    position: absolute; inset: 0; z-index: 3;
    padding: 3.5rem 4rem 4rem 4rem;
    display: flex; flex-direction: column; justify-content: flex-end;
    max-width: 880px;
    animation: heroIn .9s cubic-bezier(.2,.7,.2,1) both;
}}
.hero-tag {{
    color: {GOLD};
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}}
.hero-title {{
    font-size: clamp(2.4rem, 5.5vw, 4.6rem);
    font-weight: 900;
    line-height: 1.02;
    margin: 0 0 0.7rem 0;
    text-shadow: 0 6px 30px rgba(0,0,0,0.7);
}}
.hero-meta {{
    color: #E2E2E5;
    font-size: 1rem;
    margin-bottom: 0.7rem;
}}
.hero-meta .dot {{ color: rgba(255,255,255,0.35); margin: 0 0.55rem; }}
.hero-note {{
    display: inline-flex; align-items: center;
    background: {GOLD}; color: #0E0E10;
    font-weight: 800;
    padding: 3px 10px; border-radius: 8px;
    font-size: 0.9rem;
}}
.hero-overview {{
    color: #D3D3D6;
    font-size: 1.05rem;
    line-height: 1.6;
    max-width: 720px;
    margin: 0.4rem 0 1.3rem 0;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
    overflow: hidden;
}}
.hero-actions {{ display: flex; gap: 0.8rem; flex-wrap: wrap; }}
.btn-primary, .btn-ghost {{
    text-decoration: none;
    padding: 13px 24px;
    border-radius: 10px;
    font-weight: 800;
    font-size: 0.98rem;
    transition: transform .15s ease, background .2s ease, color .2s ease, box-shadow .2s ease;
    display: inline-flex; align-items: center; gap: 8px;
}}
.btn-primary {{
    background: {GOLD}; color: #0E0E10;
    box-shadow: 0 8px 25px rgba(245,197,24,0.30);
}}
.btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 14px 32px rgba(245,197,24,0.45); }}
.btn-ghost {{
    background: rgba(255,255,255,0.10);
    color: #FFF; backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.18);
}}
.btn-ghost:hover {{ background: rgba(255,255,255,0.18); transform: translateY(-2px); }}

@keyframes heroIn {{
  from {{ opacity: 0; transform: translateY(28px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ---------- Barre de recherche premium ---------- */
.search-wrap {{
    max-width: 640px;
    margin: -0.5rem auto 2rem auto;
    position: relative;
}}
.search-wrap::before {{
    content: ""; position: absolute;
    left: 18px; top: 50%; transform: translateY(-50%);
    width: 18px; height: 18px;
    background: no-repeat center/contain
      url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23F5C518' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='7'/><path d='m21 21-4.3-4.3'/></svg>");
    z-index: 2; pointer-events: none;
}}
.search-wrap [data-testid="stTextInput"] > div > div {{
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 999px !important;
    transition: border .2s ease, box-shadow .2s ease;
}}
.search-wrap [data-testid="stTextInput"] > div > div:focus-within {{
    border-color: {GOLD} !important;
    box-shadow: 0 0 0 4px rgba(245,197,24,0.15);
}}
.search-wrap [data-testid="stTextInput"] input {{
    background: transparent !important;
    color: #FFF !important;
    padding: 14px 18px 14px 48px !important;
    font-size: 1rem !important;
    border: 0 !important;
}}
.search-wrap [data-testid="stTextInput"] label {{ display: none !important; }}

/* ---------- Carrousel ---------- */
.row-section {{ margin: 2.2rem 0 1.2rem 0; }}
.row-head {{
    display: flex; justify-content: space-between; align-items: baseline;
    margin-bottom: 0.6rem;
}}
.row-title {{
    font-size: 1.45rem; font-weight: 800; letter-spacing: 0.2px;
    padding-left: 14px;
    border-left: 4px solid {GOLD};
}}
.row-sub {{ color: #7e7e87; font-size: 0.85rem; }}
.carousel {{
    display: flex;
    gap: 16px;
    overflow-x: auto;
    overflow-y: hidden;
    scroll-snap-type: x mandatory;
    padding: 12px 4px 22px 4px;
    scrollbar-width: thin;
    scrollbar-color: rgba(245,197,24,0.35) transparent;
}}
.carousel::-webkit-scrollbar {{ height: 10px; }}
.carousel::-webkit-scrollbar-track {{ background: transparent; }}
.carousel::-webkit-scrollbar-thumb {{
    background: rgba(245,197,24,0.30);
    border-radius: 10px;
}}
.carousel::-webkit-scrollbar-thumb:hover {{ background: rgba(245,197,24,0.55); }}

/* ---------- Carte de film ---------- */
.movie {{
    flex: 0 0 180px;
    scroll-snap-align: start;
    text-decoration: none;
    color: inherit;
    border-radius: 12px;
    overflow: hidden;
    background: transparent;
    transition: transform .35s cubic-bezier(.2,.7,.2,1), box-shadow .35s ease;
    position: relative;
}}
.movie:hover {{
    transform: translateY(-6px) scale(1.05);
    box-shadow: 0 18px 38px rgba(0,0,0,0.55), 0 0 0 2px {GOLD};
    z-index: 5;
}}
.movie .poster {{
    position: relative;
    aspect-ratio: 2/3;
    background: #131319;
    border-radius: 12px;
    overflow: hidden;
}}
.movie .poster img {{
    width: 100%; height: 100%; object-fit: cover;
    display: block;
    transition: filter .35s ease;
}}
.movie:hover .poster img {{ filter: brightness(0.78); }}
.movie .badge-note {{
    position: absolute; top: 8px; right: 8px;
    background: {GOLD}; color: #0E0E10;
    font-weight: 800; font-size: 0.78rem;
    padding: 2px 7px; border-radius: 6px;
}}
.movie .badge-rank {{
    position: absolute; top: 8px; left: 8px;
    background: rgba(0,0,0,0.70);
    color: {GOLD}; font-weight: 800; font-size: 0.72rem;
    padding: 2px 8px; border-radius: 999px;
    border: 1px solid rgba(245,197,24,0.4);
}}
.movie .ribbon {{
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 8px 10px;
    background: linear-gradient(180deg, transparent, rgba(0,0,0,0.85));
    color: #FFF;
    font-size: 0.78rem; font-weight: 600;
    opacity: 0; transform: translateY(6px);
    transition: opacity .25s ease, transform .25s ease;
}}
.movie:hover .ribbon {{ opacity: 1; transform: translateY(0); }}
.movie .ribbon b {{ color: {GOLD}; font-weight: 800; }}
.movie .m-title {{
    font-size: 0.92rem;
    font-weight: 700;
    margin: 8px 4px 2px 4px;
    line-height: 1.25;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
    overflow: hidden;
}}
.movie .m-meta {{
    color: #8e8e96;
    font-size: 0.78rem;
    margin: 0 4px 4px 4px;
}}

/* ---------- Bloc détail / casting / trailer ---------- */
.detail-grid {{
    display: grid; grid-template-columns: 1fr 2fr; gap: 24px;
    margin: 0 0 1.4rem 0;
    animation: fadeUp .5s ease both;
}}
.detail-poster img {{
    width: 100%; border-radius: 14px;
    box-shadow: 0 14px 40px rgba(0,0,0,0.55);
}}
.detail-info h2 {{
    font-size: 1.05rem; font-weight: 800;
    color: {GOLD}; letter-spacing: 1px; text-transform: uppercase;
    margin: 0 0 0.5rem 0;
}}
.detail-info p {{ color: #D3D3D6; line-height: 1.6; margin: 0 0 1rem 0; }}
.cast-row {{
    display: flex; flex-wrap: wrap; gap: 14px;
    margin-bottom: 1.2rem;
}}
.cast-card {{
    width: 92px;
    text-align: center;
    transition: transform .25s ease;
}}
.cast-card:hover {{ transform: translateY(-4px); }}
.cast-photo {{
    width: 92px; height: 92px;
    border-radius: 50%;
    overflow: hidden;
    background: #181820;
    border: 2px solid rgba(255,255,255,0.08);
    box-shadow: 0 6px 18px rgba(0,0,0,0.45);
    transition: border-color .25s ease;
    display: flex; align-items: center; justify-content: center;
}}
.cast-photo img {{
    width: 100%; height: 100%;
    object-fit: cover;
    display: block;
}}
.cast-photo .ph-fallback {{
    color: #555;
    font-size: 1.6rem;
    font-weight: 800;
}}
.cast-card:hover .cast-photo {{ border-color: {GOLD}; }}
.cast-name {{
    margin-top: 8px;
    font-size: 0.82rem;
    color: #E8E8EA;
    font-weight: 700;
    line-height: 1.2;
    /* clamp 2 lignes */
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.cast-role {{
    font-size: 0.72rem;
    color: #8e8e96;
    margin-top: 2px;
    font-style: italic;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.director-line {{
    color: #B8B8B8;
    font-size: 0.95rem;
    margin: -0.4rem 0 1rem 0;
}}
.director-line b {{ color: {GOLD}; font-weight: 700; }}
.metric-row {{
    display: grid; grid-template-columns: repeat(4,1fr); gap: 10px;
    margin-top: 0.7rem;
}}
.metric-cell {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 12px 8px;
    text-align: center;
}}
.metric-cell .v {{ font-weight: 800; color: {GOLD}; font-size: 1rem; }}
.metric-cell .l {{
    color: #8e8e96; font-size: 0.7rem;
    letter-spacing: 0.6px; text-transform: uppercase;
    margin-top: 3px;
}}

@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ancres pour scroll */
#recommandations, #detail {{ scroll-margin-top: 20px; }}
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================================
# Sidebar premium
# =====================================================================
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
    st.caption("v0.3 · Sprint 4 · 2026")
    st.markdown("---")
    st.markdown("**Moteur**")
    st.caption(
        "TF-IDF Genres + MinMax (Popularité, Note, Votes) → NearestNeighbors (cosine)."
    )
    st.markdown("---")
    st.caption("Astuce : cliquez sur n'importe quelle affiche pour la mettre en vedette.")


# =====================================================================
# Helpers généraux
# =====================================================================
def yt_id(url) -> str | None:
    if not isinstance(url, str) or not url:
        return None
    m = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{6,})", url)
    return m.group(1) if m else None


def fmt_money(x) -> str:
    if not x or pd.isna(x) or x <= 0:
        return "—"
    if x >= 1_000_000:
        return f"{x/1_000_000:.1f} M€"
    if x >= 1_000:
        return f"{x/1_000:.0f} K€"
    return f"{int(x)} €"


def fmt_int(x) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{int(x):,}".replace(",", " ")


def duration_pretty(minutes) -> str:
    if not minutes or pd.isna(minutes) or minutes <= 0:
        return "—"
    h, m = divmod(int(minutes), 60)
    return f"{h}h{m:02d}" if h else f"{m} min"


def fun_fact(row: pd.Series) -> str:
    """Petite info ludique (intègre Budget/Votes/Recette/Durée/Année en douceur)."""
    budget = float(row.get("Budget") or 0)
    recette = float(row.get("Recette") or 0)
    votes = float(row.get("Votes") or 0)
    duree = float(row.get("Durée") or 0)
    annee = int(row.get("Année") or 0)
    note = float(row.get("Note") or 0)

    if budget > 0 and recette > 0:
        roi = recette / budget
        if roi >= 5:
            return f"Carton au box-office : <b>×{roi:.1f}</b> sa mise"
        if roi >= 1.5:
            return f"Rentabilité solide : <b>×{roi:.1f}</b> le budget"
        return f"Budget couvert à <b>{roi*100:.0f}%</b>"
    if budget > 0:
        if budget < 1_000_000:
            return f"Pépite à petit budget : <b>{fmt_money(budget)}</b>"
        if budget >= 20_000_000:
            return f"Grosse production : <b>{fmt_money(budget)}</b>"
        return f"Budget maîtrisé : <b>{fmt_money(budget)}</b>"
    if votes >= 5000:
        return f"<b>{fmt_int(votes)}</b> spectateurs ont voté"
    if votes >= 500:
        return f"Plébiscité par <b>{fmt_int(votes)}</b> votants"
    if 1 <= votes < 50:
        return f"Pépite confidentielle (<b>{fmt_int(votes)}</b> votes)"
    if duree and duree <= 90:
        return f"Format court : <b>{duration_pretty(duree)}</b>"
    if duree and duree >= 130:
        return f"Soirée longue : <b>{duration_pretty(duree)}</b>"
    if annee and annee < 1990:
        return f"Un classique de <b>{annee}</b>"
    if annee and annee >= 2020:
        return f"Tout frais : <b>{annee}</b>"
    if note >= 7.8:
        return f"Très bien noté : <b>{note:.1f}/10</b>"
    return "Une comédie à découvrir."


# =====================================================================
# API TMDB (uniquement pour backdrop + trailer manquant — cache 24h)
# Le synopsis et le casting viennent maintenant du dataset local.
# =====================================================================
@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def tmdb_details(movie_id: int) -> dict:
    """Backdrop + poster_path + trailer_key + overview FR via TMDB (fallback)."""
    out = {
        "backdrop_path": None,
        "poster_path": None,
        "trailer_key": None,
        "overview": None,
        "cast": [],          # liste de dicts {name, role, photo} ordonnée
        "directors": [],     # liste de noms
    }
    if not movie_id or pd.isna(movie_id):
        return out
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{int(movie_id)}?language=fr-FR",
            headers=TMDB_HEADERS, timeout=5,
        )
        if r.ok:
            j = r.json()
            out["backdrop_path"] = j.get("backdrop_path") or None
            out["poster_path"] = j.get("poster_path") or None
            ov = (j.get("overview") or "").strip()
            out["overview"] = ov or None

        for lang in ("fr-FR", "en-US"):
            rv = requests.get(
                f"https://api.themoviedb.org/3/movie/{int(movie_id)}/videos?language={lang}",
                headers=TMDB_HEADERS, timeout=5,
            )
            if not rv.ok:
                continue
            yt = [
                v for v in rv.json().get("results", [])
                if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser")
            ]
            if yt:
                yt.sort(key=lambda v: (v.get("type") != "Trailer", not v.get("official", False)))
                out["trailer_key"] = yt[0].get("key")
                break

        # Credits : casting et réalisateurs dans l'ordre OFFICIEL
        rc = requests.get(
            f"https://api.themoviedb.org/3/movie/{int(movie_id)}/credits?language=fr-FR",
            headers=TMDB_HEADERS, timeout=5,
        )
        if rc.ok:
            jc = rc.json()
            cast_sorted = sorted(jc.get("cast", []), key=lambda c: c.get("order", 999))
            out["cast"] = [
                {
                    "name": c.get("name") or "",
                    "role": c.get("character") or "",
                    "photo": (
                        f"https://image.tmdb.org/t/p/w300{c['profile_path']}"
                        if c.get("profile_path") else ""
                    ),
                    "person_id": c.get("id") or "",
                }
                for c in cast_sorted if c.get("name")
            ]
            out["directors"] = [
                c.get("name") for c in jc.get("crew", [])
                if c.get("job") == "Director" and c.get("name")
            ]
    except requests.RequestException:
        pass
    return out


def backdrop_url(film: pd.Series) -> str:
    api = tmdb_details(film.get("id"))
    if api.get("backdrop_path"):
        return f"https://image.tmdb.org/t/p/original{api['backdrop_path']}"
    # fallback : poster FR TMDB > poster dataset
    if api.get("poster_path"):
        return f"https://image.tmdb.org/t/p/w780{api['poster_path']}"
    p = film.get("poster_url")
    return p if isinstance(p, str) and p.startswith("http") else ""


def best_poster(film: pd.Series) -> str:
    """Poster FR TMDB en priorité, sinon poster_url du dataset."""
    api = tmdb_details(film.get("id"))
    if api.get("poster_path"):
        return f"https://image.tmdb.org/t/p/w500{api['poster_path']}"
    p = film.get("poster_url")
    if isinstance(p, str) and p.startswith("http"):
        return p
    return "https://via.placeholder.com/500x750/111111/F5C518?text=No+poster"


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def prefetch_posters_fr(ids_tuple: tuple) -> dict:
    """Pré-charge en parallèle les poster_paths FR depuis TMDB pour une liste d'IDs.
    Retourne {movie_id: poster_url_fr}. Cache 24h.
    """
    def _one(mid):
        try:
            r = requests.get(
                f"https://api.themoviedb.org/3/movie/{int(mid)}",
                headers=TMDB_HEADERS,
                params={"language": "fr-FR"},
                timeout=4,
            )
            if r.status_code == 200:
                p = r.json().get("poster_path")
                if p:
                    return int(mid), f"https://image.tmdb.org/t/p/w500{p}"
        except Exception:
            pass
        return int(mid), None

    out: dict = {}
    with ThreadPoolExecutor(max_workers=20) as ex:
        for mid, url in ex.map(_one, ids_tuple):
            if url:
                out[mid] = url
    return out


# Map global rempli avant rendu des carrousels, lu par card_html
POSTER_FR_MAP: dict = {}


def best_youtube_key(row: pd.Series) -> str | None:
    k = yt_id(row.get("youtube_url"))
    if k:
        return k
    return tmdb_details(row.get("id")).get("trailer_key")


def best_overview(row: pd.Series) -> str | None:
    """Synopsis FR du dataset, sinon EN, sinon fallback API TMDB."""
    fr = row.get("Synopsis_fr")
    if isinstance(fr, str) and fr.strip():
        return fr.strip()
    en = row.get("Synopsis")
    if isinstance(en, str) and en.strip():
        return en.strip()
    # Fallback API TMDB (couvre les ~110 films sans synopsis dans le dataset)
    api = tmdb_details(row.get("id"))
    return api.get("overview")


def best_cast(row: pd.Series, n: int = 6) -> list[dict]:
    """Casting principal — TMDB (ordre officiel du générique) en priorité,
    fallback df_people_details local (trié par popularité)."""
    movie_id = row.get("id")
    if pd.isna(movie_id):
        return []
    # 1. API TMDB : ordre officiel du générique (order=0,1,2…)
    api = tmdb_details(movie_id)
    if api.get("cast"):
        return api["cast"][:n]
    # 2. Fallback dataset local
    people = load_people()
    cast = people[
        (people["movie_id"] == int(movie_id))
        & (people["Departement"] == "Acting")
    ].sort_values("Popularité", ascending=False).head(n)
    return [
        {
            "name": r["Prénom"],
            "role": r.get("NomPersonnage") or "",
            "photo": r.get("profile_url") or "",
        }
        for _, r in cast.iterrows()
    ]


def best_director(row: pd.Series) -> str | None:
    """Réalisateur — TMDB en priorité (job == 'Director'),
    fallback dataset local."""
    movie_id = row.get("id")
    if pd.isna(movie_id):
        return None
    api = tmdb_details(movie_id)
    if api.get("directors"):
        # Joindre s'il y a plusieurs co-réalisateurs (ex: Toledano & Nakache)
        return " & ".join(api["directors"][:2])
    # Fallback dataset local
    people = load_people()
    dirs = people[
        (people["movie_id"] == int(movie_id))
        & (people["Departement"] == "Directing")
    ].sort_values("Popularité", ascending=False)
    if dirs.empty:
        return None
    return dirs.iloc[0]["Prénom"]


# =====================================================================
# Données + modèle ML
# =====================================================================
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates(subset=["Titre"], keep="first").reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def load_people() -> pd.DataFrame:
    p = pd.read_csv(PEOPLE_PATH)
    # On garde tout (Acting + Directing) — on filtre au moment de l'usage
    return p


@st.cache_resource(show_spinner=False)
def fit_model(df: pd.DataFrame):
    vectorizer = TfidfVectorizer()
    scaler = MinMaxScaler()
    X_genres = vectorizer.fit_transform(df["Genres"].fillna(""))
    X_num = csr_matrix(
        scaler.fit_transform(df[["Popularité", "Note", "Votes"]].fillna(0))
    )
    X = hstack([X_genres, X_num])
    model = NearestNeighbors(n_neighbors=11, metric="cosine")
    model.fit(X)
    _, indices = model.kneighbors(X)
    return indices


def reco_indices(titre: str, df: pd.DataFrame, indices: np.ndarray, n: int = 10) -> pd.DataFrame:
    sub = df[df["Titre"] == titre]
    if sub.empty:
        return df.iloc[0:0]
    i = sub.index[0]
    return df.iloc[indices[i][1:1 + n]]


with st.spinner("Préparation du moteur cinéma…"):
    df = load_data()
    INDICES = fit_model(df)


# =====================================================================
# Sélection du film en vedette (via query param ?film=…)
# =====================================================================
qp = st.query_params
sel_title = qp.get("film")
if isinstance(sel_title, list):
    sel_title = sel_title[0] if sel_title else None

if not sel_title or sel_title not in df["Titre"].values:
    sel_title = next((t for t in FALLBACK_FILMS if t in df["Titre"].values),
                     df["Titre"].iloc[0])

film = df[df["Titre"] == sel_title].iloc[0]


# =====================================================================
# Helpers de rendu
# =====================================================================
def card_html(row, rank=None):
    title = str(row["Titre"]).replace("'", "&#39;")
    href = "?film=" + urllib.parse.quote(str(row["Titre"]))
    # 1) Poster FR depuis le pré-fetch TMDB, 2) fallback dataset, 3) placeholder
    poster = ""
    try:
        poster = POSTER_FR_MAP.get(int(row["id"]), "") or ""
    except Exception:
        pass
    if not poster:
        poster = row.get("poster_url") or ""
    if not isinstance(poster, str) or not poster.startswith("http"):
        poster = "https://via.placeholder.com/500x750/111111/F5C518?text=No+poster"
    note = float(row.get("Note") or 0)
    annee = int(row.get("Année") or 0)
    duree = duration_pretty(row.get("Durée"))
    genres = " · ".join(
        [g.strip() for g in str(row.get("Genres", "")).split("|") if g.strip()][:2]
    )
    fact = fun_fact(row)
    rank_html = f"<div class='badge-rank'>#{rank}</div>" if rank else ""
    extra_meta = f" · {genres}" if genres else ""
    return (
        f'<a class="movie" href="{href}" target="_self" title="{title}">'
        f'<div class="poster">'
        f'<img src="{poster}" loading="lazy" alt="{title}">'
        f'{rank_html}'
        f'<div class="badge-note">★ {note:.1f}</div>'
        f'<div class="ribbon">{fact}</div>'
        f'</div>'
        f'<div class="m-title">{title}</div>'
        f'<div class="m-meta">{annee} · {duree}{extra_meta}</div>'
        f'</a>'
    )


def render_row(title, films, subtitle="", ranked=False):
    if films.empty:
        return
    cards = "".join(
        card_html(r, rank=(i + 1) if ranked else None)
        for i, (_, r) in enumerate(films.iterrows())
    )
    sub = f"<div class='row-sub'>{subtitle}</div>" if subtitle else ""
    html = (
        '<div class="row-section">'
        '<div class="row-head">'
        f'<div class="row-title">{title}</div>'
        f'{sub}'
        '</div>'
        f'<div class="carousel">{cards}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# =====================================================================
# HERO
# =====================================================================
bg = backdrop_url(film)
genres_main = " · ".join(
    [g.strip() for g in str(film.get("Genres", "")).split("|") if g.strip()]
)
overview_main = best_overview(film) or "Synopsis non disponible pour le moment."
yt_main = best_youtube_key(film)
trailer_btn = (
    '<a class="btn-primary" href="#trailer">Voir la bande-annonce</a>'
    if yt_main else ""
)
genres_html = f'<span class="dot">•</span> {genres_main}' if genres_main else ""

hero_html = (
    '<div class="hero-wrap">'
    f'<div class="hero-bg-blur" style="background-image: url(\'{bg}\');"></div>'
    '<div class="hero-overlay"></div>'
    '<div class="hero-content">'
    '<div class="hero-tag">À l\'affiche</div>'
    f'<h1 class="hero-title">{film["Titre"]}</h1>'
    '<div class="hero-meta">'
    f'<span class="hero-note">★ {float(film["Note"]):.1f}/10</span>'
    f'<span class="dot">•</span> {int(film["Année"])}'
    f'<span class="dot">•</span> {duration_pretty(film["Durée"])}'
    f'{genres_html}'
    '</div>'
    f'<p class="hero-overview">{overview_main}</p>'
    '<div class="hero-actions">'
    f'{trailer_btn}'
    '<a class="btn-ghost" href="#recommandations">Voir les recommandations</a>'
    '</div>'
    '</div>'
    '</div>'
)
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
      <a href="/Recommandation" target="_top" class="active">Recommandation</a>
      <a href="/A_propos" target="_top">À propos</a>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
# =====================================================================
# MODE RECHERCHE — si ?search= est présent, afficher les résultats et stop
# =====================================================================
_search_q = st.query_params.get("search", "")
if isinstance(_search_q, list):
    _search_q = _search_q[0] if _search_q else ""

if _search_q and _search_q.strip():
    _q = _search_q.strip().lower()
    _hits = df[df["Titre"].str.lower().str.contains(re.escape(_q), na=False)]
    st.markdown(
        f"<div style='padding: 5.5rem 2rem 0; max-width:1400px; margin:0 auto;'>"
        f"<div style='color:#b8b8b8;font-size:.9rem;margin-bottom:1rem;'>"
        f"Résultats pour <strong style='color:#F5C518;'>« {_search_q} »</strong> "
        f"— {len(_hits)} film(s) trouvé(s)</div></div>",
        unsafe_allow_html=True,
    )
    if _hits.empty:
        st.info(f"Aucun film ne correspond à « {_search_q} » dans le catalogue.")
    else:
        render_row(
            f"« {_search_q} »",
            _hits,
            subtitle=f"{len(_hits)} film(s) trouvé(s)",
        )
    st.stop()

st.markdown(hero_html, unsafe_allow_html=True)


# =====================================================================
# Bloc détail du film sélectionné
# =====================================================================
st.markdown("<div id='detail'></div>", unsafe_allow_html=True)
poster_main = best_poster(film)
cast_main = best_cast(film, n=6)
director_main = best_director(film)

# Cast cards (photo ronde + nom + rôle)
cast_html = ""
if cast_main:
    cards = []
    for p in cast_main:
        name = (p["name"] or "").replace("'", "&#39;")
        role = (p["role"] or "").replace("'", "&#39;")
        photo = p["photo"]
        person_id = str(p.get("person_id") or "")
        if isinstance(photo, str) and photo.startswith("http"):
            photo_html = f'<img src="{photo}" alt="{name}" loading="lazy">'
        else:
            initial = (name[:1] or "?").upper()
            photo_html = f'<span class="ph-fallback">{initial}</span>'
        role_html = f"<div class='cast-role'>{role}</div>" if role else ""
        import urllib.parse as _up
        if person_id:
            actor_href = f"/Acteur?person_id={person_id}&name={_up.quote(p['name'] or '')}"
            cards.append(
                f"<a class='cast-card' href='{actor_href}' target='_top' style='text-decoration:none;'>"
                f"<div class='cast-photo'>{photo_html}</div>"
                f"<div class='cast-name'>{name}</div>"
                f"{role_html}"
                f"</a>"
            )
        else:
            cards.append(
                f"<div class='cast-card'>"
                f"<div class='cast-photo'>{photo_html}</div>"
                f"<div class='cast-name'>{name}</div>"
                f"{role_html}"
                f"</div>"
            )
    cast_html = "<div class='cast-row'>" + "".join(cards) + "</div>"

director_html = (
    f"<div class='director-line'>Réalisation : <b>{director_main}</b></div>"
    if director_main else ""
)

metrics_html = (
    "<div class='metric-row'>"
    f"<div class='metric-cell'><div class='v'>★ {float(film['Note']):.1f}</div><div class='l'>Note</div></div>"
    f"<div class='metric-cell'><div class='v'>{fmt_int(film['Votes'])}</div><div class='l'>Votes</div></div>"
    f"<div class='metric-cell'><div class='v'>{fmt_money(film['Budget'])}</div><div class='l'>Budget</div></div>"
    f"<div class='metric-cell'><div class='v'>{fmt_money(film['Recette'])}</div><div class='l'>Recette</div></div>"
    "</div>"
)

cast_block = ("<h2>Casting principal</h2>" + cast_html) if cast_html else ""

detail_html = (
    '<div class="detail-grid">'
    '<div class="detail-poster">'
    f'<img src="{poster_main}" alt="{film["Titre"]}">'
    '</div>'
    '<div class="detail-info">'
    '<h2>Synopsis</h2>'
    f'<p>{overview_main}</p>'
    f'{director_html}'
    f'{cast_block}'
    '<h2>En chiffres</h2>'
    f'{metrics_html}'
    '</div>'
    '</div>'
)
st.markdown(detail_html, unsafe_allow_html=True)

if yt_main:
    st.markdown("<div id='trailer'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='row-head'><div class='row-title'>Bande-annonce officielle</div></div>",
        unsafe_allow_html=True,
    )
    st.video(f"https://www.youtube.com/watch?v={yt_main}")


# =====================================================================
# Carrousels thématiques (préparés AVANT le pré-fetch des posters FR)
# =====================================================================
def has_min_votes(d, n=200):
    return d[d["Votes"].fillna(0) >= n]


recos = reco_indices(sel_title, df, INDICES, n=10)
tendances = df.sort_values("Popularité", ascending=False).head(15)
mieux_notes = has_min_votes(df, 300).sort_values("Note", ascending=False).head(15)
cultes = has_min_votes(df, 500)
cultes = cultes[(cultes["Année"] >= 1970) & (cultes["Année"] <= 2010)]
cultes = cultes.sort_values(["Note", "Votes"], ascending=False).head(15)
annees_90 = df[(df["Année"] >= 1990) & (df["Année"] <= 1999)] \
    .sort_values(["Popularité", "Note"], ascending=False).head(15)
annees_80 = df[(df["Année"] >= 1980) & (df["Année"] <= 1989)] \
    .sort_values(["Popularité", "Note"], ascending=False).head(15)
recents = df[df["Année"] >= 2020].sort_values("Popularité", ascending=False).head(15)
pepites = df[
    (df["Note"] >= 7.0)
    & (df["Votes"].fillna(0) < 200)
    & (df["Votes"].fillna(0) >= 5)
].sort_values("Note", ascending=False).head(15)

# Pré-fetch parallèle des posters FR pour TOUS les films affichés (caché 24h)
_all_ids = set()
for _block in (recos, tendances, mieux_notes, cultes, annees_90, annees_80, recents, pepites):
    if _block is not None and not _block.empty:
        for _v in _block["id"].dropna().tolist():
            try:
                _all_ids.add(int(_v))
            except Exception:
                pass
POSTER_FR_MAP = prefetch_posters_fr(tuple(sorted(_all_ids)))


# ─── Rendu des carrousels ────────────────────────────────────
st.markdown("<div id='recommandations'></div>", unsafe_allow_html=True)
render_row(
    "Films similaires",
    recos,
    subtitle="Genres et notes",
    ranked=True,
)
render_row("Les mieux notés", mieux_notes,
           subtitle="Sélection critique du catalogue", ranked=True)
render_row("Comédies cultes", cultes,
           subtitle="Les incontournables qui ont marqué le cinéma français")
render_row("Années 90", annees_90,
           subtitle="Retour vers la décennie dorée de la comédie FR")
render_row("Années 80", annees_80,
           subtitle="Le grand boum de la comédie populaire")

if not recents.empty:
    render_row("Récemment ajoutés", recents, subtitle="Sorties après 2020")

if not pepites.empty:
    render_row("Pépites cachées", pepites,
               subtitle="Bien notés, peu connus — à découvrir")

st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
