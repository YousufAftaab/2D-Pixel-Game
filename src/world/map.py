"""
STARBOUND: THE LOST REALMS
World Map & Campaign Progression Navigator
Displays nodes for Worlds 1 to 6, level progression, completion percentages, and level selection.
"""

import math
import pygame
from src.engine.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, UI_BORDER, UI_ACCENT_GOLD, UI_ACCENT_CYAN
)


class WorldMap:
    WORLD_NAMES = {
        1: "Verdant Valley",
        2: "Sunscar Desert",
        3: "Frostfall",
        4: "Sky Ruins",
        5: "Ember Depths",
        6: "The Lost Realm"
    }

    # Map node positions in virtual 480x270 coordinates
    WORLD_NODES = {
        1: (80, 190),
        2: (170, 160),
        3: (230, 200),
        4: (290, 120),
        5: (370, 170),
        6: (410, 80),
    }

    def __init__(self, save_manager, audio_manager):
        self.save = save_manager
        self.audio = audio_manager
        self.current_world = 1
        self.current_sublevel = 1  # 1 to 4
        self.timer = 0.0

    def get_selected_level_id(self):
        return f"{self.current_world}-{self.current_sublevel}"

    def update(self, dt, input_mgr):
        self.timer += dt

        # Left / Right switches world
        if input_mgr.is_action_pressed("interact"):
            # Launch level
            selected = self.get_selected_level_id()
            if self.save.is_level_unlocked(selected):
                self.audio.play_sfx("menu_select")
                return selected
            else:
                self.audio.play_sfx("hurt")

        # Directional navigation
        if input_mgr.axis_x > 0.5 or input_mgr.is_action_pressed("right") if hasattr(input_mgr, 'is_action_pressed') else False:
            pass

    def handle_key_nav(self, key):
        """Processes discrete arrow / WASD inputs for precise map node traversal."""
        prev_w = self.current_world
        prev_s = self.current_sublevel

        if key in (pygame.K_RIGHT, pygame.K_d):
            if self.current_sublevel < 4:
                next_id = f"{self.current_world}-{self.current_sublevel + 1}"
                if self.save.is_level_unlocked(next_id):
                    self.current_sublevel += 1
            else:
                if self.current_world < 6:
                    next_id = f"{self.current_world + 1}-1"
                    if self.save.is_level_unlocked(next_id):
                        self.current_world += 1
                        self.current_sublevel = 1

        elif key in (pygame.K_LEFT, pygame.K_a):
            if self.current_sublevel > 1:
                self.current_sublevel -= 1
            elif self.current_world > 1:
                self.current_world -= 1
                self.current_sublevel = 4

        elif key in (pygame.K_UP, pygame.K_w):
            if self.current_world < 6:
                next_id = f"{self.current_world + 1}-1"
                if self.save.is_level_unlocked(next_id):
                    self.current_world += 1
                    self.current_sublevel = 1

        elif key in (pygame.K_DOWN, pygame.K_s):
            if self.current_world > 1:
                self.current_world -= 1
                self.current_sublevel = 1

        if prev_w != self.current_world or prev_s != self.current_sublevel:
            self.audio.play_sfx("menu_move")

    def draw(self, surface, font, font_small):
        # Background: Cosmic map domain
        surface.fill((14, 16, 28))

        # Ambient starlight grid
        for i in range(12):
            for j in range(7):
                px = i * 42 + 10
                py = j * 40 + 10
                surface.set_at((px, py), (35, 45, 70))

        # Draw pathways between worlds
        for w in range(1, 6):
            p1 = self.WORLD_NODES[w]
            p2 = self.WORLD_NODES[w + 1]
            unlocked = self.save.is_level_unlocked(f"{w + 1}-1")
            line_color = UI_ACCENT_CYAN if unlocked else (45, 55, 75)
            pygame.draw.line(surface, line_color, p1, p2, 2)

        # Draw World Nodes
        for w, (nx, ny) in self.WORLD_NODES.items():
            first_lvl = f"{w}-1"
            unlocked = self.save.is_level_unlocked(first_lvl)
            is_active = (w == self.current_world)

            radius = 12 if is_active else 8
            border_c = UI_ACCENT_GOLD if is_active else (UI_ACCENT_CYAN if unlocked else (60, 65, 80))
            fill_c = (50, 40, 80) if is_active else ((25, 35, 55) if unlocked else (20, 20, 30))

            pygame.draw.circle(surface, fill_c, (nx, ny), radius)
            pygame.draw.circle(surface, border_c, (nx, ny), radius, 2)

            # World number label
            num_txt = font_small.render(str(w), False, COLOR_WHITE if unlocked else (100, 105, 120))
            surface.blit(num_txt, (nx - num_txt.get_width() // 2, ny - num_txt.get_height() // 2))

        # Title Header
        title_surf = font.render("ASTRAL REALM NAVIGATION", False, UI_ACCENT_GOLD)
        surface.blit(title_surf, (VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 12))

        # Campaign Completion %
        pct = self.save.get_completion_percentage()
        pct_surf = font_small.render(f"Campaign Completion: {pct:.1f}%", False, UI_ACCENT_CYAN)
        surface.blit(pct_surf, (VIRTUAL_WIDTH - pct_surf.get_width() - 14, 14))

        # Selected World & Level Details Card (Bottom Panel)
        panel_rect = pygame.Rect(40, 208, 400, 52)
        pygame.draw.rect(surface, (20, 24, 40), panel_rect)
        pygame.draw.rect(surface, UI_BORDER, panel_rect, 1)

        level_id = self.get_selected_level_id()
        is_unlocked = self.save.is_level_unlocked(level_id)
        w_name = self.WORLD_NAMES.get(self.current_world, "Unknown Realm")

        w_txt = font.render(f"World {self.current_world}: {w_name}", False, COLOR_WHITE)
        surface.blit(w_txt, (50, 212))

        lvl_status = "LOCKED"
        if is_unlocked:
            lvl_status = "COMPLETED" if level_id in self.save.data["completed_levels"] else "UNLOCKED"

        color_status = (80, 230, 120) if lvl_status == "COMPLETED" else ((255, 215, 60) if lvl_status == "UNLOCKED" else (220, 70, 70))
        st_txt = font_small.render(f"Level {level_id} [{lvl_status}]", False, color_status)
        surface.blit(st_txt, (50, 230))

        # Best score and time
        best_sc = self.save.data["high_scores"].get(level_id, 0)
        best_tm = self.save.data["best_times"].get(level_id, 0.0)
        stats_txt = font_small.render(f"Best Score: {best_sc} | Best Time: {best_tm:.1f}s", False, (170, 185, 215))
        surface.blit(stats_txt, (50, 243))

        # Instructions prompt
        if is_unlocked:
            prompt_txt = font_small.render("Press ENTER / E to Enter Level", False, (255, 240, 140))
        else:
            prompt_txt = font_small.render("Level Locked — Clear Previous Levels", False, (240, 100, 100))
        surface.blit(prompt_txt, (panel_rect.right - prompt_txt.get_width() - 10, 240))
