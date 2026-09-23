"""
STARBOUND: THE LOST REALMS
Automated Unit Tests: Save Manager & Persistence
"""

import os
import json
import pytest
from src.systems.save_manager import SaveManager


@pytest.fixture
def temp_save_manager(tmp_path):
    mgr = SaveManager()
    # Redirect save paths to temporary directory
    mgr.SAVE_FILE = str(tmp_path / "test_save.json")
    mgr.BACKUP_FILE = str(tmp_path / "test_save.bak")
    mgr.data = mgr.get_default_save()
    mgr.save()
    return mgr


def test_save_manager_defaults(temp_save_manager):
    mgr = temp_save_manager
    assert "1-1" in mgr.data["unlocked_levels"]
    assert mgr.data["total_star_shards"] == 0
    assert mgr.data["campaign_completed"] is False


def test_save_and_reload(temp_save_manager):
    mgr = temp_save_manager
    mgr.unlock_level("1-2")
    mgr.complete_level("1-1", score=2500, time_taken=45.2, shards_collected=30, new_crystals=["1-1_c1"])

    # Load fresh manager on same file
    mgr2 = SaveManager()
    mgr2.SAVE_FILE = mgr.SAVE_FILE
    mgr2.BACKUP_FILE = mgr.BACKUP_FILE
    loaded = mgr2.load()

    assert loaded is True
    assert "1-2" in mgr2.data["unlocked_levels"]
    assert "1-1" in mgr2.data["completed_levels"]
    assert mgr2.data["high_scores"]["1-1"] == 2500
    assert mgr2.data["best_times"]["1-1"] == 45.2
    assert mgr2.data["total_star_shards"] == 30
    assert "1-1_c1" in mgr2.data["secret_crystals"]


def test_save_corruption_fallback(temp_save_manager):
    mgr = temp_save_manager
    mgr.unlock_level("1-2")
    mgr.save()

    # Intentionally corrupt primary save file with bad checksum
    with open(mgr.SAVE_FILE, "w", encoding="utf-8") as f:
        f.write('{"version": "1.0", "checksum": "corrupted_hash", "data": {"unlocked_levels": ["corrupted"]}}')

    # Manager should detect corruption and fall back to backup!
    mgr2 = SaveManager()
    mgr2.SAVE_FILE = mgr.SAVE_FILE
    mgr2.BACKUP_FILE = mgr.BACKUP_FILE
    mgr2.load()

    # Backup had "1-2" unlocked
    assert "1-2" in mgr2.data["unlocked_levels"]


def test_completion_percentage(temp_save_manager):
    mgr = temp_save_manager
    # Initially 0% completed
    pct0 = mgr.get_completion_percentage()
    assert pct0 == 0.0

    # Complete 12 levels (50% of 24 levels = 35% campaign weight)
    for i in range(12):
        mgr.data["completed_levels"].append(f"lvl_{i}")

    pct1 = mgr.get_completion_percentage()
    assert pct1 == pytest.approx(35.0, 0.1)
