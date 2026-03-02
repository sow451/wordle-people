import re
import pandas as pd
from pathlib import Path

# iOS WhatsApp export format:
# [MM/DD/YY, H:MM:SS AM/PM] Sender Name: message body
MESSAGE_RE = re.compile(
    r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}:\d{2}\s+[AP]M)\]\s+([^:]+):\s+(.*)'
)

# Matches "Wordle 1,664 3/6" or "Wordle 1,664 X/6" (with optional hard-mode asterisk)
WORDLE_RE = re.compile(r'Wordle\s+([\d,]+)\s+([1-6X])/6(\*?)')


def parse_chat(filepath: str | Path, aliases: dict[str, str] | None = None) -> pd.DataFrame:
    """
    Parse a WhatsApp iOS export and return a DataFrame of Wordle results.

    Parameters:
      filepath - path to the WhatsApp export text file
      aliases  - optional dict mapping original sender names to replacements,
                 e.g. {"Old WhatsApp Name": "Pseudonym"}

    Columns returned:
      sender        - name as it appears in the chat (or aliased name)
      puzzle_number - integer puzzle ID (e.g. 1664)
      score         - integer 1–6, or None for a failed attempt (X)
      hard_mode     - True if the result was posted with a hard-mode asterisk
      timestamp     - pandas Timestamp of when the result was posted
    """
    lines = Path(filepath).read_text(encoding='utf-8').splitlines()

    # Pass 1: group lines into messages.
    # Continuation lines (no timestamp prefix) are part of the previous message —
    # this handles grids and any text the person adds after their result.
    messages = []
    current = None

    for line in lines:
        match = MESSAGE_RE.match(line)
        if match:
            if current:
                messages.append(current)
            date_str, time_str, sender, body = match.groups()
            current = {
                'date': date_str,
                'time': time_str,
                'sender': sender.strip(),
                'body': body,
            }
        elif current:
            current['body'] += '\n' + line

    if current:
        messages.append(current)

    if aliases:
        for msg in messages:
            msg['sender'] = aliases.get(msg['sender'], msg['sender'])

    # Pass 2: pull out any message that contains a Wordle result.
    records = []
    for msg in messages:
        wordle_match = WORDLE_RE.search(msg['body'])
        if not wordle_match:
            continue

        puzzle_str, score_str, hard_str = wordle_match.groups()
        puzzle_number = int(puzzle_str.replace(',', ''))
        score = None if score_str == 'X' else int(score_str)
        hard_mode = bool(hard_str)

        timestamp = pd.to_datetime(
            f"{msg['date']} {msg['time']}",
            format='%d/%m/%y %I:%M:%S %p',
        )

        records.append({
            'sender': msg['sender'],
            'puzzle_number': puzzle_number,
            'score': score,
            'hard_mode': hard_mode,
            'timestamp': timestamp,
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df = df.sort_values(['puzzle_number', 'timestamp']).reset_index(drop=True)
    df = df.drop_duplicates(subset=['sender', 'puzzle_number'], keep='first')
    return df


if __name__ == '__main__':
    df = parse_chat('data/whatsapp_export.txt')
    print(f"Parsed {len(df)} Wordle results from {df['sender'].nunique()} players")
    print(f"Puzzle range: {df['puzzle_number'].min()} – {df['puzzle_number'].max()}")
    print()
    print(df.head(20).to_string())
