"""
Quiz logic for Wordle People.

Ten questions, each answer carrying weights for one or more personality types.
Final type = whichever type accumulates the most points.

Pure Python — no Streamlit imports here.
"""

# Type name constants (match personality.py TYPES keys exactly)
STRATEGIST = "The Strategist"
WILDCARD = "The Wildcard"
RELIABLE = "The Reliable"
GHOST = "The Ghost"
COMPETITOR = "The Competitor"
WORDSMITH = "The Wordsmith"

ALL_TYPES = [STRATEGIST, WILDCARD, RELIABLE, GHOST, COMPETITOR, WORDSMITH]


# ── Question bank ─────────────────────────────────────────────────────────────
#
# Each question is a dict:
#   text    : str   — the question shown to the user
#   answers : list  — each answer is {label: str, weights: {type: points}}
#
# weights only need to list types that get points — missing types default to 0.

QUESTIONS = [
    {
        "text": "What's your opening word?",
        "answers": [
            {
                "label": "A reliable classic — CRANE, SLATE, ADIEU. It works.",
                "weights": {STRATEGIST: 2, RELIABLE: 1},
            },
            {
                "label": "Something unusual. FJORD. OVOID. EPOXY. Life's too short for CRANE.",
                "weights": {WORDSMITH: 3, WILDCARD: 1},
            },
            {
                "label": "I mix it up — no fixed opener, vibes only.",
                "weights": {WILDCARD: 2, WORDSMITH: 1},
            },
            {
                "label": "Whatever comes to mind. I don't really have a strategy.",
                "weights": {GHOST: 2, WILDCARD: 1},
            },
        ],
    },
    {
        "text": "When do you usually play?",
        "answers": [
            {
                "label": "First thing in the morning, before anyone else posts.",
                "weights": {COMPETITOR: 3, STRATEGIST: 1},
            },
            {
                "label": "Morning-ish. Sometime before lunch.",
                "weights": {RELIABLE: 2, STRATEGIST: 1},
            },
            {
                "label": "Whenever I remember — could be 9 AM, could be 11 PM.",
                "weights": {GHOST: 2, WILDCARD: 1},
            },
            {
                "label": "Late at night, no rush, just me and the word.",
                "weights": {WORDSMITH: 2, GHOST: 1},
            },
        ],
    },
    {
        "text": "You get X. You failed. What now?",
        "answers": [
            {
                "label": "I replay every guess in my head. What did I miss?",
                "weights": {STRATEGIST: 2, RELIABLE: 1},
            },
            {
                "label": "Post it with a shrug emoji and move on.",
                "weights": {WILDCARD: 2, GHOST: 1},
            },
            {
                "label": "Honestly relieved. Now I don't have to share.",
                "weights": {GHOST: 3},
            },
            {
                "label": "Annoyed, but tomorrow is a new word.",
                "weights": {RELIABLE: 1, WORDSMITH: 1},
            },
        ],
    },
    {
        "text": "Someone posts their result before you've played. Do you look?",
        "answers": [
            {
                "label": "Never. I solve it completely on my own first.",
                "weights": {STRATEGIST: 2, WORDSMITH: 1},
            },
            {
                "label": "I check the scores but shield my eyes from the colours.",
                "weights": {COMPETITOR: 2, RELIABLE: 1},
            },
            {
                "label": "Sometimes, if I'm really stuck.",
                "weights": {WILDCARD: 1, GHOST: 1},
            },
            {
                "label": "I post mine first, then go back and read everything.",
                "weights": {COMPETITOR: 3},
            },
        ],
    },
    {
        "text": "You get it in 2. Your reaction?",
        "answers": [
            {
                "label": "Pure elation. Screenshot. Posted immediately.",
                "weights": {COMPETITOR: 2, WILDCARD: 1},
            },
            {
                "label": "Nice! But... was that skill or luck? Hard to say.",
                "weights": {STRATEGIST: 1, WORDSMITH: 2},
            },
            {
                "label": "I mean, that's basically the plan every day.",
                "weights": {WILDCARD: 2, COMPETITOR: 1},
            },
            {
                "label": "A quiet moment of satisfaction. I don't need to announce it.",
                "weights": {RELIABLE: 1, WORDSMITH: 1, STRATEGIST: 1},
            },
        ],
    },
    {
        "text": "How long do you think before committing to a guess?",
        "answers": [
            {
                "label": "Seconds. I type it, I submit it. Flow state.",
                "weights": {WILDCARD: 2, COMPETITOR: 1},
            },
            {
                "label": "A few seconds — I run through my system.",
                "weights": {STRATEGIST: 3},
            },
            {
                "label": "A minute or two. I want to eliminate possibilities properly.",
                "weights": {RELIABLE: 2, STRATEGIST: 1},
            },
            {
                "label": "As long as it takes. I'm not competing with anyone.",
                "weights": {WORDSMITH: 3, GHOST: 1},
            },
        ],
    },
    {
        "text": "Your daily streak breaks. You missed yesterday. How do you feel?",
        "answers": [
            {
                "label": "Genuinely gutted. Streaks are everything.",
                "weights": {COMPETITOR: 2, STRATEGIST: 1},
            },
            {
                "label": "A bit sad, but I'll start a new one.",
                "weights": {RELIABLE: 2, WILDCARD: 1},
            },
            {
                "label": "Meh. Streaks are a trap.",
                "weights": {WILDCARD: 2, GHOST: 1},
            },
            {
                "label": "What streak? I don't track that.",
                "weights": {GHOST: 3},
            },
        ],
    },
    {
        "text": "How often do you post your score in the group?",
        "answers": [
            {
                "label": "Every day. Never miss.",
                "weights": {RELIABLE: 2, COMPETITOR: 2},
            },
            {
                "label": "Most days, but I skip if I'm busy.",
                "weights": {RELIABLE: 1, STRATEGIST: 1},
            },
            {
                "label": "In bursts — silent for two weeks, then ten posts in a row.",
                "weights": {GHOST: 3},
            },
            {
                "label": "Only when I do really well. Or really badly.",
                "weights": {WILDCARD: 2, COMPETITOR: 1},
            },
        ],
    },
    {
        "text": "Wordle is best described as...",
        "answers": [
            {
                "label": "A daily optimisation puzzle. There is a correct approach.",
                "weights": {STRATEGIST: 3},
            },
            {
                "label": "A five-minute ritual. Part of the morning routine.",
                "weights": {RELIABLE: 2, COMPETITOR: 1},
            },
            {
                "label": "A mood. I play when I feel like it.",
                "weights": {GHOST: 2, WILDCARD: 1},
            },
            {
                "label": "A small daily conversation with the English language.",
                "weights": {WORDSMITH: 3},
            },
        ],
    },
    {
        "text": "Someone in the group beats your personal best. You:",
        "answers": [
            {
                "label": "Congratulate them — then immediately start plotting tomorrow.",
                "weights": {COMPETITOR: 2, STRATEGIST: 1},
            },
            {
                "label": "Post a 🔥 emoji and genuinely mean it.",
                "weights": {WILDCARD: 1, RELIABLE: 2},
            },
            {
                "label": "Feel the sting privately. Say nothing.",
                "weights": {COMPETITOR: 2, STRATEGIST: 1},
            },
            {
                "label": "Don't really notice — you're playing for yourself.",
                "weights": {GHOST: 2, WORDSMITH: 2},
            },
        ],
    },
]


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_quiz(answer_indices: list[int]) -> dict[str, int]:
    """
    Given a list of chosen answer indices (one per question),
    return a dict of {type_name: total_points}.

    answer_indices[i] is the 0-based index of the chosen answer for QUESTIONS[i].
    """
    totals: dict[str, int] = {t: 0 for t in ALL_TYPES}

    for q_idx, a_idx in enumerate(answer_indices):
        weights = QUESTIONS[q_idx]["answers"][a_idx]["weights"]
        for type_name, points in weights.items():
            totals[type_name] += points

    return totals


def get_result(answer_indices: list[int]) -> str:
    """
    Return the winning personality type name for the given answers.
    Ties broken by the order in ALL_TYPES (earlier = higher priority).
    """
    totals = score_quiz(answer_indices)
    return max(ALL_TYPES, key=lambda t: totals[t])


# ── CLI preview ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{len(QUESTIONS)} questions loaded\n")
    for i, q in enumerate(QUESTIONS, 1):
        print(f"Q{i}: {q['text']}")
        for j, a in enumerate(q["answers"]):
            print(f"   {j+1}. {a['label']}")
            print(f"      → {a['weights']}")
        print()

    # Quick smoke test: pick the first answer every time
    test_result = get_result([0] * len(QUESTIONS))
    print(f"All-first-answer result: {test_result}")
