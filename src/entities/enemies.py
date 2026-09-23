"""
STARBOUND: THE LOST REALMS
Enemy System: 6 Original Archetypes
Walker (Prowler), Flyer (Vesper), Charger (Crag), Turret (Pulse Sentry), Jumper (Hopper), Shielded (Vanguard).
"""

import math
import pygame
from src.entities.projectile import Projectile


class BaseEnemy:
    def __init__(self, x, y, width=14, height=14, health=1, score_value=100):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = width
        self.height = height
        self.rect = pygame.Rect(int(x), int(y), width, height)
        self.health = health
        self.score_value = score_value
        self.facing_right = False
        self.alive = True
        self.state = "PATROL"  # IDLE, PATROL, CHASE, ATTACK, DEAD
        self.anim_timer = 0.0
        self.anim_frame = 0

    def take_damage(self, amount, audio_manager, particle_system):
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            audio_manager.play_sfx("hurt")
            particle_system.emit_explosion(self.rect.centerx, self.rect.centery, count=12, color_scheme="plasma")
            particle_system.add_floating_text(f"+{self.score_value}", self.rect.centerx, self.rect.top - 6)
            return True
        return False

    def can_be_stomped(self, player_rect, player_vy):
        return player_vy > 0 and player_rect.bottom <= (self.rect.top + 8)


class WalkerEnemy(BaseEnemy):
    """
    Walker (Prowler): Patrols platforms, turns at walls and floor edges.
    """
    def __init__(self, x, y, speed=40.0):
        super().__init__(x, y, width=14, height=14, health=1, score_value=100)
        self.speed = speed
        self.vx = -self.speed

    def update(self, dt, solid_tiles, player, assist_slower=False):
        spd = self.speed * (0.7 if assist_slower else 1.0)
        self.vx = spd if self.facing_right else -spd

        # Apply gravity
        self.vy += 800.0 * dt
        self.y += self.vy * dt
        self.rect.y = int(self.y)

        # Vertical collisions
        for tile in solid_tiles:
            if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0

        # Horizontal movement & Edge detection
        self.x += self.vx * dt
        self.rect.x = int(self.x)

        # Check wall collision
        hit_wall = False
        for tile in solid_tiles:
            if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                hit_wall = True
                break

        # Check edge ahead
        check_x = self.rect.right + 2 if self.facing_right else self.rect.left - 2
        foot_check_rect = pygame.Rect(check_x, self.rect.bottom + 2, 2, 4)
        has_ground_ahead = any(foot_check_rect.colliderect(t.rect) for t in solid_tiles)

        if hit_wall or not has_ground_ahead:
            self.facing_right = not self.facing_right

        # Animation
        self.anim_timer += dt
        if self.anim_timer >= 0.2:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 2

    def draw(self, surface, camera, sprites):
        screen_rect = camera.apply(self.rect)
        sprite_name = f"enemy_walker_{self.anim_frame}"
        s = sprites.get(sprite_name)
        if s:
            if self.facing_right:
                s = pygame.transform.flip(s, True, False)
            surface.blit(s, (screen_rect.x - 1, screen_rect.y - 2))
        else:
            pygame.draw.rect(surface, (200, 50, 60), screen_rect)


