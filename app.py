import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from parser import parse_chat
from features import compute_features
from personality import classify
from aliases import ALIASES

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Wordle People",
    page_icon="🟩",
    layout="wide",
)

# ── Load data (cached so pages share the same objects) ────────────────────────

DATA_PATH = Path(__file__).parent / "data" / "whatsapp_export.txt"


@st.cache_data
def load_data():
    df = parse_chat(DATA_PATH, aliases=ALIASES)
    features = compute_features(df)
    classified = classify(features)
    return df, features, classified


# Expose to session state so pages can access without re-loading
if "df" not in st.session_state:
    df, features, classified = load_data()
    st.session_state["df"] = df
    st.session_state["features"] = features
    st.session_state["classified"] = classified
else:
    df = st.session_state["df"]
    features = st.session_state["features"]
    classified = st.session_state["classified"]

# ── Home page ─────────────────────────────────────────────────────────────────

st.title("🟩 Wordle People")
st.subheader("What two months of daily Wordle scores say about our friend group")

st.markdown("---")

# Key stats across the top
col1, col2, col3, col4 = st.columns(4)

n_players = df["sender"].nunique()
n_puzzles = df["puzzle_number"].nunique()
n_results = len(df)
fail_pct = df["score"].isna().mean() * 100

col1.metric("Players", n_players)
col2.metric("Wordle puzzles", n_puzzles)
col3.metric("Results logged", n_results)
col4.metric("Fail rate", f"{fail_pct:.1f}%")

st.markdown("---")

st.markdown(
    """
    Our WhatsApp group has been sharing Wordle scores for months.
    Every morning (or afternoon, or occasionally midnight — you know who you are),
    someone posts their grid and the gentle competition begins.

    We exported the chat, ran a script over it, and asked: **what do these scores actually reveal?**

    Turns out, how you Wordle says a lot about who you are.
    """
)

col_a, col_b = st.columns(2)

with col_a:
    st.page_link("pages/1_Analysis.py", label="📊 See the analysis", icon="📊")

with col_b:
    st.page_link("pages/2_Quiz.py", label="🧩 Take the quiz", icon="🧩")

st.markdown("---")
st.caption("Built with Python + Streamlit · A companion to [sowrao.com](https://sowrao.com)")
