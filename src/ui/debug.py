"""
STARBOUND: THE LOST REALMS
Developer Debug Tools & HUD Overlay
Toggled via F1-F6 keys for testing, inspection, and verification.
"""

import pygame
from src.engine.config import (
    POWERUP_NONE, POWERUP_EMBER, POWERUP_SKY, POWERUP_SHIELD, POWERUP_SPEED
)


class DebugManager:
    def __init__(self, font_small):
        self.font = font_small
        self.enabled = False
        self.god_mode = False

        self.powerup_cycle = [
            POWERUP_NONE,
            POWERUP_EMBER,
            POWERUP_SKY,
            POWERUP_SHIELD,
            POWERUP_SPEED
        ]
        self.cycle_idx = 0

    def process_debug_inputs(self, input_mgr, level, audio_manager, particle_system):
        # F1: Toggle Debug Overlay
        if input_mgr.debug_f1:
            self.enabled = not self.enabled
            audio_manager.play_sfx("menu_select")

        # F2: Restart Level
        if input_mgr.debug_f2 and level:
            level.player.respawn()
            audio_manager.play_sfx("menu_select")

        # F3: God Mode
        if input_mgr.debug_f3 and level:
            self.god_mode = not self.god_mode
            if self.god_mode:
                level.player.health = 99
                level.player.max_health = 99
            else:
                level.player.health = 3
                level.player.max_health = 3
            audio_manager.play_sfx("powerup")

        # F4: Cycle Power-up
        if input_mgr.debug_f4 and level:
            self.cycle_idx = (self.cycle_idx + 1) % len(self.powerup_cycle)
            new_pwr = self.powerup_cycle[self.cycle_idx]
            level.player.apply_powerup(new_pwr, audio_manager, particle_system)

        # F5: Instant Skip / Complete Level
        if input_mgr.debug_f5 and level:
            level._finish_level()

        # F6: Reload Level
        if input_mgr.debug_f6 and level:
            level._load_map()
            audio_manager.play_sfx("menu_select")

    def draw(self, surface, clock, player, level, camera):
        if not self.enabled or not player or not level:
            return

        fps = int(clock.get_fps())
        lines = [
            f"DEBUG MODE [F1] | FPS: {fps}",
            f"God Mode [F3]: {'ON' if self.god_mode else 'OFF'}",
            f"Player State: {player.state} | Grounded: {player.is_grounded}",
            f"Pos: ({player.x:.1f}, {player.y:.1f}) | Vel: ({player.vx:.1f}, {player.vy:.1f})",
            f"Coyote: {player.coyote_timer:.2f}s | JumpBuf: {player.jump_buffer_timer:.2f}s",
            f"Power-up [F4]: {player.powerup}",
            f"Enemies Alive: {len([e for e in level.enemies if e.alive])}",
            f"Active Projectiles: {len(level.projectiles)}",
            f"Camera: ({camera.x:.1f}, {camera.y:.1f})",
            "F2:Respawn F3:God F4:Powerup F5:SkipLevel F6:Reload",
        ]

        # Draw semi-transparent background box
        box_h = len(lines) * 12 + 8
        overlay = pygame.Surface((280, box_h), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 210))
        surface.blit(overlay, (6, 32))

        y = 36
        for line in lines:
            txt_surf = self.font.render(line, False, (140, 240, 180))
            surface.blit(txt_surf, (10, y))
            y += 12

        # Draw entity debug bounding boxes
        player_screen = camera.apply(player.rect)
        pygame.draw.rect(surface, (0, 255, 100), player_screen, 1)

        for enemy in level.enemies:
            if enemy.alive:
                es = camera.apply(enemy.rect)
                pygame.draw.rect(surface, (255, 50, 50), es, 1)

        if level.boss and level.boss.alive:
            bs = camera.apply(level.boss.rect)
            pygame.draw.rect(surface, (255, 200, 0), bs, 1)
