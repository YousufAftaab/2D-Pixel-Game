# Build & Packaging Guide: Starbound: The Lost Realms

## 1. Prerequisites

- **Operating System**: Windows 10 or Windows 11 (x64)
- **Python Runtime**: Python 3.10 to 3.13
- **Dependencies**:
  ```powershell
  py -m pip install pygame-ce pyinstaller pytest numpy
  ```

---

## 2. Generating Assets

The game generates all original pixel art and synthesized chiptune audio procedurally:
```powershell
py -m src.systems.generator
```
This populates:
- `assets/sprites/` (41 original sprite frames)
- `assets/tiles/` (21 world tilesets and interactive objects)
- `assets/audio/sfx/` (13 44.1 kHz WAV sound effects)
- `assets/audio/music/` (9 multi-track WAV compositions)

---

## 3. Running from Source

To run the game during development:
```powershell
py run_game.py
```

---

## 4. Building the Standalone Windows Executable

To compile a standalone, portable Windows distribution using PyInstaller:
```powershell
pyinstaller --noconfirm --onedir --windowed --name StarboundLostRealms --add-data "assets;assets" --distpath "builds/windows" run_game.py
```

After building:
1. The executable is located at:
   `builds/windows/StarboundLostRealms/StarboundLostRealms.exe`
2. Ensure the `assets/` directory is present alongside the binary or in `_internal/assets`.

---

## 5. Running Automated Verification Tests

To verify physics, combat combos, save/load serialization, and level integrity:
```powershell
py -m pytest tests/ -v
```

---

## 6. Troubleshooting

- **No sound / Audio device error**:
  - The game includes graceful audio fallback. If no audio output device is detected, `pygame.mixer` logs a warning and the game continues running without crashes.
- **Display Resolution Scaling**:
  - The game renders internally at 480x270 (16:9 pixel-perfect retro aesthetic) and scales smoothly using hardware SDL2 scaling to 1280x720, 1600x900, 1920x1080, and Fullscreen.
  - You can change resolution or toggle fullscreen in the in-game Settings menu (`Settings` -> `Resolution` / `Fullscreen`).
