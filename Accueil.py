"""Page Accueil - DATAFIX (refonte cinéma premium)."""

from base64 import b64encode
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="DATAFIX – Accueil",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────────
GOLD = "#F5C518"
BG_DEEP = "#0E1117"
BG_SOFT = "#15161C"
TXT_PRIMARY = "#FFFFFF"
TXT_MUTED = "#B8B8B8"

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "df_film.csv"
LOGO = BASE_DIR / "asset" / "logo.png"

TMDB_BEARER = (
    "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5Y2IwZTY2ZDU4M2NlMjRlNzhkMWIyNzc2YmUxYTJiMCIs"
    "Im5iZiI6MTc3NzI5NjYzNS4wODksInN1YiI6IjY5ZWY2NGZiYTQ5YzYxY2QwNzE1MWFiNiIsInNj"
    "b3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.kcNXcdjcIvWsz84XKCFBrOopCYfR7g4yg-IMIV2YYbU"
)
TMDB_HEADERS = {"accept": "application/json", "Authorization": f"Bearer {TMDB_BEARER}"}

CULTES = [
    "Intouchables",
    "Le Fabuleux Destin d'Amélie Poulain",
    "Bienvenue chez les Ch'tis",
    "Le Dîner de cons",
    "OSS 117 : Le Caire, nid d'espions",
    "Les Visiteurs",
    "Astérix & Obélix : Mission Cléopâtre",
    "La Grande Vadrouille",
]

EXPRESS_CHOICES = [
    "Intouchables",
    "Le Fabuleux Destin d'Amélie Poulain",
    "OSS 117 : Le Caire, nid d'espions",
    "Bienvenue chez les Ch'tis",
]


# ─────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_df() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Année"] = pd.to_numeric(df["Année"], errors="coerce")
    df["Popularité"] = pd.to_numeric(df["Popularité"], errors="coerce").fillna(0)
    df["Note"] = pd.to_numeric(df["Note"], errors="coerce").fillna(0)
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0)
    return df


@st.cache_data(ttl=86400)
def tmdb_paths(movie_id: int) -> dict:
    """Retourne {'backdrop': url, 'poster': url} en version française."""
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{int(movie_id)}",
            headers=TMDB_HEADERS,
            params={"language": "fr-FR"},
            timeout=5,
        )
        if r.status_code == 200:
            d = r.json()
            b = d.get("backdrop_path") or ""
            p = d.get("poster_path") or ""
            return {
                "backdrop": f"https://image.tmdb.org/t/p/original{b}" if b else "",
                "poster": f"https://image.tmdb.org/t/p/w500{p}" if p else "",
            }
    except Exception:
        pass
    return {"backdrop": "", "poster": ""}


def tmdb_backdrop(movie_id: int) -> str:
    return tmdb_paths(movie_id).get("backdrop", "")


def find_row(df: pd.DataFrame, title: str):
    m = df[df["Titre"].str.lower() == title.lower()]
    if m.empty:
        m = df[df["Titre"].str.contains(title, case=False, na=False, regex=False)]
    return m.iloc[0] if not m.empty else None


def safe_poster(row) -> str:
    if row is None:
        return ""
    p = row.get("poster_url", "")
    return p if isinstance(p, str) else ""


def best_poster(row) -> str:
    """Priorise le poster TMDB en version française, fallback dataset."""
    if row is None:
        return ""
    try:
        p = tmdb_paths(int(row["id"])).get("poster", "")
        if p:
            return p
    except Exception:
        pass
    return safe_poster(row)


def creuse_image_url() -> str:
    """Cherche une photo de la Creuse posée par l'utilisateur dans asset/.
    Si trouvée, l'encode en base64 (garantie d'affichage). Sinon, fallback Unsplash.
    Pour personnaliser : déposez 'creuse.jpg' (ou .jpeg/.png/.webp) dans datafix-application/asset/.
    """
    for name in ("creuse.jpg", "creuse.jpeg", "creuse.png", "creuse.webp"):
        p = BASE_DIR / "asset" / name
        if p.exists():
            ext = p.suffix.lstrip(".").lower().replace("jpg", "jpeg")
            b = b64encode(p.read_bytes()).decode()
            return f"data:image/{ext};base64,{b}"
    # Fallback : façade du Cinéma Le Sénéchal de Guéret (Creuse)
    return (
        "https://woody.cloudly.space/app/uploads/tourisme-creuse/2022/01/thumbs/"
        "le-senechal-general-chapeau-1920x1080.jpg"
    )


