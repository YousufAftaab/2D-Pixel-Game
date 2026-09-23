"""
STARBOUND: THE LOST REALMS
Interactive Blocks, Platforms, Hazards, Checkpoints, and Portals
"""

import math
import pygame
from src.engine.config import TILE_SIZE, POWERUP_EMBER, POWERUP_SKY, POWERUP_SHIELD, POWERUP_SPEED


class SolidTile:
    def __init__(self, x, y, tile_type="mid", tile_size=TILE_SIZE):
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.tile_type = tile_type
        self.is_platform = False


class PlatformTile:
    """One-way platform: solid only when falling onto the top surface."""
    def __init__(self, x, y, tile_size=TILE_SIZE):
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.is_platform = True


class BreakableBlock:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.destroyed = False
        self.is_platform = False

    def break_block(self, particle_system, audio_manager):
        if self.destroyed:
            return
        self.destroyed = True
        particle_system.emit_explosion(self.rect.centerx, self.rect.centery, count=10, color_scheme="fire")
        audio_manager.play_sfx("stomp")

    def draw(self, surface, camera, sprite=None):
        if self.destroyed:
            return
        screen_rect = camera.apply(self.rect)
        if sprite:
            surface.blit(sprite, screen_rect)
        else:
            pygame.draw.rect(surface, (130, 120, 110), screen_rect)


class PrismBlock:
    """
    Original Question/Reward block equivalent.
    Reveals Star Shards, Power-Ups, or Hearts when bumped from below or blasted.
    """
    def __init__(self, x, y, contents="SHARD"):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.contents = contents  # "SHARD", "EMBER", "SKY", "SHIELD", "SPEED", "HEART"
        self.used = False
        self.bump_offset = 0.0
        self.bump_velocity = 0.0
        self.is_platform = False

    def bump(self):
        if self.used or self.bump_offset != 0.0:
            return None
        self.used = True
        self.bump_velocity = -80.0
        return self.contents

    def update(self, dt):
        if self.bump_velocity != 0.0 or self.bump_offset != 0.0:
            self.bump_velocity += 600.0 * dt
            self.bump_offset += self.bump_velocity * dt
            if self.bump_offset >= 0.0:
                self.bump_offset = 0.0
                self.bump_velocity = 0.0

    def draw(self, surface, camera, sprite_active=None):
        screen_rect = camera.apply(self.rect)
        draw_rect = pygame.Rect(screen_rect.x, int(screen_rect.y + self.bump_offset), self.rect.w, self.rect.h)

        if not self.used:
            if sprite_active:
                surface.blit(sprite_active, draw_rect)
            else:
                pygame.draw.rect(surface, (255, 210, 40), draw_rect)
        else:
            # Spent state
            pygame.draw.rect(surface, (90, 85, 95), draw_rect)
            pygame.draw.rect(surface, (45, 40, 50), draw_rect, 1)


class HiddenBlock:
    """Invisible solid block until triggered from below."""
    def __init__(self, x, y, contents="SHARD"):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.contents = contents
        self.revealed = False
        self.is_platform = False

    def reveal(self):
        if not self.revealed:
            self.revealed = True
            return self.contents
        return None

    def draw(self, surface, camera, sprite=None):
        if not self.revealed:
            return
        screen_rect = camera.apply(self.rect)
        if sprite:
            surface.blit(sprite, screen_rect)
        else:
            pygame.draw.rect(surface, (80, 80, 90), screen_rect)


class MovingPlatform:
    def __init__(self, x, y, width=32, height=12, move_x=60.0, move_y=0.0, speed=1.2):
        self.origin_x = float(x)
        self.origin_y = float(y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.move_x = move_x
        self.move_y = move_y
        self.speed = speed
        self.timer = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.is_platform = True

    def update(self, dt):
        self.timer += dt * self.speed
        prev_x = self.rect.x
        prev_y = self.rect.y

        new_x = self.origin_x + math.sin(self.timer) * self.move_x
        new_y = self.origin_y + math.sin(self.timer) * self.move_y

        self.rect.x = int(new_x)
        self.rect.y = int(new_y)
        self.dx = self.rect.x - prev_x
        self.dy = self.rect.y - prev_y

    def draw(self, surface, camera):
        screen_rect = camera.apply(self.rect)
        pygame.draw.rect(surface, (70, 85, 120), screen_rect)
        pygame.draw.rect(surface, (140, 170, 220), (screen_rect.x, screen_rect.y, screen_rect.w, 3))
        pygame.draw.rect(surface, (30, 35, 50), screen_rect, 1)


class Hazard:
    def __init__(self, x, y, hazard_type="spikes", w=TILE_SIZE, h=TILE_SIZE):
        self.rect = pygame.Rect(x, y, w, h)
        self.hazard_type = hazard_type

    def draw(self, surface, camera, sprite=None):
        screen_rect = camera.apply(self.rect)
        if sprite and self.hazard_type == "spikes":
            surface.blit(sprite, screen_rect)
        elif self.hazard_type == "lava":
            pygame.draw.rect(surface, (230, 50, 30), screen_rect)
            pygame.draw.rect(surface, (255, 180, 40), (screen_rect.x, screen_rect.y, screen_rect.w, 4))
        else:
            pygame.draw.rect(surface, (220, 50, 50), screen_rect)


class Checkpoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y - 8, 16, 24)
        self.activated = False

    def activate(self, audio_manager, particle_system):
        if not self.activated:
            self.activated = True
            audio_manager.play_sfx("checkpoint")
            particle_system.emit_sparkles(self.rect.centerx, self.rect.top, count=16, color=(255, 230, 80))

    def draw(self, surface, camera, sprite_on, sprite_off):
        screen_rect = camera.apply(self.rect)
        sprite = sprite_on if self.activated else sprite_off
        if sprite:
            surface.blit(sprite, screen_rect)
        else:
            c = (255, 220, 40) if self.activated else (80, 85, 95)
            pygame.draw.rect(surface, c, screen_rect)


class ExitPortal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y - 16, 16, 32)
        self.anim_timer = 0.0

    def update(self, dt, particle_system):
        self.anim_timer += dt
        if int(self.anim_timer * 10) % 3 == 0:
            particle_system.emit_sparkles(self.rect.centerx, self.rect.centery, count=1, color=(160, 100, 255))

    def draw(self, surface, camera, sprite=None):
        screen_rect = camera.apply(self.rect)
        if sprite:
            surface.blit(sprite, screen_rect)
        else:
            pygame.draw.ellipse(surface, (140, 80, 240), screen_rect)


class TraversalPortal:
    """Pipe/portal equivalent: teleports player to target coordinates when E is pressed."""
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y - 12, 16, 28)
        self.target_x = target_x
        self.target_y = target_y

    def draw(self, surface, camera):
        screen_rect = camera.apply(self.rect)
        pygame.draw.rect(surface, (40, 180, 210), screen_rect)
        pygame.draw.rect(surface, (180, 255, 255), (screen_rect.x + 3, screen_rect.y + 3, 10, screen_rect.h - 6))
