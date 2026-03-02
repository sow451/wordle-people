import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parser import parse_chat
from features import compute_features
from personality import classify, TYPES
from aliases import ALIASES

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Analysis · Wordle People",
    page_icon="📊",
    layout="wide",
)

# ── Load data ─────────────────────────────────────────────────────────────────

_REAL = Path(__file__).parent.parent / "data" / "whatsapp_export.txt"
_DEMO = Path(__file__).parent.parent / "data" / "demo_export.txt"
DATA_PATH = _REAL if _REAL.exists() else _DEMO


@st.cache_data
def load_data():
    df = parse_chat(DATA_PATH, aliases=ALIASES)
    features = compute_features(df)
    classified = classify(features)
    return df, features, classified


df, features, classified = load_data()

# Palette: Wordle greens / yellows / greys
WORDLE_GREEN = "#538d4e"
WORDLE_YELLOW = "#c9b458"
WORDLE_GREY = "#787c7e"
BG = "#f9f9f5"

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: THE GROUP STORY
# ─────────────────────────────────────────────────────────────────────────────

st.title("📊 The Group Story")
st.caption(
    f"{df['sender'].nunique()} players · "
    f"Puzzles {df['puzzle_number'].min()}–{df['puzzle_number'].max()} · "
    f"{len(df)} results"
)

# ── G1: Activity over time ────────────────────────────────────────────────────

st.markdown("### Who showed up?")
st.markdown("How many of us posted each day. The emotional spine of the whole thing.")

activity = df.groupby("puzzle_number")["sender"].count().reset_index()
activity.columns = ["puzzle_number", "players_posted"]

fig_activity = px.line(
    activity,
    x="puzzle_number",
    y="players_posted",
    labels={"puzzle_number": "Puzzle #", "players_posted": "Players who posted"},
    color_discrete_sequence=[WORDLE_GREEN],
)
fig_activity.update_traces(line_width=2.5)
fig_activity.update_layout(
    plot_bgcolor=BG,
    paper_bgcolor="white",
    yaxis=dict(dtick=1, range=[0, df["sender"].nunique() + 1]),
    height=300,
    margin=dict(l=0, r=0, t=10, b=0),
    hovermode="x unified",
)
st.plotly_chart(fig_activity, use_container_width=True)

