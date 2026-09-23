"""
STARBOUND: THE LOST REALMS
Save & Persistence Manager
Provides JSON save/load with checksum verification, automatic backup, and autosave.
"""

import os
import json
import hashlib
from src.engine.config import SAVE_DIR, DEFAULT_SETTINGS


class SaveManager:
    SAVE_FILE = os.path.join(SAVE_DIR, "save_data.json")
    BACKUP_FILE = os.path.join(SAVE_DIR, "save_data.bak")

    def __init__(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        self.data = self.get_default_save()
        self.load()

    def get_default_save(self):
        return {
            "unlocked_worlds": [1],
            "unlocked_levels": ["1-1"],
            "completed_levels": [],
            "total_star_shards": 0,
            "secret_crystals": [],
            "high_scores": {},
            "best_times": {},
            "campaign_completed": False,
            "settings": dict(DEFAULT_SETTINGS),
        }

    def _calculate_checksum(self, data_dict):
        serialized = json.dumps(data_dict, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def save(self):
        try:
            checksum = self._calculate_checksum(self.data)
            payload = {
                "version": "1.0",
                "checksum": checksum,
                "data": self.data
            }
            # Save to temporary file first, then atomic rename
            temp_file = self.SAVE_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            # Create backup of existing save if present
            if os.path.exists(self.SAVE_FILE):
                if os.path.exists(self.BACKUP_FILE):
                    os.remove(self.BACKUP_FILE)
                os.rename(self.SAVE_FILE, self.BACKUP_FILE)

            os.rename(temp_file, self.SAVE_FILE)
            return True
        except Exception as e:
            print(f"[SaveManager] Error saving data: {e}")
            return False

    def load(self):
        for filepath in [self.SAVE_FILE, self.BACKUP_FILE]:
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        payload = json.load(f)

                    raw_data = payload.get("data")
                    checksum = payload.get("checksum")
                    if raw_data and checksum and self._calculate_checksum(raw_data) == checksum:
                        self.data = self._merge_with_defaults(raw_data)
                        return True
                    else:
                        print(f"[SaveManager] Checksum mismatch in {filepath}, trying backup...")
                except Exception as e:
                    print(f"[SaveManager] Failed to parse {filepath}: {e}")

        # If loading fails or files do not exist, use default
        self.data = self.get_default_save()
        self.save()
        return False

    def _merge_with_defaults(self, loaded_data):
        defaults = self.get_default_save()
        merged = dict(defaults)
        merged.update(loaded_data)
        # Deep merge settings
        merged_settings = dict(defaults["settings"])
        if "settings" in loaded_data and isinstance(loaded_data["settings"], dict):
            merged_settings.update(loaded_data["settings"])
        merged["settings"] = merged_settings
        return merged

    def is_level_unlocked(self, level_id):
        return level_id in self.data["unlocked_levels"]

    def unlock_level(self, level_id):
        if level_id not in self.data["unlocked_levels"]:
            self.data["unlocked_levels"].append(level_id)
            self.save()

    def complete_level(self, level_id, score, time_taken, shards_collected, new_crystals):
        if level_id not in self.data["completed_levels"]:
            self.data["completed_levels"].append(level_id)

        self.data["total_star_shards"] += shards_collected

        for c_id in new_crystals:
            if c_id not in self.data["secret_crystals"]:
                self.data["secret_crystals"].append(c_id)

        # High score
        current_best_score = self.data["high_scores"].get(level_id, 0)
        if score > current_best_score:
            self.data["high_scores"][level_id] = score

        # Best time
        current_best_time = self.data["best_times"].get(level_id, 999999.0)
        if time_taken < current_best_time:
            self.data["best_times"][level_id] = time_taken

        self.save()

    def get_completion_percentage(self):
        total_possible_levels = 24  # 6 worlds * 4 levels
        total_possible_crystals = 24 * 3
        levels_done = len(self.data["completed_levels"])
        crystals_done = len(self.data["secret_crystals"])

        level_weight = (levels_done / total_possible_levels) * 70.0
        crystal_weight = (crystals_done / total_possible_crystals) * 30.0
        return min(100.0, level_weight + crystal_weight)
