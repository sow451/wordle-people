# Proposal 03: Visualizations & Storytelling

## Design philosophy

The visuals should feel like a group chat reveal night — the moment you hold up a mirror and everyone laughs at what they see. Warm colours, playful labels, friend-group energy. Not a dashboard for a data team; a scrapbook for people who text each other Wordle scores every morning.

**Colour palette**: Wordle-inspired. Greens (#6aaa64, #538d4e), yellows (#c9b458), greys (#787c7e, #3a3a3c), with a warm off-white background (#f5f5f0). Each personality type also gets its own accent colour for cards and highlights.

**Chart library**: Plotly for the Streamlit app (interactive hover, friendly defaults). Matplotlib/seaborn for static PNG exports embedded in the blog post.

---

## Part 1: Full Chart List

### Group-level charts (Section: "The Group")

| # | Chart type | Data / axes | Story it tells |
|---|-----------|-------------|----------------|
| G1 | **Line chart: Group activity over time** | X = puzzle number (or date), Y = number of players who posted that day | Shows when the group was hooked, when interest dipped, and any comeback arcs. The emotional spine of the blog post. |
| G2 | **Stacked bar: Score distribution** | X = score (1, 2, 3, 4, 5, 6, X), Y = count, stacked by player | How the whole group performs. Are we a 3-guess group? A 4-guess group? Where do the fails live? |
| G3 | **Heatmap: Who played when** | X = week number, Y = player name, colour = played/not played | Instantly reveals Ghosts vs Competitors. A satisfying grid that looks like a Wordle board itself. |
| G4 | **Small multiples: Individual score distributions** | One mini histogram per player, arranged in a grid | Side-by-side comparison. Some players are tight bell curves (Reliable); others are all over the map (Lucky One). |
| G5 | **Bump chart: Weekly rank over time** | X = week, Y = rank (1 = best avg that week), one line per player | The competitive narrative. Who held the top spot? Did anyone have a dramatic fall? |

### Personality-reveal charts (Section: "The Types")

| # | Chart type | Data / axes | Story it tells | Personality it reveals |
|---|-----------|-------------|----------------|----------------------|
| P1 | **Radar chart (per player)** | 6 axes: consistency, avg score, fail rate, streak length, lucky rate, early bird rate | A fingerprint. Each player's shape is visually distinct. The Strategist is a big even hexagon; the Lucky One is spiky. | All types |
| P2 | **Strip plot: Score volatility** | X = player, Y = individual game scores (jittered dots) | Shows variance at a glance. Tight clusters vs scattered dots. | The Reliable vs The Lucky One |
| P3 | **Calendar heatmap: Playing streak** | Calendar grid, colour = score that day, blank = no play | Beautiful and immediately readable. Long green runs vs patchy gaps. | The Ghost vs The Competitor |
| P4 | **Bar chart: Time of day** | X = hour bucket (morning/midday/evening/night), Y = % of posts | When do you solve? The early bird catches the Wordle. | The Competitor (early poster) |
| P5 | **Scatter plot: Skill vs Luck** | X = avg score, Y = lucky rate (% of 1s and 2s), bubble size = games played | Places everyone on a 2D personality map. Top-right = skilled AND lucky. Bottom-left = grinders. | The Strategist vs The Lucky One |
| P6 | **Timeline: Posting gaps** | X = date, one row per player, marks where they played | A "train schedule" view. Some lines are solid; Ghosts have big gaps. | The Ghost |

---

## Part 2: Streamlit Dashboard Layout

```
+============================================================+
|                    WORDLE PEOPLE                             |
|           "What your Wordle scores say about you"            |
+============================================================+

[TAB: Analysis]    [TAB: Quiz]

============================================================
SECTION 1: THE GROUP STORY
------------------------------------------------------------
| Intro text: "N players, M puzzles, over K months..."       |
|                                                             |
| [G1] Activity Over Time (full width line chart)            |
|  - Annotations for peaks: "The week everyone was hooked"   |
|  - Annotations for dips: "Holiday slump"                   |
------------------------------------------------------------
| Two columns:                                               |
| [G2] Score Distribution    |  [G5] Weekly Rankings        |
| (stacked bar)              |  (bump chart)                |
------------------------------------------------------------
| [G3] Who Played When (full width heatmap)                  |
|  "Some of us showed up every day. Some... didn't."         |
============================================================

SECTION 2: MEET THE TYPES
------------------------------------------------------------
| Short intro: "We found 6 personality types in the data..." |
|                                                             |
| [P5] Skill vs Luck scatter (full width)                    |
|  - Each dot is a player, labelled with pseudonym            |
|  - Quadrants lightly labelled: "Lucky", "Skilled",          |
|    "Grinder", "Needs a hug"                                 |
------------------------------------------------------------
| Type cards (2x3 grid, or expandable accordion):            |
|                                                             |
| +------------------+  +------------------+                  |
| | THE STRATEGIST   |  | THE LUCKY ONE    |                  |
| | [radar chart]    |  | [radar chart]    |                  |
| | Key stats        |  | Key stats        |                  |
| | Players: ...     |  | Players: ...     |                  |
| +------------------+  +------------------+                  |
|                                                             |
| +------------------+  +------------------+                  |
| | THE RELIABLE     |  | THE GHOST        |                  |
| | [radar chart]    |  | [radar chart]    |                  |
| | Key stats        |  | Key stats        |                  |
| | Players: ...     |  | Players: ...     |                  |
| +------------------+  +------------------+                  |
|                                                             |
| +------------------+  +------------------+                  |
| | THE COMPETITOR   |  | THE WORDSMITH    |                  |
| | [radar chart]    |  | [radar chart]    |                  |
| | Key stats        |  | Key stats        |                  |
| | Players: ...     |  | Players: ...     |                  |
| +------------------+  +------------------+                  |
============================================================

SECTION 3: PLAYER PROFILES
------------------------------------------------------------
| Dropdown: "Select a player"                                |
|                                                             |
| +------------------------------------------------------+   |
| | PLAYER CARD (see design below)                       |   |
| | [P1 Radar] | Stats column | Personality badge        |   |
| +------------------------------------------------------+   |
|                                                             |
| Below the card:                                            |
| [P3] Calendar heatmap (their playing pattern)              |
| [P2] Strip plot (their score distribution vs group)        |
| [G4] Their mini histogram highlighted in the grid          |
============================================================

SECTION 4: TAKE THE QUIZ
------------------------------------------------------------
| "Think you know your type? Take the quiz."                 |
| [Button: Go to Quiz -->]                                   |
============================================================
```

---

## Part 3: Personality Type Card Design

Each player gets a card that feels like opening a trading card pack.

```
+----------------------------------------------------------+
|  [TYPE ICON]     THE STRATEGIST                          |
|                  "You don't guess. You deduce."           |
+----------------------------------------------------------+
|                                                          |
|  [RADAR CHART]     |   YOUR NUMBERS                     |
|  (small, 150px)    |   Avg score:     2.8               |
|                     |   Fail rate:     2%                |
|                     |   Best streak:   47 days           |
|                     |   Games played:  312               |
|                     |   Consistency:   ★★★★★             |
|                     |   Lucky rate:    12%               |
|                     |                                    |
+----------------------------------------------------------+
|  FUN FACT: "You've never gone more than 3 days without   |
|  playing. The group can set their clocks by you."        |
+----------------------------------------------------------+
|  YOUR SIGNATURE: [mini score strip — last 30 games]      |
|  ■■■■□■■■■■□■■■ (green=3 or under, yellow=4-5, red=X)  |
+----------------------------------------------------------+
```

**Card elements:**

| Element | Source | Purpose |
|---------|--------|---------|
| Type name + icon | personality.py classification | Identity |
| One-liner tagline | Pre-written per type (see below) | Personality flavour |
| Radar chart | 6 normalised feature axes | Visual fingerprint |
| Key stats (6 numbers) | features.py output | Concrete proof |
| Consistency stars | consistency score mapped to 1-5 stars | Accessible shorthand |
| Fun fact | Template filled with player-specific data | The moment they share with the group |
| Signature strip | Last 30 game scores as coloured blocks | A personal Wordle board |

**Taglines per type:**

| Type | Tagline |
|------|---------|
| The Strategist | "You don't guess. You deduce." |
| The Lucky One | "Some days you're a genius. Some days... well." |
| The Reliable | "You always finish. Always." |
| The Ghost | "You appear, dominate, and vanish." |
| The Competitor | "First to solve. First to post. First to check." |
| The Wordsmith | "You play Wordle like you're writing poetry." |

---

## Part 4: Blog Post Visual Flow

The blog post on sowrao.com needs 3-5 static, embeddable charts that carry the narrative without the interactivity of Streamlit. These are the images exported as PNGs.

### Narrative arc: Setup --> Tension --> Reveal --> Payoff --> CTA

| Order | Chart | Caption / context in the post | Role in narrative |
|-------|-------|------------------------------|-------------------|
| 1 | **G1: Activity over time** | "Our group has been sharing Wordle scores for over a year. Some weeks everyone's in. Some weeks, it's a ghost town." | **Setup** -- establish the group, the timeframe, the emotional arc of participation. Reader thinks: "Oh, this is a real friend group." |
| 2 | **G2: Score distribution (stacked bar)** | "Most of us live in the 3-4 range. But look at the extremes." | **Tension** -- hint that there are different player profiles hiding in the aggregate. Reader thinks: "Who are the outliers?" |
| 3 | **P5: Skill vs Luck scatter** | "When we plotted skill against luck, the group split into clear clusters." | **Reveal** -- the personality types emerge. This is the centrepiece chart. Reader thinks: "I want to know where I'd fall." |
| 4 | **Type cards (2-3 examples)** | "Meet The Strategist and The Ghost." Show 2-3 of the most contrasting types as static card images. | **Payoff** -- the personality types come alive with real (pseudonymised) data. Reader thinks: "This is so specific, I love it." |
| 5 | **Quiz screenshot / CTA** | "Which type are you? Take the quiz." | **CTA** -- link to the Streamlit quiz. |

### Blog chart specifications:

- **Dimensions**: 800x500px for full-width charts, 400x400px for cards
- **Font**: System sans-serif (matches sowrao.com), 14px labels, 18px titles
- **Background**: Transparent or #f5f5f0 (matches blog)
- **Annotation style**: Handwritten-feel arrows or callout boxes where needed (matplotlib FancyArrowPatch or simple text annotations)
- **Export format**: PNG at 2x resolution for retina screens

---

## Part 5: Implementation Notes

### Chart-to-code mapping

| Chart | Library | Complexity | Notes |
|-------|---------|-----------|-------|
| G1 Activity line | Plotly (Streamlit) / matplotlib (blog) | Low | `px.line` with range slider |
| G2 Score distribution | Plotly bar / seaborn countplot | Low | Stacked, sorted by score |
| G3 Who played when | seaborn heatmap or Plotly heatmap | Medium | Needs pivot table: player x week |
| G4 Small multiples | matplotlib subplots | Medium | `fig, axes = plt.subplots(nrows, ncols)` |
| G5 Bump chart | Plotly line or matplotlib | Medium | Requires weekly ranking calc |
| P1 Radar chart | Plotly scatterpolar or matplotlib polar | Medium | Needs normalised features (0-1 scale) |
| P2 Strip plot | seaborn stripplot | Low | Jitter + group highlight |
| P3 Calendar heatmap | matplotlib with custom grid | High | Consider `calplot` library |
| P4 Time of day | Plotly bar / seaborn | Low | Bucket timestamps into 4 periods |
| P5 Skill vs Luck | Plotly scatter | Low | `px.scatter` with text labels |
| P6 Posting gaps | matplotlib broken_barh or timeline | Medium | One row per player |

### Colour assignments for personality types

| Type | Primary colour | Hex | Rationale |
|------|---------------|-----|-----------|
| The Strategist | Deep green | #2d6a4f | Precision, mastery |
| The Lucky One | Gold | #e9c46a | Fortune, sparkle |
| The Reliable | Steady blue | #457b9d | Dependable, calm |
| The Ghost | Muted purple | #7b2d8e | Mysterious, elusive |
| The Competitor | Bright red-orange | #e76f51 | Urgency, fire |
| The Wordsmith | Teal | #2a9d8f | Creative, unusual |

---

## Tone reminder

Every chart title should sound like something you'd say in the group chat, not in a boardroom:

- Yes: "The week we all forgot Wordle existed"
- No: "Player participation rate by calendar week"
- Yes: "Lucky or good? The eternal question."
- No: "Scatter plot of average score vs lucky rate"
- Yes: "Your Wordle DNA"
- No: "Normalised feature comparison radar chart"

The data is real, the analysis is rigorous, but the presentation is a love letter to the friend group.
