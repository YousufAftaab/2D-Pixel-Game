"""
STARBOUND: THE LOST REALMS
Parallax Background & Atmospheric System
Multi-layer depth rendering with world-themed color gradients and atmospheric particles.
"""

import math
import random
import pygame
from src.engine.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT,
    PALETTE_VERDANT, PALETTE_SUNSCAR, PALETTE_FROSTFALL,
    PALETTE_SKYRUINS, PALETTE_EMBER, PALETTE_LOSTREALM
)


class ParallaxBackground:
    def __init__(self, world_theme="verdant"):
        self.world_theme = world_theme
        self.palette = self._get_palette(world_theme)

        # Pre-render sky gradient surface
        self.sky_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self._render_sky_gradient()

        # Ambient floating particles
        self.ambient_particles = []
        for _ in range(25):
            self.ambient_particles.append({
                'x': random.uniform(0, VIRTUAL_WIDTH),
                'y': random.uniform(0, VIRTUAL_HEIGHT),
                'vx': random.uniform(-15, -5) if world_theme != "ember" else random.uniform(-5, 5),
                'vy': random.uniform(5, 15) if world_theme == "frostfall" else (random.uniform(-15, -5) if world_theme == "ember" else random.uniform(2, 6)),
                'size': random.randint(1, 2),
                'color': self.palette["accent"]
            })

    def _get_palette(self, theme):
        palettes = {
            "verdant": PALETTE_VERDANT,
            "sunscar": PALETTE_SUNSCAR,
            "frostfall": PALETTE_FROSTFALL,
            "skyruins": PALETTE_SKYRUINS,
            "ember": PALETTE_EMBER,
            "lostrealm": PALETTE_LOSTREALM,
        }
        return palettes.get(theme, PALETTE_VERDANT)

    def _render_sky_gradient(self):
        c1 = self.palette["sky_top"]
        c2 = self.palette["sky_bottom"]
        for y in range(VIRTUAL_HEIGHT):
            ratio = y / float(VIRTUAL_HEIGHT)
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            pygame.draw.line(self.sky_surface, (r, g, b), (0, y), (VIRTUAL_WIDTH, y))

    def update(self, dt):
        for p in self.ambient_particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt

            if p['x'] < 0:
                p['x'] = VIRTUAL_WIDTH
            elif p['x'] > VIRTUAL_WIDTH:
                p['x'] = 0

            if p['y'] < 0:
                p['y'] = VIRTUAL_HEIGHT
            elif p['y'] > VIRTUAL_HEIGHT:
                p['y'] = 0

    def draw(self, surface, camera):
        # 1. Sky Gradient (Fixed in view)
        surface.blit(self.sky_surface, (0, 0))

        cam_x = camera.x
        cam_y = camera.y

        # 2. Far Background Layer (Mountain Silhouettes at 0.12x scroll)
        far_offset = int(-cam_x * 0.12) % VIRTUAL_WIDTH
        for rep in [-VIRTUAL_WIDTH, 0, VIRTUAL_WIDTH]:
            x = far_offset + rep
            # Procedural mountain ridges
            pts = [
                (x, VIRTUAL_HEIGHT),
                (x + 40, VIRTUAL_HEIGHT - 90),
                (x + 120, VIRTUAL_HEIGHT - 60),
                (x + 220, VIRTUAL_HEIGHT - 120),
                (x + 320, VIRTUAL_HEIGHT - 70),
                (x + 420, VIRTUAL_HEIGHT - 110),
                (x + VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
            ]
            c = self.palette["stone"]
            dim_c = (max(0, c[0] - 35), max(0, c[1] - 35), max(0, c[2] - 35))
            pygame.draw.polygon(surface, dim_c, pts)

        # 3. Mid Background Layer (Rolling Hills at 0.3x scroll)
        mid_offset = int(-cam_x * 0.3) % VIRTUAL_WIDTH
        for rep in [-VIRTUAL_WIDTH, 0, VIRTUAL_WIDTH]:
            x = mid_offset + rep
            pts = [
                (x, VIRTUAL_HEIGHT),
                (x + 60, VIRTUAL_HEIGHT - 55),
                (x + 160, VIRTUAL_HEIGHT - 35),
                (x + 260, VIRTUAL_HEIGHT - 65),
                (x + 360, VIRTUAL_HEIGHT - 40),
                (x + VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
            ]
            c = self.palette["foliage"]
            pygame.draw.polygon(surface, c, pts)

        # 4. Floating Atmospheric Particles
        for p in self.ambient_particles:
            surface.set_at((int(p['x']), int(p['y'])), p['color'])
