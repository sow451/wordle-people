import pandas as pd


# ── Type definitions ──────────────────────────────────────────────────────────

TYPES = {
    "The Strategist": {
        "tagline": "You don't guess. You deduce.",
        "description": (
            "Low scores, low variance, relentless consistency. "
            "They probably have a spreadsheet somewhere."
        ),
        "color": "#2d6a4f",
    },
    "The Wildcard": {
        "tagline": "Some days you're a genius. Some days... well.",
        "description": (
            "One day they get it in 1. The next day, X. "
            "There is no pattern. There is only chaos — and occasionally, glory."
        ),
        "color": "#e9c46a",
    },
    "The Reliable": {
        "tagline": "You always finish. Always.",
        "description": (
            "They will never blow your mind. They will also never let you down. "
            "4/6 is not a failure — it's a lifestyle."
        ),
        "color": "#457b9d",
    },
    "The Ghost": {
        "tagline": "You appear, dominate, and vanish.",
        "description": (
            "They vanish for weeks. Then one Tuesday they post a 2/6 "
            "like nothing happened. No explanation. No apology."
        ),
        "color": "#7b2d8e",
    },
    "The Competitor": {
        "tagline": "First to solve. First to post. First to check.",
        "description": (
            "Awake at 6 AM not because they love mornings, "
            "but because they need to post first."
        ),
        "color": "#e76f51",
    },
    "The Wordsmith": {
        "tagline": "You play Wordle like you're writing poetry.",
        "description": (
            "They don't use CRANE or ADIEU. They open with FJORD. "
            "Wordle is art, not sport."
        ),
        "color": "#2a9d8f",
    },
}

FALLBACK_TYPE = "The Reliable"


# ── Helpers ───────────────────────────────────────────────────────────────────

def describe_type(type_name: str) -> dict:
    """Returns a dict with keys: name, tagline, description, color for a type."""
    info = TYPES[type_name]
    return {
        "name": type_name,
        "tagline": info["tagline"],
        "description": info["description"],
        "color": info["color"],
    }


# ── Percentile ranks ─────────────────────────────────────────────────────────

# Features used by the classifier — only these get _pct columns.
RANKED_FEATURES = [
    "avg_score",
    "fail_rate",
    "consistency",
    "lucky_rate",
    "active_days_pct",
    "gap_max",
    "speed_rank_avg",
    "early_bird_rate",
]


def add_percentile_ranks(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each numeric feature column, add a corresponding _pct column
    containing each player's percentile rank within the group (0.0 to 1.0).

    Higher _pct = higher raw value. For features where lower is better
    (avg_score, consistency), a *low* _pct means the player is skilled.
    """
    df = features_df.copy()
    for col in RANKED_FEATURES:
        if col in df.columns:
            df[f"{col}_pct"] = df[col].rank(pct=True)
    return df


# ── Rule-based classifier ────────────────────────────────────────────────────

def classify_player(row: pd.Series) -> str:
    """
    Given a single player's features row (with _pct columns),
    return their personality type as a string.

    Rules are applied in priority order — first match wins.
    All thresholds reference group-relative percentile ranks.
    """

    # 1. GHOST: sparse player with long absences
    if (row["active_days_pct_pct"] <= 0.25
            and row["gap_max_pct"] >= 0.75):
        return "The Ghost"

    # 2. COMPETITOR: posts early and often
    if (row["speed_rank_avg_pct"] <= 0.25
            and row["early_bird_rate_pct"] >= 0.70
            and row["active_days_pct_pct"] >= 0.50):
        return "The Competitor"

    # 3. WILDCARD: high variance plus lucky streaks or frequent fails
    if (row["consistency_pct"] >= 0.75
            and (row["lucky_rate_pct"] >= 0.70
                 or row["fail_rate_pct"] >= 0.70)):
        return "The Wildcard"

    # 4. STRATEGIST: low score, low variance, low fail rate
    if (row["avg_score_pct"] <= 0.30
            and row["consistency_pct"] <= 0.40
            and row["fail_rate_pct"] <= 0.40):
        return "The Strategist"

    # 5. RELIABLE: rarely fails, plays often, reasonably consistent
    if (row["fail_rate_pct"] <= 0.25
            and row["active_days_pct_pct"] >= 0.50
            and row["consistency_pct"] <= 0.50):
        return "The Reliable"

    # 6. WORDSMITH: low fail rate, doesn't rely on luck
    if (row["fail_rate_pct"] <= 0.40
            and row["lucky_rate_pct"] <= 0.50):
        return "The Wordsmith"

    # 7. FALLBACK
    return FALLBACK_TYPE


# ── Main classify entry point ─────────────────────────────────────────────────

def classify(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Input:  features DataFrame (output of features.compute_features).
    Output: same DataFrame with two new columns added:
              personality_type  — string type name
              type_color        — hex colour for that type (for charts)
    """
    df = add_percentile_ranks(features_df)
    df["personality_type"] = df.apply(classify_player, axis=1)
    df["type_color"] = df["personality_type"].map(
        lambda t: TYPES[t]["color"]
    )
    return df


# ── CLI preview ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")

    import parser
    import features

    df = parser.parse_chat("data/whatsapp_export.txt")
    features_df = features.compute_features(df)
    results = classify(features_df)

    print(f"{'Player':<25} {'Type':<20} {'Avg Score':>9}")
    print("-" * 56)
    for sender, row in results.iterrows():
        print(f"{sender:<25} {row['personality_type']:<20} {row['avg_score']:>9.2f}")
