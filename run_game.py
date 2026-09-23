"""
STARBOUND: THE LOST REALMS
Desktop Executable Launcher
"""

import sys
import os

# Set working directory to script location
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Attach to user's interactive 'Default' desktop on Windows
if sys.platform == "win32":
    try:
        import ctypes
        h_desk = ctypes.windll.user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if h_desk:
            ctypes.windll.user32.SetThreadDesktop(h_desk)
    except Exception:
        pass

from src.main import main

if __name__ == "__main__":
    main()
