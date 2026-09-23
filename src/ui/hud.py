"""
STARBOUND: THE LOST REALMS
Heads-Up Display (HUD)
Renders player health, active power-up badge, score, star shards, crystals, and timer.
"""

import pygame
from src.engine.config import (
    VIRTUAL_WIDTH, UI_HEALTH_RED, UI_HEALTH_EMPTY, UI_ACCENT_GOLD,
    UI_ACCENT_CYAN, COLOR_WHITE, POWERUP_NONE, POWERUP_EMBER,
    POWERUP_SKY, POWERUP_SHIELD, POWERUP_SPEED
)


class HUD:
    def __init__(self, font, font_small):
        self.font = font
        self.font_small = font_small

    def draw(self, surface, player, level, assets):
        # 1. TOP-LEFT: Health Hearts & Power-up Badge
        start_x = 10
        start_y = 8
        for i in range(player.max_health):
            hx = start_x + i * 14
            hy = start_y
            color = UI_HEALTH_RED if i < player.health else UI_HEALTH_EMPTY
            # Draw pixel heart
            pygame.draw.circle(surface, color, (hx + 3, hy + 3), 3)
            pygame.draw.circle(surface, color, (hx + 8, hy + 3), 3)
            pygame.draw.polygon(surface, color, [(hx + 1, hy + 4), (hx + 10, hy + 4), (hx + 5, hy + 9)])
            # Outline
            pygame.draw.polygon(surface, (20, 20, 30), [(hx + 1, hy + 4), (hx + 10, hy + 4), (hx + 5, hy + 9)], 1)

        # Power-Up Icon Badge below hearts
        if player.powerup != POWERUP_NONE:
            badge_rect = pygame.Rect(start_x, start_y + 13, 14, 14)
            pygame.draw.rect(surface, (25, 30, 45), badge_rect)
            pygame.draw.rect(surface, UI_ACCENT_CYAN, badge_rect, 1)

            key_map = {
                POWERUP_EMBER: "powerup_ember",
                POWERUP_SKY: "powerup_sky",
                POWERUP_SHIELD: "powerup_shield",
                POWERUP_SPEED: "powerup_speed"
            }
            sprite = assets["sprites"].get(key_map.get(player.powerup))
            if sprite:
                surface.blit(sprite, (start_x - 1, start_y + 12))

            # Timer bar for temporary speed core
            if player.powerup == POWERUP_SPEED and player.speed_core_timer > 0:
                bar_pct = player.speed_core_timer / 15.0
                pygame.draw.rect(surface, (255, 220, 40), (start_x, start_y + 29, int(14 * bar_pct), 2))

        # 2. TOP-CENTER: Score
        score_str = f"{level.score:06d}"
        score_surf = self.font.render(score_str, False, COLOR_WHITE)
        score_shadow = self.font.render(score_str, False, (15, 15, 25))
        cx = VIRTUAL_WIDTH // 2 - score_surf.get_width() // 2
        surface.blit(score_shadow, (cx + 1, start_y + 1))
        surface.blit(score_surf, (cx, start_y))

        # Level name subtitle
        lvl_name = level.data.get("name", "")
        if lvl_name:
            name_surf = self.font_small.render(f"{level.level_id} {lvl_name}", False, (170, 185, 215))
            surface.blit(name_surf, (VIRTUAL_WIDTH // 2 - name_surf.get_width() // 2, start_y + 14))

        # 3. TOP-RIGHT: Star Shards, Astral Crystals & Timer
        rx = VIRTUAL_WIDTH - 85

        # Shards
        shard_icon = assets["sprites"].get("star_shard_0")
        if shard_icon:
            surface.blit(shard_icon, (rx - 14, start_y - 2))
        shards_str = f"x{level.shards_collected:02d}"
        shards_surf = self.font_small.render(shards_str, False, UI_ACCENT_GOLD)
        surface.blit(shards_surf, (rx + 2, start_y))

        # Crystals (Secret)
        cryst_icon = assets["sprites"].get("astral_crystal")
        if cryst_icon:
            surface.blit(cryst_icon, (rx + 34, start_y - 2))
        cryst_str = f"{len(level.crystals_found)}/3"
        cryst_surf = self.font_small.render(cryst_str, False, UI_ACCENT_CYAN)
        surface.blit(cryst_surf, (rx + 50, start_y))

        # Timer
        mins = int(level.time_elapsed // 60)
        secs = int(level.time_elapsed % 60)
        time_str = f"{mins:02d}:{secs:02d}"
        time_surf = self.font_small.render(time_str, False, (200, 210, 230))
        surface.blit(time_surf, (VIRTUAL_WIDTH - time_surf.get_width() - 10, start_y + 14))
