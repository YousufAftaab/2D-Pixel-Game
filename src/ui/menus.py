"""
STARBOUND: THE LOST REALMS
Menus & UI Screens
Main Menu, Pause, Settings, Level Complete, Game Over, Controls, and Credits.
"""

import pygame
from src.engine.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, UI_BG_DARK,
    UI_BORDER, UI_ACCENT_GOLD, UI_ACCENT_CYAN, UI_TEXT_MUTED,
    AVAILABLE_RESOLUTIONS
)


class BaseMenu:
    def __init__(self, font, font_small, options):
        self.font = font
        self.font_small = font_small
        self.options = options
        self.selected_idx = 0

    def navigate(self, delta, audio_manager):
        prev = self.selected_idx
        self.selected_idx = (self.selected_idx + delta) % len(self.options)
        if prev != self.selected_idx:
            audio_manager.play_sfx("menu_move")

    def get_selected(self):
        return self.options[self.selected_idx]


class MainMenu(BaseMenu):
    def __init__(self, font, font_small):
        super().__init__(font, font_small, [
            "Start Game",
            "World Map",
            "Settings",
            "Controls",
            "Credits",
            "Quit"
        ])
        self.star_offset = 0.0

    def update(self, dt):
        self.star_offset += dt * 20.0

    def draw(self, surface):
        # Cosmic deep blue gradient
        surface.fill((12, 14, 26))

        # Animated starfield
        for i in range(40):
            sx = int((i * 37 + self.star_offset * (0.3 + (i % 3) * 0.2)) % VIRTUAL_WIDTH)
            sy = int((i * 23) % VIRTUAL_HEIGHT)
            surface.set_at((sx, sy), (90, 110, 160))

        # Game Title Banner
        title = "STARBOUND"
        sub = "THE LOST REALMS"
        t_surf = self.font.render(title, False, UI_ACCENT_GOLD)
        t_shadow = self.font.render(title, False, (20, 20, 40))
        cx = VIRTUAL_WIDTH // 2 - t_surf.get_width() // 2
        surface.blit(t_shadow, (cx + 2, 38))
        surface.blit(t_surf, (cx, 36))

        sub_surf = self.font_small.render(sub, False, UI_ACCENT_CYAN)
        surface.blit(sub_surf, (VIRTUAL_WIDTH // 2 - sub_surf.get_width() // 2, 54))

        # Menu Options
        start_y = 95
        for i, opt in enumerate(self.options):
            is_sel = (i == self.selected_idx)
            color = UI_ACCENT_GOLD if is_sel else UI_TEXT_MUTED
            prefix = "> " if is_sel else "  "
            opt_surf = self.font.render(f"{prefix}{opt}", False, color)
            opt_x = VIRTUAL_WIDTH // 2 - opt_surf.get_width() // 2
            opt_y = start_y + i * 22
            surface.blit(opt_surf, (opt_x, opt_y))

        # Footer Prompt
        ft_surf = self.font_small.render("UP / DOWN: Select   |   ENTER / SPACE: Confirm", False, (120, 135, 170))
        surface.blit(ft_surf, (VIRTUAL_WIDTH // 2 - ft_surf.get_width() // 2, VIRTUAL_HEIGHT - 22))


class PauseMenu(BaseMenu):
    def __init__(self, font, font_small):
        super().__init__(font, font_small, [
            "Resume",
            "Restart Level",
            "Settings",
            "Exit to World Map",
            "Main Menu"
        ])

    def draw(self, surface):
        # Dark overlay
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 22, 185))
        surface.blit(overlay, (0, 0))

        # Box
        box = pygame.Rect(VIRTUAL_WIDTH // 2 - 110, 35, 220, 195)
        pygame.draw.rect(surface, UI_BG_DARK, box)
        pygame.draw.rect(surface, UI_BORDER, box, 2)

        t_surf = self.font.render("GAME PAUSED", False, UI_ACCENT_GOLD)
        surface.blit(t_surf, (VIRTUAL_WIDTH // 2 - t_surf.get_width() // 2, 50))

        start_y = 85
        for i, opt in enumerate(self.options):
            is_sel = (i == self.selected_idx)
            color = UI_ACCENT_CYAN if is_sel else UI_TEXT_MUTED
            prefix = "> " if is_sel else "  "
            opt_surf = self.font.render(f"{prefix}{opt}", False, color)
            surface.blit(opt_surf, (box.left + 25, start_y + i * 24))


class LevelCompleteMenu(BaseMenu):
    def __init__(self, font, font_small):
        super().__init__(font, font_small, [
            "Next Level",
            "Replay Level",
            "World Map"
        ])

    def draw(self, surface, level, is_new_record=False):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 25, 200))
        surface.blit(overlay, (0, 0))

        box = pygame.Rect(VIRTUAL_WIDTH // 2 - 130, 25, 260, 215)
        pygame.draw.rect(surface, UI_BG_DARK, box)
        pygame.draw.rect(surface, UI_ACCENT_GOLD, box, 2)

        t_surf = self.font.render("LEVEL COMPLETE!", False, UI_ACCENT_GOLD)
        surface.blit(t_surf, (VIRTUAL_WIDTH // 2 - t_surf.get_width() // 2, 38))

        if is_new_record:
            rec_surf = self.font_small.render("*** NEW HIGH SCORE ***", False, (255, 110, 80))
            surface.blit(rec_surf, (VIRTUAL_WIDTH // 2 - rec_surf.get_width() // 2, 56))

        # Stats summary
        mins = int(level.time_elapsed // 60)
        secs = int(level.time_elapsed % 60)
        stats = [
            f"Score: {level.score}",
            f"Star Shards: {level.shards_collected}/{level.total_level_shards}",
            f"Astral Crystals: {len(level.crystals_found)}/3",
            f"Enemies Defeated: {level.enemies_defeated}",
            f"Clear Time: {mins:02d}:{secs:02d}",
        ]

        stat_y = 74
        for s in stats:
            s_surf = self.font_small.render(s, False, COLOR_WHITE)
            surface.blit(s_surf, (box.left + 35, stat_y))
            stat_y += 15

        # Buttons
        btn_y = 156
        for i, opt in enumerate(self.options):
            is_sel = (i == self.selected_idx)
            color = UI_ACCENT_CYAN if is_sel else UI_TEXT_MUTED
            prefix = "> " if is_sel else "  "
            opt_surf = self.font.render(f"{prefix}{opt}", False, color)
            surface.blit(opt_surf, (box.left + 45, btn_y + i * 20))


class GameOverMenu(BaseMenu):
    def __init__(self, font, font_small):
        super().__init__(font, font_small, [
            "Respawn at Checkpoint",
            "Restart Level",
            "World Map",
            "Main Menu"
        ])

    def draw(self, surface):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 8, 12, 210))
        surface.blit(overlay, (0, 0))

        box = pygame.Rect(VIRTUAL_WIDTH // 2 - 120, 35, 240, 190)
        pygame.draw.rect(surface, UI_BG_DARK, box)
        pygame.draw.rect(surface, (230, 60, 70), box, 2)

        t_surf = self.font.render("MISSION FAILED", False, (240, 70, 80))
        surface.blit(t_surf, (VIRTUAL_WIDTH // 2 - t_surf.get_width() // 2, 50))

        start_y = 85
        for i, opt in enumerate(self.options):
            is_sel = (i == self.selected_idx)
            color = UI_ACCENT_GOLD if is_sel else UI_TEXT_MUTED
            prefix = "> " if is_sel else "  "
            opt_surf = self.font.render(f"{prefix}{opt}", False, color)
            surface.blit(opt_surf, (box.left + 25, start_y + i * 24))


class SettingsMenu(BaseMenu):
    def __init__(self, font, font_small, settings):
        self.settings = settings
        super().__init__(font, font_small, [
            "Resolution",
            "Fullscreen",
            "Master Volume",
            "Music Volume",
            "SFX Volume",
            "Screen Shake",
            "Assist Mode",
            "Back"
        ])

    def adjust_setting(self, delta, audio_manager):
        opt = self.options[self.selected_idx]
        if opt == "Resolution":
            count = len(AVAILABLE_RESOLUTIONS)
            self.settings["resolution_index"] = (self.settings.get("resolution_index", 0) + delta) % count
        elif opt == "Fullscreen":
            self.settings["fullscreen"] = not self.settings.get("fullscreen", False)
        elif opt == "Master Volume":
            vol = max(0.0, min(1.0, self.settings.get("master_volume", 0.8) + delta * 0.1))
            self.settings["master_volume"] = round(vol, 1)
        elif opt == "Music Volume":
            vol = max(0.0, min(1.0, self.settings.get("music_volume", 0.7) + delta * 0.1))
            self.settings["music_volume"] = round(vol, 1)
        elif opt == "SFX Volume":
            vol = max(0.0, min(1.0, self.settings.get("sfx_volume", 0.85) + delta * 0.1))
            self.settings["sfx_volume"] = round(vol, 1)
        elif opt == "Screen Shake":
            self.settings["screen_shake"] = not self.settings.get("screen_shake", True)
        elif opt == "Assist Mode":
            self.settings["assist_mode"] = not self.settings.get("assist_mode", False)
            if self.settings["assist_mode"]:
                self.settings["assist_extra_health"] = True
                self.settings["assist_extra_coyote"] = True
                self.settings["assist_slower_enemies"] = True

        audio_manager.apply_settings(self.settings)
        audio_manager.play_sfx("menu_select")

    def draw(self, surface):
        surface.fill((14, 16, 28))

        t_surf = self.font.render("SETTINGS & ACCESSIBILITY", False, UI_ACCENT_GOLD)
        surface.blit(t_surf, (VIRTUAL_WIDTH // 2 - t_surf.get_width() // 2, 16))

        start_y = 48
        res = AVAILABLE_RESOLUTIONS[self.settings.get("resolution_index", 0)]
        res_str = f"{res[0]}x{res[1]}"

        values = {
            "Resolution": res_str,
            "Fullscreen": "ON" if self.settings.get("fullscreen", False) else "OFF",
            "Master Volume": f"{int(self.settings.get('master_volume', 0.8) * 100)}%",
            "Music Volume": f"{int(self.settings.get('music_volume', 0.7) * 100)}%",
            "SFX Volume": f"{int(self.settings.get('sfx_volume', 0.85) * 100)}%",
            "Screen Shake": "ENABLED" if self.settings.get("screen_shake", True) else "DISABLED",
            "Assist Mode": "ENABLED" if self.settings.get("assist_mode", False) else "DISABLED",
            "Back": ""
        }

        for i, opt in enumerate(self.options):
            is_sel = (i == self.selected_idx)
            color = UI_ACCENT_CYAN if is_sel else UI_TEXT_MUTED
            prefix = "> " if is_sel else "  "

            opt_surf = self.font.render(f"{prefix}{opt}", False, color)
            surface.blit(opt_surf, (50, start_y + i * 22))

            val = values.get(opt, "")
            if val:
                val_surf = self.font.render(f"< {val} >", False, UI_ACCENT_GOLD if is_sel else COLOR_WHITE)
                surface.blit(val_surf, (310, start_y + i * 22))

        hint_surf = self.font_small.render("LEFT / RIGHT: Adjust Value   |   ENTER: Toggle / Select", False, (140, 155, 185))
        surface.blit(hint_surf, (VIRTUAL_WIDTH // 2 - hint_surf.get_width() // 2, VIRTUAL_HEIGHT - 22))


class ControlsMenu:
    def __init__(self, font, font_small):
        self.font = font
        self.font_small = font_small

    def draw(self, surface):
        surface.fill((14, 16, 28))

        t_surf = self.font.render("CONTROLS & SCHEME", False, UI_ACCENT_GOLD)
        surface.blit(t_surf, (VIRTUAL_WIDTH // 2 - t_surf.get_width() // 2, 16))

        # Dual Column Layout (Keyboard vs Controller)
        box_kb = pygame.Rect(30, 48, 200, 180)
        box_pad = pygame.Rect(250, 48, 200, 180)

        pygame.draw.rect(surface, UI_BG_DARK, box_kb)
        pygame.draw.rect(surface, UI_BORDER, box_kb, 1)
        pygame.draw.rect(surface, UI_BG_DARK, box_pad)
        pygame.draw.rect(surface, UI_BORDER, box_pad, 1)

        # Keyboard Column
        surface.blit(self.font.render("KEYBOARD", False, UI_ACCENT_CYAN), (box_kb.left + 15, box_kb.top + 10))
        kb_bindings = [
            ("A / D or Left / Right", "Move"),
            ("Space / W", "Jump"),
            ("S / Down", "Crouch / Slide"),
            ("L-Shift / J", "Sprint / Fire Blast"),
            ("E / Enter", "Interact / Enter"),
            ("ESC", "Pause Game"),
            ("F1 - F6", "Debug Controls"),
        ]
        ky = box_kb.top + 34
        for k, a in kb_bindings:
            s1 = self.font_small.render(k, False, UI_ACCENT_GOLD)
            s2 = self.font_small.render(a, False, COLOR_WHITE)
            surface.blit(s1, (box_kb.left + 12, ky))
            surface.blit(s2, (box_kb.left + 120, ky))
            ky += 19

        # Gamepad Column
        surface.blit(self.font.render("CONTROLLER", False, UI_ACCENT_CYAN), (box_pad.left + 15, box_pad.top + 10))
        pad_bindings = [
            ("Left Stick / D-Pad", "Move"),
            ("A / Cross Button", "Jump"),
            ("Down Stick", "Crouch / Slide"),
            ("B / Circle / X", "Sprint / Fire Blast"),
            ("Y / Triangle", "Interact"),
            ("Start / Menu", "Pause Game"),
            ("Auto-detected", "Plug & Play"),
        ]
        py = box_pad.top + 34
        for k, a in pad_bindings:
            s1 = self.font_small.render(k, False, UI_ACCENT_GOLD)
            s2 = self.font_small.render(a, False, COLOR_WHITE)
            surface.blit(s1, (box_pad.left + 12, py))
            surface.blit(s2, (box_pad.left + 120, py))
            py += 19

        ft_surf = self.font_small.render("Press ESC / ENTER to Return", False, (140, 155, 185))
        surface.blit(ft_surf, (VIRTUAL_WIDTH // 2 - ft_surf.get_width() // 2, VIRTUAL_HEIGHT - 20))


class CreditsMenu:
    def __init__(self, font, font_small):
        self.font = font
        self.font_small = font_small

    def draw(self, surface):
        surface.fill((12, 14, 26))

        t_surf = self.font.render("STARBOUND: THE LOST REALMS", False, UI_ACCENT_GOLD)
        surface.blit(t_surf, (VIRTUAL_WIDTH // 2 - t_surf.get_width() // 2, 20))

        lines = [
            ("Lead Game Engineer & Designer", "Mohammad Yousuf Aftaab"),
            ("Game Engine", "Python 3.13 & Pygame-CE 2.5.8"),
            ("Visual Artwork", "100% Original Bespoke Procedural Pixel Art"),
            ("Audio & Synthesizer", "Algorithmic Chiptune Multi-Track & SFX"),
            ("Platform", "Windows PC (Standalone Native Executable)"),
            ("Testing & QA", "Automated Pytest Suite & Engine Integration"),
            ("Thank you for playing!", "Enjoy your journey through the Lost Realms!"),
        ]

        start_y = 56
        for role, name in lines:
            r_surf = self.font_small.render(role, False, UI_ACCENT_CYAN)
            n_surf = self.font.render(name, False, COLOR_WHITE)
            surface.blit(r_surf, (VIRTUAL_WIDTH // 2 - r_surf.get_width() // 2, start_y))
            surface.blit(n_surf, (VIRTUAL_WIDTH // 2 - n_surf.get_width() // 2, start_y + 12))
            start_y += 28

        ft_surf = self.font_small.render("Press ESC / ENTER to Return", False, (140, 155, 185))
        surface.blit(ft_surf, (VIRTUAL_WIDTH // 2 - ft_surf.get_width() // 2, VIRTUAL_HEIGHT - 18))