df = load_df()

# Hero film (Intouchables prioritaire, fallback Amélie)
hero_row = find_row(df, "Intouchables")
if hero_row is None:
    hero_row = find_row(df, "Amélie")
hero_backdrop = tmdb_backdrop(int(hero_row["id"])) if hero_row is not None else ""
creuse_bg = creuse_image_url()

# Stats globales
annee_min = int(df["Année"].dropna().min()) if df["Année"].notna().any() else 1960
annee_max = int(df["Année"].dropna().max()) if df["Année"].notna().any() else 2025
note_moy = round(float(df["Note"].mean()), 2)

# ─────────────────────────────────────────────────────────────
# CSS — ambiance cinéma premium
# ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
:root {{
  --gold: {GOLD};
  --bg-deep: {BG_DEEP};
  --bg-soft: {BG_SOFT};
  --txt: {TXT_PRIMARY};
  --muted: {TXT_MUTED};
}}

.stApp {{ background: var(--bg-deep); color: var(--txt); }}
[data-testid="stHeader"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
section.main > div {{ padding: 0 !important; }}
footer, #MainMenu {{ visibility: hidden; }}

/* NAVBAR custom (toujours visible) */
.topnav {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  background: rgba(14,17,23,0.72);
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

/* HERO */
.hero {{
  position: relative; width: 100%; min-height: 92vh;
  display: flex; align-items: center; justify-content: center;
  text-align: center; overflow: hidden; background-color: #000;
}}
.hero-bg {{
  position: absolute; inset: 0;
  background-image: url('{hero_backdrop}');
  background-size: cover; background-position: center;
  filter: brightness(0.55) saturate(1.1);
  transform: scale(1.05);
  animation: heroIn 1.6s ease-out both;
}}
.hero-overlay {{
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at center, rgba(0,0,0,0.30) 0%, rgba(14,17,23,0.92) 85%),
    linear-gradient(180deg, rgba(14,17,23,0.45) 0%, rgba(14,17,23,0.98) 100%);
}}
.hero-content {{
  position: relative; z-index: 2; max-width: 1100px; padding: 0 2rem;
  animation: fadeUp 1.2s ease-out 0.3s both;
}}
.hero-eyebrow {{
  display: inline-block; letter-spacing: 0.42em; font-size: 0.78rem;
  font-weight: 700; color: var(--gold);
  border: 1px solid rgba(245,197,24,0.4);
  padding: 0.4rem 1rem; border-radius: 999px; margin-bottom: 1.8rem;
  text-transform: uppercase;
}}
.hero-title {{
  font-size: clamp(2.6rem, 6vw, 5.4rem); font-weight: 900;
  line-height: 1.05; margin: 0 0 1.4rem 0;
  letter-spacing: -0.02em; color: var(--txt);
}}
.hero-title em {{ color: var(--gold); font-style: normal; }}
.hero-subtitle {{
  font-size: clamp(1.05rem, 1.6vw, 1.35rem); line-height: 1.6;
  color: var(--muted); max-width: 720px; margin: 0 auto 2.6rem auto;
}}
.hero-ctas {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
.btn {{
  display: inline-block; padding: 1rem 2.2rem; border-radius: 999px;
  font-weight: 700; font-size: 1rem; letter-spacing: 0.02em;
  text-decoration: none !important; transition: all 0.25s ease;
  cursor: pointer; border: none;
}}
.btn-primary {{
  background: var(--gold); color: #0E0E10 !important;
  box-shadow: 0 10px 30px rgba(245,197,24,0.25);
}}
.btn-primary:hover {{
  transform: translateY(-2px);
  box-shadow: 0 14px 36px rgba(245,197,24,0.45);
}}
.btn-ghost {{
  background: rgba(255,255,255,0.06); color: var(--txt) !important;
  border: 1px solid rgba(255,255,255,0.18); backdrop-filter: blur(8px);
}}
.btn-ghost:hover {{
  background: rgba(255,255,255,0.12);
  border-color: rgba(245,197,24,0.5); transform: translateY(-2px);
}}
.hero-scroll {{
  position: absolute; bottom: 2rem; left: 50%;
  transform: translateX(-50%); color: var(--muted);
  font-size: 0.78rem; letter-spacing: 0.3em;
  text-transform: uppercase; z-index: 2; opacity: 0.7;
}}

/* STATS */
.stats-bar {{
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
  max-width: 1000px; margin: -4rem auto 0 auto; padding: 2rem;
  background: rgba(21,22,28,0.85);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px; backdrop-filter: blur(12px);
  position: relative; z-index: 3;
  box-shadow: 0 30px 60px rgba(0,0,0,0.5);
}}
.stat {{ text-align: center; padding: 0.5rem; border-right: 1px solid rgba(255,255,255,0.05); }}
.stat:last-child {{ border-right: none; }}
.stat-num {{
  font-size: clamp(1.8rem, 3vw, 2.6rem); font-weight: 900;
  color: var(--gold); line-height: 1;
}}
.stat-label {{
  margin-top: 0.5rem; font-size: 0.78rem; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--muted);
}}

/* SECTIONS */
.section {{ max-width: 1300px; margin: 0 auto; padding: 6rem 2rem 2rem 2rem; }}
.section-eyebrow {{
  color: var(--gold); font-size: 0.78rem; letter-spacing: 0.35em;
  font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;
}}
.section-title {{
  font-size: clamp(2rem, 3.5vw, 3rem); font-weight: 900;
  letter-spacing: -0.01em; margin: 0 0 1rem 0; color: var(--txt);
}}
.section-lead {{
  color: var(--muted); font-size: 1.1rem; line-height: 1.7;
  max-width: 720px; margin: 0 0 3rem 0;
}}

/* STORY */
.story-grid {{ display: grid; grid-template-columns: 1.1fr 1fr; gap: 3rem; align-items: center; }}
.story-visual {{
  position: relative; border-radius: 22px; overflow: hidden;
  aspect-ratio: 4/3;
  background-image: url('{creuse_bg}');
  background-size: cover; background-position: center;
  border: 1px solid rgba(245,197,24,0.2);
}}
.story-visual::after {{
  content: ''; position: absolute; inset: 0;
  background:
    linear-gradient(180deg, transparent 55%, rgba(14,17,23,0.85) 100%),
    linear-gradient(135deg, rgba(245,197,24,0.05) 0%, transparent 40%);
}}
.story-badge {{
  position: absolute; bottom: 1.5rem; left: 1.5rem; z-index: 2;
  padding: 0.5rem 1rem; background: var(--gold); color: #0E0E10;
  font-weight: 800; border-radius: 999px; font-size: 0.85rem; letter-spacing: 0.1em;
}}
.story-text h3 {{
  font-size: clamp(1.6rem, 2.6vw, 2.2rem); font-weight: 800;
  margin: 0 0 1.2rem 0; line-height: 1.2;
}}
.story-text p {{
  color: var(--muted); font-size: 1.05rem; line-height: 1.75; margin: 0 0 1rem 0;
}}
.story-list {{ margin-top: 1.5rem; display: flex; flex-direction: column; gap: 0.8rem; }}
.story-list-item {{ display: flex; align-items: center; gap: 0.8rem; color: var(--txt); font-size: 1rem; }}
.story-list-item::before {{
  content: ''; display: inline-block; width: 8px; height: 8px;
  background: var(--gold); border-radius: 50%; flex-shrink: 0;
}}

/* CARROUSEL */
.row {{ margin: 4rem auto; max-width: 1400px; padding: 0 2rem; }}
.row-head {{ display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 1.5rem; }}
.row-title {{ font-size: 1.5rem; font-weight: 800; color: var(--txt); letter-spacing: -0.01em; }}
.row-sub {{ color: var(--muted); font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase; }}
.cards {{
  display: flex; gap: 1rem; overflow-x: auto;
  scroll-snap-type: x mandatory; padding-bottom: 1.2rem;
  scrollbar-width: thin; scrollbar-color: rgba(245,197,24,0.4) transparent;
}}
.cards::-webkit-scrollbar {{ height: 8px; }}
.cards::-webkit-scrollbar-thumb {{ background: rgba(245,197,24,0.4); border-radius: 4px; }}
.card {{
  flex: 0 0 200px; scroll-snap-align: start; position: relative;
  border-radius: 14px; overflow: hidden; background: var(--bg-soft);
  text-decoration: none !important;
  transition: transform 0.35s ease, box-shadow 0.35s ease;
  border: 1px solid rgba(255,255,255,0.05); cursor: pointer;
}}
.card:hover {{
  transform: translateY(-8px) scale(1.04);
  box-shadow: 0 18px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(245,197,24,0.5);
  z-index: 5;
}}
.card-poster {{
  width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block; background: #1a1b22;
}}
.card-rank {{
  position: absolute; top: 0.6rem; left: 0.6rem;
  background: rgba(0,0,0,0.78); color: var(--gold);
  font-weight: 900; font-size: 1.6rem; width: 42px; height: 42px;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(245,197,24,0.5);
}}
.card-note {{
  position: absolute; top: 0.6rem; right: 0.6rem;
  background: var(--gold); color: #0E0E10; font-weight: 800;
  font-size: 0.82rem; padding: 0.25rem 0.55rem; border-radius: 6px;
}}
.card-info {{
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 1.2rem 0.8rem 0.8rem 0.8rem;
  background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.95) 70%);
  color: var(--txt);
}}
.card-title {{
  font-size: 0.92rem; font-weight: 700; margin: 0; line-height: 1.25;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.card-meta {{ font-size: 0.75rem; color: var(--muted); margin-top: 0.25rem; }}

/* METHODE */
.method-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; margin-top: 2rem; }}
.method-card {{
  padding: 2rem 1.6rem; background: var(--bg-soft); border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.07); transition: all 0.3s ease;
}}
.method-card:hover {{ border-color: rgba(245,197,24,0.4); transform: translateY(-4px); }}
.method-num {{ color: var(--gold); font-weight: 900; font-size: 0.85rem; letter-spacing: 0.15em; margin-bottom: 1rem; }}
.method-title {{ font-size: 1.15rem; font-weight: 800; margin: 0 0 0.8rem 0; color: var(--txt); }}
.method-text {{ color: var(--muted); font-size: 0.92rem; line-height: 1.6; }}

