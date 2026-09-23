"""
STARBOUND: THE LOST REALMS
Automated Unit Tests: Combat, Stomp Combos & Power-Ups
"""

import pytest
import pygame
from src.entities.player import Player
from src.entities.enemies import WalkerEnemy, FlyerEnemy, ShieldedEnemy
from src.entities.projectile import Projectile
from src.engine.config import (
    POWERUP_EMBER, POWERUP_SKY, POWERUP_SHIELD, POWERUP_SPEED,
    COMBO_POINTS, SPEED_CORE_DURATION
)
from tests.test_player import DummyInput, DummyAudio, DummyParticles, DummyCamera


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_ember_core_projectile_fire():
    player = Player(100, 100)
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()
    input_mgr = DummyInput()

    # Apply Ember Core
    player.apply_powerup(POWERUP_EMBER, audio, particles)
    assert player.powerup == POWERUP_EMBER

    projectiles = []
    input_mgr.actions_pressed.add("ability")

    # Update player
    player.update(0.016, input_mgr, audio, particles, camera, [], [], [], projectiles)

    # A player-owned projectile should be launched
    assert len(projectiles) == 1
    assert projectiles[0].is_player_owned is True
    assert projectiles[0].vx > 0.0


def test_sky_core_double_jump():
    player = Player(100, 100)
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()
    input_mgr = DummyInput()

    # Apply Sky Core
    player.apply_powerup(POWERUP_SKY, audio, particles)
    assert player.can_double_jump is True

    # Mid-air jump
    player.is_grounded = False
    player.coyote_timer = 0.0
    input_mgr.actions_pressed.add("jump")

    player.update(0.016, input_mgr, audio, particles, camera, [], [], [], [])

    # Double jump executed: vy should be negative and can_double_jump consumed
    assert player.vy < 0.0
    assert player.can_double_jump is False


def test_shield_core_absorbs_damage():
    player = Player(100, 100)
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()

    # Apply Shield Core
    player.apply_powerup(POWERUP_SHIELD, audio, particles)
    assert player.shield_active is True
    initial_health = player.health

    # Take damage hit
    hit = player.take_damage(1, 50, audio, particles, camera)
    assert hit is True
    # Health must be preserved!
    assert player.health == initial_health
    # Shield must be broken
    assert player.shield_active is False
    assert player.powerup != POWERUP_SHIELD


def test_speed_core_boost_and_expiration():
    player = Player(100, 100)
    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()
    input_mgr = DummyInput()

    player.apply_powerup(POWERUP_SPEED, audio, particles)
    assert player.powerup == POWERUP_SPEED
    assert player.speed_core_timer == SPEED_CORE_DURATION

    # Simulate timer expiration
    player.update(SPEED_CORE_DURATION + 0.1, input_mgr, audio, particles, camera, [], [], [], [])
    assert player.powerup != POWERUP_SPEED


def test_stomp_combo_multiplier():
    player = Player(100, 100)
    audio = DummyAudio()
    particles = DummyParticles()

    pts1 = player.register_stomp(100, audio, particles)
    assert pts1 == COMBO_POINTS[0]  # 100
    assert player.combo_count == 1

    pts2 = player.register_stomp(100, audio, particles)
    assert pts2 == COMBO_POINTS[1]  # 200
    assert player.combo_count == 2

    pts3 = player.register_stomp(100, audio, particles)
    assert pts3 == COMBO_POINTS[2]  # 400
    assert player.combo_count == 3


def test_shielded_enemy_blocks_front_only():
    enemy = ShieldedEnemy(100, 100)
    enemy.facing_right = True

    # Attack from front (right of enemy) -> Blocked
    assert enemy.check_frontal_block(120) is True

    # Attack from behind (left of enemy) -> Vulnerable
    assert enemy.check_frontal_block(80) is False