class FlyerEnemy(BaseEnemy):
    """
    Flyer (Vesper): Flies with sinusoidal hover, dives towards player when near.
    """
    def __init__(self, x, y, patrol_range=60.0, speed=45.0):
        super().__init__(x, y, width=14, height=12, health=1, score_value=150)
        self.origin_x = float(x)
        self.origin_y = float(y)
        self.patrol_range = patrol_range
        self.speed = speed
        self.hover_timer = 0.0
        self.dive_cooldown = 0.0

    def update(self, dt, solid_tiles, player, assist_slower=False):
        spd = self.speed * (0.7 if assist_slower else 1.0)
        self.hover_timer += dt * 3.0
        self.anim_timer += dt

        # Check distance to player for diving
        dist_x = player.rect.centerx - self.rect.centerx
        dist_y = player.rect.centery - self.rect.centery
        dist = math.hypot(dist_x, dist_y)

        if self.state == "PATROL":
            self.x += (spd if self.facing_right else -spd) * dt
            self.y = self.origin_y + math.sin(self.hover_timer) * 8.0

            if abs(self.x - self.origin_x) >= self.patrol_range:
                self.facing_right = not self.facing_right

            if dist < 110.0 and dist_y > 10.0 and self.dive_cooldown <= 0:
                self.state = "DIVE"
                self.vx = (dist_x / dist) * spd * 1.8
                self.vy = (dist_y / dist) * spd * 1.8

        elif self.state == "DIVE":
            self.x += self.vx * dt
            self.y += self.vy * dt

            # If passed player or hit wall, return to patrol
            if self.y > self.origin_y + 60.0 or any(self.rect.colliderect(t.rect) for t in solid_tiles):
                self.state = "RETREAT"
                self.dive_cooldown = 2.5

        elif self.state == "RETREAT":
            # Float back to origin
            dx = self.origin_x - self.x
            dy = self.origin_y - self.y
            dist_origin = math.hypot(dx, dy)
            if dist_origin > 4.0:
                self.x += (dx / dist_origin) * spd * dt
                self.y += (dy / dist_origin) * spd * dt
            else:
                self.state = "PATROL"

        if self.dive_cooldown > 0:
            self.dive_cooldown -= dt

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.anim_timer >= 0.15:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 2

    def draw(self, surface, camera, sprites):
        screen_rect = camera.apply(self.rect)
        sprite_name = f"enemy_flyer_{self.anim_frame}"
        s = sprites.get(sprite_name)
        if s:
            surface.blit(s, (screen_rect.x - 1, screen_rect.y - 2))
        else:
            pygame.draw.rect(surface, (140, 60, 200), screen_rect)


class ChargerEnemy(BaseEnemy):
    """
    Charger (Crag): Heavy ramming enemy that sprints rapidly when player is in line of sight.
    """
    def __init__(self, x, y, speed=30.0, charge_speed=130.0):
        super().__init__(x, y, width=16, height=14, health=2, score_value=200)
        self.speed = speed
        self.charge_speed = charge_speed
        self.state = "PATROL"
        self.charge_timer = 0.0

    def update(self, dt, solid_tiles, player, assist_slower=False):
        spd = self.charge_speed if self.state == "CHASE" else self.speed
        if assist_slower:
            spd *= 0.75

        # Gravity
        self.vy += 800.0 * dt
        self.y += self.vy * dt
        self.rect.y = int(self.y)

        for tile in solid_tiles:
            if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0

        # Player detection
        dist_x = player.rect.centerx - self.rect.centerx
        dist_y = abs(player.rect.centery - self.rect.centery)

        if self.state == "PATROL":
            if dist_y < 24.0 and abs(dist_x) < 140.0:
                # Player in sight
                is_player_ahead = (dist_x > 0 and self.facing_right) or (dist_x < 0 and not self.facing_right)
                if is_player_ahead:
                    self.state = "CHASE"
                    self.charge_timer = 2.0

            # Normal patrol
            self.x += (spd if self.facing_right else -spd) * dt
            self.rect.x = int(self.x)

            # Check walls
            for tile in solid_tiles:
                if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                    self.facing_right = not self.facing_right
                    break

        elif self.state == "CHASE":
            self.charge_timer -= dt
            self.x += (spd if self.facing_right else -spd) * dt
            self.rect.x = int(self.x)

            # Wall impact ends charge
            for tile in solid_tiles:
                if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                    self.state = "PATROL"
                    self.facing_right = not self.facing_right
                    break

            if self.charge_timer <= 0:
                self.state = "PATROL"

        self.anim_timer += dt
        if self.anim_timer >= (0.1 if self.state == "CHASE" else 0.2):
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 2

    def draw(self, surface, camera, sprites):
        screen_rect = camera.apply(self.rect)
        sprite_name = f"enemy_charger_{self.anim_frame}"
        s = sprites.get(sprite_name)
        if s:
            if self.facing_right:
                s = pygame.transform.flip(s, True, False)
            surface.blit(s, (screen_rect.x, screen_rect.y - 2))
        else:
            pygame.draw.rect(surface, (210, 110, 40), screen_rect)


