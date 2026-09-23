# STARBOUND: THE LOST REALMS

A polished, original 2D side-scrolling retro platformer built from scratch for Windows PC.

---

## 🌌 Overview

In **Starbound: The Lost Realms**, the celestial world was once sustained by the radiant **Astral Core**. When a cosmic catastrophe shattered the Core into thousands of **Star Shards**, six distinct planetary realms fractured and fell into instability. 

Playing as **Nova**—an adventurous young celestial explorer equipped with an energy backpack and cosmic scarf—you must run, jump, dash, stomp, and blast your way through six diverse realms, restore the Astral Core, and confront **The Warden of the Lost Realm**!

---

## ✨ Features

- **Responsive Physics & Game Feel**:
  - Variable jump height (releasing jump early truncates jump arc).
  - Generous Coyote Time (120 ms grace period after walking off edges).
  - Jump Buffering (120 ms input grace before touching down).
  - Crouching and sliding under low obstacles.
  - Subpixel floating-point collision resolution.
- **Original Power-Up System**:
  - 💥 **Ember Core**: Unleashes forward energy blasts to destroy cracked blocks and defeat enemies at range.
  - 🚀 **Sky Core**: Grants high jump clearance and a mid-air double jump with jetpack sparkle effects.
  - 🛡️ **Shield Core**: Generates a prismatic barrier absorbing one full hit without taking damage.
  - ⚡ **Speed Core**: Hyper-accelerates Nova's running speed, creating a glowing particle trail.
- **6 Original Enemy Archetypes**:
  - **Walker (Prowler)**: Edge-aware robotic patroller that reverses at walls and ledges; stompable.
  - **Flyer (Vesper)**: Sinusoidal aerial hunter that dive-bombs when Nova enters proximity.
  - **Charger (Crag)**: Armored beast that charges forward with ground-shaking speed upon spotting the player.
  - **Turret (Pulse Sentry)**: Stationary crystal sentinel firing targeted plasma bolts.
  - **Jumper (Hopper)**: Spring-legged bio-mechanical cricket that leaps in high arcs.
  - **Shielded (Vanguard)**: Frontal energy shield ricochets projectile attacks; vulnerable only from behind or above.
- **Boss Encounters**:
  - **World 1 Boss**: *The Ancient Sentinel* — charges, ground slams shockwaves, and stuns upon hitting walls.
  - **World 6 Final Boss**: *The Warden of the Lost Realm* — a multi-phase cosmic battle with teleportation, orbiting astral shields, and bullet curtains.
- **6 Diverse Themed Worlds (24 Levels)**:
  - **World 1: Verdant Valley** — Lush green hills, waterfalls, ancient stone ruins.
  - **World 2: Sunscar Desert** — Shifting sands, sinking pillars, dune citadels.
  - **World 3: Frostfall** — Slippery ice platforms, falling icicles, frozen caverns.
  - **World 4: Sky Ruins** — Floating islands, cloud updrafts, crumbling bridges.
  - **World 5: Ember Depths** — Volcanic caverns, rising magma rivers, timed basalt platforms.
  - **World 6: The Lost Realm** — Shattered cosmic void combining all mechanics.
- **Stomp Combo & Scoring System**:
  - Chain stomp enemy heads without touching the ground to multiply score: `100 -> 200 -> 400 -> 800 -> 1600 -> 3200`!
  - Real-time floating score popups.
- **Complete World Map & Level Select**:
  - Campaign node graph displaying unlocked levels, star shard counts, clear times, and completion percentage.
- **100% Bespoke Original Assets**:
  - Procedurally generated pixel art (sprites, tilesets, hazards, animations).
  - Procedurally synthesized multi-track chiptune music and authentic retro SFX via mathematical audio synthesis.
  - **Zero copyrighted or external Mario/Nintendo assets**.
- **Robust Persistence & Autosave**:
  - JSON save format protected with SHA-256 checksums and automated `.bak` backup redundancy.
  - Autosaves upon level completion and settings adjustments.
