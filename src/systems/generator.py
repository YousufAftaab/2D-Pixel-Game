"""
STARBOUND: THE LOST REALMS
Procedural Asset Generator
Generates original, high-quality pixel art sprites and synthesized chiptune audio files.
Zero copyrighted assets: 100% bespoke procedural generation.
"""

import os
import math
import struct
import wave
import numpy as np
import pygame
from src.engine.config import (
    ASSETS_DIR, SPRITES_DIR, TILES_DIR, SFX_DIR, MUSIC_DIR,
    TILE_SIZE, PALETTE_VERDANT, PALETTE_SUNSCAR, PALETTE_FROSTFALL,
    PALETTE_SKYRUINS, PALETTE_EMBER, PALETTE_LOSTREALM
)


def ensure_directories():
    for d in [ASSETS_DIR, SPRITES_DIR, TILES_DIR, SFX_DIR, MUSIC_DIR]:
        os.makedirs(d, exist_ok=True)


# -------------------------------------------------------------------------
# PIXEL ART DRAWING UTILITIES
# -------------------------------------------------------------------------
def create_surface(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    return surf


def set_pixels(surf, pixel_data, colormap):
    """
    pixel_data: list of strings where each character maps to a color in colormap.
    '.' or ' ' is transparent.
    """
    for y, row in enumerate(pixel_data):
        for x, char in enumerate(row):
            if char in colormap and char not in ('.', ' '):
                surf.set_at((x, y), colormap[char])


# -------------------------------------------------------------------------
# SPRITE GENERATION: NOVA (PROTAGONIST)
# Distinctive silhouette: Explorers jacket, celestial scarf, visor helmet, backpack
# -------------------------------------------------------------------------
def generate_nova_sprites():
    # Palette
    C_OUTLINE = (20, 20, 35)
    C_VISOR   = (80, 240, 255)
    C_VISOR_H = (180, 255, 255)
    C_HELMET  = (240, 240, 250)
    C_HELM_SH = (170, 180, 205)
    C_SUIT    = (35, 90, 210)
    C_SUIT_SH = (20, 50, 140)
    C_SCARF   = (255, 75, 95)
    C_SCARF_H = (255, 150, 165)
    C_PACK    = (255, 195, 35)
    C_BOOTS   = (40, 45, 60)

    cm = {
        '#': C_OUTLINE,
        'V': C_VISOR,
        'v': C_VISOR_H,
        'H': C_HELMET,
        'h': C_HELM_SH,
        'S': C_SUIT,
        's': C_SUIT_SH,
        'R': C_SCARF,
        'r': C_SCARF_H,
        'P': C_PACK,
        'B': C_BOOTS,
    }

    # 16x24 canvas for Nova
    frames = {}

    # 1. IDLE Frame 0
    idle_0 = [
        "....######......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#.....",
        "....#RRRR#......",
        "...#RRRRRR#r#...",
        "..#SS#SS#SS#r#..",
        "..#SS#PP#SS#.#..",
        "..#SS#PP#SS#....",
        "...#ssssss#.....",
        "...#SS##SS#.....",
        "...#SS##SS#.....",
        "...#ss##ss#.....",
        "...#BB##BB#.....",
        "...####..###....",
    ]
    s_idle0 = create_surface(16, 24)
    set_pixels(s_idle0, idle_0, cm)

    # 2. IDLE Frame 1 (Breathing / Scarf flutter)
    idle_1 = [
        "....######......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#.....",
        "....#RRRR##r....",
        "...#RRRRRR#rr#..",
        "..#SS#SS#SS#.#..",
        "..#SS#PP#SS#....",
        "..#SS#PP#SS#....",
        "...#ssssss#.....",
        "...#SS##SS#.....",
        "...#SS##SS#.....",
        "...#ss##ss#.....",
        "...#BB##BB#.....",
        "...####..###....",
    ]
    s_idle1 = create_surface(16, 24)
    set_pixels(s_idle1, idle_1, cm)
    frames["nova_idle_0"] = s_idle0
    frames["nova_idle_1"] = s_idle1

    # 3. RUN Frames (4 frames)
    run_0 = [
        "....######......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#r#...",
        "....#RRRR#rr#...",
        "..##SSSSSS###...",
        ".#SS#SS#SS#.....",
        ".#SS#PP#SS#.....",
        "..#ssssssss#....",
        "...#SS#..#SS#...",
        "..#SS#....#SS#..",
        "..#ss#....#ss#..",
        "..#BB#....#BB#..",
        "..###......###..",
        "................",
    ]
    run_1 = [
        "....######......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#r#...",
        "....#RRRR#rr#...",
        "...#SSSSSS#.....",
        "..#SS#PP#SS#....",
        "..#SS#PP#SS#....",
        "...#ssssss#.....",
        "....#SS#SS#.....",
        "....#SS#SS#.....",
        "....#ss#ss#.....",
        "....#BB#BB#.....",
        "....###.###.....",
        "................",
    ]
    run_2 = [
        "....######......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#r#...",
        "....#RRRR#rr#...",
        "..##SSSSSS###...",
        ".#SS#PP#SS#.....",
        ".#SS#PP#SS#.....",
        "..#ssssssss#....",
        "...#SS#..#SS#...",
        "..#SS#....#SS#..",
        "..#BB#....#BB#..",
        "..###......###..",
        "................",
        "................",
    ]
    run_3 = [
        "....######......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#r#...",
        "....#RRRR#rr#...",
        "...#SSSSSS#.....",
        "..#SS#PP#SS#....",
        "..#SS#PP#SS#....",
        "...#ssssss#.....",
        ".....#SSSS#.....",
        "....#SS##SS#....",
        "...#BB####BB#...",
        "...###....###...",
        "................",
        "................",
    ]
    for idx, r_data in enumerate([run_0, run_1, run_2, run_3]):
        s_run = create_surface(16, 24)
        set_pixels(s_run, r_data, cm)
        frames[f"nova_run_{idx}"] = s_run

    # 4. JUMP
    jump = [
        "....######......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#rrr#.",
        "....#RRRR#r#..#.",
        "...#SSSSSS#.....",
        "..#SS#PP#SS#....",
        "..#SS#PP#SS#....",
        "...#ssssss#.....",
        "..#SS#..#SS#....",
        ".#BB#....#BB#...",
        ".###......###...",
        "................",
        "................",
        "................",
    ]
    s_jump = create_surface(16, 24)
    set_pixels(s_jump, jump, cm)
    frames["nova_jump"] = s_jump

    # 5. FALL
    fall = [
        "....######...r#.",
        "...#HHHHHH#rrr#.",
        "..#HVVvvvVH#r#..",
        "..#HVVVVVVH#....",
        "...#hhhhhh#.....",
        "....#RRRR#......",
        "...#SSSSSS#.....",
        "..#SS#PP#SS#....",
        "..#SS#PP#SS#....",
        "...#ssssss#.....",
        "...#SS##SS#.....",
        "...#SS##SS#.....",
        "..#BB####BB#....",
        "..###....###....",
        "................",
        "................",
    ]
    s_fall = create_surface(16, 24)
    set_pixels(s_fall, fall, cm)
    frames["nova_fall"] = s_fall

    # 6. CROUCH
    crouch = [
        "................",
        "................",
        "....######......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#rr#..",
        "....#RRRR#..#...",
        "..##SSSSSS##....",
        ".#SS#PP#SS#.....",
        ".#SS#PP#SS#.....",
        "..#ssssssss#....",
        ".#BBBB##BBBB#...",
        ".#####..#####...",
        "................",
        "................",
    ]
    s_crouch = create_surface(16, 24)
    set_pixels(s_crouch, crouch, cm)
    frames["nova_crouch"] = s_crouch

    # 7. HURT (Flashes white/red)
    hurt = [
        "....######......",
        "...#HHHHHH#.....",
        "..#HrrRRRrH#....",
        "..#HRRRRRRH#....",
        "...#hhhhhh#.....",
        "....#RRRR#......",
        "...#SSSSSS#.....",
        "..#SS#PP#SS#....",
        "...#ssssss#.....",
        "...#SS##SS#.....",
        "...#BB##BB#.....",
        "...####..###....",
        "................",
        "................",
        "................",
        "................",
    ]
    s_hurt = create_surface(16, 24)
    set_pixels(s_hurt, hurt, cm)
    frames["nova_hurt"] = s_hurt

    # 8. VICTORY (Hands up, glowing scarf)
    victory_0 = [
        "..#......#......",
        "..#S#..#S#......",
        "...#HHHHHH#.....",
        "..#HVVvvvVH#....",
        "..#HVVVVVVH#....",
        "...#hhhhhh#r#...",
        "....#RRRR#rr#...",
        "...#SSSSSS#.#...",
        "..#SS#PP#SS#....",
        "..#SS#PP#SS#....",
        "...#ssssss#.....",
        "...#SS##SS#.....",
        "...#BB##BB#.....",
        "...####..###....",
        "................",
        "................",
    ]
    s_vic0 = create_surface(16, 24)
    set_pixels(s_vic0, victory_0, cm)
    frames["nova_victory"] = s_vic0

    for name, s in frames.items():
        pygame.image.save(s, os.path.join(SPRITES_DIR, f"{name}.png"))


# -------------------------------------------------------------------------
# SPRITE GENERATION: ENEMIES (6 ARCHETYPES)
# -------------------------------------------------------------------------
def generate_enemy_sprites():
    # 1. WALKER: "Prowler" (Robotic biomechanical bug)
    cm_w = {
        '#': (20, 20, 30),
        'B': (180, 50, 60),
        'b': (230, 90, 100),
        'E': (255, 230, 80),
        'L': (80, 90, 110),
    }
    w_0 = [
        "....######......",
        "...#bbbbbb#.....",
        "..#bBBBBBBb#....",
        ".#bBEEBBEEBb#...",
        ".#bBE#BBE#Bb#...",
        ".#bbBBBBBBbb#...",
        "..#bbbbbbbb#....",
        "...#L####L#.....",
        "..#L#....#L#....",
        "..##......##....",
    ]
    w_1 = [
        "....######......",
        "...#bbbbbb#.....",
        "..#bBBBBBBb#....",
        ".#bBEEBBEEBb#...",
        ".#bBE#BBE#Bb#...",
        ".#bbBBBBBBbb#...",
        "..#bbbbbbbb#....",
        "...#LL##LL#.....",
        "....##..##......",
        "................",
    ]
    sw0 = create_surface(16, 16)
    set_pixels(sw0, w_0, cm_w)
    sw1 = create_surface(16, 16)
    set_pixels(sw1, w_1, cm_w)
    pygame.image.save(sw0, os.path.join(SPRITES_DIR, "enemy_walker_0.png"))
    pygame.image.save(sw1, os.path.join(SPRITES_DIR, "enemy_walker_1.png"))

    # 2. FLYER: "Vesper" (Bat/Drone with glowing wing edges)
    cm_f = {
        '#': (20, 15, 35),
        'W': (120, 60, 180),
        'w': (190, 120, 255),
        'E': (255, 80, 100),
        'B': (70, 35, 110),
    }
    f_0 = [
        ".#............#.",
        "#w#..........#w#",
        "#Ww#..####..#wW#",
        ".#Ww##BBBB##wW#.",
        "..#W#BEEBEE#W#..",
        "...##BBBBBB##...",
        "....#BBBBBB#....",
        ".....######.....",
    ]
    f_1 = [
        "....########....",
        "..##wWWBBWWw##..",
        ".#wwW#BEEB#Www#.",
        "#wwW##BBBB##Www#",
        ".##...#BB#...##.",
        "......####......",
        "................",
        "................",
    ]
    sf0 = create_surface(16, 16)
    set_pixels(sf0, f_0, cm_f)
    sf1 = create_surface(16, 16)
    set_pixels(sf1, f_1, cm_f)
    pygame.image.save(sf0, os.path.join(SPRITES_DIR, "enemy_flyer_0.png"))
    pygame.image.save(sf1, os.path.join(SPRITES_DIR, "enemy_flyer_1.png"))

    # 3. CHARGER: "Crag" (Heavy armored rammer with horn)
    cm_c = {
        '#': (15, 15, 20),
        'A': (190, 100, 40),
        'a': (240, 160, 70),
        'H': (255, 220, 160),
        'E': (255, 40, 40),
        'T': (80, 80, 95),
    }
    c_0 = [
        "......######....",
        "....##aaaaaa##..",
        "...#aaAAAAAAaa#.",
        "..#aAAHEEHAAAAa#",
        ".#aAAHH##HHAAAA#",
        "#HHAAAAAAAAAAAA#",
        "#H##AAAAAAAAAA#.",
        ".###TT######TT#.",
        "...#TT#....#TT#.",
        "...####....####.",
    ]
    sc0 = create_surface(16, 16)
    set_pixels(sc0, c_0, cm_c)
    pygame.image.save(sc0, os.path.join(SPRITES_DIR, "enemy_charger_0.png"))
    pygame.image.save(sc0, os.path.join(SPRITES_DIR, "enemy_charger_1.png"))

    # 4. TURRET: "Pulse Sentry" (Crystal stationary turret)
    cm_t = {
        '#': (20, 25, 35),
        'B': (60, 70, 90),
        'C': (0, 220, 240),
        'c': (160, 255, 255),
        'E': (255, 60, 80),
    }
    t_0 = [
        "......####......",
        ".....#cccc#.....",
        "....#cCCCCc#....",
        "....#cCEECc#....",
        "....#cCCCCc#.....",
        ".....#cccc#.....",
        "....########....",
        "...#BBBBBBBB#...",
        "..#BBBBBBBBBB#..",
        "..############..",
    ]
    st0 = create_surface(16, 16)
    set_pixels(st0, t_0, cm_t)
    pygame.image.save(st0, os.path.join(SPRITES_DIR, "enemy_turret_0.png"))
    pygame.image.save(st0, os.path.join(SPRITES_DIR, "enemy_turret_1.png"))

    # 5. JUMPER: "Hopper" (Spring cricket/frog)
    cm_j = {
        '#': (15, 25, 15),
        'G': (50, 170, 70),
        'g': (120, 230, 110),
        'E': (255, 255, 100),
        'S': (180, 180, 190),
    }
    j_0 = [
        "....######......",
        "...#gggggg#.....",
        "..#gGGGGGGg#....",
        ".#gGEEGGEEGg#...",
        ".#ggGGGGGGgg#...",
        "..#gggggggg#....",
        "...#SS##SS#.....",
        "..#SS#..#SS#....",
        ".#SS#....#SS#...",
        ".###......###...",
    ]
    sj0 = create_surface(16, 16)
    set_pixels(sj0, j_0, cm_j)
    pygame.image.save(sj0, os.path.join(SPRITES_DIR, "enemy_jumper_0.png"))
    pygame.image.save(sj0, os.path.join(SPRITES_DIR, "enemy_jumper_1.png"))

    # 6. SHIELDED: "Vanguard" (Holds an energy barrier in front)
    cm_s = {
        '#': (20, 20, 25),
        'M': (80, 90, 110),
        'm': (130, 145, 170),
        'S': (80, 220, 255),
        's': (200, 250, 255),
        'E': (255, 180, 40),
    }
    sh_0 = [
        "...######..#s#..",
        "..#mmmmmm#.#s#..",
        ".#mMMMMMM#.#S#..",
        ".#mMEEMMM#.#S#..",
        ".#mMMMMMM#.#S#..",
        "..#mmmmmm#.#S#..",
        "..#MM##MM#.#S#..",
        "..#MM##MM#.#s#..",
        "..####.###.#s#..",
        "...........###..",
    ]
    ssh0 = create_surface(16, 16)
    set_pixels(ssh0, sh_0, cm_s)
    pygame.image.save(ssh0, os.path.join(SPRITES_DIR, "enemy_shielded_0.png"))
    pygame.image.save(ssh0, os.path.join(SPRITES_DIR, "enemy_shielded_1.png"))


# -------------------------------------------------------------------------
# SPRITE GENERATION: BOSSES
# -------------------------------------------------------------------------
def generate_boss_sprites():
    # 1. WORLD 1 BOSS: "Ancient Sentinel" (32x32 Stone Golem)
    s_boss1 = create_surface(32, 32)
    cm_b1 = {
        '#': (25, 30, 35),
        'S': (110, 120, 130),
        's': (160, 175, 185),
        'M': (60, 130, 70),   # Moss
        'C': (0, 240, 255),    # Glowing Core
        'c': (180, 255, 255),
    }
    b1_data = [
        ".........##############.........",
        ".......##ssssssssssssss##.......",
        "......#ssSSSSSSSSSSSSSSss#......",
        ".....#ssSSMMMMSSSSMMMMSSss#.....",
        "....#ssSSMMMMMMSSMMMMMMSSss#....",
        "....#ssSSMMcCMMSSMMcCMMSSss#....",
        "....#ssSSMMCCMMSSMMCCMMSSss#....",
        "....#ssSSSSSSSSSSSSSSSSSSss#....",
        ".....#ssSSSSSSSSSSSSSSSSss#.....",
        "......##ssssssssssssssss##......",
        "....####SSSSSSSSSSSSSSSS####....",
        "..##ssss#ssssssssssssss#ssss##..",
        ".#ssSSSS#sSSSSSSSSSSSSs#SSSSss#.",
        ".#sSSSSs#sSSScCCCCsSSSs#sSSSSs#.",
        ".#sSSSSs#sSSCCCCCCsSSSs#sSSSSs#.",
        ".#sSSSSs#sSSScCCCCsSSSs#sSSSSs#.",
        ".#ssSSSS#sSSSSSSSSSSSSs#SSSSss#.",
        "..##ssss#ssssssssssssss#ssss##..",
        "....####SSSSSSSSSSSSSSSS####....",
        ".......#ssssssssssssssss#.......",
        ".......#sSSSSs####sSSSSs#.......",
        ".......#sSSSSs#..#sSSSSs#.......",
        ".......#sSSSSs#..#sSSSSs#.......",
        ".......#ssssss#..#ssssss#.......",
        "........######....######........",
    ]
    set_pixels(s_boss1, b1_data, cm_b1)
    pygame.image.save(s_boss1, os.path.join(SPRITES_DIR, "boss_sentinel.png"))

    # 2. FINAL BOSS: "The Warden of the Lost Realm" (48x48 Multi-Phase Boss)
    cm_w = {
        '#': (15, 10, 25),
        'V': (90, 45, 140),    # Void mantle
        'v': (145, 80, 210),
        'G': (240, 195, 50),   # Astral Gold
        'g': (255, 235, 140),
        'A': (60, 220, 255),   # Astral Core
        'a': (180, 250, 255),
        'R': (255, 60, 80),    # Enraged eyes
    }
    s_warden1 = create_surface(48, 48)
    s_warden2 = create_surface(48, 48)

    # Base Warden layout
    # Center aura + Wings + Core
    pygame.draw.circle(s_warden1, (60, 20, 90), (24, 24), 20)
    pygame.draw.circle(s_warden1, (130, 60, 190), (24, 24), 16)
    pygame.draw.circle(s_warden1, (240, 195, 50), (24, 24), 10)
    pygame.draw.circle(s_warden1, (60, 220, 255), (24, 24), 6)
    # Eyes
    pygame.draw.circle(s_warden1, (255, 255, 255), (20, 18), 3)
    pygame.draw.circle(s_warden1, (255, 255, 255), (28, 18), 3)
    pygame.draw.circle(s_warden1, (20, 10, 40), (20, 18), 1)
    pygame.draw.circle(s_warden1, (20, 10, 40), (28, 18), 1)
    # Crown / Halo
    pygame.draw.polygon(s_warden1, (255, 215, 70), [(12, 10), (24, 2), (36, 10), (30, 14), (24, 8), (18, 14)])
    # Astral blade wings
    pygame.draw.polygon(s_warden1, (60, 220, 255), [(4, 12), (18, 22), (12, 34)])
    pygame.draw.polygon(s_warden1, (60, 220, 255), [(44, 12), (30, 22), (36, 34)])

    # Enraged Phase (Crimson & Purple)
    pygame.draw.circle(s_warden2, (100, 10, 30), (24, 24), 22)
    pygame.draw.circle(s_warden2, (180, 30, 60), (24, 24), 18)
    pygame.draw.circle(s_warden2, (255, 70, 40), (24, 24), 12)
    pygame.draw.circle(s_warden2, (255, 230, 80), (24, 24), 7)
    pygame.draw.circle(s_warden2, (255, 20, 20), (20, 18), 3)
    pygame.draw.circle(s_warden2, (255, 20, 20), (28, 18), 3)
    pygame.draw.polygon(s_warden2, (255, 70, 40), [(10, 8), (24, 0), (38, 8), (32, 12), (24, 6), (16, 12)])
    pygame.draw.polygon(s_warden2, (255, 80, 50), [(0, 8), (16, 22), (8, 38)])
    pygame.draw.polygon(s_warden2, (255, 80, 50), [(48, 8), (32, 22), (40, 38)])

    pygame.image.save(s_warden1, os.path.join(SPRITES_DIR, "boss_warden_1.png"))
    pygame.image.save(s_warden2, os.path.join(SPRITES_DIR, "boss_warden_2.png"))


# -------------------------------------------------------------------------
# SPRITE GENERATION: COLLECTIBLES & POWERUPS
# -------------------------------------------------------------------------
def generate_items_and_tiles():
    # 1. STAR SHARD (Common collectible)
    for frame in range(4):
        s_shard = create_surface(16, 16)
        angle = frame * (math.pi / 2.0) / 4.0
        pts = []
        cx, cy = 8, 8
        for i in range(8):
            r = 7 if (i % 2 == 0) else 3
            a = angle + i * (math.pi / 4.0)
            pts.append((cx + int(math.cos(a) * r), cy + int(math.sin(a) * r)))
        pygame.draw.polygon(s_shard, (255, 215, 0), pts)
        pygame.draw.polygon(s_shard, (255, 255, 200), pts, 1)
        s_shard.set_at((cx, cy), (255, 255, 255))
        pygame.image.save(s_shard, os.path.join(SPRITES_DIR, f"star_shard_{frame}.png"))

    # 2. ASTRAL CRYSTAL (Secret collectible)
    s_cryst = create_surface(16, 16)
    c_pts = [(8, 1), (14, 6), (11, 14), (5, 14), (2, 6)]
    pygame.draw.polygon(s_cryst, (60, 230, 255), c_pts)
    pygame.draw.polygon(s_cryst, (190, 255, 255), [(8, 1), (11, 6), (8, 14), (5, 6)])
    pygame.draw.polygon(s_cryst, (20, 40, 80), c_pts, 1)
    pygame.image.save(s_cryst, os.path.join(SPRITES_DIR, "astral_crystal.png"))

    # 3. POWER-UP CORES
    # Ember Core (Fire projectile)
    s_ember = create_surface(16, 16)
    pygame.draw.circle(s_ember, (240, 80, 20), (8, 8), 7)
    pygame.draw.circle(s_ember, (255, 190, 40), (8, 8), 5)
    pygame.draw.circle(s_ember, (255, 255, 200), (8, 8), 2)
    pygame.draw.circle(s_ember, (15, 15, 20), (8, 8), 7, 1)
    pygame.image.save(s_ember, os.path.join(SPRITES_DIR, "powerup_ember.png"))

    # Sky Core (High jump / Double jump)
    s_sky = create_surface(16, 16)
    pygame.draw.circle(s_sky, (40, 160, 255), (8, 8), 7)
    pygame.draw.circle(s_sky, (140, 230, 255), (8, 8), 5)
    pygame.draw.circle(s_sky, (255, 255, 255), (8, 8), 2)
    pygame.draw.circle(s_sky, (15, 15, 20), (8, 8), 7, 1)
    pygame.image.save(s_sky, os.path.join(SPRITES_DIR, "powerup_sky.png"))

    # Shield Core (Extra hit protection)
    s_shield = create_surface(16, 16)
    pygame.draw.circle(s_shield, (70, 230, 120), (8, 8), 7)
    pygame.draw.circle(s_shield, (180, 255, 200), (8, 8), 5)
    pygame.draw.circle(s_shield, (255, 255, 255), (8, 8), 2)
    pygame.draw.circle(s_shield, (15, 15, 20), (8, 8), 7, 1)
    pygame.image.save(s_shield, os.path.join(SPRITES_DIR, "powerup_shield.png"))

    # Speed Core (Boosted speed)
    s_spd = create_surface(16, 16)
    pygame.draw.circle(s_spd, (255, 220, 40), (8, 8), 7)
    pygame.draw.circle(s_spd, (255, 250, 170), (8, 8), 5)
    pygame.draw.circle(s_spd, (255, 255, 255), (8, 8), 2)
    pygame.draw.circle(s_spd, (15, 15, 20), (8, 8), 7, 1)
    pygame.image.save(s_spd, os.path.join(SPRITES_DIR, "powerup_speed.png"))

    # Health Restore Orb (Heart/Cell)
    s_hp = create_surface(16, 16)
    pygame.draw.circle(s_hp, (240, 50, 70), (5, 6), 4)
    pygame.draw.circle(s_hp, (240, 50, 70), (11, 6), 4)
    pygame.draw.polygon(s_hp, (240, 50, 70), [(2, 7), (14, 7), (8, 14)])
    pygame.draw.circle(s_hp, (255, 180, 190), (5, 5), 1)
    pygame.image.save(s_hp, os.path.join(SPRITES_DIR, "item_heart.png"))

    # 4. TILES AND INTERACTIVE BLOCKS
    # Prism/Reward Block (cycling rune block)
    s_prism = create_surface(TILE_SIZE, TILE_SIZE)
    s_prism.fill((210, 160, 40))
    pygame.draw.rect(s_prism, (255, 220, 90), (1, 1, 14, 14))
    pygame.draw.rect(s_prism, (140, 95, 20), (0, 0, 16, 16), 1)
    # Central star emblem
    pygame.draw.circle(s_prism, (255, 255, 255), (8, 8), 3)
    pygame.draw.line(s_prism, (200, 140, 20), (8, 2), (8, 14))
    pygame.draw.line(s_prism, (200, 140, 20), (2, 8), (14, 8))
    pygame.image.save(s_prism, os.path.join(TILES_DIR, "block_prism.png"))

    # Breakable Block (Chiseled stone with cracks)
    s_break = create_surface(TILE_SIZE, TILE_SIZE)
    s_break.fill((120, 110, 100))
    pygame.draw.rect(s_break, (150, 140, 130), (1, 1, 14, 14))
    pygame.draw.rect(s_break, (60, 55, 50), (0, 0, 16, 16), 1)
    # Cracks
    pygame.draw.line(s_break, (60, 55, 50), (3, 3), (8, 7), 1)
    pygame.draw.line(s_break, (60, 55, 50), (8, 7), (13, 5), 1)
    pygame.draw.line(s_break, (60, 55, 50), (8, 7), (8, 13), 1)
    pygame.image.save(s_break, os.path.join(TILES_DIR, "block_breakable.png"))

    # Checkpoint (Inactive / Active)
    s_cp_off = create_surface(16, 24)
    pygame.draw.rect(s_cp_off, (70, 75, 90), (6, 4, 4, 18))
    pygame.draw.rect(s_cp_off, (40, 45, 55), (4, 20, 8, 4))
    pygame.draw.circle(s_cp_off, (100, 110, 130), (8, 4), 4)
    pygame.image.save(s_cp_off, os.path.join(SPRITES_DIR, "checkpoint_off.png"))

    s_cp_on = create_surface(16, 24)
    pygame.draw.rect(s_cp_on, (80, 180, 220), (6, 4, 4, 18))
    pygame.draw.rect(s_cp_on, (40, 45, 55), (4, 20, 8, 4))
    pygame.draw.circle(s_cp_on, (255, 230, 80), (8, 4), 5)
    pygame.draw.circle(s_cp_on, (255, 255, 255), (8, 4), 2)
    pygame.image.save(s_cp_on, os.path.join(SPRITES_DIR, "checkpoint_on.png"))

    # Goal / Exit Portal (16x32)
    s_portal = create_surface(16, 32)
    pygame.draw.ellipse(s_portal, (80, 40, 160), (1, 1, 14, 30))
    pygame.draw.ellipse(s_portal, (140, 80, 240), (3, 3, 10, 26))
    pygame.draw.ellipse(s_portal, (200, 160, 255), (5, 6, 6, 20))
    pygame.draw.ellipse(s_portal, (255, 255, 255), (7, 10, 2, 12))
    pygame.image.save(s_portal, os.path.join(SPRITES_DIR, "portal_exit.png"))

    # Hazard Spikes
    s_spikes = create_surface(TILE_SIZE, TILE_SIZE)
    spike_pts = [(0, 16), (4, 4), (8, 16), (12, 4), (16, 16)]
    pygame.draw.polygon(s_spikes, (190, 50, 60), spike_pts)
    pygame.draw.polygon(s_spikes, (240, 120, 130), spike_pts, 1)
    pygame.image.save(s_spikes, os.path.join(TILES_DIR, "hazard_spikes.png"))

    # Projectiles
    s_proj_nova = create_surface(8, 8)
    pygame.draw.circle(s_proj_nova, (255, 160, 40), (4, 4), 4)
    pygame.draw.circle(s_proj_nova, (255, 255, 200), (4, 4), 2)
    pygame.image.save(s_proj_nova, os.path.join(SPRITES_DIR, "proj_nova.png"))

    s_proj_enemy = create_surface(8, 8)
    pygame.draw.circle(s_proj_enemy, (240, 50, 90), (4, 4), 4)
    pygame.draw.circle(s_proj_enemy, (255, 220, 230), (4, 4), 2)
    pygame.image.save(s_proj_enemy, os.path.join(SPRITES_DIR, "proj_enemy.png"))

    # 5. WORLD TILESETS (6 Worlds)
    palettes = {
        "verdant": PALETTE_VERDANT,
        "sunscar": PALETTE_SUNSCAR,
        "frostfall": PALETTE_FROSTFALL,
        "skyruins": PALETTE_SKYRUINS,
        "ember": PALETTE_EMBER,
        "lostrealm": PALETTE_LOSTREALM,
    }

    for w_name, p in palettes.items():
        # Top grass/surface tile
        s_top = create_surface(TILE_SIZE, TILE_SIZE)
        s_top.fill(p["dirt"])
        pygame.draw.rect(s_top, p["grass"], (0, 0, 16, 5))
        pygame.draw.line(s_top, p["accent"], (0, 0), (16, 0))
        pygame.draw.rect(s_top, (20, 20, 30), (0, 0, 16, 16), 1)
        pygame.image.save(s_top, os.path.join(TILES_DIR, f"tile_{w_name}_top.png"))

        # Middle dirt/solid tile
        s_mid = create_surface(TILE_SIZE, TILE_SIZE)
        s_mid.fill(p["dirt"])
        pygame.draw.rect(s_mid, (p["dirt"][0] + 15, p["dirt"][1] + 15, p["dirt"][2] + 15), (2, 2, 12, 12))
        pygame.draw.rect(s_mid, (20, 20, 30), (0, 0, 16, 16), 1)
        pygame.image.save(s_mid, os.path.join(TILES_DIR, f"tile_{w_name}_mid.png"))

        # Stone/Platform tile
        s_plat = create_surface(TILE_SIZE, TILE_SIZE)
        s_plat.fill(p["stone"])
        pygame.draw.rect(s_plat, (p["stone"][0] + 25, p["stone"][1] + 25, p["stone"][2] + 25), (1, 1, 14, 3))
        pygame.draw.rect(s_plat, (20, 20, 30), (0, 0, 16, 16), 1)
        pygame.image.save(s_plat, os.path.join(TILES_DIR, f"tile_{w_name}_plat.png"))


# -------------------------------------------------------------------------
# PROCEDURAL AUDIO SYNTHESIS VIA NUMPY & WAVE
# Authentic retro sound effects + rich chiptune melodic loops
# -------------------------------------------------------------------------
SAMPLE_RATE = 44100


def save_wav(filename, samples, channels=1):
    """
    Saves float numpy array (-1.0 to 1.0) as 16-bit PCM WAV.
    """
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 32767).astype(np.int16)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_samples.tobytes())


