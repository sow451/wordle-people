"""
Display name aliases for the Wordle People app.

Real WhatsApp names → short display names used in all charts and the quiz.
Sowmya keeps her full name; everyone else gets the first 2 letters of their
first name. Where two names share the same 2-letter prefix a 3rd letter is
added to keep them distinct.
"""

ALIASES: dict[str, str] = {
    "Sowmya Rao":                       "Sowmya",
    "Apoorva Sudharshan":               "Ap",
    "Avinash Bajaj":                    "Av",
    "Bharat Ram Nivi Kriti's Dad":      "Bh",
    "Darshi":                           "Da",
    "Megha Pranshu":                    "Me",
    "Pallavi Palkar":                   "Pa",
    "Pavan Ruas Dad":                   "Pav",   # Pa + v to distinguish from Pallavi
    "Pranshu Diwan":                    "Pr",
    "Sudarshan S Nidhi":                "Su",
    "Vaish Bharat Rudra":               "Va",
    "Vaishnavi C605":                   "Vn",    # V + n (the distinctive part of Vaishnavi)
    "Vidisha Hegde Nivriti's Mom":      "Vid",   # Vi + d to distinguish from Vinay
    "Vinay Kesari":                     "Vin",   # Vi + n to distinguish from Vidisha
}
