"""
STARBOUND: THE LOST REALMS
Main Game Application Entry Point
"""

import sys
import os
import pygame

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.engine.config import (
    GAME_TITLE, VIRTUAL_WIDTH, VIRTUAL_HEIGHT, TARGET_FPS,
    AVAILABLE_RESOLUTIONS, SPRITES_DIR, TILES_DIR,
    STATE_MAIN_MENU, STATE_WORLD_MAP, STATE_LEVEL, STATE_PAUSE,
    STATE_LEVEL_COMPLETE, STATE_GAME_OVER, STATE_SETTINGS, STATE_CREDITS
)
from src.engine.input import InputManager
from src.engine.audio import AudioManager
from src.engine.camera import Camera
from src.engine.particles import ParticleSystem
from src.systems.save_manager import SaveManager
from src.systems.generator import generate_all_assets
from src.world.level import Level
from src.world.map import WorldMap
from src.ui.hud import HUD
from src.ui.menus import (
    MainMenu, PauseMenu, LevelCompleteMenu, GameOverMenu, SettingsMenu, ControlsMenu, CreditsMenu
)
from src.ui.debug import DebugManager


class Game:
    def __init__(self, headless=False):
        self.headless = headless

        # Attach to user's interactive 'Default' desktop on Windows
        if not self.headless and sys.platform == "win32":
            try:
                import ctypes
                h_desk = ctypes.windll.user32.OpenDesktopW("Default", 0, False, 0x01FF)
                if h_desk:
                    ctypes.windll.user32.SetThreadDesktop(h_desk)
            except Exception:
                pass

        pygame.init()
        pygame.font.init()

        # Check and ensure assets exist
        if not os.path.exists(os.path.join(SPRITES_DIR, "nova_idle_0.png")):
            generate_all_assets()

        # Save System & Settings
        self.save_manager = SaveManager()
        self.settings = self.save_manager.data["settings"]

        # Audio Manager
        self.audio = AudioManager(self.settings)

        # Input & Systems
        self.input_mgr = InputManager()
        self.camera = Camera(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        self.particles = ParticleSystem()

        # Fonts
        self.font = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.particles.set_font(self.font_small)

        # Window & Render surfaces
        self.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        if not self.headless:
            self._apply_display_mode()
            pygame.display.set_caption(GAME_TITLE)
        else:
            pygame.display.set_mode((1, 1), pygame.HIDDEN)

        # Assets cache
        self.assets = {"sprites": {}, "tiles": {}}
        self._load_assets()

        # UI & Menus
        self.hud = HUD(self.font, self.font_small)
        self.debug_mgr = DebugManager(self.font_small)
        self.menu_main = MainMenu(self.font, self.font_small)
        self.menu_pause = PauseMenu(self.font, self.font_small)
        self.menu_complete = LevelCompleteMenu(self.font, self.font_small)
        self.menu_gameover = GameOverMenu(self.font, self.font_small)
        self.menu_settings = SettingsMenu(self.font, self.font_small, self.settings)
        self.menu_controls = ControlsMenu(self.font, self.font_small)
        self.menu_credits = CreditsMenu(self.font, self.font_small)
        self.world_map = WorldMap(self.save_manager, self.audio)

        # Game State
        self.state = STATE_MAIN_MENU
        self.prev_state = STATE_MAIN_MENU
        self.current_level = None
        self.selected_level_id = "1-1"

        # Start menu BGM
        self.audio.play_music("theme_menu")

    def _apply_display_mode(self):
        res_idx = self.settings.get("resolution_index", 0)
        if res_idx >= len(AVAILABLE_RESOLUTIONS):
            res_idx = 0
        w, h = AVAILABLE_RESOLUTIONS[res_idx]
        is_fullscreen = self.settings.get("fullscreen", False)

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        flags = pygame.RESIZABLE
        if is_fullscreen:
            flags |= pygame.FULLSCREEN

        self.window = pygame.display.set_mode((w, h), flags)

        # Force window to foreground
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info().get("window")
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

    def _load_assets(self):
        # Load sprites
        if os.path.exists(SPRITES_DIR):
            for fname in os.listdir(SPRITES_DIR):
                if fname.endswith(".png"):
                    key = fname[:-4]
                    path = os.path.join(SPRITES_DIR, fname)
                    try:
                        self.assets["sprites"][key] = pygame.image.load(path).convert_alpha()
                    except Exception:
                        pass

        # Load tiles
        if os.path.exists(TILES_DIR):
            for fname in os.listdir(TILES_DIR):
                if fname.endswith(".png"):
                    key = fname[:-4]
                    path = os.path.join(TILES_DIR, fname)
                    try:
                        self.assets["tiles"][key] = pygame.image.load(path).convert_alpha()
                    except Exception:
                        pass

    def start_level(self, level_id):
        self.selected_level_id = level_id
        self.current_level = Level(
            level_id, self.settings, self.audio, self.particles, self.camera
        )
        self.state = STATE_LEVEL

    def run(self):
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap delta time to prevent physics tunnel/lag spikes

            # Handle SDL events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event.key)

            self.input_mgr.process_events(events)

            # Update Game Loop
            self.update(dt)

            # Render
            self.draw()

            if not self.headless:
                # Scale virtual surface to window
                scaled = pygame.transform.scale(self.virtual_surface, self.window.get_size())
                self.window.blit(scaled, (0, 0))
                pygame.display.flip()

        # Shutdown
        self.save_manager.save()
        pygame.quit()

    def _handle_keydown(self, key):
        # Menu Navigation Key Handling
        if self.state == STATE_MAIN_MENU:
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_main.navigate(-1, self.audio)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_main.navigate(1, self.audio)
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self._select_main_menu()

        elif self.state == STATE_WORLD_MAP:
            self.world_map.handle_key_nav(key)
            if key == pygame.K_ESCAPE:
                self.state = STATE_MAIN_MENU
                self.audio.play_music("theme_menu")

        elif self.state == STATE_PAUSE:
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_pause.navigate(-1, self.audio)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_pause.navigate(1, self.audio)
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self._select_pause_menu()
            elif key == pygame.K_ESCAPE:
                self.state = STATE_LEVEL
                self.audio.resume_music()

        elif self.state == STATE_LEVEL_COMPLETE:
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_complete.navigate(-1, self.audio)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_complete.navigate(1, self.audio)
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self._select_complete_menu()

        elif self.state == STATE_GAME_OVER:
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_gameover.navigate(-1, self.audio)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_gameover.navigate(1, self.audio)
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self._select_gameover_menu()

        elif self.state == STATE_SETTINGS:
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_settings.navigate(-1, self.audio)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_settings.navigate(1, self.audio)
            elif key in (pygame.K_LEFT, pygame.K_a):
                self.menu_settings.adjust_setting(-1, self.audio)
                if not self.headless:
                    self._apply_display_mode()
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.menu_settings.adjust_setting(1, self.audio)
                if not self.headless:
                    self._apply_display_mode()
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                if self.menu_settings.get_selected() == "Back":
                    self.state = self.prev_state
                    self.save_manager.save()
                else:
                    self.menu_settings.adjust_setting(1, self.audio)
                    if not self.headless:
                        self._apply_display_mode()
            elif key == pygame.K_ESCAPE:
                self.state = self.prev_state
                self.save_manager.save()

        elif self.state in (STATE_CREDITS, "CONTROLS"):
            if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.state = STATE_MAIN_MENU

        elif self.state == STATE_LEVEL:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PAUSE
                self.audio.pause_music()

    def _select_main_menu(self):
        sel = self.menu_main.get_selected()
        self.audio.play_sfx("menu_select")
        if sel == "Start Game":
            self.start_level("1-1")
        elif sel == "World Map":
            self.state = STATE_WORLD_MAP
        elif sel == "Settings":
            self.prev_state = STATE_MAIN_MENU
            self.state = STATE_SETTINGS
        elif sel == "Controls":
            self.state = "CONTROLS"
        elif sel == "Credits":
            self.state = STATE_CREDITS
        elif sel == "Quit":
            self.running = False

    def _select_pause_menu(self):
        sel = self.menu_pause.get_selected()
        self.audio.play_sfx("menu_select")
        if sel == "Resume":
            self.state = STATE_LEVEL
            self.audio.resume_music()
        elif sel == "Restart Level":
            self.start_level(self.selected_level_id)
        elif sel == "Settings":
            self.prev_state = STATE_PAUSE
            self.state = STATE_SETTINGS
        elif sel == "Exit to World Map":
            self.state = STATE_WORLD_MAP
            self.audio.play_music("theme_menu")
        elif sel == "Main Menu":
            self.state = STATE_MAIN_MENU
            self.audio.play_music("theme_menu")

    def _select_complete_menu(self):
        sel = self.menu_complete.get_selected()
        self.audio.play_sfx("menu_select")
        if sel == "Next Level":
            # Determine next level
            w, lvl = map(int, self.selected_level_id.split("-"))
            if lvl < 4:
                next_id = f"{w}-{lvl + 1}"
            elif w < 6:
                next_id = f"{w + 1}-1"
            else:
                # Victory Campaign Complete
                next_id = "1-1"
            self.start_level(next_id)
        elif sel == "Replay Level":
            self.start_level(self.selected_level_id)
        elif sel == "World Map":
            self.state = STATE_WORLD_MAP
            self.audio.play_music("theme_menu")

    def _select_gameover_menu(self):
        sel = self.menu_gameover.get_selected()
        self.audio.play_sfx("menu_select")
        if sel == "Respawn at Checkpoint":
            if self.current_level:
                self.current_level.player.respawn()
                self.state = STATE_LEVEL
        elif sel == "Restart Level":
            self.start_level(self.selected_level_id)
        elif sel == "World Map":
            self.state = STATE_WORLD_MAP
            self.audio.play_music("theme_menu")
        elif sel == "Main Menu":
            self.state = STATE_MAIN_MENU
            self.audio.play_music("theme_menu")

    def update(self, dt):
        self.camera.shake_enabled = self.settings.get("screen_shake", True)

        if self.state == STATE_MAIN_MENU:
            self.menu_main.update(dt)

        elif self.state == STATE_WORLD_MAP:
            target_level = self.world_map.update(dt, self.input_mgr)
            if target_level:
                self.start_level(target_level)

        elif self.state == STATE_LEVEL:
            if self.current_level:
                self.current_level.update(dt, self.input_mgr)
                self.particles.update(dt)

                # Process Debug key shortcuts
                self.debug_mgr.process_debug_inputs(
                    self.input_mgr, self.current_level, self.audio, self.particles
                )

                # Check level completion
                if self.current_level.completed:
                    # Save progression
                    self.save_manager.complete_level(
                        self.selected_level_id,
                        self.current_level.score,
                        self.current_level.time_elapsed,
                        self.current_level.shards_collected,
                        self.current_level.crystals_found
                    )
                    # Unlock next level
                    w, lvl = map(int, self.selected_level_id.split("-"))
                    if lvl < 4:
                        self.save_manager.unlock_level(f"{w}-{lvl + 1}")
                    elif w < 6:
                        self.save_manager.unlock_level(f"{w + 1}-1")
                    self.state = STATE_LEVEL_COMPLETE

                # Check player death game over
                elif self.current_level.player.state == "DEAD":
                    if self.current_level.player.rect.top > self.current_level.level_pixel_height + 30 or self.current_level.player.y > 600:
                        self.state = STATE_GAME_OVER

    def draw(self):
        if self.state == STATE_MAIN_MENU:
            self.menu_main.draw(self.virtual_surface)

        elif self.state == STATE_WORLD_MAP:
            self.world_map.draw(self.virtual_surface, self.font, self.font_small)

        elif self.state == STATE_LEVEL:
            if self.current_level:
                self.current_level.draw(self.virtual_surface, self.assets)
                self.hud.draw(self.virtual_surface, self.current_level.player, self.current_level, self.assets)
                self.debug_mgr.draw(
                    self.virtual_surface, self.clock, self.current_level.player, self.current_level, self.camera
                )

        elif self.state == STATE_PAUSE:
            if self.current_level:
                self.current_level.draw(self.virtual_surface, self.assets)
                self.hud.draw(self.virtual_surface, self.current_level.player, self.current_level, self.assets)
            self.menu_pause.draw(self.virtual_surface)

        elif self.state == STATE_LEVEL_COMPLETE:
            if self.current_level:
                self.current_level.draw(self.virtual_surface, self.assets)
            self.menu_complete.draw(self.virtual_surface, self.current_level)

        elif self.state == STATE_GAME_OVER:
            if self.current_level:
                self.current_level.draw(self.virtual_surface, self.assets)
            self.menu_gameover.draw(self.virtual_surface)

        elif self.state == STATE_SETTINGS:
            self.menu_settings.draw(self.virtual_surface)

        elif self.state == "CONTROLS":
            self.menu_controls.draw(self.virtual_surface)

        elif self.state == STATE_CREDITS:
            self.menu_credits.draw(self.virtual_surface)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
