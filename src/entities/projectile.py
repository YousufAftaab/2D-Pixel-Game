"""
STARBOUND: THE LOST REALMS
Projectile System
Nova energy blasts, Turret plasma projectiles, and Boss energy attacks.
"""

import pygame


class Projectile:
    def __init__(self, x, y, vx, vy, is_player_owned=True, damage=1, lifetime=2.5):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.width = 8
        self.height = 8
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        self.is_player_owned = is_player_owned
        self.damage = damage
        self.lifetime = lifetime
        self.alive = True

    def update(self, dt, solid_tiles):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return False

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Check collision with solid tiles
        for tile in solid_tiles:
            if self.rect.colliderect(tile.rect):
                self.alive = False
                return False

        return True

    def draw(self, surface, camera, sprite=None):
        screen_rect = camera.apply(self.rect)
        if sprite:
            surface.blit(sprite, screen_rect)
        else:
            c = (255, 180, 40) if self.is_player_owned else (240, 60, 90)
            pygame.draw.circle(surface, c, screen_rect.center, 4)
