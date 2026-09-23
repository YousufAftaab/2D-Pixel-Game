"""
STARBOUND: THE LOST REALMS
Collectibles & Power-Up Items
Star Shards, Secret Astral Crystals, Energy Restores, and Core Upgrades.
"""

import math
import pygame
from src.engine.config import (
    POWERUP_EMBER, POWERUP_SKY, POWERUP_SHIELD, POWERUP_SPEED
)


class StarShard:
    def __init__(self, x, y):
        self.base_x = float(x)
        self.base_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.width = 12
        self.height = 12
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        self.bob_timer = float(x % 10)  # offset phase
        self.anim_frame = 0
        self.frame_timer = 0.0
        self.collected = False

    def update(self, dt):
        self.bob_timer += dt * 3.5
        self.y = self.base_y + math.sin(self.bob_timer) * 3.0
        self.rect.y = int(self.y)

        self.frame_timer += dt
        if self.frame_timer >= 0.12:
            self.frame_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 4

    def draw(self, surface, camera, frames):
        screen_pos = camera.apply((int(self.x - 2), int(self.y - 2)))
        if frames and len(frames) > self.anim_frame and frames[self.anim_frame] is not None:
            surface.blit(frames[self.anim_frame], screen_pos)
        else:
            pygame.draw.circle(surface, (255, 215, 0), (screen_pos[0] + 6, screen_pos[1] + 6), 5)


class AstralCrystal:
    def __init__(self, crystal_id, x, y):
        self.crystal_id = crystal_id
        self.base_x = float(x)
        self.base_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.width = 14
        self.height = 14
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        self.timer = 0.0
        self.collected = False

    def update(self, dt):
        self.timer += dt * 2.5
        self.y = self.base_y + math.sin(self.timer) * 4.0
        self.rect.y = int(self.y)

    def draw(self, surface, camera, sprite=None):
        screen_pos = camera.apply((int(self.x - 1), int(self.y - 1)))
        if sprite:
            surface.blit(sprite, screen_pos)
        else:
            pygame.draw.rect(surface, (60, 230, 255), (*screen_pos, 14, 14))


class HeartOrb:
    def __init__(self, x, y):
        self.base_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(self.x), int(self.y), 12, 12)
        self.timer = 0.0
        self.collected = False

    def update(self, dt):
        self.timer += dt * 3.0
        self.y = self.base_y + math.sin(self.timer) * 2.5
        self.rect.y = int(self.y)

    def draw(self, surface, camera, sprite=None):
        screen_pos = camera.apply((int(self.x - 2), int(self.y - 2)))
        if sprite:
            surface.blit(sprite, screen_pos)
        else:
            pygame.draw.circle(surface, (240, 60, 70), (screen_pos[0] + 6, screen_pos[1] + 6), 5)


class PowerUpItem:
    def __init__(self, powerup_type, x, y):
        self.powerup_type = powerup_type
        self.x = float(x)
        self.y = float(y)
        self.vy = -120.0  # initial upward pop
        self.rect = pygame.Rect(int(self.x), int(self.y), 14, 14)
        self.collected = False
        self.on_ground = False

    def update(self, dt, solid_tiles):
        if not self.on_ground:
            self.vy += 600.0 * dt
            self.y += self.vy * dt
            self.rect.y = int(self.y)

            # Ground collision
            for tile in solid_tiles:
                if self.rect.colliderect(tile.rect):
                    if self.vy > 0:
                        self.rect.bottom = tile.rect.top
                        self.y = float(self.rect.y)
                        self.vy = 0.0
                        self.on_ground = True
                        break

    def draw(self, surface, camera, sprites):
        screen_pos = camera.apply((int(self.x - 1), int(self.y - 1)))
        key_map = {
            POWERUP_EMBER: "powerup_ember",
            POWERUP_SKY: "powerup_sky",
            POWERUP_SHIELD: "powerup_shield",
            POWERUP_SPEED: "powerup_speed"
        }
        sprite_key = key_map.get(self.powerup_type)
        sprite = sprites.get(sprite_key) if sprites else None

        if sprite:
            surface.blit(sprite, screen_pos)
        else:
            pygame.draw.circle(surface, (255, 200, 50), (screen_pos[0] + 7, screen_pos[1] + 7), 6)
