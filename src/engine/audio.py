"""
STARBOUND: THE LOST REALMS
Audio Manager
Handles sound effect playback, multi-track looping music, volume management, and fallback.
"""

import os
import pygame
from src.engine.config import SFX_DIR, MUSIC_DIR


class AudioManager:
    def __init__(self, settings=None):
        self.enabled = False
        self.sounds = {}
        self.current_music = None
        self.music_paused = False

        self.master_volume = 0.8
        self.music_volume = 0.7
        self.sfx_volume = 0.85

        if settings:
            self.apply_settings(settings)

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.enabled = True
            self.load_sounds()
        except Exception as e:
            print(f"[Audio] Warning: Failed to initialize audio mixer: {e}")
            self.enabled = False

    def apply_settings(self, settings):
        self.master_volume = settings.get("master_volume", 0.8)
        self.music_volume = settings.get("music_volume", 0.7)
        self.sfx_volume = settings.get("sfx_volume", 0.85)

        if self.enabled:
            pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
            for s in self.sounds.values():
                s.set_volume(self.master_volume * self.sfx_volume)

    def load_sounds(self):
        if not self.enabled:
            return

        sound_files = [
            "jump", "double_jump", "land", "stomp", "shard", "crystal",
            "powerup", "shoot", "hurt", "death", "checkpoint",
            "menu_move", "menu_select"
        ]
        for name in sound_files:
            path = os.path.join(SFX_DIR, f"{name}.wav")
            if os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(self.master_volume * self.sfx_volume)
                    self.sounds[name] = snd
                except Exception as e:
                    print(f"[Audio] Could not load SFX {name}: {e}")

    def play_sfx(self, name):
        if not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd:
            # Find an open channel
            try:
                ch = pygame.mixer.find_channel()
                if ch:
                    ch.play(snd)
                else:
                    snd.play()
            except Exception:
                pass

    def play_music(self, track_name, loops=-1):
        if not self.enabled:
            return
        if self.current_music == track_name and pygame.mixer.music.get_busy():
            return

        music_file = os.path.join(MUSIC_DIR, f"{track_name}.wav")
        if not os.path.exists(music_file):
            print(f"[Audio] Music track {track_name} not found.")
            return

        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
            pygame.mixer.music.play(loops)
            self.current_music = track_name
            self.music_paused = False
        except Exception as e:
            print(f"[Audio] Error playing music {track_name}: {e}")

    def stop_music(self):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
            self.current_music = None
        except Exception:
            pass

    def pause_music(self):
        if not self.enabled or not pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.pause()
            self.music_paused = True
        except Exception:
            pass

    def resume_music(self):
        if not self.enabled or not self.music_paused:
            return
        try:
            pygame.mixer.music.unpause()
            self.music_paused = False
        except Exception:
            pass