class TurretEnemy(BaseEnemy):
    """
    Turret (Pulse Sentry): Stationary crystal turret firing timed plasma bolts.
    """
    def __init__(self, x, y, fire_rate=2.0):
        super().__init__(x, y, width=14, height=14, health=2, score_value=250)
        self.fire_rate = fire_rate
        self.fire_timer = fire_rate

    def update(self, dt, solid_tiles, player, assist_slower=False, projectiles=None):
        self.fire_timer -= dt * (0.7 if assist_slower else 1.0)
        dist_x = player.rect.centerx - self.rect.centerx
        dist_y = player.rect.centery - self.rect.centery
        dist = math.hypot(dist_x, dist_y)

        if dist < 220.0 and self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            if projectiles is not None:
                vx = (dist_x / dist) * 120.0
                vy = (dist_y / dist) * 120.0
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery, vx, vy, is_player_owned=False, damage=1))

    def draw(self, surface, camera, sprites):
        screen_rect = camera.apply(self.rect)
        s = sprites.get("enemy_turret_0")
        if s:
            surface.blit(s, (screen_rect.x - 1, screen_rect.y - 2))
        else:
            pygame.draw.rect(surface, (0, 200, 240), screen_rect)


class JumperEnemy(BaseEnemy):
    """
    Jumper (Hopper): Periodically crouches and leaps in an arc toward the player.
    """
    def __init__(self, x, y, jump_delay=2.2):
        super().__init__(x, y, width=14, height=14, health=1, score_value=175)
        self.jump_delay = jump_delay
        self.jump_timer = jump_delay
        self.is_grounded = True

    def update(self, dt, solid_tiles, player, assist_slower=False):
        self.jump_timer -= dt * (0.8 if assist_slower else 1.0)

        # Apply gravity
        self.vy += 750.0 * dt
        self.y += self.vy * dt
        self.rect.y = int(self.y)

        self.is_grounded = False
        for tile in solid_tiles:
            if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0
                    self.vx = 0.0
                    self.is_grounded = True

        self.x += self.vx * dt
        self.rect.x = int(self.x)

        if self.is_grounded and self.jump_timer <= 0:
            self.jump_timer = self.jump_delay
            self.vy = -260.0
            dist_x = player.rect.centerx - self.rect.centerx
            self.facing_right = (dist_x > 0)
            self.vx = 75.0 if self.facing_right else -75.0
            self.is_grounded = False

    def draw(self, surface, camera, sprites):
        screen_rect = camera.apply(self.rect)
        s = sprites.get("enemy_jumper_0")
        if s:
            if self.facing_right:
                s = pygame.transform.flip(s, True, False)
            surface.blit(s, (screen_rect.x - 1, screen_rect.y - 2))
        else:
            pygame.draw.rect(surface, (60, 200, 80), screen_rect)


class ShieldedEnemy(BaseEnemy):
    """
    Shielded (Vanguard): Holds an energy shield in front; ricochets frontal attacks.
    Can only be defeated from behind or by stomping from above.
    """
    def __init__(self, x, y, speed=35.0):
        super().__init__(x, y, width=16, height=14, health=2, score_value=250)
        self.speed = speed
        self.vx = -self.speed

    def update(self, dt, solid_tiles, player, assist_slower=False):
        spd = self.speed * (0.7 if assist_slower else 1.0)
        self.vx = spd if self.facing_right else -spd

        self.vy += 800.0 * dt
        self.y += self.vy * dt
        self.rect.y = int(self.y)

        for tile in solid_tiles:
            if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0

        self.x += self.vx * dt
        self.rect.x = int(self.x)

        hit_wall = False
        for tile in solid_tiles:
            if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                hit_wall = True
                break

        if hit_wall:
            self.facing_right = not self.facing_right

    def check_frontal_block(self, attack_x):
        """Returns True if the attack came from the front (blocked by shield)."""
        if self.facing_right:
            return attack_x >= self.rect.centerx
        else:
            return attack_x <= self.rect.centerx

    def draw(self, surface, camera, sprites):
        screen_rect = camera.apply(self.rect)
        s = sprites.get("enemy_shielded_0")
        if s:
            if not self.facing_right:
                s = pygame.transform.flip(s, True, False)
            surface.blit(s, (screen_rect.x, screen_rect.y - 2))
        else:
            pygame.draw.rect(surface, (90, 110, 140), screen_rect)
