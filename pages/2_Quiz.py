import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quiz import QUESTIONS, ALL_TYPES, score_quiz, get_result
from personality import TYPES

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Quiz · Wordle People",
    page_icon="🧩",
    layout="centered",
)

# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Tighten up radio label spacing */
    div[data-testid="stRadio"] label { font-size: 0.95rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────

st.title("🧩 What's your Wordle type?")
st.markdown(
    "Ten questions. No wrong answers. Just tell us how you actually play — "
    "not how you wish you played."
)
st.markdown("---")

# ── Questions ─────────────────────────────────────────────────────────────────

answer_indices: list[int | None] = []

for i, q in enumerate(QUESTIONS):
    st.markdown(f"**{i + 1}. {q['text']}**")

    options = [a["label"] for a in q["answers"]]
    choice = st.radio(
        label=q["text"],
        options=options,
        index=None,
        label_visibility="collapsed",
        key=f"q{i}",
    )

    if choice is None:
        answer_indices.append(None)
    else:
        answer_indices.append(options.index(choice))

    st.markdown("")

# ── Submit ────────────────────────────────────────────────────────────────────

all_answered = all(idx is not None for idx in answer_indices)
n_answered = sum(1 for idx in answer_indices if idx is not None)

if not all_answered:
    st.caption(f"{n_answered} of {len(QUESTIONS)} answered — complete all questions to see your type.")

submitted = st.button(
    "Find my type →",
    type="primary",
    disabled=not all_answered,
)

# ── Result ────────────────────────────────────────────────────────────────────

if submitted and all_answered:
    indices = [idx for idx in answer_indices]  # all are ints at this point
    result_type = get_result(indices)
    scores = score_quiz(indices)
    info = TYPES[result_type]
    color = info["color"]

    st.markdown("---")
    st.balloons()

    # ── Result card ──────────────────────────────────────────────────────────

    st.markdown(
        f"""
        <div style="
            border: 3px solid {color};
            border-radius: 12px;
            padding: 24px 28px;
            background: #fafafa;
            text-align: center;
            margin: 16px 0;
        ">
            <div style="font-size: 2.2em; font-weight: 800; color: {color}; margin-bottom: 4px;">
                {result_type}
            </div>
            <div style="font-size: 1.1em; color: #555; font-style: italic; margin-bottom: 16px;">
                {info['tagline']}
            </div>
            <div style="font-size: 0.95em; color: #444; max-width: 480px; margin: 0 auto;">
                {info['description']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Score breakdown radar ─────────────────────────────────────────────────

    st.markdown("### How the scores broke down")
    st.caption("Each bar shows how many points you accumulated for each type.")

    max_score = max(scores.values()) if scores else 1

    # Sort by score descending for the chart
    sorted_types = sorted(ALL_TYPES, key=lambda t: scores[t], reverse=True)
    bar_colors = [TYPES[t]["color"] for t in sorted_types]
    bar_values = [scores[t] for t in sorted_types]
    bar_labels = [t.replace("The ", "") for t in sorted_types]

    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("#f9f9f5")

    bars = ax.barh(bar_labels[::-1], bar_values[::-1], color=bar_colors[::-1], height=0.6)

    # Highlight the winning type
    for bar, label in zip(bars, bar_labels[::-1]):
        if f"The {label}" == result_type or label == result_type.replace("The ", ""):
            bar.set_edgecolor("#333")
            bar.set_linewidth(2)

    ax.set_xlim(0, max_score + 2)
    ax.set_xlabel("Points", fontsize=9, color="#666")
    ax.tick_params(axis="y", labelsize=9, colors="#333")
    ax.tick_params(axis="x", labelsize=8, colors="#888")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # ── Radar chart ───────────────────────────────────────────────────────────

    st.markdown("### Your Wordle fingerprint")

    labels = list(bar_labels)
    values = [scores[t] / max_score for t in sorted_types]  # normalise 0–1

    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles_plot = angles + [angles[0]]

    fig2, ax2 = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    fig2.patch.set_facecolor("none")
    ax2.set_facecolor("none")

    ax2.plot(angles_plot, values_plot, color=color, linewidth=2.5)
    ax2.fill(angles_plot, values_plot, color=color, alpha=0.3)
    ax2.set_xticks(angles)
    ax2.set_xticklabels(labels, size=8, color="#333")
    ax2.set_ylim(0, 1)
    ax2.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax2.set_yticklabels([], size=0)
    ax2.grid(color="#cccccc", linewidth=0.6)
    ax2.spines["polar"].set_visible(False)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.pyplot(fig2, use_container_width=True)
    plt.close(fig2)

    # ── Share nudge ───────────────────────────────────────────────────────────

    st.markdown("---")
    st.markdown(
        f"**Share your result** — tell the group you're *{result_type}* and watch "
        f"them agree (or argue) about it."
    )

    st.page_link("pages/1_Analysis.py", label="← See how we classified the group", icon="📊")