/* RECO EXPRESS */
.express {{
  max-width: 1200px; margin: 5rem auto; padding: 4rem 2rem;
  background:
    radial-gradient(ellipse at top left, rgba(245,197,24,0.12) 0%, transparent 50%),
    var(--bg-soft);
  border-radius: 28px; border: 1px solid rgba(245,197,24,0.18); text-align: center;
}}
.express h3 {{ font-size: clamp(1.8rem, 3vw, 2.5rem); font-weight: 900; margin: 0 0 0.8rem 0; }}
.express p {{ color: var(--muted); font-size: 1.05rem; margin: 0 0 2.5rem 0; }}
.express-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; max-width: 900px; margin: 0 auto; }}
.express-card {{
  position: relative; border-radius: 14px; overflow: hidden; aspect-ratio: 2/3;
  text-decoration: none !important; transition: all 0.3s ease;
  border: 1px solid rgba(255,255,255,0.08); cursor: pointer; background: #1a1b22;
}}
.express-card:hover {{
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(245,197,24,0.3);
  border-color: var(--gold);
}}
.express-card img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.express-card-label {{
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 1.2rem 0.7rem 0.7rem 0.7rem;
  background: linear-gradient(180deg, transparent, rgba(0,0,0,0.92));
  color: var(--txt); font-size: 0.85rem; font-weight: 700; text-align: left;
}}

