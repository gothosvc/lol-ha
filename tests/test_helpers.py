import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components" / "lol_ha"))
from helpers import apply_streak, compare_rank, rank_ordinal  # noqa: E402


def test_rank_ordinal_orders_tiers_and_divisions():
    assert rank_ordinal("IRON", "IV") < rank_ordinal("IRON", "I")
    assert rank_ordinal("IRON", "I") < rank_ordinal("BRONZE", "IV")
    assert rank_ordinal("MASTER", None) < rank_ordinal("GRANDMASTER", None)


def test_compare_rank_detects_promotion_and_demotion():
    assert compare_rank(("GOLD", "II"), ("GOLD", "I")) == "promotion"
    assert compare_rank(("GOLD", "I"), ("PLATINUM", "IV")) == "promotion"
    assert compare_rank(("PLATINUM", "IV"), ("GOLD", "I")) == "demotion"
    assert compare_rank(("GOLD", "II"), ("GOLD", "II")) is None


def test_apply_streak_extends_and_resets():
    streak = 0
    streak = apply_streak(streak, won=True)
    streak = apply_streak(streak, won=True)
    assert streak == 2
    streak = apply_streak(streak, won=False)
    assert streak == -1
    streak = apply_streak(streak, won=False)
    assert streak == -2


if __name__ == "__main__":
    test_rank_ordinal_orders_tiers_and_divisions()
    test_compare_rank_detects_promotion_and_demotion()
    test_apply_streak_extends_and_resets()
    print("ok")
