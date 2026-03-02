"""
make_demo_export.py
-------------------
Reads the private WhatsApp export and writes a publishable version:
  - Keeps ONLY messages that contain a Wordle result
  - Replaces every sender's real name with their display alias
  - Strips any personal text from the message body (keeps only the
    Wordle result line + the emoji grid lines)

Output: data/demo_export.txt  (safe to commit)

Usage:
    python scripts/make_demo_export.py
"""

import re
import sys
from pathlib import Path

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from aliases import ALIASES  # noqa: E402

SRC = Path(__file__).parent.parent / "data" / "whatsapp_export.txt"
DST = Path(__file__).parent.parent / "data" / "demo_export.txt"

# Matches a timestamp-prefixed message line
MESSAGE_RE = re.compile(
    r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}:\d{2}\s+[AP]M)\]\s+([^:]+):\s+(.*)'
)

# Matches the Wordle result line itself
WORDLE_LINE_RE = re.compile(r'Wordle\s+[\d,]+\s+[1-6X]/6\*?')

# Matches emoji grid lines (only Wordle-tile emoji, optional spaces)
GRID_LINE_RE = re.compile(r'^[🟩🟨⬛🟦🟧⬜\s]+$')


def strip_to_wordle_body(body: str) -> str:
    """Return only the Wordle result line + grid lines from a message body."""
    kept = []
    for line in body.splitlines():
        if WORDLE_LINE_RE.search(line) or GRID_LINE_RE.match(line.strip()):
            kept.append(line)
    return "\n".join(kept)


def main() -> None:
    if not SRC.exists():
        print(f"Source file not found: {SRC}")
        sys.exit(1)

    raw_lines = SRC.read_text(encoding="utf-8").splitlines()

    # Group into messages (same multi-line logic as parser.py)
    messages: list[dict] = []
    current: dict | None = None

    for line in raw_lines:
        m = MESSAGE_RE.match(line)
        if m:
            if current:
                messages.append(current)
            date_str, time_str, sender, body = m.groups()
            current = {
                "prefix": f"[{date_str}, {time_str}]",
                "sender": sender.strip(),
                "body": body,
            }
        elif current:
            current["body"] += "\n" + line

    if current:
        messages.append(current)

    # Filter to Wordle messages only, apply aliases, strip personal text
    output_lines: list[str] = []
    kept = 0

    for msg in messages:
        if not WORDLE_LINE_RE.search(msg["body"]):
            continue  # not a Wordle message — skip entirely

        alias = ALIASES.get(msg["sender"], msg["sender"])
        clean_body = strip_to_wordle_body(msg["body"])

        if not clean_body:
            continue  # grid lines didn't survive — skip

        # Reconstruct as a single WhatsApp-format message block
        first_line, *rest = clean_body.splitlines()
        output_lines.append(f"{msg['prefix']} {alias}: {first_line}")
        output_lines.extend(rest)
        kept += 1

    DST.parent.mkdir(exist_ok=True)
    DST.write_text("\n".join(output_lines) + "\n", encoding="utf-8")

    print(f"Done. {kept} Wordle messages written to {DST}")
    print("Real names replaced with aliases. Personal text stripped.")
    print("Review the file before committing.")


if __name__ == "__main__":
    main()
