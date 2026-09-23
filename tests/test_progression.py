"""
STARBOUND: THE LOST REALMS
Automated Unit Tests: World Progression & Level Layout Integrity
"""

import pytest
from src.world.levels_data import generate_level_data


def test_all_campaign_levels_exist():
    # Verify all 24 levels across 6 worlds have valid layouts
    for w in range(1, 7):
        for lvl in range(1, 5):
            lvl_id = f"{w}-{lvl}"
            data = generate_level_data(lvl_id)
            assert data is not None
            assert "name" in data
            assert "theme" in data
            assert "map" in data
            assert len(data["map"]) > 5
            # Must have Player spawn ('P')
            has_player = any('P' in row for row in data["map"])
            assert has_player is True, f"Level {lvl_id} missing player spawn 'P'"
            # Must have Exit Portal ('X')
            has_exit = any('X' in row for row in data["map"])
            assert has_exit is True, f"Level {lvl_id} missing exit portal 'X'"


def test_boss_levels_configured():
    boss_levels = ["1-4", "2-4", "3-4", "4-4", "5-4", "6-4"]
    for b_lvl in boss_levels:
        data = generate_level_data(b_lvl)
        assert data.get("is_boss", False) is True
        assert "boss_type" in data
        # Must have boss spawn in grid
        has_boss = any(('1' in row or '6' in row) for row in data["map"])
        assert has_boss is True, f"Boss level {b_lvl} missing boss entity spawn"


def test_final_boss_warden_level():
    data = generate_level_data("6-4")
    assert data["boss_type"] == "warden"
    assert data["theme"] == "lostrealm"
    has_warden = any('6' in row for row in data["map"])
    assert has_warden is True
