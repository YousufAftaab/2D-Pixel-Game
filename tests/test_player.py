"""
STARBOUND: THE LOST REALMS
Automated Unit Tests: Player Controller & Physics
"""

import pytest
import pygame
from src.entities.player import Player
from src.engine.config import (
    PLAYER_DEFAULT_MAX_HEALTH, JUMP_VELOCITY, VARIABLE_JUMP_CUTOFF,
    COYOTE_TIME, JUMP_BUFFER_TIME, POWERUP_NONE, POWERUP_SKY
)


class DummyInput:
    def __init__(self):
        self.axis_x = 0.0
        self.axis_y = 0.0
        self.actions_down = set()
        self.actions_pressed = set()
        self.actions_released = set()

    def is_action_down(self, action):
        return action in self.actions_down

    def is_action_pressed(self, action):
        return action in self.actions_pressed

    def is_action_released(self, action):
        return action in self.actions_released


class DummyAudio:
    def play_sfx(self, name):
        pass


class DummyParticles:
    def emit_dust(self, *args, **kwargs):
        pass
    def emit_sparkles(self, *args, **kwargs):
        pass
    def emit_stomp(self, *args, **kwargs):
        pass
    def emit_explosion(self, *args, **kwargs):
        pass
    def add_floating_text(self, *args, **kwargs):
        pass


class DummyCamera:
    def add_shake(self, *args, **kwargs):
        pass


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_player_initial_state():
    player = Player(100, 100)
    assert player.x == 100
    assert player.y == 100
    assert player.health == PLAYER_DEFAULT_MAX_HEALTH
    assert player.powerup == POWERUP_NONE
    assert player.state == "IDLE"
    assert player.can_double_jump is False


def test_player_horizontal_acceleration():
    from src.entities.blocks import SolidTile
    player = Player(100, 100)
    floor = [SolidTile(x, 120, tile_type="top") for x in range(60, 240, 16)]
    input_mgr = DummyInput()
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()

    # Press right on ground
    input_mgr.axis_x = 1.0
    player.update(0.1, input_mgr, audio, particles, camera, floor, [], [], [])

    assert player.vx > 0.0
    assert player.facing_right is True
    assert player.state == "RUN"
    assert player.is_grounded is True


def test_player_coyote_time_and_jump():
    player = Player(100, 100)
    input_mgr = DummyInput()
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()

    # Step off ledge: grounded -> not grounded
    player.is_grounded = True
    player.update(0.016, input_mgr, audio, particles, camera, [], [], [], [])
    player.is_grounded = False

    # Coyote timer should be active
    assert player.coyote_timer > 0.0

    # Press jump within coyote window
    input_mgr.actions_pressed.add("jump")
    player.update(0.016, input_mgr, audio, particles, camera, [], [], [], [])

    # Jump impulse should have triggered
    assert player.vy < 0.0
    assert player.coyote_timer == 0.0


def test_player_variable_jump_height():
    player = Player(100, 100)
    input_mgr = DummyInput()
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()

    player.vy = -350.0  # Jumping upward rapidly
    # Release jump button early
    input_mgr.actions_released.add("jump")
    player.update(0.016, input_mgr, audio, particles, camera, [], [], [], [])

    # Upward velocity should be cut to cutoff limit (plus 1 frame of gravity)
    assert player.vy >= VARIABLE_JUMP_CUTOFF
    assert player.vy > -200.0


def test_player_damage_and_invulnerability():
    player = Player(100, 100)
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()

    initial_hp = player.health
    # Take damage from left (source_x = 50)
    hit = player.take_damage(1, 50, audio, particles, camera)
    assert hit is True
    assert player.health == initial_hp - 1
    assert player.invulnerable_timer > 0.0
    assert player.vx > 0.0  # knocked back to the right

    # Immediate second hit should be blocked by i-frames
    hit_again = player.take_damage(1, 50, audio, particles, camera)
    assert hit_again is False
    assert player.health == initial_hp - 1


def test_player_death_at_zero_health():
    player = Player(100, 100)
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()

    player.take_damage(player.health, 50, audio, particles, camera)
    assert player.health == 0
    assert player.state == "DEAD"


def test_assist_mode_extra_health():
    player = Player(100, 100, assist_mode=True, assist_extra_health=True)
    assert player.health == PLAYER_DEFAULT_MAX_HEALTH + 2
    assert player.max_health == PLAYER_DEFAULT_MAX_HEALTH + 2
