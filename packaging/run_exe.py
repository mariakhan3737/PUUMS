"""
PUUMS Executable Bootstrap Entry Point
Used exclusively by the PyInstaller packaging step in the packaging/ folder.
Ensures that the directory containing the compiled .exe is at the top of sys.path,
allowing the executable to dynamically load an external config.py (containing MySQL
host, port, user, and password) without hardcoding database credentials or requiring
Python to be installed on the host machine.
"""
import os
import sys
from pathlib import Path

# When running as a frozen executable (PyInstaller), sys.executable is the .exe path.
if getattr(sys, "frozen", False):
    exe_dir = Path(sys.executable).resolve().parent
    # Add the directory containing the exe to sys.path so config.py can be loaded from there
    if str(exe_dir) not in sys.path:
        sys.path.insert(0, str(exe_dir))
    # Also ensure current working directory is the exe directory
    os.chdir(exe_dir)
else:
    # Running directly from source for testing
    root_dir = Path(__file__).resolve().parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

# Import main application
from main import App

if __name__ == "__main__":
    app = App()
    sys.exit(app.run())
