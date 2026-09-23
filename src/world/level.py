"""
STARBOUND: THE LOST REALMS
Level Manager & Physics Orchestrator
Loads tile grids, handles entity updates, triggers collisions, and manages the gameplay loop.
"""

import pygame
from src.engine.config import (
    TILE_SIZE, VIRTUAL_WIDTH, VIRTUAL_HEIGHT,
    POWERUP_EMBER, POWERUP_SKY, POWERUP_SHIELD, POWERUP_SPEED
)
from src.entities.player import Player
from src.entities.enemies import (
    WalkerEnemy, FlyerEnemy, ChargerEnemy, TurretEnemy, JumperEnemy, ShieldedEnemy
)
from src.entities.bosses import BossSentinel, BossWarden
from src.entities.collectibles import StarShard, AstralCrystal, HeartOrb, PowerUpItem
from src.entities.blocks import (
    SolidTile, PlatformTile, BreakableBlock, PrismBlock, MovingPlatform, Hazard, Checkpoint, ExitPortal
)
from src.world.parallax import ParallaxBackground
from src.world.levels_data import generate_level_data


class Level:
    def __init__(self, level_id, settings, audio_manager, particle_system, camera):
        self.level_id = level_id
        self.settings = settings
        self.audio = audio_manager
        self.particles = particle_system
        self.camera = camera

        # Level data
        self.data = generate_level_data(level_id)
        self.theme = self.data.get("theme", "verdant")
        self.parallax = ParallaxBackground(self.theme)

        # Entity lists
        self.solid_tiles = []
        self.platform_tiles = []
        self.interactive_blocks = []
        self.hazards = []
        self.checkpoints = []
        self.exit_portal = None

        self.shards = []
        self.crystals = []
        self.powerup_items = []
        self.enemies = []
        self.projectiles = []
        self.boss = None

        # Level statistics
        self.score = 0
        self.shards_collected = 0
        self.total_level_shards = 0
        self.crystals_found = []
        self.enemies_defeated = 0
        self.time_elapsed = 0.0
        self.completed = False
        self.is_game_over = False

        # Build level grid
        self._load_map()

        # Play level music
        bgm = self.data.get("bgm", "theme_verdant")
        self.audio.play_music(bgm)

    def _load_map(self):
        grid = self.data["map"]
        self.height_tiles = len(grid)
        self.width_tiles = max(len(row) for row in grid)

        self.level_pixel_width = self.width_tiles * TILE_SIZE
        self.level_pixel_height = self.height_tiles * TILE_SIZE
        self.camera.set_bounds(0, 0, self.level_pixel_width, self.level_pixel_height)

        player_start_x = 40
        player_start_y = 100

        for row_idx, row in enumerate(grid):
            y = row_idx * TILE_SIZE
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE

                if char == '#':
                    # Top/surface solid tile
                    self.solid_tiles.append(SolidTile(x, y, tile_type="top"))
                elif char == '=':
                    # Dirt/deep solid tile
                    self.solid_tiles.append(SolidTile(x, y, tile_type="mid"))
                elif char == '-':
                    # One-way jump-through platform
                    self.solid_tiles.append(PlatformTile(x, y))
                elif char == 'B':
                    self.interactive_blocks.append(BreakableBlock(x, y))
                elif char == '?':
                    self.interactive_blocks.append(PrismBlock(x, y, contents="SHARD"))
                elif char == 'E':
                    self.interactive_blocks.append(PrismBlock(x, y, contents="EMBER"))
                elif char == 'S':
                    self.interactive_blocks.append(PrismBlock(x, y, contents="SKY"))
                elif char == 'H':
                    self.interactive_blocks.append(PrismBlock(x, y, contents="HEART"))
                elif char == '^':
                    self.hazards.append(Hazard(x, y, hazard_type="spikes"))
                elif char == 'L':
                    self.hazards.append(Hazard(x, y, hazard_type="lava"))
                elif char == 'C':
                    self.checkpoints.append(Checkpoint(x, y))
                elif char == 'X':
                    self.exit_portal = ExitPortal(x, y)
                elif char == '*':
                    self.shards.append(StarShard(x, y))
                    self.total_level_shards += 1
                elif char == 'A':
                    c_id = f"{self.level_id}_c{len(self.crystals) + 1}"
                    self.crystals.append(AstralCrystal(c_id, x, y))
                elif char == 'P':
                    player_start_x = x
                    player_start_y = y
                elif char == 'w':
                    self.enemies.append(WalkerEnemy(x, y))
                elif char == 'f':
                    self.enemies.append(FlyerEnemy(x, y))
                elif char == 'c':
                    self.enemies.append(ChargerEnemy(x, y))
                elif char == 't':
                    self.enemies.append(TurretEnemy(x, y))
                elif char == 'j':
                    self.enemies.append(JumperEnemy(x, y))
                elif char == 'd':
                    self.enemies.append(ShieldedEnemy(x, y))
                elif char == 'M':
                    self.interactive_blocks.append(MovingPlatform(x, y, width=32, move_x=45.0, speed=1.4))
                elif char == '1':
                    self.boss = BossSentinel(x, y - 16)
                elif char == '6':
                    self.boss = BossWarden(x + 24, y)

        # Instantiate player
        self.player = Player(
            player_start_x, player_start_y,
            assist_mode=self.settings.get("assist_mode", False),
            assist_extra_health=self.settings.get("assist_extra_health", False),
            assist_extra_coyote=self.settings.get("assist_extra_coyote", False)
        )

    def update(self, dt, input_mgr):
        if self.completed:
            return

        self.time_elapsed += dt
        self.parallax.update(dt)

        # Update moving platforms
        moving_platforms = [b for b in self.interactive_blocks if isinstance(b, MovingPlatform)]
        for mp in moving_platforms:
            mp.update(dt)

        # Update Prism blocks (bump animation)
        for b in self.interactive_blocks:
            if isinstance(b, PrismBlock):
                b.update(dt)

        # Update Player
        self.player.update(
            dt, input_mgr, self.audio, self.particles, self.camera,
            self.solid_tiles, moving_platforms, self.interactive_blocks, self.projectiles
        )

        # Camera follow player
        self.camera.update(self.player.rect, self.player.facing_right, dt)

        # Update Enemies
        assist_slower = self.settings.get("assist_mode", False) and self.settings.get("assist_slower_enemies", False)
        for enemy in self.enemies:
            if isinstance(enemy, TurretEnemy):
                enemy.update(dt, self.solid_tiles, self.player, assist_slower=assist_slower, projectiles=self.projectiles)
            else:
                enemy.update(dt, self.solid_tiles, self.player, assist_slower=assist_slower)

        # Update Boss
        if self.boss and self.boss.alive:
            if isinstance(self.boss, BossSentinel):
                self.boss.update(dt, self.solid_tiles, self.player, self.audio, self.particles, self.camera, self.projectiles)
            elif isinstance(self.boss, BossWarden):
                self.boss.update(dt, self.player, self.audio, self.particles, self.camera, self.projectiles)

        # Update Collectibles & Items
        for s in self.shards:
            s.update(dt)
        for c in self.crystals:
            c.update(dt)
        for p in self.powerup_items:
            p.update(dt, self.solid_tiles)

        # Update Projectiles
        self.projectiles = [p for p in self.projectiles if p.update(dt, self.solid_tiles)]

        # Update Exit Portal particles
        if self.exit_portal:
            self.exit_portal.update(dt, self.particles)

        # -----------------------------------------------------------------
        # COLLISION DETECTION & RESOLUTION
        # -----------------------------------------------------------------
        self._check_shards()
        self._check_crystals()
        self._check_powerup_items()
        self._check_block_rewards()
        self._check_hazards()
        self._check_checkpoints()
        self._check_enemy_combat()
        self._check_projectiles()
        self._check_boss_combat()
        self._check_exit()

        # Check death fall out of bounds
        if self.player.rect.top > self.level_pixel_height + 40 and self.player.state != "DEAD":
            self.player.take_damage(self.player.max_health, self.player.rect.centerx, self.audio, self.particles, self.camera)

    def _check_shards(self):
        for s in self.shards:
            if not s.collected and self.player.rect.colliderect(s.rect):
                s.collected = True
                self.shards_collected += 1
                self.score += 100
                self.audio.play_sfx("shard")
                self.particles.emit_sparkles(s.rect.centerx, s.rect.centery, count=8, color=(255, 230, 80))
                self.particles.add_floating_text("+100", s.rect.centerx, s.rect.top - 4)

    def _check_crystals(self):
        for c in self.crystals:
            if not c.collected and self.player.rect.colliderect(c.rect):
                c.collected = True
                self.crystals_found.append(c.crystal_id)
                self.score += 1000
                self.audio.play_sfx("crystal")
                self.particles.emit_sparkles(c.rect.centerx, c.rect.centery, count=16, color=(60, 230, 255))
                self.particles.add_floating_text("+1000", c.rect.centerx, c.rect.top - 8, color=(60, 230, 255))

    def _check_powerup_items(self):
        for p in self.powerup_items:
            if not p.collected and self.player.rect.colliderect(p.rect):
                p.collected = True
                self.player.apply_powerup(p.powerup_type, self.audio, self.particles)
                self.score += 500

    def _check_block_rewards(self):
        for b in self.interactive_blocks:
            if isinstance(b, PrismBlock) and b.bump_velocity < -50.0:
                # Spawn reward item
                content = b.contents
                bx, by = b.rect.x, b.rect.y - 16
                if content == "EMBER":
                    self.powerup_items.append(PowerUpItem(POWERUP_EMBER, bx, by))
                elif content == "SKY":
                    self.powerup_items.append(PowerUpItem(POWERUP_SKY, bx, by))
                elif content == "SHIELD":
                    self.powerup_items.append(PowerUpItem(POWERUP_SHIELD, bx, by))
                elif content == "SPEED":
                    self.powerup_items.append(PowerUpItem(POWERUP_SPEED, bx, by))
                elif content == "HEART":
                    if self.player.health < self.player.max_health:
                        self.player.health += 1
                        self.audio.play_sfx("crystal")
                        self.particles.emit_sparkles(self.player.rect.centerx, self.player.rect.centery, count=10, color=(240, 60, 70))
                else:  # SHARD
                    self.shards_collected += 1
                    self.score += 100
                    self.audio.play_sfx("shard")
                    self.particles.emit_sparkles(b.rect.centerx, b.rect.y - 8, count=8, color=(255, 230, 80))

    def _check_hazards(self):
        for h in self.hazards:
            if self.player.rect.colliderect(h.rect):
                self.player.take_damage(1, h.rect.centerx, self.audio, self.particles, self.camera)

    def _check_checkpoints(self):
        for cp in self.checkpoints:
            if not cp.activated and self.player.rect.colliderect(cp.rect):
                cp.activate(self.audio, self.particles)
                self.player.set_spawn(cp.rect.centerx - 6, cp.rect.bottom - 20)

    def _check_enemy_combat(self):
        for enemy in self.enemies:
            if not enemy.alive:
                continue

            if self.player.rect.colliderect(enemy.rect):
                # Check Stomp from above
                if enemy.can_be_stomped(self.player.rect, self.player.vy):
                    enemy.take_damage(1, self.audio, self.particles)
                    pts = self.player.register_stomp(enemy.rect.centerx, self.audio, self.particles)
                    self.score += pts
                    self.enemies_defeated += 1
                else:
                    # Enemy damages player
                    self.player.take_damage(1, enemy.rect.centerx, self.audio, self.particles, self.camera)

    def _check_projectiles(self):
        for proj in self.projectiles:
            if not proj.alive:
                continue

            if proj.is_player_owned:
                # Hits enemies
                for enemy in self.enemies:
                    if enemy.alive and proj.rect.colliderect(enemy.rect):
                        # Shielded enemy block check
                        if isinstance(enemy, ShieldedEnemy) and enemy.check_frontal_block(proj.x):
                            proj.alive = False
                            self.audio.play_sfx("land")
                            self.particles.emit_sparkles(proj.x, proj.y, count=5, color=(140, 200, 255))
                            break

                        enemy.take_damage(proj.damage, self.audio, self.particles)
                        self.score += enemy.score_value
                        self.enemies_defeated += 1
                        proj.alive = False
                        break

                # Hits Boss
                if self.boss and self.boss.alive and proj.rect.colliderect(self.boss.rect):
                    self.boss.take_hit(proj.damage, self.audio, self.particles, self.camera)
                    proj.alive = False

                # Hits Breakable Blocks
                for b in self.interactive_blocks:
                    if isinstance(b, BreakableBlock) and not b.destroyed and proj.rect.colliderect(b.rect):
                        b.break_block(self.particles, self.audio)
                        proj.alive = False
                        break
            else:
                # Enemy projectile hits player
                if self.player.rect.colliderect(proj.rect):
                    self.player.take_damage(proj.damage, proj.x, self.audio, self.particles, self.camera)
                    proj.alive = False

    def _check_boss_combat(self):
        if not self.boss or not self.boss.alive:
            return

        # Player stomp or collision with boss
        if self.player.rect.colliderect(self.boss.rect):
            if self.player.vy > 0 and self.player.rect.bottom <= (self.boss.rect.top + 10):
                self.boss.take_hit(1, self.audio, self.particles, self.camera)
                self.player.vy = -340.0
                self.particles.emit_stomp(self.player.rect.centerx, self.player.rect.bottom)
            else:
                self.player.take_damage(1, self.boss.rect.centerx, self.audio, self.particles, self.camera)

    def _check_exit(self):
        # In boss level, exit portal activates only after boss is defeated
        if self.boss:
            if not self.boss.alive and self.exit_portal and self.player.rect.colliderect(self.exit_portal.rect):
                self._finish_level()
        else:
            if self.exit_portal and self.player.rect.colliderect(self.exit_portal.rect):
                self._finish_level()

    def _finish_level(self):
        self.completed = True
        self.player.state = "VICTORY"
        self.audio.play_sfx("crystal")
        self.audio.play_music("theme_victory", loops=0)
        self.particles.emit_sparkles(self.player.rect.centerx, self.player.rect.centery, count=30, color=(255, 235, 90))

    def draw(self, surface, assets):
        # 1. Parallax background
        self.parallax.draw(surface, self.camera)

        # 2. Solid & platform tiles
        theme_prefix = f"tile_{self.theme}"
        tile_top = assets["tiles"].get(f"{theme_prefix}_top")
        tile_mid = assets["tiles"].get(f"{theme_prefix}_mid")
        tile_plat = assets["tiles"].get(f"{theme_prefix}_plat")

        for tile in self.solid_tiles:
            sr = self.camera.apply(tile.rect)
            if getattr(tile, 'is_platform', False):
                if tile_plat:
                    surface.blit(tile_plat, sr)
                else:
                    pygame.draw.rect(surface, (120, 140, 160), sr)
            else:
                s = tile_top if tile.tile_type == "top" else tile_mid
                if s:
                    surface.blit(s, sr)
                else:
                    pygame.draw.rect(surface, (90, 70, 50), sr)

        # 3. Interactive Blocks
        block_prism = assets["tiles"].get("block_prism")
        block_break = assets["tiles"].get("block_breakable")
        for b in self.interactive_blocks:
            if isinstance(b, PrismBlock):
                b.draw(surface, self.camera, block_prism)
            elif isinstance(b, BreakableBlock):
                b.draw(surface, self.camera, block_break)
            elif isinstance(b, MovingPlatform):
                b.draw(surface, self.camera)

        # 4. Hazards
        spike_sprite = assets["tiles"].get("hazard_spikes")
        for h in self.hazards:
            h.draw(surface, self.camera, spike_sprite)

        # 5. Checkpoints
        cp_on = assets["sprites"].get("checkpoint_on")
        cp_off = assets["sprites"].get("checkpoint_off")
        for cp in self.checkpoints:
            cp.draw(surface, self.camera, cp_on, cp_off)

        # 6. Exit Portal
        if self.exit_portal:
            portal_sprite = assets["sprites"].get("portal_exit")
            self.exit_portal.draw(surface, self.camera, portal_sprite)

        # 7. Collectibles
        shard_frames = [assets["sprites"].get(f"star_shard_{i}") for i in range(4)]
        cryst_sprite = assets["sprites"].get("astral_crystal")
        for s in self.shards:
            if not s.collected:
                s.draw(surface, self.camera, shard_frames)

        for c in self.crystals:
            if not c.collected:
                c.draw(surface, self.camera, cryst_sprite)

        for p in self.powerup_items:
            if not p.collected:
                p.draw(surface, self.camera, assets["sprites"])

        # 8. Enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(surface, self.camera, assets["sprites"])

        # 9. Boss
        if self.boss and self.boss.alive:
            if isinstance(self.boss, BossSentinel):
                s_sentinel = assets["sprites"].get("boss_sentinel")
                self.boss.draw(surface, self.camera, s_sentinel)
            elif isinstance(self.boss, BossWarden):
                s_w1 = assets["sprites"].get("boss_warden_1")
                s_w2 = assets["sprites"].get("boss_warden_2")
                self.boss.draw(surface, self.camera, s_w1, s_w2)

        # 10. Projectiles
        proj_nova = assets["sprites"].get("proj_nova")
        proj_enemy = assets["sprites"].get("proj_enemy")
        for proj in self.projectiles:
            s = proj_nova if proj.is_player_owned else proj_enemy
            proj.draw(surface, self.camera, s)

        # 11. Player
        self.player.draw(surface, self.camera, assets["sprites"])

        # 12. Particles & floating score popups
        self.particles.draw(surface, self.camera)
