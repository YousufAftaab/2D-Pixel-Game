"""
STARBOUND: THE LOST REALMS
Central Configuration and Game Constants
"""

import os

# -------------------------------------------------------------------------
# PATH CONFIGURATION
# -------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
TILES_DIR = os.path.join(ASSETS_DIR, "tiles")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
SFX_DIR = os.path.join(AUDIO_DIR, "sfx")
MUSIC_DIR = os.path.join(AUDIO_DIR, "music")
SAVE_DIR = os.path.join(BASE_DIR, "saves")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# -------------------------------------------------------------------------
# DISPLAY SETTINGS
# -------------------------------------------------------------------------
GAME_TITLE = "Starbound: The Lost Realms"
VERSION = "1.0.0"

# Virtual internal rendering resolution (16:9 pixel-perfect retro aesthetic)
VIRTUAL_WIDTH = 480
VIRTUAL_HEIGHT = 270
TARGET_FPS = 60

# Default window display dimensions
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 720

AVAILABLE_RESOLUTIONS = [
    (1280, 720),
    (1600, 900),
    (1920, 1080),
]

TILE_SIZE = 16

# -------------------------------------------------------------------------
# COLOR PALETTES (Original Stylized Sci-Fi / Fantasy)
# -------------------------------------------------------------------------
COLOR_BLACK = (10, 10, 18)
COLOR_WHITE = (245, 245, 255)
COLOR_TRANSPARENT = (0, 0, 0, 0)

# UI Colors
UI_BG_DARK = (16, 20, 36, 220)
UI_BORDER = (86, 122, 200)
UI_ACCENT_GOLD = (255, 200, 40)
UI_ACCENT_CYAN = (60, 220, 240)
UI_HEALTH_RED = (235, 60, 70)
UI_HEALTH_EMPTY = (70, 30, 40)
UI_TEXT_MUTED = (160, 175, 205)

# World Palettes
PALETTE_VERDANT = {
    "sky_top": (45, 85, 140),
    "sky_bottom": (120, 195, 180),
    "grass": (76, 175, 80),
    "dirt": (110, 75, 45),
    "stone": (90, 95, 110),
    "foliage": (46, 125, 50),
    "accent": (255, 220, 100)
}

PALETTE_SUNSCAR = {
    "sky_top": (180, 90, 50),
    "sky_bottom": (240, 180, 110),
    "grass": (220, 160, 60),
    "dirt": (175, 115, 40),
    "stone": (140, 95, 55),
    "foliage": (200, 130, 40),
    "accent": (255, 235, 140)
}

PALETTE_FROSTFALL = {
    "sky_top": (20, 40, 80),
    "sky_bottom": (110, 170, 210),
    "grass": (210, 240, 255),
    "dirt": (80, 110, 145),
    "stone": (130, 160, 190),
    "foliage": (160, 210, 240),
    "accent": (140, 240, 255)
}

PALETTE_SKYRUINS = {
    "sky_top": (30, 80, 160),
    "sky_bottom": (140, 200, 255),
    "grass": (100, 180, 220),
    "dirt": (160, 170, 195),
    "stone": (205, 215, 230),
    "foliage": (120, 215, 200),
    "accent": (255, 240, 160)
}

PALETTE_EMBER = {
    "sky_top": (40, 10, 20),
    "sky_bottom": (140, 40, 25),
    "grass": (220, 70, 30),
    "dirt": (70, 30, 35),
    "stone": (50, 40, 45),
    "foliage": (255, 110, 40),
    "accent": (255, 210, 50)
}

PALETTE_LOSTREALM = {
    "sky_top": (20, 10, 40),
    "sky_bottom": (90, 45, 130),
    "grass": (140, 80, 210),
    "dirt": (55, 35, 75),
    "stone": (95, 75, 120),
    "foliage": (180, 110, 255),
    "accent": (255, 220, 90)
}

# -------------------------------------------------------------------------
# PLAYER PHYSICS CONSTANTS (Tuned for extremely responsive, polished feel)
# -------------------------------------------------------------------------
PLAYER_WIDTH = 12
PLAYER_HEIGHT = 20

# Horizontal movement
PLAYER_ACCELERATION = 950.0       # px / s^2
PLAYER_DECELERATION = 1100.0      # px / s^2 (ground friction)
PLAYER_AIR_DECEL = 450.0          # px / s^2 (air friction)
PLAYER_MAX_RUN_SPEED = 145.0      # px / s
PLAYER_SPRINT_SPEED = 205.0       # px / s (sprint mode)
PLAYER_CROUCH_SPEED = 65.0        # px / s

# Vertical movement / Jump
GRAVITY = 1100.0                  # px / s^2 downward
FALL_GRAVITY = 1400.0             # extra snap downward when falling
TERMINAL_VELOCITY = 420.0         # px / s max fall speed
JUMP_VELOCITY = -370.0            # initial jump impulse
VARIABLE_JUMP_CUTOFF = -140.0     # min jump speed when releasing jump button early

# Forgiving platformer juice buffers
COYOTE_TIME = 0.12                # 120 ms grace after walking off edge
JUMP_BUFFER_TIME = 0.12           # 120 ms input buffer before landing

# Combat & Stats
PLAYER_DEFAULT_MAX_HEALTH = 3
INVULNERABILITY_TIME = 1.6        # seconds of i-frames when taking damage
DAMAGE_KNOCKBACK_X = 130.0
DAMAGE_KNOCKBACK_Y = -180.0
STOMP_BOUNCE_VELOCITY = -300.0

# Combos
COMBO_TIMEOUT = 1.8               # seconds between stomps to sustain combo
COMBO_POINTS = [100, 200, 400, 800, 1600, 3200]

# -------------------------------------------------------------------------
# POWER-UP CONSTANTS
# -------------------------------------------------------------------------
POWERUP_NONE = "NONE"
POWERUP_EMBER = "EMBER_CORE"      # Shoot celestial energy bolts
POWERUP_SKY = "SKY_CORE"          # Higher jumps & mid-air double jump
POWERUP_SHIELD = "SHIELD_CORE"    # Absorbs 1 extra hit
POWERUP_SPEED = "SPEED_CORE"      # Hyper speed + trail effect (15s duration)

SPEED_CORE_DURATION = 15.0
SPEED_CORE_SPEED_MULT = 1.45

# -------------------------------------------------------------------------
# GAME STATE ENUM
# -------------------------------------------------------------------------
STATE_BOOT = "BOOT"
STATE_MAIN_MENU = "MAIN_MENU"
STATE_INTRO = "INTRO"
STATE_WORLD_MAP = "WORLD_MAP"
STATE_LEVEL = "LEVEL"
STATE_PAUSE = "PAUSE"
STATE_LEVEL_COMPLETE = "LEVEL_COMPLETE"
STATE_GAME_OVER = "GAME_OVER"
STATE_VICTORY = "VICTORY"
STATE_SETTINGS = "SETTINGS"
STATE_CREDITS = "CREDITS"

# -------------------------------------------------------------------------
# DEFAULT USER SETTINGS
# -------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "resolution_index": 0,       # 1280x720
    "fullscreen": False,
    "vsync": True,
    "master_volume": 0.8,
    "music_volume": 0.7,
    "sfx_volume": 0.85,
    "screen_shake": True,
    "assist_mode": False,
    "assist_extra_health": False,
    "assist_extra_coyote": False,
    "assist_slower_enemies": False,
}
