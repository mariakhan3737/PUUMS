"""
PUUMS Build Automation Script
-----------------------------
Builds a standalone Windows executable (.exe) for the PUUMS desktop application.
Keeps all build artifacts isolated within the `packaging/` folder:
  - Working directory (intermediate compilation): packaging/build/
  - Output directory (final executable & config):  packaging/dist/
  - Spec file:                                    packaging/PUUMS.spec

Usage:
    py packaging/build_exe.py
    py packaging/build_exe.py --onefile
    py packaging/build_exe.py --clean

Prerequisites:
    py -m pip install pyinstaller
    py -m pip install -r requirements.txt
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGING_DIR = Path(__file__).resolve().parent
ROOT_DIR = PACKAGING_DIR.parent
BOOTSTRAP_ENTRY = PACKAGING_DIR / "run_exe.py"
BUILD_DIR = PACKAGING_DIR / "build"
DIST_DIR = PACKAGING_DIR / "dist"
SPEC_FILE = PACKAGING_DIR / "PUUMS.spec"


def check_prerequisites():
    """Verify PyInstaller is installed."""
    try:
        import PyInstaller  # noqa: F401
        print(" [OK] PyInstaller detected.")
    except ImportError:
        print("\n [ERROR] PyInstaller is not installed in the current Python environment.")
        print(" To install PyInstaller, run:")
        print("     py -m pip install pyinstaller\n")
        sys.exit(1)


def clean_build_artifacts():
    """Remove temporary build and dist directories."""
    print(" Cleaning packaging directories...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        print(f"  Removed: {BUILD_DIR}")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR, ignore_errors=True)
        print(f"  Removed: {DIST_DIR}")
    if SPEC_FILE.exists():
        SPEC_FILE.unlink(missing_ok=True)
        print(f"  Removed: {SPEC_FILE}")


def build_executable(onefile=True, clean_first=False):
    """Run PyInstaller with isolated paths."""
    check_prerequisites()

    if clean_first:
        clean_build_artifacts()

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    mode = "--onefile" if onefile else "--onedir"
    print(f"\n=======================================================")
    print(f" Building PUUMS Executable ({mode.upper()})")
    print(f" Root Directory:      {ROOT_DIR}")
    print(f" Packaging Directory: {PACKAGING_DIR}")
    print(f" Work / Build Dir:    {BUILD_DIR}")
    print(f" Output / Dist Dir:   {DIST_DIR}")
    print(f"=======================================================\n")

    # Command line arguments for PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=PUUMS",
        mode,
        "--windowed",                               # No command prompt window popup for desktop GUI
        f"--workpath={str(BUILD_DIR)}",
        f"--distpath={str(DIST_DIR)}",
        f"--specpath={str(PACKAGING_DIR)}",
        f"--paths={str(ROOT_DIR)}",                  # Add project root to Python search paths
        # Hidden imports to ensure pymysql and cryptography run smoothly
        "--hidden-import=pymysql",
        "--hidden-import=pymysql.cursors",
        "--hidden-import=cryptography",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        # Include app package modules
        "--hidden-import=app",
        "--hidden-import=app.config",
        "--hidden-import=app.db",
        "--hidden-import=app.ui",
        "--hidden-import=app.ui.ui_common",
        "--hidden-import=app.ui.login_window",
        "--hidden-import=app.ui.xp_style",
        "--hidden-import=app.portals",
        "--hidden-import=app.portals.portal_base",
        "--hidden-import=app.portals.admin_portal",
        "--hidden-import=app.portals.citizen_portal",
        "--hidden-import=app.portals.employee_portal",
        # Include assets (fonts)
        f"--add-data={str(ROOT_DIR / 'assets')};assets",
        # Explicit bootstrap script
        str(BOOTSTRAP_ENTRY)
    ]

    print("Executing command:")
    print(" ".join(cmd) + "\n")

    result = subprocess.run(cmd, cwd=str(PACKAGING_DIR))
    if result.returncode != 0:
        print(f"\n[ERROR] PyInstaller failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    # Post-build: Ensure config.example.py is copied to dist folder
    # so whoever receives the .exe knows how to configure MySQL
    target_config_dir = DIST_DIR if onefile else DIST_DIR / "PUUMS"
    target_config = target_config_dir / "config.py"
    target_readme = target_config_dir / "HOW_TO_RUN.txt"

    # Copy config.py if it exists, or create default config template
    src_config = ROOT_DIR / "config.py"
    if src_config.exists():
        shutil.copy2(src_config, target_config)
        print(f" [OK] Copied config.py -> {target_config}")
    else:
        with open(target_config, "w", encoding="utf-8") as f:
            f.write('# Edit these to match your local MySQL server\n'
                    'DB_HOST = "localhost"\n'
                    'DB_PORT = 3306\n'
                    'DB_USER = "root"\n'
                    'DB_PASSWORD = ""           # put your MySQL root password here\n'
                    'DB_NAME = "puums"\n')
        print(f" [OK] Generated default config.py -> {target_config}")

    # Create a quick instruction text file in the dist folder
    with open(target_readme, "w", encoding="utf-8") as f:
        f.write("PUUMS - Pakistan Unified Utility Management System\n"
                "Standalone Executable Distribution\n"
                "==================================================\n\n"
                "PREREQUISITES:\n"
                "1. MySQL Server 8.0+ running locally or accessible via network on port 3306.\n"
                "2. The 'puums' database schema initialized.\n\n"
                "HOW TO RUN:\n"
                "1. Open 'config.py' in this folder and enter your MySQL root password:\n"
                "       DB_PASSWORD = \"your_mysql_password\"\n"
                "2. Double-click 'PUUMS.exe' to launch the desktop application.\n"
                "3. Log in with demo accounts:\n"
                "   - Citizen:   42101-1234567-1  (Maria Khan)   / pass123\n"
                "   - Employee:  usman.tariq@puums.pk           / pass123\n"
                "   - Admin:     admin@puums.pk                 / admin123\n")
    print(f" [OK] Created HOW_TO_RUN.txt -> {target_readme}")

    print("\n=======================================================")
    print(" Build completed successfully!")
    print(f" Executable and configuration located in: {target_config_dir}")
    print("=======================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build PUUMS standalone Windows executable.")
    parser.add_argument("--onefile", action="store_true", default=True,
                        help="Build a single standalone .exe (default: True)")
    parser.add_argument("--onedir", action="store_false", dest="onefile",
                        help="Build a folder containing .exe and DLL dependencies")
    parser.add_argument("--clean", action="store_true",
                        help="Clean previous build artifacts before building")
    args = parser.parse_args()

    build_executable(onefile=args.onefile, clean_first=args.clean)
