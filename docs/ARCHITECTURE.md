# Technical Architecture: Starbound: The Lost Realms

## 1. System Architecture Overview

```
+-------------------------------------------------------------------------+
|                               Main Game Loop                            |
|                          (60 FPS Fixed Timestep)                        |
+-------------------------------------------------------------------------+
       |                         |                        |
       v                         v                        v
+-------------------+   +--------------------+   +-----------------------+
|   InputManager    |   |    AudioManager    |   |     SaveManager       |
| Keyboard & Gamepad|   | Mixer, SFX & Music |   | JSON + SHA256 Checksum|
+-------------------+   +--------------------+   +-----------------------+
       |                         |                        |
       +------------+------------+------------------------+
                    |
                    v
       +-------------------------+
       |   Finite State Machine  |
       |  (MENU, MAP, LEVEL...)  |
       +-------------------------+
                    |
         +----------+----------+
         |                     |
         v                     v
+------------------+  +--------------------------------------------------+
|   WorldMap / UI  |  |                     Level Scene                  |
| Menus, Settings, |  |  +--------------------+   +--------------------+ |
| HUD, Debug Tools |  |  |       Camera       |   | Parallax Background| |
+------------------+  |  | Lerp, Shake, Bounds|   | Depth layers & FX  | |
                      |  +--------------------+   +--------------------+ |
                      |            |                         |           |
                      |            v                         v           |
                      |  +--------------------+   +--------------------+ |
                      |  |     Player (Nova)  |   | Enemies & Bosses   | |
                      |  | Physics, Abilities |   | AI State Machines  | |
                      |  +--------------------+   +--------------------+ |
                      |            |                         |           |
                      |            v                         v           |
                      |  +--------------------+   +--------------------+ |
                      |  | Interactive Blocks |   | Collectibles & FX  | |
                      |  | Prism, Breakable   |   | Shards, Particles  | |
                      |  +--------------------+   +--------------------+ |
                      +--------------------------------------------------+
```

---

## 2. Finite State Machine (FSM)

The top-level application states are managed deterministically by `src/main.py`:
- `STATE_MAIN_MENU`: Title screen, campaign start, settings, controls, credits.
- `STATE_WORLD_MAP`: Campaign navigation across Worlds 1 to 6.
- `STATE_LEVEL`: Active gameplay scene execution.
- `STATE_PAUSE`: Overlay pausing physics, providing restart/exit/settings options.
- `STATE_LEVEL_COMPLETE`: Victory tally, score breakdown, next level unlocking.
- `STATE_GAME_OVER`: Mission failed screen with checkpoint respawn and restart options.
- `STATE_SETTINGS`: Live adjustment of resolution, fullscreen, volume, and assist mode.
- `STATE_CREDITS`: Developer attribution and technical credits.

---

## 3. Player Movement & Physics Pipeline

Player physics are implemented in `src/entities/player.py` and tuned in `src/engine/config.py`:
1. **Subpixel Position Integration**:
   - Positions `(x, y)` and velocities `(vx, vy)` are maintained as IEEE-754 64-bit floats.
   - Bounding rect `self.rect` is synchronized each frame to integer pixels, avoiding rounding drift.
2. **Coyote Time**:
   - A timer (`coyote_timer`) is initialized to 120 ms whenever the player is grounded.
   - When walking off a ledge, the timer counts down. If jump is pressed while `coyote_timer > 0`, the jump is granted.
3. **Jump Buffering**:
   - Pressing jump sets `jump_buffer_timer` to 120 ms. If the player makes contact with ground while buffer is active, an immediate jump executes.
4. **Variable Jump Height**:
   - When the jump button is released and `vy < VARIABLE_JUMP_CUTOFF` (-140 px/s), upward velocity is capped to create responsive variable jump arcs.
5. **Separate Axis Collision Resolution**:
   - Horizontal movement is integrated first: solid tile collisions resolve `self.rect.right` or `self.rect.left` and zero `vx`.
   - Vertical movement is integrated second: solid tile collisions resolve `self.rect.bottom` (landing) or `self.rect.top` (ceiling bump) and zero `vy`.
   - One-way platform tiles check if `vy > 0` and previous bottom position was above the platform top.

---

## 4. Combat & Power-Up Subsystems

- **Stomp Combos**:
  - Enemy stomp detection checks `player.vy > 0 and player.rect.bottom <= enemy.rect.top + 8`.
  - Stomp launches player upward (`STOMP_BOUNCE_VELOCITY = -300 px/s`) and chains combo multiplier: `100 -> 200 -> 400 -> 800 -> 1600 -> 3200`.
- **Power-Up Hierarchy**:
  - `Ember Core`: Emits player-owned projectiles (`Projectile`) traveling at 320 px/s that damage enemies and shatter breakable blocks.
  - `Sky Core`: Modifies jump velocity and enables mid-air double jump with jetpack sparkle particles.
  - `Shield Core`: Absorbs 1 incoming damage hit entirely, providing i-frame recovery without HP penalty.
  - `Speed Core`: Boosts movement velocity by 1.45x for 15 seconds with motion trail particles.

---

## 5. Enemy AI State Machines

Enemies inherit from `BaseEnemy` and implement discrete state machines:
- **Walker (Prowler)**: `PATROL` (checks ground foot probes 2px ahead of edges and wall collisions; reverses upon edge).
- **Flyer (Vesper)**: `PATROL` (sinusoidal hover) -> `DIVE` (vectors towards player when within 110px) -> `RETREAT` (returns to origin).
- **Charger (Crag)**: `PATROL` -> `CHASE` (sprints at 130 px/s when player enters line of sight) -> Wall impact stun.
- **Turret (Pulse Sentry)**: Stationary; calculates Euclidean angle to player every 2.0s and fires plasma bolts.
- **Jumper (Hopper)**: `GROUNDED` -> crouch charge -> leap in parabolic arc toward player.
- **Shielded (Vanguard)**: Checks incoming attack coordinates against facing direction to deflect frontal projectiles.

---

## 6. Procedural Audio Synthesis Architecture

Implemented in `src/systems/generator.py`:
- Employs mathematical signal synthesis (`numpy`) sampled at 44.1 kHz 16-bit PCM.
- **Waveform primitives**:
  - Square wave with variable pulse width.
  - Triangle wave for smooth basslines.
  - White noise generator for percussive hits, explosions, and footsteps.
  - Linear and exponential ADSR envelopes.
- Generates 13 responsive sound effects and 9 multi-track melodic compositions across all world themes.

---

## 7. Persistence & Anti-Corruption

Implemented in `src/systems/save_manager.py`:
- Saves to `saves/save_data.json` with an atomic temporary file rename pattern (`.tmp` -> `.json`).
- Pre-existing valid saves are automatically archived to `saves/save_data.bak`.
- Every save payload contains a SHA-256 hash of its serialized content. On boot, the hash is verified; if corruption is detected, the manager seamlessly rolls back to `save_data.bak`.
