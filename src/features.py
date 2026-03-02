import numpy as np
import pandas as pd


def get_excluded_players(df: pd.DataFrame, min_plays: int = 10) -> list[str]:
    """Return senders with fewer than min_plays games."""
    counts = df.groupby('sender').size()
    return counts[counts < min_plays].index.tolist()


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build one row of behavioural features per player from parsed Wordle results.

    Input:  DataFrame with columns [sender, puzzle_number, score, timestamp, hard_mode].
            score is NaN for failed (X) attempts.
    Output: DataFrame indexed by sender with 13 feature columns.
            All players are included regardless of how many times they played.
    """
    df = df.copy()

    if df.empty:
        return pd.DataFrame()

    # Global puzzle range — used for active_days_pct
    global_min_puzzle = df['puzzle_number'].min()
    global_max_puzzle = df['puzzle_number'].max()
    global_puzzle_span = global_max_puzzle - global_min_puzzle + 1

    # --- Speed rank: per puzzle, rank players by timestamp ---
    df['speed_rank'] = (
        df.groupby('puzzle_number')['timestamp']
        .rank(method='average')
    )

    players = df['sender'].unique()
    rows = []

    for sender in players:
        p = df[df['sender'] == sender].sort_values('puzzle_number')

        total_plays = len(p)
        valid = p[p['score'].notna()]
        n_valid = len(valid)
        n_failed = total_plays - n_valid

        # --- Core features ---
        if n_valid == 0:
            avg_score = 7.0
            consistency = 0.0
            lucky_rate = 0.0
            clutch_rate = 0.0
            variance_score = 0.0
        else:
            scores = valid['score']
            avg_score = scores.mean()
            consistency = scores.std(ddof=0)
            lucky_rate = (scores <= 2).sum() / n_valid
            clutch_rate = scores.isin([5, 6]).sum() / n_valid
            variance_score = scores.max() - scores.min()

        fail_rate = n_failed / total_plays

        # --- Streaks and gaps ---
        puzzles = p['puzzle_number'].sort_values().values
        diffs = np.diff(puzzles)

        # streak_max: longest run of diff==1 (consecutive days)
        streak_max = 1  # a single play counts as streak of 1
        if len(diffs) > 0:
            current_streak = 1
            best_streak = 1
            for d in diffs:
                if d == 1:
                    current_streak += 1
                    best_streak = max(best_streak, current_streak)
                else:
                    current_streak = 1
            streak_max = best_streak

        # gap_max: largest diff > 1 (or 0 if no gaps)
        gaps = diffs[diffs > 1]
        gap_max = int(gaps.max()) if len(gaps) > 0 else 0

        # --- Participation ---
        active_days_pct = total_plays / global_puzzle_span

        # --- Early bird ---
        early_bird_rate = (p['timestamp'].dt.hour < 9).sum() / total_plays

        # --- Speed rank average ---
        speed_rank_avg = p['speed_rank'].mean()

        # --- Improvement trend (slope via polyfit) ---
        if n_valid >= 5:
            x = valid['puzzle_number'].values.astype(float)
            y = valid['score'].values.astype(float)
            improvement_trend = np.polyfit(x, y, 1)[0]
        else:
            improvement_trend = 0.0

        rows.append({
            'sender': sender,
            'total_plays': total_plays,
            'avg_score': round(avg_score, 3),
            'fail_rate': round(fail_rate, 4),
            'consistency': round(consistency, 3),
            'lucky_rate': round(lucky_rate, 4),
            'clutch_rate': round(clutch_rate, 4),
            'streak_max': streak_max,
            'gap_max': gap_max,
            'active_days_pct': round(active_days_pct, 4),
            'early_bird_rate': round(early_bird_rate, 4),
            'speed_rank_avg': round(speed_rank_avg, 3),
            'variance_score': variance_score,
            'improvement_trend': round(improvement_trend, 6),
        })

    features = pd.DataFrame(rows).set_index('sender')
    return features


if __name__ == '__main__':
    from parser import parse_chat

    df = parse_chat('data/whatsapp_export.txt')
    print(f"Parsed {len(df)} results from {df['sender'].nunique()} players\n")

    excluded = get_excluded_players(df)
    if excluded:
        print(f"Excluded (< 10 plays): {', '.join(excluded)}\n")

    features = compute_features(df)
    print(features.to_string())