# ── G2 + G3: Score distribution + Who played when ────────────────────────────

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### How did we do?")
    st.markdown("Every guess, stacked up.")

    score_counts = df.copy()
    score_counts["score_label"] = score_counts["score"].apply(
        lambda s: "X (fail)" if pd.isna(s) else str(int(s))
    )
    order = ["1", "2", "3", "4", "5", "6", "X (fail)"]
    color_map = {
        "1": "#538d4e",
        "2": "#6aaa64",
        "3": "#c9b458",
        "4": "#e9c46a",
        "5": "#e76f51",
        "6": "#d62828",
        "X (fail)": "#3a3a3c",
    }
    counts = (
        score_counts["score_label"]
        .value_counts()
        .reindex(order, fill_value=0)
        .reset_index()
    )
    counts.columns = ["Score", "Count"]

    fig_dist = px.bar(
        counts,
        x="Score",
        y="Count",
        color="Score",
        color_discrete_map=color_map,
        text="Count",
    )
    fig_dist.update_traces(textposition="outside", showlegend=False)
    fig_dist.update_layout(
        plot_bgcolor=BG,
        paper_bgcolor="white",
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        xaxis_title="Guesses",
        yaxis_title="Number of games",
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with col_right:
    st.markdown("### Who played when?")
    st.markdown("Every square is one puzzle. Green = played, blank = didn't.")

    all_players = sorted(df["sender"].unique())
    all_puzzles = list(range(df["puzzle_number"].min(), df["puzzle_number"].max() + 1))

    played = df.groupby(["sender", "puzzle_number"]).size().reset_index(name="played")
    played_pivot = played.pivot(index="sender", columns="puzzle_number", values="played").fillna(0)
    played_pivot = played_pivot.reindex(columns=all_puzzles, fill_value=0)
    played_pivot = played_pivot.reindex(all_players, fill_value=0)

    # Shorten names for display
    fig_heat = go.Figure(
        data=go.Heatmap(
            z=played_pivot.values,
            x=all_puzzles,
            y=played_pivot.index.tolist(),
            colorscale=[[0, "#eeeeea"], [1, WORDLE_GREEN]],
            showscale=False,
            hovertemplate="Puzzle %{x}<br>%{y}: %{z:.0f}<extra></extra>",
        )
    )
    fig_heat.update_layout(
        plot_bgcolor=BG,
        paper_bgcolor="white",
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="Puzzle #",
        yaxis_title="",
        yaxis=dict(tickfont=dict(size=10)),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: MEET THE TYPES
# ─────────────────────────────────────────────────────────────────────────────

st.title("🧬 Meet the Types")
st.markdown(
    "After two months of data, the numbers reveal six personality archetypes. "
    "Here's where everyone in the group landed."
)

# ── P5: Skill vs Luck scatter ─────────────────────────────────────────────────

st.markdown("### Lucky or good? The eternal question.")
st.markdown(
    "Each dot is a player. Left = better average score. Up = more lucky (1s and 2s). "
    "The quadrants reveal everything."
)

scatter_df = classified.reset_index()
fig_scatter = px.scatter(
    scatter_df,
    x="avg_score",
    y="lucky_rate",
    color="personality_type",
    color_discrete_map={t: TYPES[t]["color"] for t in TYPES},
    text="sender",
    size="total_plays",
    size_max=40,
    hover_data={"sender": True, "avg_score": ":.2f", "lucky_rate": ":.1%", "total_plays": True},
    labels={
        "avg_score": "Average score (lower = better)",
        "lucky_rate": "Lucky rate (1s & 2s)",
        "personality_type": "Type",
    },
)
fig_scatter.update_traces(textposition="top center", marker_line_width=1.5)
fig_scatter.update_xaxes(autorange="reversed")
fig_scatter.update_layout(
    plot_bgcolor=BG,
    paper_bgcolor="white",
    height=420,
    margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(title="Type", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ── Type cards ────────────────────────────────────────────────────────────────

st.markdown("### The six archetypes")
st.markdown("We found these personality types in the data. Some of us match perfectly.")

present_types = classified["personality_type"].unique()
all_type_names = list(TYPES.keys())


def make_radar(row: pd.Series, color: str) -> plt.Figure:
    """Draw a small radar chart for one player's feature percentiles."""
    labels = ["Skill\n(avg score)", "Consistency", "Dedication\n(active days)", "Lucky", "Early bird", "Speed"]
    # For avg_score and consistency, lower is better — invert so radar shows "more = better"
    values = [
        1 - row.get("avg_score_pct", 0.5),
        1 - row.get("consistency_pct", 0.5),
        row.get("active_days_pct_pct", 0.5),
        row.get("lucky_rate_pct", 0.5),
        row.get("early_bird_rate_pct", 0.5),
        1 - row.get("speed_rank_avg_pct", 0.5),
    ]

    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles_plot = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(2.2, 2.2), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")

    ax.plot(angles_plot, values_plot, color=color, linewidth=2)
    ax.fill(angles_plot, values_plot, color=color, alpha=0.25)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, size=5.5, color="#333")
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_yticklabels([], size=0)
    ax.grid(color="#cccccc", linewidth=0.5)
    ax.spines["polar"].set_visible(False)
    return fig


cols = st.columns(3)
for i, type_name in enumerate(all_type_names):
    info = TYPES[type_name]
    players_of_type = classified[classified["personality_type"] == type_name].index.tolist()

    with cols[i % 3]:
        badge_color = info["color"]
        st.markdown(
            f"""
            <div style="
                border-left: 4px solid {badge_color};
                padding: 10px 14px;
                border-radius: 4px;
                background: #fafafa;
                margin-bottom: 6px;
            ">
                <strong style="color:{badge_color}; font-size:1.05em">{type_name}</strong><br>
                <em style="font-size:0.85em; color:#555">{info['tagline']}</em>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(info["description"])

        if players_of_type:
            st.markdown(
                f"**In our group:** {', '.join(players_of_type)}"
            )
        else:
            st.markdown("*No one in our group (yet)*")

        st.markdown("")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: PLAYER PROFILES
# ─────────────────────────────────────────────────────────────────────────────

st.title("👤 Player Profiles")
st.markdown("Pick someone and see their Wordle DNA.")

classifiable_players = classified.index.tolist()
selected = st.selectbox(
    "Select a player",
    options=classifiable_players,
    format_func=lambda n: n,
)

if selected:
    row = classified.loc[selected]
    player_df = df[df["sender"] == selected].sort_values("puzzle_number")
    type_name = row["personality_type"]
    type_color = TYPES[type_name]["color"]

    # ── Player card ──────────────────────────────────────────────────────────

    st.markdown(
        f"""
        <div style="
            border: 2px solid {type_color};
            border-radius: 10px;
            padding: 18px;
            background: #fafafa;
            margin-bottom: 16px;
        ">
            <span style="font-size:1.5em; font-weight:700; color:{type_color}">{type_name}</span>
            &nbsp;&nbsp;<span style="color:#777; font-size:0.95em">{selected}</span><br>
            <em style="color:#555">{TYPES[type_name]['tagline']}</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    card_left, card_mid, card_right = st.columns([1.2, 1, 1])

    with card_left:
        st.markdown("**Radar chart**")
        fig_radar = make_radar(row, type_color)
        st.pyplot(fig_radar, use_container_width=False)
        plt.close(fig_radar)

    with card_mid:
        st.markdown("**Key numbers**")
        st.metric("Games played", int(row["total_plays"]))
        st.metric("Avg score", f"{row['avg_score']:.2f}")
        fail_display = f"{row['fail_rate']:.1%}" if row["fail_rate"] > 0 else "0%"
        st.metric("Fail rate", fail_display)

    with card_right:
        st.markdown("**More numbers**")
        st.metric("Best streak", f"{int(row['streak_max'])} days")
        st.metric("Longest gap", f"{int(row['gap_max'])} days")
        st.metric("Early bird rate", f"{row['early_bird_rate']:.1%}")

    # ── Score strip (last 30 games) ───────────────────────────────────────────

    st.markdown("**Your last 30 games**")

    recent = player_df.tail(30)
    strip_cols = st.columns(len(recent))

    for col, (_, game_row) in zip(strip_cols, recent.iterrows()):
        score = game_row["score"]
        if pd.isna(score):
            emoji = "⬛"
        elif score <= 2:
            emoji = "🟩"
        elif score <= 4:
            emoji = "🟨"
        else:
            emoji = "🟧"
        col.markdown(
            f"<div style='text-align:center; font-size:1.2em'>{emoji}</div>"
            f"<div style='text-align:center; font-size:0.6em; color:#999'>{int(score) if not pd.isna(score) else 'X'}</div>",
            unsafe_allow_html=True,
        )

    # ── Score over time ───────────────────────────────────────────────────────

    st.markdown("**Score over time**")

    plot_df = player_df.copy()
    plot_df["score_display"] = plot_df["score"].fillna(7)  # 7 = fail for chart height

    fig_timeline = go.Figure()
    fig_timeline.add_trace(
        go.Scatter(
            x=plot_df["puzzle_number"],
            y=plot_df["score_display"],
            mode="lines+markers",
            line=dict(color=type_color, width=2),
            marker=dict(
                color=[
                    "#3a3a3c" if pd.isna(s) else type_color
                    for s in player_df["score"]
                ],
                size=8,
            ),
            customdata=plot_df["score"].apply(lambda s: "X" if pd.isna(s) else int(s)),
            hovertemplate="Puzzle %{x}: %{customdata}/6<extra></extra>",
        )
    )
    fig_timeline.update_layout(
        plot_bgcolor=BG,
        paper_bgcolor="white",
        height=260,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(
            tickvals=[1, 2, 3, 4, 5, 6, 7],
            ticktext=["1", "2", "3", "4", "5", "6", "X"],
            autorange="reversed",
        ),
        xaxis_title="Puzzle #",
        yaxis_title="Score",
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: QUIZ CTA
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### 🧩 Think you know your type?")
st.markdown("We classified our friends. Now it's your turn.")
st.page_link("pages/2_Quiz.py", label="Take the quiz →", icon="🧩")
