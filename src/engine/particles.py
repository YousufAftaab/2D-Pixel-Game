"""
STARBOUND: THE LOST REALMS
Particle & Juice System
Handles physics particles, sparkling stars, dust puffs, and floating score popups.
"""

import random
import pygame


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'size', 'life', 'max_life', 'gravity', 'shrink')

    def __init__(self, x, y, vx, vy, color, size, life, gravity=180.0, shrink=True):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.size = float(size)
        self.life = float(life)
        self.max_life = float(life)
        self.gravity = float(gravity)
        self.shrink = shrink

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            return False
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return True

    def draw(self, surface, camera):
        sx, sy = camera.apply((self.x, self.y))
        if self.shrink:
            current_size = max(1, int(self.size * (self.life / self.max_life)))
        else:
            current_size = int(self.size)

        if current_size <= 1:
            surface.set_at((int(sx), int(sy)), self.color)
        else:
            pygame.draw.rect(surface, self.color, (int(sx - current_size / 2), int(sy - current_size / 2), current_size, current_size))


class FloatingText:
    __slots__ = ('text', 'x', 'y', 'vy', 'color', 'life', 'max_life')

    def __init__(self, text, x, y, color=(255, 220, 60), life=0.8):
        self.text = str(text)
        self.x = float(x)
        self.y = float(y)
        self.vy = -35.0  # float upward
        self.color = color
        self.life = float(life)
        self.max_life = float(life)

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            return False
        self.y += self.vy * dt
        return True

    def draw(self, surface, camera, font):
        sx, sy = camera.apply((self.x, self.y))
        rendered = font.render(self.text, False, self.color)
        # Shadow for contrast
        shadow = font.render(self.text, False, (20, 20, 30))
        surface.blit(shadow, (int(sx - rendered.get_width() / 2 + 1), int(sy + 1)))
        surface.blit(rendered, (int(sx - rendered.get_width() / 2), int(sy)))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        self._font = None

    def set_font(self, font):
        self._font = font

    def emit_dust(self, x, y, count=4):
        for _ in range(count):
            vx = random.uniform(-25, 25)
            vy = random.uniform(-15, -5)
            c = random.choice([(200, 200, 215), (160, 165, 180), (225, 225, 235)])
            self.particles.append(Particle(x, y, vx, vy, c, size=random.randint(2, 3), life=random.uniform(0.2, 0.4), gravity=40))

    def emit_sparkles(self, x, y, count=8, color=(255, 230, 80)):
        for _ in range(count):
            vx = random.uniform(-60, 60)
            vy = random.uniform(-70, 30)
            self.particles.append(Particle(x, y, vx, vy, color, size=random.randint(2, 4), life=random.uniform(0.3, 0.6), gravity=100))

    def emit_stomp(self, x, y):
        # Burst of sparks + debris
        for _ in range(12):
            vx = random.uniform(-90, 90)
            vy = random.uniform(-120, -20)
            c = random.choice([(255, 220, 70), (255, 80, 90), (255, 255, 255)])
            self.particles.append(Particle(x, y, vx, vy, c, size=random.randint(2, 4), life=random.uniform(0.3, 0.5), gravity=250))

    def emit_explosion(self, x, y, count=20, color_scheme="fire"):
        colors = [(255, 210, 40), (255, 90, 30), (240, 40, 50), (255, 255, 255)]
        if color_scheme == "plasma":
            colors = [(60, 220, 255), (140, 90, 255), (255, 255, 255)]
        for _ in range(count):
            vx = random.uniform(-120, 120)
            vy = random.uniform(-120, 120)
            c = random.choice(colors)
            self.particles.append(Particle(x, y, vx, vy, c, size=random.randint(3, 5), life=random.uniform(0.35, 0.7), gravity=150))

    def add_floating_text(self, text, x, y, color=(255, 220, 60)):
        self.floating_texts.append(FloatingText(text, x, y, color))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)
        if self._font:
            for ft in self.floating_texts:
                ft.draw(surface, camera, self._font)

    def clear(self):
        self.particles.clear()
        self.floating_texts.clear()
