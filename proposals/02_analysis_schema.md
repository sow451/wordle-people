# Proposal 02: Analysis Schema & Personality Classification

## Overview

This document defines the feature engineering pipeline and rule-based personality classifier for the Wordle People project. The goal: take a flat table of `(sender, puzzle_number, score, timestamp)` rows and produce a per-player profile that maps to one of six personality types.

---

## 1. Per-Player Feature Engineering

All features are computed per player from the parsed DataFrame. Where relevant, formulas treat `None` scores (failed attempts / X) specially.

### Core Features

| Feature | Formula | What it captures |
|---------|---------|-----------------|
| `total_plays` | `count(rows for player)` | Volume — how much data do we have? Also a proxy for dedication. |
| `avg_score` | `mean(score) where score is not None` | Skill — lower is better. Only counts games that weren't failures. |
| `fail_rate` | `count(score is None) / total_plays` | Resilience — what fraction of games ended in X? |
| `consistency` | `std(score) where score is not None` | Predictability — low std dev means they hover around their mean. |
| `lucky_rate` | `count(score <= 2) / count(score is not None)` | Brilliance (or luck) — how often do they nail it in 1 or 2? |
| `clutch_rate` | `count(score in {5, 6}) / count(score is not None)` | Living on the edge — how often do they barely scrape through? |
| `streak_max` | longest run of consecutive puzzle_numbers played | Dedication — longest unbroken streak of daily play. |
| `gap_max` | largest difference between consecutive puzzle_numbers played | Ghosting — longest disappearance from the group. |
| `active_days_pct` | `total_plays / (max_puzzle - min_puzzle + 1)` | Participation — what fraction of available days did they play? |
| `early_bird_rate` | `count(timestamp.hour < 9) / total_plays` | Eagerness — fraction of results posted before 9 AM. |
| `speed_rank_avg` | `mean(rank among group for that puzzle by timestamp)` | Competitiveness — on average, how early do they post relative to others? Lower = posts first. |

### Derived / Composite Features

| Feature | Formula | What it captures |
|---------|---------|-----------------|
| `variance_score` | `max(score) - min(score)` across non-None scores | Range — how wild are their swings? A player who gets 1s and 6s is very different from one who always gets 3s. |
| `improvement_trend` | slope of linear regression of `score` over `puzzle_number` (non-None only) | Trajectory — are they getting better or worse over time? Negative slope = improving. |

### Computation Notes