/* FOOTER */
.footer {{
  margin-top: 6rem; padding: 3rem 2rem 2rem 2rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  text-align: center; color: var(--muted);
}}
.footer-brand {{
  color: var(--gold); font-weight: 800; letter-spacing: 0.15em;
  font-size: 0.95rem; margin-bottom: 0.6rem;
}}
.footer-links {{
  margin-top: 1rem; display: flex; justify-content: center;
  gap: 2rem; flex-wrap: wrap; font-size: 0.85rem;
}}
.footer-links a {{ color: var(--muted); text-decoration: none; transition: color 0.2s ease; }}
.footer-links a:hover {{ color: var(--gold); }}
.footer-bottom {{ margin-top: 1.5rem; font-size: 0.75rem; letter-spacing: 0.1em; opacity: 0.6; }}

/* ANIMATIONS */
@keyframes heroIn {{
  from {{ transform: scale(1.15); opacity: 0; }}
  to {{ transform: scale(1.05); opacity: 1; }}
}}
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(30px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

@media (max-width: 900px) {{
  .story-grid {{ grid-template-columns: 1fr; }}
  .method-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .express-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .stats-bar {{ grid-template-columns: repeat(2, 1fr); }}
  .card {{ flex: 0 0 150px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
    st.caption("v0.3 · Sprint 4 · 2026")

# ─── NAVBAR (toujours visible) ───────────────────────────────
st.markdown(
    """
<div class="topnav">
  <div class="topnav-inner">
    <a href="/" target="_top" class="topnav-brand">DATAFIX</a>
    <form class="topnav-search" action="/Recommandation" method="get" target="_top">
      <input type="text" name="search" placeholder="Rechercher un film dans le catalogue…" autocomplete="off" />
    </form>
    <div class="topnav-links">
      <a href="/" target="_top" class="active">Accueil</a>
      <a href="/Recommandation" target="_top">Recommandation</a>
      <a href="/A_propos" target="_top">À propos</a>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── 1. HERO ─────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
  <div class="hero-bg"></div>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-eyebrow">DATAFIX · Cinéma de la Creuse</div>
    <h1 class="hero-title">
      Le cinéma de la Creuse,<br/>réinventé par la <em>data</em>.
    </h1>
    <p class="hero-subtitle">
      Retrouvez les meilleures comédies françaises adaptées aux goûts du public creusois.
      Un moteur de recommandation pensé pour le territoire.
    </p>
    <div class="hero-ctas">
      <a href="Recommandation" target="_self" class="btn btn-primary">Découvrir les films</a>
      <a href="Recommandation?film=Intouchables" target="_self" class="btn btn-ghost">Obtenir une recommandation</a>
    </div>
  </div>
  <div class="hero-scroll">▼ Faites défiler</div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── 2. STATS ────────────────────────────────────────────────
st.markdown(
    f"""
<div class="stats-bar">
  <div class="stat">
    <div class="stat-num">{annee_max - annee_min}+</div>
    <div class="stat-label">Années de cinéma</div>
  </div>
  <div class="stat">
    <div class="stat-num">{note_moy}</div>
    <div class="stat-label">Note moyenne</div>
  </div>
  <div class="stat">
    <div class="stat-num">100%</div>
    <div class="stat-label">Français</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── 3. STORY — LE CINÉMA DE LA CREUSE ───────────────────────
st.markdown(
    """
<div class="section">
  <div class="story-grid">
    <div class="story-visual">
      <div class="story-badge">CREUSE · 23</div>
    </div>
    <div class="story-text">
      <div class="section-eyebrow">Notre territoire</div>
      <h3>Un cinéma pensé pour les habitants de la Creuse.</h3>
      <p>
        Des films fédérateurs, populaires et intergénérationnels.
        Un cinéma local, chaleureux et accessible à toutes les générations,
        au cœur d'un territoire authentique.
      </p>
      <div class="story-list">
        <div class="story-list-item">Une programmation pensée pour le public rural</div>
        <div class="story-list-item">Des comédies françaises cultes et accessibles</div>
        <div class="story-list-item">Une expérience cinéma de proximité</div>
        <div class="story-list-item">Des recommandations adaptées à toutes les générations</div>
      </div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ─── Helpers card ────────────────────────────────────────────
def render_card(row, rank=None) -> str:
    poster = best_poster(row)
    title = str(row["Titre"]).replace('"', "'")
    annee = ""
    if pd.notna(row.get("Année")):
        try:
            annee = str(int(row["Année"]))
        except Exception:
            annee = ""
    note = ""
    if pd.notna(row.get("Note")) and float(row["Note"]) > 0:
        note = f"{float(row['Note']):.1f}"
    href = f"Recommandation?film={quote(str(row['Titre']))}"
    rank_html = f'<div class="card-rank">{rank}</div>' if rank else ""
    note_html = f'<div class="card-note">{note}</div>' if note else ""
    poster_html = (
        f'<img class="card-poster" src="{poster}" alt="{title}" loading="lazy"/>'
        if poster
        else '<div class="card-poster"></div>'
    )
    return (
        f'<a class="card" href="{href}" target="_self" title="{title}">'
        f"{poster_html}{rank_html}{note_html}"
        f'<div class="card-info">'
        f'<div class="card-title">{title}</div>'
        f'<div class="card-meta">{annee}</div>'
        f"</div></a>"
    )


def render_row(title: str, eyebrow: str, films, ranked: bool = False) -> None:
    cards_html = "".join(
        render_card(r, rank=i + 1 if ranked else None) for i, r in enumerate(films)
    )
    st.markdown(
        f"""
<div class="row">
  <div class="row-head">
    <div class="row-title">{title}</div>
    <div class="row-sub">{eyebrow}</div>
  </div>
  <div class="cards">{cards_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ─── 4. CARROUSEL "LES INCONTOURNABLES" ──────────────────────
cultes_rows = []
seen_ids = set()
for t in CULTES:
    r = find_row(df, t)
    if r is not None and r["id"] not in seen_ids:
        cultes_rows.append(r)
        seen_ids.add(r["id"])

render_row("Les incontournables", "À voir absolument", cultes_rows, ranked=False)

# ─── 5. POURQUOI CES FILMS ───────────────────────────────────
st.markdown(
    """
<div class="section">
  <div class="section-eyebrow">Notre méthode</div>
  <h2 class="section-title">Pourquoi ces films ?</h2>
  <div class="method-grid">
    <div class="method-card">
      <div class="method-num">01</div>
      <div class="method-title">Préférences du public</div>
      <div class="method-text">
        Analyse des comédies françaises les plus appréciées
        par tranche d'âge et profil de spectateurs.
      </div>
    </div>
    <div class="method-card">
      <div class="method-num">02</div>
      <div class="method-title">Notes TMDB</div>
      <div class="method-text">
        Plus de 800 films notés par les communautés
        cinéma françaises et internationales.
      </div>
    </div>
    <div class="method-card">
      <div class="method-num">03</div>
      <div class="method-title">Habitudes locales</div>
      <div class="method-text">
        Une programmation pensée pour un public rural,
        familial et intergénérationnel.
      </div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── 7. RECOMMANDATION EXPRESS ───────────────────────────────
express_cards_html = ""
for t in EXPRESS_CHOICES:
    r = find_row(df, t)
    if r is not None:
        poster = best_poster(r)
        title = str(r["Titre"]).replace('"', "'")
        href = f"Recommandation?film={quote(str(r['Titre']))}"
        img_html = (
            f'<img src="{poster}" alt="{title}" loading="lazy"/>'
            if poster
            else ""
        )
        express_cards_html += (
            f'<a class="express-card" href="{href}" target="_self">'
            f'{img_html}'
            f'<div class="express-card-label">{title}</div>'
            f'</a>'
        )

st.markdown(
    f"""
<div class="express">
  <h3>Vous ne savez pas quoi choisir ?</h3>
  <p>Laissez-vous guider par nos coups de cœur — cliquez sur un film pour obtenir vos recommandations personnalisées.</p>
  <div class="express-grid">
    {express_cards_html}
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
    <a href="Recommandation" target="_self">Recommandation</a>
    <a href="A_propos" target="_self">À propos</a>
    <a href="https://www.themoviedb.org/" target="_blank">TMDB</a>
  </div>
  <div class="footer-bottom">Wild Code School · Cinéma de la Creuse · Sprint 4 · 2026</div>
</div>
""",
    unsafe_allow_html=True,
)
