from __future__ import annotations

TIERS = [
    "IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM",
    "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER",
]
DIVISIONS = ["IV", "III", "II", "I"]


def rank_ordinal(tier: str, division: str | None) -> int:
    tier_idx = TIERS.index(tier)
    division_idx = DIVISIONS.index(division) if division in DIVISIONS else 0
    return tier_idx * len(DIVISIONS) + division_idx


def compare_rank(old: tuple[str, str | None], new: tuple[str, str | None]) -> str | None:
    old_ord = rank_ordinal(*old)
    new_ord = rank_ordinal(*new)
    if new_ord > old_ord:
        return "promotion"
    if new_ord < old_ord:
        return "demotion"
    return None


def apply_streak(current_streak: int, won: bool) -> int:
    if won:
        return current_streak + 1 if current_streak >= 0 else 1
    return current_streak - 1 if current_streak <= 0 else -1