- **Streaks and gaps** are computed from sorted `puzzle_number` sequences per player. A "consecutive" play means `puzzle_n+1 - puzzle_n == 1`. Gaps are the differences themselves.
- **speed_rank_avg** is computed per puzzle: for each puzzle, rank all players who posted that day by timestamp (1 = first). Then average a player's rank across all puzzles they played. This needs at least 2 players per puzzle to be meaningful.
- **early_bird_rate** uses `timestamp.hour < 9` (local time, assuming the WhatsApp export timestamps are already in the group's timezone).
- **improvement_trend** uses `scipy.stats.linregress` or `numpy.polyfit(degree=1)` on `(puzzle_number, score)` pairs. The slope value itself is tiny (score-per-puzzle), so we primarily care about sign (negative = improving) and relative magnitude across players.

---

## 2. Personality Types (Revised)

The six types from CLAUDE.md, refined to map cleanly onto measurable features. Each type has a primary signal (the feature that most defines it) and secondary signals (that distinguish it from other types).

### Type 1: The Strategist

> They don't just play Wordle — they've *solved* Wordle. Low scores, low variance, relentless consistency. They probably have a spreadsheet somewhere.

- **Primary signal:** Low `avg_score` AND low `consistency` (std dev)
- **Secondary signals:** Low `fail_rate`, moderate-to-high `active_days_pct`
- **Vibe:** Quiet excellence. They never brag, they just... always get it in 3.

### Type 2: The Wildcard

> One day they get it in 1. The next day, X. There is no pattern. There is no strategy. There is only chaos — and occasionally, glory.

- **Primary signal:** High `variance_score` AND high `lucky_rate` relative to their `avg_score`
- **Secondary signals:** `consistency` (std dev) is high, `fail_rate` above average
- **Vibe:** The friend whose Wordle score you genuinely cannot predict.
- *Note: Renamed from "The Lucky One" because the defining trait isn't luck — it's unpredictability.*

### Type 3: The Reliable

> They will never blow your mind. They will also never let you down. 4/6 is not a failure — it's a lifestyle.

- **Primary signal:** Very low `fail_rate` AND moderate `avg_score` (3.5 - 4.5)
- **Secondary signals:** Low `consistency` (std dev), high `active_days_pct`
- **Vibe:** The bedrock of the group. Wordle is a daily habit, like brushing teeth.

### Type 4: The Ghost

> They vanish for weeks. Then one Tuesday they post a 2/6 like nothing happened. No explanation. No apology. Absolute power move.

- **Primary signal:** Low `active_days_pct` AND high `gap_max`
- **Secondary signals:** `streak_max` is low, total_plays is below group median
- **Vibe:** Wordle is not a commitment. Wordle is a mood.

### Type 5: The Competitor

> They are awake at 6 AM not because they love mornings, but because they need to post first. They know everyone's average. They definitely keep score.

- **Primary signal:** Low `speed_rank_avg` (they post early relative to others) AND high `early_bird_rate`
- **Secondary signals:** High `active_days_pct`, decent `avg_score` (they care about winning, not just playing)
- **Vibe:** The group's unofficial scorekeeper. Probably sent "nice!" when they beat you.

### Type 6: The Wordsmith

> They don't use CRANE or ADIEU. They open with FJORD. They treat Wordle less like a puzzle and more like a conversation with the English language.

- **Primary signal:** Low `fail_rate` despite moderate `avg_score` — they take scenic routes but still arrive
- **Secondary signals:** `improvement_trend` is flat or slightly negative (they're not optimising, they're vibing), `lucky_rate` is low (they don't stumble into 1s — they earn their 3s)
- **Vibe:** Wordle is art, not sport.

---

## 3. Classification Rules

A rule-based classifier using thresholds relative to the group's distribution. This avoids hardcoded numbers that break across different friend groups. All thresholds use percentile ranks within the group.

### Preprocessing

For each feature, compute the player's **percentile rank** within the group (0 = lowest, 1 = highest). This normalises everything so thresholds work regardless of group size or skill level.

```
For each feature f:
  pct[player][f] = (rank of player among all players for f) / (N - 1)
```

Where N is the number of players with sufficient data (see edge cases below).

### Decision Rules (evaluated in priority order)

The classifier walks through these rules top-to-bottom. The first match wins. This ordering is intentional — it resolves ambiguity when a player could fit multiple types.

```
1. GHOST CHECK (first, because Ghosts have sparse data that distorts other features)
   IF active_days_pct is in BOTTOM 25% of group
   AND gap_max is in TOP 25% of group
   → The Ghost

2. COMPETITOR CHECK
   IF speed_rank_avg is in BOTTOM 25% of group (i.e. they post early)
   AND early_bird_rate is in TOP 30% of group
   AND active_days_pct is in TOP 50% of group
   → The Competitor

3. WILDCARD CHECK
   IF consistency (std dev) is in TOP 25% of group
   AND (lucky_rate is in TOP 30% OR fail_rate is in TOP 30%)
   → The Wildcard

4. STRATEGIST CHECK
   IF avg_score is in BOTTOM 30% of group (low = good)
   AND consistency (std dev) is in BOTTOM 40% of group (low = predictable)
   AND fail_rate is in BOTTOM 40% of group
   → The Strategist

5. RELIABLE CHECK
   IF fail_rate is in BOTTOM 25% of group
   AND active_days_pct is in TOP 50% of group
   AND consistency (std dev) is in BOTTOM 50% of group
   → The Reliable

6. WORDSMITH (default thoughtful player)
   IF fail_rate is in BOTTOM 40% of group
   AND lucky_rate is in BOTTOM 50% of group
   → The Wordsmith

7. FALLBACK
   → The Reliable (safe default — most people are reliable)
```

### Why this order?

- **Ghost first** because low participation warps all other features — someone who played 5 times might have a great avg_score purely by chance.
- **Competitor next** because it relies on a unique signal (timing) that no other type uses.
- **Wildcard before Strategist/Reliable** because high variance is a strong, unmistakable signal.
- **Strategist before Reliable** because they share low fail_rate, but the Strategist is *better* — catch them first.
- **Wordsmith last** (before fallback) because it's the subtlest type — defined by what they're *not* as much as what they are.

---

## 4. Edge Cases & Minimum Data

### Minimum play threshold

**Players with fewer than 10 plays are excluded from classification** and labelled "Not enough data" in the output. Rationale:

- `consistency` (std dev) is unreliable with < 10 data points
- `streak_max` and `gap_max` are meaningless with sparse data
- `improvement_trend` needs at least ~10 points for a regression to mean anything
- 10 is also a nice round number for the blog: "you need at least 10 games to earn a personality"

### Small group sizes

If the group has fewer than 5 classifiable players (after the 10-play threshold), percentile-based thresholds become jumpy. In that case, fall back to **absolute thresholds**:

| Feature | Absolute threshold | Direction |
|---------|-------------------|-----------|
| `avg_score` | < 3.5 | Low = Strategist signal |
| `fail_rate` | < 0.05 | Low = Reliable/Strategist signal |
| `consistency` | < 0.9 | Low = consistent |
| `active_days_pct` | < 0.3 | Low = Ghost signal |
| `early_bird_rate` | > 0.4 | High = Competitor signal |
| `lucky_rate` | > 0.15 | High = Wildcard signal |

These absolute thresholds were calibrated against publicly shared Wordle statistics and are approximate. They work well enough for a blog project.

### Ties in speed_rank

When multiple players post the same puzzle at the exact same timestamp (rare but possible), assign them the same rank (average rank method). This avoids artificially inflating one player's competitiveness over another.

### Players who only fail

If a player has zero non-None scores (every game was X), they cannot have an `avg_score`. Set their features to:
- `avg_score` = 7.0 (worse than the worst possible real score, so they sort last)
- `consistency` = 0.0 (no variance in failure)
- They will likely be classified as a Ghost (low participation) or Wildcard (high fail_rate).

---

## 5. Blog Presentation Angle

### How to talk about this without math

The blog post should present the personality types first and the methodology second. The reader's journey:

1. **Open with the types as a personality quiz vibe** — "after two years of daily Wordle in our WhatsApp group, patterns emerged. Turns out, how you Wordle says a lot about who you are."

2. **Show the types as character cards** — each type gets an illustration (or emoji-based graphic), a punchy one-liner, and a "you might be this type if..." list. No formulas. No feature names.

3. **Reveal the friends** — anonymised player profiles with mini charts (sparklines of score over time, a radar chart of their feature percentiles). The fun is in the recognition: "oh, I know exactly who The Ghost is."

4. **Methodology as a collapsible aside** — "How we built this" section at the bottom for curious readers. Frame features as questions, not formulas:
   - "How good are you, really?" → avg_score
   - "Can we predict your score tomorrow?" → consistency
   - "Do you disappear?" → active_days_pct + gap_max
   - "Are you racing to post first?" → speed_rank_avg

5. **End with the quiz** — "We classified our friends. Now it's your turn." Link to the Streamlit quiz page.

### Chart ideas for the blog

- **Radar chart per player** — axes are the key features (normalised 0-1), with the personality type name in the centre. Instantly visual.
- **Score distribution violin plots** — one per player, side by side. The Strategist is a tight cluster; the Wildcard is a wide spread.
- **"When do they play?" heatmap** — hour of day vs day of week, coloured by post count. The Competitor lights up at 6 AM.
- **Streak timeline** — horizontal bar chart showing each player's streaks and gaps over time. The Ghost's bar is mostly empty with bright bursts.

### Tone notes

- Name the types with affection, not mockery (per CLAUDE.md)
- "The Reliable" is a compliment, not a backhanded one — frame it as the glue of the group
- "The Ghost" should feel mysterious and cool, not flaky
- "The Wildcard" should feel exciting, not incompetent
- Use second person in descriptions: "You probably..." — makes the reader see themselves

---

## 6. Implementation Notes

### Feature computation function signature

```python
def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input:  parsed DataFrame with columns [sender, puzzle_number, score, timestamp]
    Output: DataFrame indexed by sender with one row per player and feature columns
    """
```

### Classifier function signature

```python
def classify(features_df: pd.DataFrame) -> pd.Series:
    """
    Input:  features DataFrame (output of compute_features)
    Output: Series mapping sender → personality type name (str)
    """
```

### Feature → type mapping summary table

| Feature | Strategist | Wildcard | Reliable | Ghost | Competitor | Wordsmith |
|---------|-----------|----------|----------|-------|------------|-----------|
| avg_score | LOW | any | MED | any | LOW-MED | MED |
| fail_rate | LOW | HIGH-ish | V.LOW | any | LOW | LOW |
| consistency | LOW | HIGH | LOW | any | any | any |
| lucky_rate | any | HIGH | any | any | any | LOW |
| active_days_pct | MED-HIGH | any | HIGH | LOW | HIGH | any |
| gap_max | any | any | any | HIGH | any | any |
| speed_rank_avg | any | any | any | any | LOW | any |
| early_bird_rate | any | any | any | any | HIGH | any |
| variance_score | LOW | HIGH | LOW | any | any | any |

---

## Summary

- **13 features** computed per player from raw scores and timestamps
- **6 personality types** mapped via priority-ordered rule-based classification using group-relative percentiles
- **10-play minimum** for classification; absolute-threshold fallback for very small groups
- Blog presentation leads with the human story, tucks the math away for curious readers
