"""
STARBOUND: THE LOST REALMS
Input System
Supports Keyboard and Gamepad (SDL2 Controller) with unified actions and edge triggers.
"""

import pygame


class InputManager:
    def __init__(self):
        self.joysticks = []
        self.init_joysticks()

        # Digital action states
        self.actions_down = set()
        self.actions_pressed = set()
        self.actions_released = set()

        # Analog/directional axes
        self.axis_x = 0.0
        self.axis_y = 0.0

        # Debug triggers
        self.debug_f1 = False
        self.debug_f2 = False
        self.debug_f3 = False
        self.debug_f4 = False
        self.debug_f5 = False
        self.debug_f6 = False

    def init_joysticks(self):
        self.joysticks = []
        if pygame.joystick.get_init():
            count = pygame.joystick.get_count()
            for i in range(count):
                try:
                    joy = pygame.joystick.Joystick(i)
                    joy.init()
                    self.joysticks.append(joy)
                except Exception:
                    pass

    def process_events(self, events):
        """
        Processes pygame event loop to update single-frame edge triggers (pressed, released).
        """
        self.actions_pressed.clear()
        self.actions_released.clear()
        self.debug_f1 = False
        self.debug_f2 = False
        self.debug_f3 = False
        self.debug_f4 = False
        self.debug_f5 = False
        self.debug_f6 = False

        for event in events:
            if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
                self.init_joysticks()

            elif event.type == pygame.KEYDOWN:
                # Debug keys
                if event.key == pygame.K_F1:
                    self.debug_f1 = True
                elif event.key == pygame.K_F2:
                    self.debug_f2 = True
                elif event.key == pygame.K_F3:
                    self.debug_f3 = True
                elif event.key == pygame.K_F4:
                    self.debug_f4 = True
                elif event.key == pygame.K_F5:
                    self.debug_f5 = True
                elif event.key == pygame.K_F6:
                    self.debug_f6 = True

                # Game actions
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    self.actions_pressed.add("jump")
                    self.actions_down.add("jump")
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_j, pygame.K_x):
                    self.actions_pressed.add("ability")
                    self.actions_down.add("ability")
                if event.key in (pygame.K_e, pygame.K_z, pygame.K_RETURN):
                    self.actions_pressed.add("interact")
                    self.actions_down.add("interact")
                if event.key == pygame.K_ESCAPE:
                    self.actions_pressed.add("pause")
                    self.actions_down.add("pause")

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    self.actions_released.add("jump")
                    self.actions_down.discard("jump")
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_j, pygame.K_x):
                    self.actions_released.add("ability")
                    self.actions_down.discard("ability")
                if event.key in (pygame.K_e, pygame.K_z, pygame.K_RETURN):
                    self.actions_released.add("interact")
                    self.actions_down.discard("interact")
                if event.key == pygame.K_ESCAPE:
                    self.actions_released.add("pause")
                    self.actions_down.discard("pause")

            # Gamepad buttons
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A / Cross
                    self.actions_pressed.add("jump")
                    self.actions_down.add("jump")
                elif event.button in (1, 2):  # B / X / Circle
                    self.actions_pressed.add("ability")
                    self.actions_down.add("ability")
                elif event.button == 3:  # Y / Triangle
                    self.actions_pressed.add("interact")
                    self.actions_down.add("interact")
                elif event.button in (6, 7):  # Back / Start
                    self.actions_pressed.add("pause")
                    self.actions_down.add("pause")

            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    self.actions_released.add("jump")
                    self.actions_down.discard("jump")
                elif event.button in (1, 2):
                    self.actions_released.add("ability")
                    self.actions_down.discard("ability")
                elif event.button == 3:
                    self.actions_released.add("interact")
                    self.actions_down.discard("interact")
                elif event.button in (6, 7):
                    self.actions_released.add("pause")
                    self.actions_down.discard("pause")

        # Directional axes
        keys = pygame.key.get_pressed()
        ax = 0.0
        ay = 0.0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ay -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ay += 1.0

        # Gamepad joystick check
        for joy in self.joysticks:
            try:
                jx = joy.get_axis(0)
                jy = joy.get_axis(1)
                if abs(jx) > 0.25:
                    ax = jx
                if abs(jy) > 0.25:
                    ay = jy

                # D-Pad (Hat)
                if joy.get_numhats() > 0:
                    hx, hy = joy.get_hat(0)
                    if hx != 0:
                        ax = float(hx)
                    if hy != 0:
                        ay = float(-hy)
            except Exception:
                pass

        self.axis_x = max(-1.0, min(1.0, ax))
        self.axis_y = max(-1.0, min(1.0, ay))

    def is_action_down(self, action):
        return action in self.actions_down

    def is_action_pressed(self, action):
        return action in self.actions_pressed

    def is_action_released(self, action):
        return action in self.actions_released
