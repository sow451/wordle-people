# Wordle People

> What two months of daily Wordle scores say about our friend group.

A companion app for a post on [sowrao.com](https://sowrao.com). We exported our WhatsApp group chat, parsed everyone's Wordle results, and used the data to classify each player into a personality type. There's also a quiz so anyone can find their own type.

---

## What it does

- **Parses** a WhatsApp iOS chat export and extracts Wordle scores per person per day
- **Computes** behavioural features: average score, consistency, fail rate, streak length, posting time, and more
- **Classifies** each player into one of six types: The Strategist, The Wildcard, The Reliable, The Ghost, The Competitor, The Wordsmith
- **Visualises** group stats and individual player profiles in an interactive Streamlit app
- **Hosts a quiz** so readers can find their own Wordle personality type

## Running it

```bash
# Install dependencies (first time only)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Place your WhatsApp export at data/whatsapp_export.txt
# then:
streamlit run app.py
```

Open http://localhost:8501.

## Project layout

```
├── app.py                    # Home page
├── pages/
│   ├── 1_Analysis.py         # Group stats + player profiles
│   └── 2_Quiz.py             # Personality quiz
├── src/
│   ├── parser.py             # WhatsApp export → DataFrame
│   ├── features.py           # Per-player behavioural features
│   ├── personality.py        # Rule-based type classifier
│   ├── quiz.py               # Quiz questions + scoring logic
│   └── aliases.py            # Display name mappings
└── data/
    └── whatsapp_export.txt   # Raw export (gitignored)
```

## The six types

| Type | Defining trait |
|------|---------------|
| The Strategist | Low scores, low variance — they have a system |
| The Wildcard | Nails it in 2 one day, X the next |
| The Reliable | Never fails, always finishes, never spectacular |
| The Ghost | Plays in bursts with long disappearing acts |
| The Competitor | Posts first, checks everyone else's score |
| The Wordsmith | Unusual openers, scenic routes, still arrives |

---

Built with Python, pandas, Streamlit, and Plotly.