- **Full Accessibility & Assist Mode**:
  - Toggleable Assist Mode: Extra Health (+2 HP), extended Coyote Time, slower enemy movement.
  - Screen shake toggle, resolution scaling (1280x720, 1600x900, 1920x1080, Fullscreen), volume mixers.
- **Developer Debug Tools**:
  - `F1`: Debug HUD overlay (FPS, coordinates, velocity, state, entity counts, hitboxes).
  - `F2`: Quick Respawn.
  - `F3`: Toggle God Mode.
  - `F4`: Cycle Power-ups (None -> Ember -> Sky -> Shield -> Speed).
  - `F5`: Instant Level Skip.
  - `F6`: Reload Level.

---

## 🎮 Controls

### Keyboard
| Action | Key(s) |
|---|---|
| **Move Left / Right** | `A` / `D` or `Left` / `Right` Arrow |
| **Jump** | `Space` or `W` or `Up` Arrow |
| **Crouch / Slide** | `S` or `Down` Arrow |
| **Sprint / Fire Ember Blast** | `Left Shift` or `J` or `X` |
| **Interact / Select** | `Enter` or `E` or `Z` |
| **Pause / Back** | `ESC` |
| **Developer Debug Overlay** | `F1` |
| **God Mode (Debug)** | `F3` |
| **Cycle Power-Up (Debug)** | `F4` |

### Controller (XInput / SDL2 Gamepad)
| Action | Button |
|---|---|
| **Move** | Left Analog Stick or D-Pad |
| **Jump** | `A` (Xbox) / `Cross` (PlayStation) |
| **Sprint / Ability** | `B` / `X` (Xbox) / `Circle` / `Square` (PlayStation) |
| **Interact** | `Y` (Xbox) / `Triangle` (PlayStation) |
| **Pause** | `Start` / `Menu` |

---

## 🚀 How to Run

### Option 1: Standalone Windows Executable (No Python Required)
Run the pre-compiled executable directly:
```powershell
.\builds\windows\StarboundLostRealms\StarboundLostRealms.exe
```
Or double-click `Launch_Starbound.bat` in the workspace root.

### Option 2: Run from Python Source
Ensure dependencies are installed:
```powershell
py -m pip install pygame-ce pyinstaller pytest numpy
```
Run the launcher:
```powershell
py run_game.py
```

---

## 🧪 Running Automated Tests

Run the full pytest automated test suite covering player physics, coyote time, combat combos, power-up states, save serialization, and 24-level integrity:
```powershell
py -m pytest tests/ -v
```

---

## 📦 Project Structure

```
2D Pixel Game/
├── assets/                 # Bespoke procedural pixel art & synthesized audio
│   ├── sprites/            # Nova, enemies, bosses, items, particles
│   ├── tiles/              # Tilesets for Worlds 1 through 6
│   └── audio/              # SFX (.wav) & Music themes (.wav)
├── src/
│   ├── engine/             # Core engine, config, camera, audio, input, particles
│   ├── entities/           # Player (Nova), 6 enemies, bosses, collectibles, blocks
│   ├── world/              # Level loader, 24 level designs, parallax, world map
│   ├── ui/                 # HUD, Main menu, Pause, Settings, Game Over, Credits
│   └── systems/            # SaveManager (SHA256), Procedural Asset Generator
├── tests/                  # 20 Automated Pytest verification tests
├── builds/windows/         # Standalone StarboundLostRealms.exe distribution
├── docs/                   # ARCHITECTURE.md, LEVEL_DESIGN.md, BUILD.md
├── run_game.py             # Root launch script
└── README.md
```

---

## 📜 Credits & License

- **Game Design & Engineering**: Mohammad Yousuf Aftaab
- **Technology**: Python 3.13 & Pygame-CE 2.5.8 (SDL 2.32)
- **Art & Audio**: 100% Bespoke Original Procedural Generation
