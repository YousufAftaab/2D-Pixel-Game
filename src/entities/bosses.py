"""
STARBOUND: THE LOST REALMS
Boss Encounters
World 1 Boss (Ancient Sentinel) and Final Boss (The Warden of the Lost Realm).
"""

import math
import random
import pygame
from src.entities.projectile import Projectile


class BossSentinel:
    """
    World 1 Boss: Ancient Sentinel
    Ancient stone titan guarding the Verdant Valley gateway.
    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.max_health = 6
        self.health = 6
        self.state = "IDLE"  # IDLE, CHARGE, REST, JUMP_SLAM
        self.timer = 2.0
        self.facing_right = False
        self.alive = True
        self.flash_timer = 0.0
        self.score_value = 5000

    def update(self, dt, solid_tiles, player, audio_manager, particle_system, camera, projectiles):
        if not self.alive:
            return

        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Apply gravity
        self.vy += 800.0 * dt
        self.y += self.vy * dt
        self.rect.y = int(self.y)

        for t in solid_tiles:
            if not getattr(t, 'is_platform', False) and self.rect.colliderect(t.rect):
                if self.vy > 0:
                    self.rect.bottom = t.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0

        # State behavior
        self.timer -= dt

        if self.state == "IDLE":
            self.vx = 0.0
            dist_x = player.rect.centerx - self.rect.centerx
            self.facing_right = (dist_x > 0)
            if self.timer <= 0:
                # Alternate between Charge and Jump Slam
                if random.random() < 0.6:
                    self.state = "CHARGE"
                    self.timer = 1.8
                else:
                    self.state = "JUMP_SLAM"
                    self.vy = -280.0
                    self.vx = 80.0 if self.facing_right else -80.0
                    self.timer = 2.0

        elif self.state == "CHARGE":
            charge_spd = 110.0
            self.vx = charge_spd if self.facing_right else -charge_spd
            self.x += self.vx * dt
            self.rect.x = int(self.x)

            # Hit wall -> Stunned/Rest state (vulnerable window!)
            for t in solid_tiles:
                if not getattr(t, 'is_platform', False) and self.rect.colliderect(t.rect):
                    self.state = "REST"
                    self.timer = 2.4
                    self.vx = 0.0
                    camera.add_shake(5.0, 0.25)
                    audio_manager.play_sfx("stomp")
                    particle_system.emit_dust(self.rect.centerx, self.rect.bottom, count=10)
                    break

            if self.timer <= 0:
                self.state = "REST"
                self.timer = 2.0

        elif self.state == "JUMP_SLAM":
            self.x += self.vx * dt
            self.rect.x = int(self.x)

            # Ground slam shockwave
            if self.vy == 0.0 and self.timer < 1.6:
                camera.add_shake(7.0, 0.3)
                audio_manager.play_sfx("land")
                particle_system.emit_explosion(self.rect.centerx, self.rect.bottom, count=16, color_scheme="fire")
                # Spawn left and right ground shockwaves
                projectiles.append(Projectile(self.rect.left - 10, self.rect.bottom - 8, -140.0, 0.0, is_player_owned=False))
                projectiles.append(Projectile(self.rect.right + 2, self.rect.bottom - 8, 140.0, 0.0, is_player_owned=False))
                self.state = "REST"
                self.timer = 2.0

        elif self.state == "REST":
            self.vx = 0.0
            if self.timer <= 0:
                self.state = "IDLE"
                self.timer = 1.0

    def take_hit(self, amount, audio_manager, particle_system, camera):
        if self.flash_timer > 0:
            return False

        self.health -= amount
        self.flash_timer = 0.8
        camera.add_shake(6.0, 0.25)
        audio_manager.play_sfx("hurt")
        particle_system.emit_sparkles(self.rect.centerx, self.rect.top, count=18, color=(255, 230, 80))

        if self.health <= 0:
            self.health = 0
            self.alive = False
            camera.add_shake(12.0, 0.6)
            particle_system.emit_explosion(self.rect.centerx, self.rect.centery, count=35, color_scheme="fire")
            particle_system.add_floating_text("+5000", self.rect.centerx, self.rect.top - 12)
        return True

    def draw(self, surface, camera, sprite=None):
        if not self.alive:
            return

        screen_rect = camera.apply(self.rect)

        # Flash white on hit
        if self.flash_timer > 0 and int(self.flash_timer * 20) % 2 == 0:
            pygame.draw.rect(surface, (255, 255, 255), screen_rect)
            return

        if sprite:
            if self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            surface.blit(sprite, screen_rect)
        else:
            pygame.draw.rect(surface, (110, 120, 130), screen_rect)

        # Boss health bar
        bar_w = 40
        bar_h = 4
        bar_x = screen_rect.centerx - bar_w // 2
        bar_y = screen_rect.top - 8
        pygame.draw.rect(surface, (40, 20, 20), (bar_x, bar_y, bar_w, bar_h))
        hp_pct = max(0.0, self.health / self.max_health)
        pygame.draw.rect(surface, (230, 50, 60), (bar_x, bar_y, int(bar_w * hp_pct), bar_h))


class BossWarden:
    """
    Final Boss: The Warden of the Lost Realm
    Multi-phase cosmic encounter featuring teleportation, orbital astral lances, and bullet storms.
    """
    def __init__(self, arena_center_x, arena_center_y):
        self.arena_cx = float(arena_center_x)
        self.arena_cy = float(arena_center_y)
        self.x = self.arena_cx - 24
        self.y = self.arena_cy - 40
        self.width = 44
        self.height = 44
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

        self.max_health = 12
        self.health = 12
        self.phase = 1  # Phase 1, Phase 2, Phase 3
        self.state = "FLOAT"
        self.timer = 2.0
        self.alive = True
        self.flash_timer = 0.0
        self.attack_cooldown = 2.2
        self.orbit_angle = 0.0
        self.score_value = 20000

    def update(self, dt, player, audio_manager, particle_system, camera, projectiles):
        if not self.alive:
            return

        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Determine phase based on remaining health
        if self.health <= 4 and self.phase != 3:
            self.phase = 3
            camera.add_shake(10.0, 0.5)
            particle_system.emit_explosion(self.rect.centerx, self.rect.centery, count=30, color_scheme="plasma")
        elif self.health <= 8 and self.health > 4 and self.phase != 2:
            self.phase = 2
            camera.add_shake(8.0, 0.4)
            particle_system.emit_explosion(self.rect.centerx, self.rect.centery, count=20, color_scheme="plasma")

        self.orbit_angle += dt * (2.0 if self.phase < 3 else 3.5)
        # Sinusoidal floating
        hover_speed = 3.0 if self.phase < 3 else 5.0
        self.y = (self.arena_cy - 40) + math.sin(self.orbit_angle * 0.7) * 20.0
        self.x = (self.arena_cx - 24) + math.cos(self.orbit_angle * 0.5) * (40.0 if self.phase >= 2 else 20.0)

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Attack logic
        self.attack_cooldown -= dt
        rate = 2.0 if self.phase == 1 else (1.5 if self.phase == 2 else 0.9)

        if self.attack_cooldown <= 0:
            self.attack_cooldown = rate
            audio_manager.play_sfx("shoot")

            # Phase 1: Targeted triple spread
            if self.phase == 1:
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                base_angle = math.atan2(dy, dx)
                for spread in [-0.25, 0.0, 0.25]:
                    spd = 140.0
                    ang = base_angle + spread
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, is_player_owned=False))

            # Phase 2: Ring nova burst
            elif self.phase == 2:
                for i in range(8):
                    ang = (i / 8.0) * math.pi * 2.0 + self.orbit_angle
                    spd = 125.0
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, is_player_owned=False))

            # Phase 3: Enraged spiral bullet curtain + camera shake
            elif self.phase == 3:
                for i in range(12):
                    ang = (i / 12.0) * math.pi * 2.0 + self.orbit_angle
                    spd = 150.0
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, is_player_owned=False))
                camera.add_shake(3.0, 0.15)

    def take_hit(self, amount, audio_manager, particle_system, camera):
        if self.flash_timer > 0:
            return False

        self.health -= amount
        self.flash_timer = 0.7
        camera.add_shake(7.0, 0.3)
        audio_manager.play_sfx("hurt")
        particle_system.emit_sparkles(self.rect.centerx, self.rect.centery, count=20, color=(180, 100, 255))

        if self.health <= 0:
            self.health = 0
            self.alive = False
            camera.add_shake(15.0, 0.8)
            particle_system.emit_explosion(self.rect.centerx, self.rect.centery, count=50, color_scheme="plasma")
            particle_system.add_floating_text("+20000", self.rect.centerx, self.rect.top - 16)
        return True

    def draw(self, surface, camera, sprite_p1, sprite_p2):
        if not self.alive:
            return

        screen_rect = camera.apply(self.rect)

        if self.flash_timer > 0 and int(self.flash_timer * 20) % 2 == 0:
            pygame.draw.circle(surface, (255, 255, 255), screen_rect.center, 22)
            return

        s = sprite_p2 if self.phase == 3 else sprite_p1
        if s:
            surface.blit(s, (screen_rect.x - 2, screen_rect.y - 2))
        else:
            c = (140, 40, 190) if self.phase < 3 else (220, 30, 50)
            pygame.draw.rect(surface, c, screen_rect)

        # Health bar on top of screen
        bar_w = 120
        bar_h = 6
        bar_x = (surface.get_width() - bar_w) // 2
        bar_y = 24
        pygame.draw.rect(surface, (30, 20, 40), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        hp_pct = max(0.0, self.health / self.max_health)
        color = (255, 80, 80) if self.phase == 3 else (180, 100, 255)
        pygame.draw.rect(surface, color, (bar_x, bar_y, int(bar_w * hp_pct), bar_h))
