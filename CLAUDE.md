# Wordle People

A fun Python + Streamlit project for a post on [sowrao.com](https://sowrao.com) — "Daily stories, and notes from building things." The blog is personal and ideas-driven; posts range from fintech/product thinking to essays, parenting, and side projects. The audience is intelligent and curious but not necessarily technical — code snippets that appear in posts should be readable and explained in plain English.

We parsed Wordle results shared in a WhatsApp group chat, analysed everyone's playing patterns, and classified players into "Wordle personality types". The project also includes an interactive quiz so readers can find their own type.

## What this project is

- **Blog post companion app** — lightweight, opinionated, not production software
- **WhatsApp chat parser** → extract Wordle scores per person per day
- **Data analysis** → derive behavioural signals (consistency, luck, skill, risk-taking, etc.)
- **Personality type classifier** → assign each player to one of N archetypes
- **Streamlit quiz** → visitors to the blog can answer a few questions and get their type

## Tech stack

- **Python 3.12+**
- **Streamlit** — UI for both the analysis dashboard and the quiz
- **pandas** — data wrangling
- **matplotlib / seaborn** (or Plotly) — charts embedded in the Streamlit app
- **regex** — WhatsApp export parsing

No database. No auth. No deployment config needed beyond `streamlit run`.

## Project structure

```
wordle people/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── data/
│   └── whatsapp_export.txt      # raw WhatsApp chat export (gitignored)
├── parsed/
│   └── scores.csv               # cleaned scores (gitignored if private)
├── src/
│   ├── parser.py                # parse WhatsApp export → DataFrame
│   ├── features.py              # derive per-player behavioural features
│   ├── personality.py           # classify players into types
│   └── quiz.py                  # quiz logic (questions → type mapping)
├── pages/
│   ├── 1_Analysis.py            # Streamlit page: group stats & player profiles
│   └── 2_Quiz.py                # Streamlit page: the personality quiz
└── app.py                       # Streamlit entry point
```

## Wordle personality types (design)

Six types, each with a punchy name and a short description for the blog:

| Type | Name | Defining trait |
|------|------|----------------|
| 1 | **The Strategist** | Consistent, low guesses, uses hard mode |
| 2 | **The Lucky One** | High variance — sometimes 1-2, sometimes fails |
| 3 | **The Reliable** | Never fails, always finishes, never spectacular |
| 4 | **The Ghost** | Plays in bursts, long gaps, then suddenly active |
| 5 | **The Competitor** | Posts immediately, watches the leaderboard |
| 6 | **The Wordsmith** | Rare fails, unusual opening words, poetic about it |

Types are derived from a small set of features (see `src/features.py`).

## Behavioural features we extract

From the raw scores (1–6 or X per day) and timestamps:

- `avg_score` — mean guesses across all plays
- `fail_rate` — fraction of days ending in X
- `consistency` — std dev of scores (low = reliable)
- `streak_max` — longest consecutive playing streak
- `gap_max` — longest gap between plays
- `early_bird_rate` — fraction of scores posted before 9 AM
- `lucky_rate` — fraction of scores ≤ 2
- `come_from_behind_rate` — fraction of scores that were 5 or 6 but not X

## WhatsApp export format

Confirmed iOS format (12-hour clock, 2-digit year, US-style date):

```
[MM/DD/YY, H:MM:SS AM/PM] Name: message body
```

Real example:
```
[08/01/26, 1:27:20 PM] Vaish Bharat Rudra: Wordle 1,664 3/6
🟨🟨⬛🟨⬛
⬛⬛🟩⬛🟩
🟩🟩🟩🟩🟩 playing wordle for the first time. This is so much fun!
```

Notes:
- Puzzle numbers have commas (`1,664`)
- People sometimes add text after the grid — parser handles this
- Names can contain spaces and apostrophes
- Failed attempts show `X/6`

The parser (`src/parser.py`) extracts:
- Sender name
- Wordle puzzle number
- Score (integer 1–6, or `None` for X/fail)
- Timestamp

Messages that are not Wordle results are ignored.

## Quiz design

10 questions, each answer mapped to one or more personality type weights. Final type = highest weighted match. Questions avoid spoilers and are written to be fun, not rigorous. Examples:

- "What's your opening word strategy?" → informs Strategist vs Wordsmith
- "How do you feel when you fail?" → informs Reliable vs Lucky One
- "Do you check what others got before posting?" → informs Competitor

Quiz is implemented in `src/quiz.py` (pure logic) and rendered in `pages/2_Quiz.py` (Streamlit).

## Running the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

Place your WhatsApp export at `data/whatsapp_export.txt` before running the analysis page.

## Data privacy

- Real names are replaced with fun pseudonyms in all charts and the blog post
- The raw export file is gitignored
- No data leaves the local machine — everything runs in-browser via Streamlit

## Build order

1. **Analysis pipeline first** — parse the WhatsApp export, compute features, classify the friend group into types, build the analysis Streamlit page with charts
2. **Quiz second** — once the personality types are validated against real data, build the quiz logic and Streamlit page

The quiz types should feel like they emerged from the data, not be designed in a vacuum.

## Blog post structure (for reference)

1. Intro — "our WhatsApp group has been sharing Wordle scores for 2 years..."
2. The data — how we exported and parsed the chat
3. The personality types — profiles with charts
4. Player reveals — anonymised breakdown of who is who
5. Quiz CTA — "which type are you?"

The tone should match sowrao.com: warm, specific, a little self-deprecating. Name the friend archetypes with affection, not mockery.

## Conventions

- Keep it fun — this is a blog project, not enterprise software
- Prefer readable code over clever code; the blog audience may read snippets
- One Streamlit file per page in `pages/`, shared logic lives in `src/`
- Charts should be self-contained and export-friendly (PNG or inline Plotly)
- Commit data files only if they contain no real names
