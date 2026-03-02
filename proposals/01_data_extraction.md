# Proposal 01 -- Data Extraction

## Assessment

### What the parser handles well

1. **Two-pass architecture is solid.** Pass 1 groups continuation lines (emoji grids, trailing commentary) into the parent message. Pass 2 extracts Wordle results. This cleanly separates structure parsing from content extraction and avoids the fragile alternative of trying to match a multi-line regex across the raw file.

2. **Comma-separated puzzle numbers.** `WORDLE_RE` matches `1,664` and the code strips commas before converting to int. This is correct for the confirmed format.

3. **Score + fail handling.** `[1-6X]` captures both numeric scores and fails (`X`), mapping X to `None`. Clean and intentional.

4. **Flexible timestamp regex.** `MESSAGE_RE` allows 1- or 2-digit month/day and 2- or 4-digit year, so it would survive minor format variations across iOS versions.

5. **Non-Wordle messages are silently dropped.** The `WORDLE_RE.search()` call in Pass 2 means the parser only keeps messages containing a Wordle result line; everything else is ignored without error.

### Gaps and fragile assumptions

| # | Issue | Severity | Detail |
|---|-------|----------|--------|
| 1 | **Hard mode asterisk not handled** | Medium | Wordle hard mode results display as `Wordle 1,664 3/6*`. The trailing `*` is not captured by `WORDLE_RE`, so these messages are silently dropped. |
| 2 | **Duplicate results per player per puzzle** | Low | If someone posts their result twice (copy-paste accident, correction), both are kept. Downstream features will double-count. |
| 3 | **System messages matched as senders** | Low | WhatsApp system messages (e.g., `[01/01/24, 12:00:00 AM] Messages and calls are end-to-end encrypted...`) have no colon-delimited sender but some system messages do match the `[^:]+:` pattern. The parser may create phantom senders. |
| 4 | **4-digit year format string mismatch** | Low | `MESSAGE_RE` accepts 4-digit years, but `pd.to_datetime` uses `%y` (2-digit). If an export uses `2024` instead of `24`, parsing will raise a `ValueError`. |
| 5 | **WhatsApp name changes** | Low | If a user changes their WhatsApp display name mid-export, they appear as two different senders. The parser has no aliasing mechanism. |
| 6 | **Media-only messages** | None | Messages like `<Media omitted>` are correctly ignored because they won't match `WORDLE_RE`. No action needed. |
| 7 | **Non-Wordle puzzle shares** | None | Messages like "Quordle 345 3/6" won't match because the regex requires the literal word `Wordle`. Safe. |

---

## Output schema

### Columns

| Column | dtype | Description |
|--------|-------|-------------|
| `sender` | `str` | Display name as it appears in the export |
| `puzzle_number` | `int64` | Wordle puzzle ID with commas stripped |
| `score` | `float64` (nullable) | 1--6 for successful attempts, `NaN` for X/fail |
| `timestamp` | `datetime64[ns]` | When the result was posted |

Note: `score` will be `float64` because pandas upcasts `int` columns that contain `None` values. Downstream code should use `pd.isna(score)` to detect fails rather than checking for `None`.

### Sample DataFrame

```
   sender                   puzzle_number  score  timestamp
0  Vaish Bharat Rudra       1664           3.0    2026-08-01 13:27:20
1  Vaish Bharat Rudra       1665           NaN    2026-08-02 07:15:03
2  Sowmya                   1664           4.0    2026-08-01 14:02:11
3  Sowmya                   1665           5.0    2026-08-02 08:30:44
4  Arun K                   1664           2.0    2026-08-01 18:45:00
```

### Downstream expectations

- `features.py` should join on `(sender, puzzle_number)` for per-player-per-puzzle analysis.
- `early_bird_rate` requires the `timestamp` column and a timezone assumption (the export's local time is used as-is; no tz conversion is applied by the parser).
- `fail_rate` should count rows where `pd.isna(score)`, not where `score == 'X'`.

---

## Edge case checklist

### Must fix (will lose data or produce errors)

- [ ] **Hard mode asterisk.** Change `WORDLE_RE` to: `r'Wordle\s+([\d,]+)\s+([1-6X])/6\*?'` and optionally capture a `hard_mode` boolean column. This is the only bug that silently drops valid results.

### Should fix (data quality)

- [ ] **Deduplicate results.** After building the DataFrame, drop duplicate `(sender, puzzle_number)` pairs, keeping the first occurrence. This prevents double-counting if someone posts a result twice.
- [ ] **Sender aliasing.** Add an optional `aliases` dict (e.g., `{"Old Name": "New Name"}`) and apply it after parsing. This handles WhatsApp name changes and also prepares the pipeline for the pseudonym substitution mentioned in CLAUDE.md's data privacy section.
- [ ] **4-digit year tolerance.** Either tighten `MESSAGE_RE` to only allow 2-digit years (matching the confirmed iOS format), or detect year length and switch the `strptime` format accordingly.

### Nice to have (robustness)

- [ ] **Filter system messages.** After Pass 1, drop messages where `sender` matches known system-message patterns (e.g., contains "end-to-end encrypted", "changed the subject", "added", "left").
- [ ] **Record hard mode flag.** If `*` is captured, store it as a `hard_mode: bool` column. This could feed into personality type classification (Strategist signal).
- [ ] **Timezone annotation.** Add a docstring or constant noting the assumed timezone. Not critical for relative features (streaks, gaps) but matters if `early_bird_rate` is compared across time zones.

---

## Blog post angle

For the "how we got the data" section of the blog post, consider framing it around the fun human mess of WhatsApp exports rather than the technical parsing: "We exported two years of our group chat and asked a script to find the Wordle scores hiding inside thousands of messages about kids, weekend plans, and unsolicited recipe links. The hardest part wasn't the code -- it was convincing everyone to let us peek at their scores." This keeps the tone warm, relatable, and honest about the fact that real-world data is messy, which is the whole charm of the project. The parser itself can be a one-line mention ("a short Python script that knows what a Wordle share looks like") rather than a walkthrough.