def synth_square(freq, duration, duty=0.5):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    phase = (freq * t) % 1.0
    return np.where(phase < duty, 0.4, -0.4)


def synth_triangle(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    phase = (freq * t) % 1.0
    return 2.0 * np.abs(2.0 * (phase - np.floor(phase + 0.5))) - 1.0


def synth_noise(duration):
    return np.random.uniform(-0.4, 0.4, int(SAMPLE_RATE * duration))


def apply_envelope(samples, attack_sec, decay_sec, sustain_level, release_sec):
    n = len(samples)
    att_len = int(attack_sec * SAMPLE_RATE)
    dec_len = int(decay_sec * SAMPLE_RATE)
    rel_len = int(release_sec * SAMPLE_RATE)
    sus_len = max(0, n - att_len - dec_len - rel_len)

    env = []
    if att_len > 0:
        env.append(np.linspace(0.0, 1.0, att_len))
    if dec_len > 0:
        env.append(np.linspace(1.0, sustain_level, dec_len))
    if sus_len > 0:
        env.append(np.full(sus_len, sustain_level))
    if rel_len > 0:
        env.append(np.linspace(sustain_level, 0.0, rel_len))

    full_env = np.concatenate(env)
    if len(full_env) < n:
        full_env = np.pad(full_env, (0, n - len(full_env)), 'constant')
    elif len(full_env) > n:
        full_env = full_env[:n]

    return samples * full_env


def generate_sfx():
    # 1. JUMP: Ascending pitch sweep
    t = np.linspace(0, 0.16, int(SAMPLE_RATE * 0.16), endpoint=False)
    freq = np.linspace(180, 520, len(t))
    phase = np.cumsum(freq) / SAMPLE_RATE
    s_jump = 0.4 * np.sign(np.sin(2 * np.pi * phase))
    s_jump = apply_envelope(s_jump, 0.01, 0.04, 0.6, 0.11)
    save_wav(os.path.join(SFX_DIR, "jump.wav"), s_jump)

    # 2. DOUBLE JUMP: Higher 2-tone chirp
    t = np.linspace(0, 0.18, int(SAMPLE_RATE * 0.18), endpoint=False)
    freq = np.linspace(420, 880, len(t))
    phase = np.cumsum(freq) / SAMPLE_RATE
    s_djump = 0.4 * np.sin(2 * np.pi * phase) + 0.2 * np.sign(np.sin(4 * np.pi * phase))
    s_djump = apply_envelope(s_djump, 0.01, 0.05, 0.5, 0.12)
    save_wav(os.path.join(SFX_DIR, "double_jump.wav"), s_djump)

    # 3. LAND: Quick thud + noise burst
    t = np.linspace(0, 0.09, int(SAMPLE_RATE * 0.09), endpoint=False)
    thud = 0.5 * np.sin(2 * np.pi * 90 * t)
    noise = synth_noise(0.09) * 0.3
    s_land = apply_envelope(thud + noise, 0.005, 0.02, 0.3, 0.065)
    save_wav(os.path.join(SFX_DIR, "land.wav"), s_land)

    # 4. STOMP: Crunch + ascending punch
    t = np.linspace(0, 0.15, int(SAMPLE_RATE * 0.15), endpoint=False)
    f_crunch = np.linspace(350, 110, len(t))
    phase = np.cumsum(f_crunch) / SAMPLE_RATE
    crunch = 0.4 * np.sign(np.sin(2 * np.pi * phase))
    pop = 0.3 * np.sin(2 * np.pi * np.linspace(400, 750, len(t)) * t)
    s_stomp = apply_envelope(crunch + pop + synth_noise(0.15) * 0.2, 0.005, 0.03, 0.4, 0.11)
    save_wav(os.path.join(SFX_DIR, "stomp.wav"), s_stomp)

    # 5. STAR SHARD: Crisp dual-tone crystalline bell (E6 + B6)
    t = np.linspace(0, 0.22, int(SAMPLE_RATE * 0.22), endpoint=False)
    tone1 = 0.35 * np.sin(2 * np.pi * 1318.5 * t)
    tone2 = 0.25 * np.sin(2 * np.pi * 1975.5 * t)
    s_shard = apply_envelope(tone1 + tone2, 0.005, 0.04, 0.4, 0.175)
    save_wav(os.path.join(SFX_DIR, "shard.wav"), s_shard)

    # 6. ASTRAL CRYSTAL: Triumphant 3-chord shimmer
    t = np.linspace(0, 0.45, int(SAMPLE_RATE * 0.45), endpoint=False)
    c1 = 0.3 * np.sin(2 * np.pi * 880 * t)
    c2 = 0.3 * np.sin(2 * np.pi * 1108 * t)
    c3 = 0.3 * np.sin(2 * np.pi * 1320 * t)
    c4 = 0.2 * np.sin(2 * np.pi * 1760 * t)
    s_cryst = apply_envelope(c1 + c2 + c3 + c4, 0.01, 0.1, 0.5, 0.34)
    save_wav(os.path.join(SFX_DIR, "crystal.wav"), s_cryst)

    # 7. POWERUP: 4-note ascending fanfare
    chunks = []
    freqs = [392, 523, 659, 784]  # G4, C5, E5, G5
    for f in freqs:
        t_note = np.linspace(0, 0.08, int(SAMPLE_RATE * 0.08), endpoint=False)
        note = 0.4 * np.sign(np.sin(2 * np.pi * f * t_note)) + 0.2 * np.sin(4 * np.pi * f * t_note)
        chunks.append(apply_envelope(note, 0.005, 0.02, 0.7, 0.055))
    s_pwr = np.concatenate(chunks)
    save_wav(os.path.join(SFX_DIR, "powerup.wav"), s_pwr)

    # 8. SHOOT: Snappy laser zap
    t = np.linspace(0, 0.14, int(SAMPLE_RATE * 0.14), endpoint=False)
    freq = np.linspace(1200, 200, len(t))
    phase = np.cumsum(freq) / SAMPLE_RATE
    s_shoot = 0.4 * np.sin(2 * np.pi * phase) + 0.2 * np.sign(np.sin(4 * np.pi * phase))
    s_shoot = apply_envelope(s_shoot, 0.005, 0.02, 0.5, 0.115)
    save_wav(os.path.join(SFX_DIR, "shoot.wav"), s_shoot)

    # 9. HURT: Jarring crunch
    t = np.linspace(0, 0.25, int(SAMPLE_RATE * 0.25), endpoint=False)
    f_hurt = np.linspace(320, 80, len(t))
    phase = np.cumsum(f_hurt) / SAMPLE_RATE
    s_hurt = 0.5 * np.sign(np.sin(2 * np.pi * phase)) + synth_noise(0.25) * 0.35
    s_hurt = apply_envelope(s_hurt, 0.005, 0.04, 0.4, 0.205)
    save_wav(os.path.join(SFX_DIR, "hurt.wav"), s_hurt)

    # 10. DEATH: Descending solemn chime
    t = np.linspace(0, 0.6, int(SAMPLE_RATE * 0.6), endpoint=False)
    f_d = np.linspace(440, 110, len(t))
    phase = np.cumsum(f_d) / SAMPLE_RATE
    s_death = 0.4 * np.sin(2 * np.pi * phase) + 0.2 * synth_triangle(130, 0.6)
    s_death = apply_envelope(s_death, 0.02, 0.1, 0.4, 0.48)
    save_wav(os.path.join(SFX_DIR, "death.wav"), s_death)

    # 11. CHECKPOINT: Ethereal harmonic chime
    t = np.linspace(0, 0.5, int(SAMPLE_RATE * 0.5), endpoint=False)
    h1 = 0.35 * np.sin(2 * np.pi * 659.2 * t)
    h2 = 0.35 * np.sin(2 * np.pi * 987.7 * t)
    h3 = 0.25 * np.sin(2 * np.pi * 1318.5 * t)
    s_cp = apply_envelope(h1 + h2 + h3, 0.01, 0.1, 0.6, 0.39)
    save_wav(os.path.join(SFX_DIR, "checkpoint.wav"), s_cp)

    # 12. UI CLICKS
    t = np.linspace(0, 0.04, int(SAMPLE_RATE * 0.04), endpoint=False)
    s_ui_move = apply_envelope(0.3 * np.sin(2 * np.pi * 600 * t), 0.005, 0.01, 0.3, 0.025)
    save_wav(os.path.join(SFX_DIR, "menu_move.wav"), s_ui_move)

    t = np.linspace(0, 0.08, int(SAMPLE_RATE * 0.08), endpoint=False)
    s_ui_sel = apply_envelope(0.35 * np.sin(2 * np.pi * 900 * t), 0.005, 0.02, 0.5, 0.055)
    save_wav(os.path.join(SFX_DIR, "menu_select.wav"), s_ui_sel)


def generate_music():
    """
    Generates dynamic multi-track looping chiptune soundtracks.
    """
    def note_to_freq(note_idx):
        # A4 = 440 Hz = note index 69
        return 440.0 * (2.0 ** ((note_idx - 69) / 12.0))

    # Notes indices (MIDI equivalents)
    # C4 = 60, D4 = 62, E4 = 64, F4 = 65, G4 = 67, A4 = 69, B4 = 71, C5 = 72
    tracks = {
        "theme_menu": {
            "bpm": 115,
            "melody": [64, 67, 71, 72, 71, 67, 64, 62, 60, 64, 67, 69, 67, 64, 62, 60],
            "bass":   [36, 36, 43, 43, 41, 41, 38, 38, 36, 36, 43, 43, 41, 41, 36, 36],
        },
        "theme_verdant": {
            "bpm": 130,
            "melody": [60, 64, 67, 72, 69, 67, 64, 60, 62, 65, 69, 71, 67, 65, 64, 62],
            "bass":   [48, 48, 48, 48, 53, 53, 53, 53, 50, 50, 50, 50, 43, 43, 43, 43],
        },
        "theme_sunscar": {
            "bpm": 125,
            "melody": [57, 60, 64, 65, 64, 60, 57, 56, 57, 61, 64, 67, 65, 64, 61, 57],
            "bass":   [45, 45, 45, 45, 45, 45, 44, 44, 45, 45, 45, 45, 46, 46, 45, 45],
        },
        "theme_frostfall": {
            "bpm": 110,
            "melody": [67, 72, 76, 74, 71, 67, 69, 71, 72, 74, 76, 79, 76, 74, 72, 67],
            "bass":   [48, 48, 55, 55, 53, 53, 50, 50, 48, 48, 55, 55, 53, 53, 48, 48],
        },
        "theme_skyruins": {
            "bpm": 135,
            "melody": [60, 67, 65, 69, 67, 72, 71, 76, 72, 69, 67, 64, 62, 65, 64, 60],
            "bass":   [36, 48, 41, 53, 43, 55, 36, 48, 41, 53, 43, 55, 36, 48, 43, 55],
        },
        "theme_ember": {
            "bpm": 140,
            "melody": [58, 61, 65, 64, 61, 58, 60, 61, 65, 68, 67, 65, 64, 61, 60, 58],
            "bass":   [34, 34, 34, 34, 37, 37, 37, 37, 34, 34, 34, 34, 33, 33, 33, 33],
        },
        "theme_lostrealm": {
            "bpm": 132,
            "melody": [60, 63, 67, 70, 68, 67, 63, 62, 60, 65, 68, 72, 70, 68, 67, 63],
            "bass":   [36, 36, 44, 44, 41, 41, 38, 38, 36, 36, 44, 44, 41, 41, 36, 36],
        },
        "theme_boss": {
            "bpm": 148,
            "melody": [60, 60, 72, 60, 63, 63, 75, 63, 65, 65, 77, 65, 67, 67, 79, 67],
            "bass":   [36, 36, 36, 36, 39, 39, 39, 39, 41, 41, 41, 41, 43, 43, 43, 43],
        },
        "theme_victory": {
            "bpm": 128,
            "melody": [60, 64, 67, 72, 72, 72, 74, 76, 76, 76, 74, 72, 76, 79, 84, 84],
            "bass":   [48, 48, 48, 48, 53, 53, 53, 53, 50, 50, 50, 50, 55, 55, 48, 48],
        },
    }

    for track_name, data in tracks.items():
        bpm = data["bpm"]
        beat_dur = 60.0 / bpm
        note_dur = beat_dur * 0.5  # eighth notes

        mel_chunks = []
        for m_note in data["melody"]:
            f = note_to_freq(m_note)
            t = np.linspace(0, note_dur, int(SAMPLE_RATE * note_dur), endpoint=False)
            # Lead synth: Pulse wave + slight vibrato
            vibrato = 3.0 * np.sin(2 * np.pi * 5.0 * t)
            phase = np.cumsum(f + vibrato) / SAMPLE_RATE
            note_samp = 0.28 * np.sign(np.sin(2 * np.pi * phase))
            note_samp = apply_envelope(note_samp, 0.01, 0.05, 0.7, 0.04)
            mel_chunks.append(note_samp)

        bass_chunks = []
        for b_note in data["bass"]:
            f = note_to_freq(b_note)
            b_samp = synth_triangle(f, note_dur) * 0.35
            b_samp = apply_envelope(b_samp, 0.01, 0.03, 0.8, 0.02)
            bass_chunks.append(b_samp)

        mel_audio = np.concatenate(mel_chunks)
        bass_audio = np.concatenate(bass_chunks)

        # Percussion tick on beat
        total_len = len(mel_audio)
        perc = np.zeros(total_len)
        beat_samples = int(beat_dur * SAMPLE_RATE)
        for b_idx in range(0, total_len, beat_samples):
            p_len = min(int(0.04 * SAMPLE_RATE), total_len - b_idx)
            perc[b_idx:b_idx + p_len] = synth_noise(0.04)[:p_len] * 0.15

        mix = mel_audio + bass_audio + perc
        out_path = os.path.join(MUSIC_DIR, f"{track_name}.wav")
        save_wav(out_path, mix)


def generate_all_assets():
    print("Generating Starbound: The Lost Realms procedural assets...")
    ensure_directories()
    pygame.init()
    # Dummy display if needed for surface manipulation
    try:
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
    except Exception:
        pass

    generate_nova_sprites()
    generate_enemy_sprites()
    generate_boss_sprites()
    generate_items_and_tiles()
    generate_sfx()
    generate_music()
    print("Asset generation complete!")


if __name__ == "__main__":
    generate_all_assets()
