"""Page acteur — biographie + filmographie TMDB."""
from __future__ import annotations

import requests
import streamlit as st

# ──────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Acteur — DATAFIX",
    page_icon="🎬",
    layout="wide",
)

GOLD      = "#F5C518"
BG_DEEP   = "#0E1117"
BG_SOFT   = "#161B22"
TXT       = "#E8E8EC"

TMDB_BEARER = (
    "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5Y2IwZTY2ZDU4M2NlMjRlNzhkMWIyNzc2YmUxYTJiMCIs"
    "Im5iZiI6MTc3NzI5NjYzNS4wODksInN1YiI6IjY5ZWY2NGZiYTQ5YzYxY2QwNzE1MWFiNiIsInNj"
    "b3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.kcNXcdjcIvWsz84XKCFBrOopCYfR7g4yg-IMIV2YYbU"
)
TMDB_HEADERS = {"accept": "application/json", "Authorization": f"Bearer {TMDB_BEARER}"}

# ──────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
* {{ font-family: 'Inter', sans-serif; box-sizing: border-box; }}
:root {{ --gold: {GOLD}; }}
.stApp {{ background: {BG_DEEP}; color: {TXT}; }}
[data-testid="stHeader"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
section.main > div {{ padding: 0 !important; }}
footer, #MainMenu {{ visibility: hidden; }}

/* NAVBAR */
.topnav {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  background: rgba(14,17,23,0.92);
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
.topnav-search input {{
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px; padding: 0.35rem 1rem;
  color: #fff; font-size: 0.85rem; width: 260px;
  outline: none; transition: border 0.2s;
}}
.topnav-search input:focus {{ border-color: {GOLD}; }}
.topnav-search input::placeholder {{ color: rgba(255,255,255,0.4); }}
.topnav-links {{ display: flex; gap: 2rem; }}
.topnav-links a {{
  color: #D8D8DC !important; text-decoration: none !important;
  font-weight: 600; font-size: 0.9rem;
  padding: 0.4rem 0.8rem; border-radius: 8px;
  transition: all 0.2s ease;
}}
.topnav-links a:hover {{ color: {GOLD} !important; background: rgba(245,197,24,0.08); }}

/* PAGE */
.actor-page {{
  max-width: 1100px; margin: 0 auto;
  padding: 6rem 2rem 4rem;
}}
.back-btn {{
  display: inline-flex; align-items: center; gap: 0.4rem;
  color: {GOLD}; text-decoration: none; font-weight: 600;
  font-size: 0.9rem; margin-bottom: 2.5rem;
  opacity: 0.85; transition: opacity .2s;
}}
.back-btn:hover {{ opacity: 1; }}
.actor-header {{
  display: flex; gap: 2.5rem; align-items: flex-start;
  margin-bottom: 3rem;
}}
.actor-photo {{
  width: 200px; height: 280px; object-fit: cover;
  border-radius: 14px; flex-shrink: 0;
  box-shadow: 0 8px 32px rgba(0,0,0,0.6);
}}
.actor-photo-placeholder {{
  width: 200px; height: 280px; border-radius: 14px;
  background: {BG_SOFT}; display: flex; align-items: center;
  justify-content: center; font-size: 4rem; flex-shrink: 0;
  color: rgba(255,255,255,0.3);
}}
.actor-info h1 {{
  color: {GOLD}; font-size: 2.2rem; font-weight: 900;
  margin: 0 0 0.4rem;
}}
.actor-meta {{
  color: rgba(255,255,255,0.5); font-size: 0.88rem;
  margin-bottom: 1.2rem;
}}
.actor-bio {{
  color: #ccc; font-size: 0.95rem; line-height: 1.75;
  max-width: 680px;
}}
.section-title {{
  color: {GOLD}; font-size: 1.3rem; font-weight: 800;
  margin: 2.5rem 0 1.2rem;
  border-left: 3px solid {GOLD}; padding-left: 0.8rem;
}}
.film-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 1.2rem;
}}
.film-card {{
  text-decoration: none; color: {TXT};
  transition: transform .2s;
}}
.film-card:hover {{ transform: translateY(-4px); }}
.film-card img {{
  width: 100%; border-radius: 8px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.5);
}}
.film-card-title {{
  font-size: 0.8rem; margin-top: 0.4rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.film-card-year {{
  font-size: 0.72rem; color: rgba(255,255,255,0.4);
}}
.no-poster {{
  width: 100%; aspect-ratio: 2/3; border-radius: 8px;
  background: {BG_SOFT}; display: flex; align-items: center;
  justify-content: center; font-size: 2rem; color: rgba(255,255,255,0.2);
}}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# Navbar
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="topnav">
  <div class="topnav-inner">
    <a href="/" target="_top" class="topnav-brand">DATAFIX</a>
    <form class="topnav-search" action="/Recommandation" method="get" target="_top">
      <input type="text" name="search" placeholder="Rechercher un film dans le catalogue…" autocomplete="off" />
    </form>
    <div class="topnav-links">
      <a href="/" target="_top">Accueil</a>
      <a href="/Recommandation" target="_top">Recommandation</a>
      <a href="/A_propos" target="_top">À propos</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# Params
# ──────────────────────────────────────────────────────────────
qp = st.query_params
person_id = qp.get("person_id")
person_name = qp.get("name", "Acteur inconnu")

if not person_id:
    st.markdown("""
    <div class="actor-page">
      <a class="back-btn" href="/Recommandation" target="_top">← Retour</a>
      <p style="color:#b8b8b8;">Aucun acteur sélectionné.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ──────────────────────────────────────────────────────────────
# TMDB fetch
# ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_person(pid: str) -> dict:
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/person/{pid}?language=fr-FR",
            headers=TMDB_HEADERS, timeout=6,
        )
        return r.json() if r.ok else {}
    except Exception:
        return {}

@st.cache_data(ttl=3600)
def fetch_credits(pid: str) -> list[dict]:
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/person/{pid}/movie_credits?language=fr-FR",
            headers=TMDB_HEADERS, timeout=6,
        )
        if not r.ok:
            return []
        data = r.json()
        movies = data.get("cast", [])
        movies = sorted(movies, key=lambda m: m.get("popularity", 0), reverse=True)
        return movies
    except Exception:
        return []

person  = fetch_person(str(person_id))
credits = fetch_credits(str(person_id))

# ──────────────────────────────────────────────────────────────
# Build HTML
# ──────────────────────────────────────────────────────────────
name     = person.get("name") or person_name
birthday = person.get("birthday") or ""
place    = person.get("place_of_birth") or ""
bio      = person.get("biography") or "Biographie non disponible pour cet acteur."
photo    = person.get("profile_path")

photo_html = (
    f'<img class="actor-photo" src="https://image.tmdb.org/t/p/w300{photo}" alt="{name}">'
    if photo
    else f'<div class="actor-photo-placeholder">?</div>'
)

meta_parts = []
if birthday:
    meta_parts.append(f"📅 Né(e) le {birthday}")
if place:
    meta_parts.append(f"📍 {place}")
meta_html = " &nbsp;·&nbsp; ".join(meta_parts) if meta_parts else ""

# Film grid — keep best 24 with poster
films_with_poster = [m for m in credits if m.get("poster_path")][:24]
films_without     = [m for m in credits if not m.get("poster_path")]

film_cards = ""
for m in films_with_poster:
    title = (m.get("title") or "").replace("'", "&#39;")
    year  = str(m.get("release_date") or "")[:4]
    href  = f"/Recommandation?film={__import__('urllib.parse', fromlist=['quote']).quote(m.get('title',''))}"
    film_cards += (
        f'<a class="film-card" href="{href}" target="_top" title="{title}">'
        f'<img src="https://image.tmdb.org/t/p/w185{m["poster_path"]}" alt="{title}" loading="lazy">'
        f'<div class="film-card-title">{title}</div>'
        f'<div class="film-card-year">{year}</div>'
        f'</a>'
    )

if not film_cards:
    film_cards = '<p style="color:#b8b8b8;">Aucune filmographie disponible.</p>'

films_section = (
    f'<div class="section-title">Filmographie ({len(films_with_poster)} films)</div>'
    f'<div class="film-grid">{film_cards}</div>'
)

page_html = f"""
<div class="actor-page">
  <a class="back-btn" href="/Recommandation" target="_top">← Retour</a>
  <div class="actor-header">
    {photo_html}
    <div class="actor-info">
      <h1>{name}</h1>
      <div class="actor-meta">{meta_html}</div>
      <div class="actor-bio">{bio}</div>
    </div>
  </div>
  {films_section}
</div>
"""

st.markdown(page_html, unsafe_allow_html=True)
