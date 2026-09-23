"""
STARBOUND: THE LOST REALMS
Player Character: Nova
Full state machine, responsive movement physics, coyote time, jump buffer, combat, and power-up handling.
"""

import math
import pygame
from src.engine.config import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_ACCELERATION, PLAYER_DECELERATION,
    PLAYER_AIR_DECEL, PLAYER_MAX_RUN_SPEED, PLAYER_SPRINT_SPEED, PLAYER_CROUCH_SPEED,
    GRAVITY, FALL_GRAVITY, TERMINAL_VELOCITY, JUMP_VELOCITY, VARIABLE_JUMP_CUTOFF,
    COYOTE_TIME, JUMP_BUFFER_TIME, PLAYER_DEFAULT_MAX_HEALTH, INVULNERABILITY_TIME,
    DAMAGE_KNOCKBACK_X, DAMAGE_KNOCKBACK_Y, STOMP_BOUNCE_VELOCITY,
    COMBO_TIMEOUT, COMBO_POINTS, POWERUP_NONE, POWERUP_EMBER, POWERUP_SKY,
    POWERUP_SHIELD, POWERUP_SPEED, SPEED_CORE_DURATION, SPEED_CORE_SPEED_MULT
)
from src.entities.projectile import Projectile


class Player:
    def __init__(self, x, y, assist_mode=False, assist_extra_health=False, assist_extra_coyote=False):
        # Position and Float Physics
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing_right = True

        # Collision Bounding Box (FRect simulation)
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.crouch_height = 13
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

        # State Machine
        self.state = "IDLE"  # IDLE, RUN, JUMP, FALL, CROUCH, HURT, DEAD, VICTORY
        self.is_grounded = False
        self.was_grounded = False
        self.is_crouched = False
        self.is_sprinting = False

        # Timers & Juice Buffers
        self.coyote_timer = 0.0
        self.coyote_duration = COYOTE_TIME * (1.8 if assist_extra_coyote else 1.0)
        self.jump_buffer_timer = 0.0
        self.invulnerable_timer = 0.0
        self.shoot_cooldown = 0.0
        self.speed_core_timer = 0.0

        # Double jump state (Sky Core)
        self.can_double_jump = False

        # Health & Combat
        max_hp = PLAYER_DEFAULT_MAX_HEALTH + (2 if (assist_mode and assist_extra_health) else 0)
        self.max_health = max_hp
        self.health = max_hp
        self.shield_active = False

        # Power-Up Status
        self.powerup = POWERUP_NONE

        # Combo system
        self.combo_count = 0
        self.combo_timer = 0.0

        # Animation tracking
        self.anim_timer = 0.0
        self.run_frame = 0

        # Respawn point
        self.spawn_x = float(x)
        self.spawn_y = float(y)

    def set_spawn(self, x, y):
        self.spawn_x = float(x)
        self.spawn_y = float(y)

    def respawn(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.vx = 0.0
        self.vy = 0.0
        self.health = self.max_health
        self.shield_active = False
        self.powerup = POWERUP_NONE
        self.state = "IDLE"
        self.rect.topleft = (int(self.x), int(self.y))
        self.invulnerable_timer = 1.0

    def apply_powerup(self, powerup_type, audio_manager, particle_system):
        self.powerup = powerup_type
        audio_manager.play_sfx("powerup")
        particle_system.emit_sparkles(self.rect.centerx, self.rect.centery, count=24, color=(255, 230, 80))

        if powerup_type == POWERUP_SHIELD:
            self.shield_active = True
        elif powerup_type == POWERUP_SPEED:
            self.speed_core_timer = SPEED_CORE_DURATION
        elif powerup_type == POWERUP_SKY:
            self.can_double_jump = True

    def take_damage(self, amount, source_x, audio_manager, particle_system, camera):
        if self.invulnerable_timer > 0 or self.state in ("DEAD", "VICTORY"):
            return False

        # Shield Core absorbs 1 damage hit completely!
        if self.shield_active:
            self.shield_active = False
            self.powerup = POWERUP_NONE
            self.invulnerable_timer = INVULNERABILITY_TIME * 0.75
            audio_manager.play_sfx("hurt")
            particle_system.emit_explosion(self.rect.centerx, self.rect.centery, count=12, color_scheme="plasma")
            camera.add_shake(4.0, 0.2)
            return True

        self.health -= amount
        audio_manager.play_sfx("hurt")
        particle_system.emit_explosion(self.rect.centerx, self.rect.centery, count=14, color_scheme="fire")
        camera.add_shake(6.0, 0.25)

        if self.health <= 0:
            self.health = 0
            self.state = "DEAD"
            self.vx = 0.0
            self.vy = -260.0
            audio_manager.play_sfx("death")
        else:
            self.state = "HURT"
            self.invulnerable_timer = INVULNERABILITY_TIME
            # Knockback away from damage source
            direction = 1.0 if self.rect.centerx >= source_x else -1.0
            self.vx = direction * DAMAGE_KNOCKBACK_X
            self.vy = DAMAGE_KNOCKBACK_Y

            # Lose offensive power-up upon taking hit
            if self.powerup != POWERUP_NONE:
                self.powerup = POWERUP_NONE

        return True

    def register_stomp(self, enemy_center_x, audio_manager, particle_system):
        """Bounces Nova upon enemy stomp and calculates combo."""
        self.vy = STOMP_BOUNCE_VELOCITY
        self.can_double_jump = (self.powerup == POWERUP_SKY)
        self.combo_count += 1
        self.combo_timer = COMBO_TIMEOUT

        idx = min(self.combo_count - 1, len(COMBO_POINTS) - 1)
        points = COMBO_POINTS[idx]

        audio_manager.play_sfx("stomp")
        particle_system.emit_stomp(self.rect.centerx, self.rect.bottom)
        particle_system.add_floating_text(f"+{points}", self.rect.centerx, self.rect.top - 8)
        return points

    def update(self, dt, input_mgr, audio_manager, particle_system, camera, solid_tiles, moving_platforms, interactive_blocks, projectiles):
        # 1. Timers
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.speed_core_timer > 0:
            self.speed_core_timer -= dt
            if self.speed_core_timer <= 0 and self.powerup == POWERUP_SPEED:
                self.powerup = POWERUP_NONE

        # Combo expiration
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0

        # Dead state processing
        if self.state == "DEAD":
            self.vy += GRAVITY * dt
            self.y += self.vy * dt
            self.rect.y = int(self.y)
            return

        if self.state == "VICTORY":
            self.vx = 0.0
            self.vy += GRAVITY * dt
            # Simple ground landing
            for t in solid_tiles:
                if self.rect.colliderect(t.rect) and self.vy > 0:
                    self.rect.bottom = t.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0
            return

        # 2. Input Handling
        axis_x = input_mgr.axis_x
        axis_y = input_mgr.axis_y
        is_jump_pressed = input_mgr.is_action_pressed("jump")
        is_jump_down = input_mgr.is_action_down("jump")
        is_jump_released = input_mgr.is_action_released("jump")
        is_ability_pressed = input_mgr.is_action_pressed("ability")

        # Crouch logic
        self.is_crouched = (axis_y > 0.5 and self.is_grounded)
        current_target_height = self.crouch_height if self.is_crouched else PLAYER_HEIGHT
        if self.rect.h != current_target_height:
            diff = self.rect.h - current_target_height
            self.rect.h = current_target_height
            self.rect.y += diff
            self.y = float(self.rect.y)

        # Sprint logic
        self.is_sprinting = input_mgr.is_action_down("ability") and self.powerup != POWERUP_EMBER

        # 3. Horizontal Movement Physics
        if self.is_crouched:
            target_max_speed = PLAYER_CROUCH_SPEED
        elif self.powerup == POWERUP_SPEED:
            target_max_speed = PLAYER_SPRINT_SPEED * SPEED_CORE_SPEED_MULT
        elif self.is_sprinting:
            target_max_speed = PLAYER_SPRINT_SPEED
        else:
            target_max_speed = PLAYER_MAX_RUN_SPEED

        target_vx = axis_x * target_max_speed

        if axis_x != 0:
            self.facing_right = (axis_x > 0)
            accel = PLAYER_ACCELERATION if self.is_grounded else (PLAYER_ACCELERATION * 0.75)
            if (self.vx * axis_x) < 0:
                # Turning around quickly
                accel *= 1.8
            self.vx += axis_x * accel * dt
            if abs(self.vx) > target_max_speed:
                self.vx = math.copysign(target_max_speed, self.vx)
        else:
            decel = PLAYER_DECELERATION if self.is_grounded else PLAYER_AIR_DECEL
            if abs(self.vx) <= decel * dt:
                self.vx = 0.0
            else:
                self.vx -= math.copysign(decel * dt, self.vx)

        # 4. Jump & Gravity Logic
        # Jump buffer
        if is_jump_pressed:
            self.jump_buffer_timer = JUMP_BUFFER_TIME
        else:
            if self.jump_buffer_timer > 0:
                self.jump_buffer_timer -= dt

        # Coyote time tracking
        if self.is_grounded:
            self.coyote_timer = self.coyote_duration
            if self.powerup == POWERUP_SKY:
                self.can_double_jump = True
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= dt

        # Jump execution (Normal jump via Coyote Time & Buffer)
        jump_executed = False
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0:
            jump_speed = JUMP_VELOCITY * (1.15 if self.powerup == POWERUP_SKY else 1.0)
            self.vy = jump_speed
            self.jump_buffer_timer = 0.0
            self.coyote_timer = 0.0
            self.is_grounded = False
            jump_executed = True
            audio_manager.play_sfx("jump")
            particle_system.emit_dust(self.rect.centerx, self.rect.bottom, count=5)

        # Double Jump (Sky Core)
        elif is_jump_pressed and not self.is_grounded and self.can_double_jump and self.powerup == POWERUP_SKY:
            self.vy = JUMP_VELOCITY * 1.05
            self.can_double_jump = False
            jump_executed = True
            audio_manager.play_sfx("double_jump")
            particle_system.emit_sparkles(self.rect.centerx, self.rect.bottom, count=12, color=(100, 220, 255))

        # Variable jump height: release jump button early to truncate jump
        if is_jump_released and self.vy < VARIABLE_JUMP_CUTOFF:
            self.vy = VARIABLE_JUMP_CUTOFF

        # Apply gravity (snappier falling gravity)
        current_gravity = FALL_GRAVITY if (self.vy > 0 and not is_jump_down) else GRAVITY
        self.vy += current_gravity * dt
        if self.vy > TERMINAL_VELOCITY:
            self.vy = TERMINAL_VELOCITY

        # 5. Offensive Ability: Ember Core Energy Blast
        if is_ability_pressed and self.powerup == POWERUP_EMBER and self.shoot_cooldown <= 0:
            self.shoot_cooldown = 0.28
            p_vx = 320.0 if self.facing_right else -320.0
            spawn_x = self.rect.right if self.facing_right else (self.rect.left - 8)
            spawn_y = self.rect.centery - 4
            projectiles.append(Projectile(spawn_x, spawn_y, p_vx, 0.0, is_player_owned=True, damage=1))
            audio_manager.play_sfx("shoot")
            particle_system.emit_sparkles(spawn_x, spawn_y, count=6, color=(255, 170, 40))

        # 6. Movement & Collision Resolution (Separate X and Y)
        # Check moving platform passenger attachment
        for mp in moving_platforms:
            if self.is_grounded and self.rect.bottom == mp.rect.top and self.rect.right > mp.rect.left and self.rect.left < mp.rect.right:
                self.x += mp.dx
                self.y += mp.dy
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)

        # Apply Horizontal Movement
        self.x += self.vx * dt
        self.rect.x = int(self.x)

        # Horizontal solid collisions
        for tile in solid_tiles:
            if not getattr(tile, 'is_platform', False) and self.rect.colliderect(tile.rect):
                if self.vx > 0:
                    self.rect.right = tile.rect.left
                elif self.vx < 0:
                    self.rect.left = tile.rect.right
                self.x = float(self.rect.x)
                self.vx = 0.0

        for b in interactive_blocks:
            if not b.is_platform and self.rect.colliderect(b.rect):
                if self.vx > 0:
                    self.rect.right = b.rect.left
                elif self.vx < 0:
                    self.rect.left = b.rect.right
                self.x = float(self.rect.x)
                self.vx = 0.0

        # Apply Vertical Movement
        self.was_grounded = self.is_grounded
        self.is_grounded = False

        self.y += self.vy * dt
        self.rect.y = int(self.y)

        # Vertical solid collisions
        for tile in solid_tiles:
            if getattr(tile, 'is_platform', False):
                # One-way platform: only land on top when falling
                if self.vy > 0 and self.rect.bottom >= tile.rect.top and (self.rect.bottom - int(self.vy * dt) - 2) <= tile.rect.top:
                    self.rect.bottom = tile.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0
                    self.is_grounded = True
            else:
                if self.rect.colliderect(tile.rect):
                    if self.vy > 0:
                        self.rect.bottom = tile.rect.top
                        self.y = float(self.rect.y)
                        self.vy = 0.0
                        self.is_grounded = True
                    elif self.vy < 0:
                        self.rect.top = tile.rect.bottom
                        self.y = float(self.rect.y)
                        self.vy = 0.0

        # Vertical interactive block collisions (Prism, Breakable)
        for b in interactive_blocks:
            if getattr(b, 'destroyed', False):
                continue
            if self.rect.colliderect(b.rect):
                if self.vy > 0:
                    self.rect.bottom = b.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0
                    self.is_grounded = True
                elif self.vy < 0:
                    self.rect.top = b.rect.bottom
                    self.y = float(self.rect.y)
                    self.vy = 0.0
                    # Hit block from below!
                    if hasattr(b, 'bump'):
                        b.bump()
                    elif hasattr(b, 'break_block'):
                        b.break_block(particle_system, audio_manager)

        # Vertical moving platform collisions
        for mp in moving_platforms:
            if self.vy >= 0 and self.rect.bottom >= mp.rect.top and (self.rect.bottom - int(self.vy * dt) - 4) <= mp.rect.top:
                if self.rect.right > mp.rect.left and self.rect.left < mp.rect.right:
                    self.rect.bottom = mp.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0.0
                    self.is_grounded = True

        # Landing feedback juice
        if not self.was_grounded and self.is_grounded:
            audio_manager.play_sfx("land")
            particle_system.emit_dust(self.rect.centerx, self.rect.bottom, count=4)
            if self.vy > 350.0:
                camera.add_shake(2.0, 0.1)

        # 7. Update Animation & Visual State
        if self.state != "HURT":
            if not self.is_grounded:
                self.state = "JUMP" if self.vy < 0 else "FALL"
            elif self.is_crouched:
                self.state = "CROUCH"
            elif abs(self.vx) > 15.0:
                self.state = "RUN"
            else:
                self.state = "IDLE"
        elif self.invulnerable_timer <= 1.2:
            self.state = "IDLE"

        self.anim_timer += dt
        if self.state == "RUN":
            run_speed_factor = 12.0 if self.is_sprinting else 8.0
            if self.anim_timer >= (1.0 / run_speed_factor):
                self.anim_timer = 0.0
                self.run_frame = (self.run_frame + 1) % 4
                if self.is_sprinting:
                    particle_system.emit_dust(self.rect.centerx, self.rect.bottom, count=1)
        elif self.state == "IDLE":
            if self.anim_timer >= 0.6:
                self.anim_timer = 0.0
                self.run_frame = (self.run_frame + 1) % 2

        # Speed Core particle trail
        if self.powerup == POWERUP_SPEED and abs(self.vx) > 30.0:
            if int(self.anim_timer * 30) % 2 == 0:
                particle_system.emit_sparkles(self.rect.centerx, self.rect.centery, count=1, color=(255, 220, 60))

    def draw(self, surface, camera, sprites):
        # Damage flashing effect
        if self.invulnerable_timer > 0 and int(self.invulnerable_timer * 20) % 2 == 0:
            return  # Skip rendering on alternate flash frames

        screen_rect = camera.apply(self.rect)
        # Position sprite relative to bounding box
        draw_x = screen_rect.x - (2 if self.facing_right else 2)
        draw_y = screen_rect.y - (4 if not self.is_crouched else 11)

        # Determine frame name
        if self.state == "DEAD":
            frame_name = "nova_hurt"
        elif self.state == "VICTORY":
            frame_name = "nova_victory"
        elif self.state == "HURT":
            frame_name = "nova_hurt"
        elif self.state == "CROUCH":
            frame_name = "nova_crouch"
        elif self.state == "JUMP":
            frame_name = "nova_jump"
        elif self.state == "FALL":
            frame_name = "nova_fall"
        elif self.state == "RUN":
            frame_name = f"nova_run_{self.run_frame}"
        else:
            frame_name = f"nova_idle_{self.run_frame % 2}"

        sprite = sprites.get(frame_name)
        if sprite:
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            surface.blit(sprite, (draw_x, draw_y))
        else:
            # Fallback primitive rendering
            pygame.draw.rect(surface, (60, 140, 240), screen_rect)

        # Draw Shield Core bubble if active
        if self.shield_active:
            shield_pos = (screen_rect.centerx, screen_rect.centery)
            pygame.draw.circle(surface, (80, 230, 150), shield_pos, 13, 1)
            pygame.draw.circle(surface, (180, 255, 220), shield_pos, 11, 1)
