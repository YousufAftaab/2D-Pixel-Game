"""
STARBOUND: THE LOST REALMS
Camera System
Smooth 2D scrolling camera with look-ahead, deadzone, level clamping, and screen shake.
"""

import random
import pygame
from src.engine.config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT


class Camera:
    def __init__(self, width=VIRTUAL_WIDTH, height=VIRTUAL_HEIGHT):
        self.width = width
        self.height = height
        self.x = 0.0
        self.y = 0.0

        # Bounds
        self.min_x = 0.0
        self.max_x = 1000.0
        self.min_y = 0.0
        self.max_y = 600.0

        # Smoothing & Lookahead
        self.smooth_speed = 8.0     # Lerp speed
        self.lookahead_x = 35.0     # px forward
        self.current_lookahead = 0.0

        # Arena lock (for boss fights)
        self.locked = False
        self.lock_bounds = None

        # Screen shake
        self.shake_magnitude = 0.0
        self.shake_timer = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.shake_enabled = True

    def set_bounds(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max(min_x + self.width, max_x)
        self.max_y = max(min_y + self.height, max_y)

    def lock_to_arena(self, rect):
        """Locks camera to a boss arena bounding box."""
        self.locked = True
        self.lock_bounds = rect

    def unlock_arena(self):
        self.locked = False
        self.lock_bounds = None

    def add_shake(self, magnitude, duration):
        if not self.shake_enabled:
            return
        self.shake_magnitude = max(self.shake_magnitude, magnitude)
        self.shake_timer = max(self.shake_timer, duration)

    def update(self, target_rect, facing_right, dt):
        # 1. Update shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            fade = max(0.0, self.shake_timer / 0.3)
            current_mag = self.shake_magnitude * fade
            self.shake_offset_x = random.uniform(-current_mag, current_mag)
            self.shake_offset_y = random.uniform(-current_mag, current_mag)
            if self.shake_timer <= 0:
                self.shake_magnitude = 0.0
                self.shake_offset_x = 0.0
                self.shake_offset_y = 0.0
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0

        if self.locked and self.lock_bounds:
            # Center on arena
            target_x = self.lock_bounds.centerx - self.width / 2.0
            target_y = self.lock_bounds.centery - self.height / 2.0
            self.x += (target_x - self.x) * min(1.0, self.smooth_speed * dt)
            self.y += (target_y - self.y) * min(1.0, self.smooth_speed * dt)
            return

        # 2. Lookahead calculation
        desired_look = self.lookahead_x if facing_right else -self.lookahead_x
        self.current_lookahead += (desired_look - self.current_lookahead) * min(1.0, 4.0 * dt)

        # 3. Target position (center target on screen + lookahead)
        target_center_x = target_rect.centerx + self.current_lookahead
        target_center_y = target_rect.centery - 10.0  # slight upward bias

        desired_x = target_center_x - self.width / 2.0
        desired_y = target_center_y - self.height / 2.0

        # 4. Lerp smoothing
        self.x += (desired_x - self.x) * min(1.0, self.smooth_speed * dt)
        self.y += (desired_y - self.y) * min(1.0, self.smooth_speed * dt)

        # 5. Clamping to level boundaries
        self.x = max(self.min_x, min(self.max_x - self.width, self.x))
        self.y = max(self.min_y, min(self.max_y - self.height, self.y))

    def apply(self, rect_or_pos):
        """Converts world coordinate/rect into screen space coordinate/rect."""
        cam_x = int(self.x + self.shake_offset_x)
        cam_y = int(self.y + self.shake_offset_y)

        if isinstance(rect_or_pos, pygame.Rect):
            return pygame.Rect(rect_or_pos.x - cam_x, rect_or_pos.y - cam_y, rect_or_pos.w, rect_or_pos.h)
        else:
            return (rect_or_pos[0] - cam_x, rect_or_pos[1] - cam_y)

    def get_view_rect(self):
        """Returns the world-space bounding rect of what the camera sees."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
