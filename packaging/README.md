# PUUMS Packaging & Standalone Executable Build Step

This directory (`packaging/`) contains isolated tools to compile the PUUMS PyQt5 desktop application into a standalone Windows executable (`PUUMS.exe`).

## Purpose & Design Philosophy
- **Isolated from Core Application**: All build artifacts (`build/`, `dist/`, `.spec` files) stay contained inside `packaging/` and are automatically ignored by Git. The core software remains 100% pure Python.
- **Python-Free Distribution**: Allows sharing the software with evaluators, classmates, or non-technical users who do not have Python, PyQt5, or dependencies installed.
- **External Configuration Strategy**: The compiled executable loads `config.py` from the directory where `PUUMS.exe` sits. This means users can configure their MySQL database credentials (`DB_HOST`, `DB_PORT`, `DB_PASSWORD`) directly in `config.py` without recompiling the executable.

---

## Prerequisites
Before running the build script, ensure PyInstaller and dependencies are installed in your Python environment:

```bat
py -m pip install -r ../requirements.txt
py -m pip install pyinstaller
```

---

## How to Build

### Option 1: One-Click Windows Batch Script
Double-click `build.bat` or run:
```bat
packaging\build.bat
```

### Option 2: Python Command Line
From the project root:
```bat
py packaging\build_exe.py
```

### Build Options:
- **Single Executable (Default)**:
  ```bat
  py packaging\build_exe.py --onefile
  ```
  Generates `packaging/dist/PUUMS.exe` along with `config.py` and `HOW_TO_RUN.txt`.
- **Directory Mode (Faster startup)**:
  ```bat
  py packaging\build_exe.py --onedir
  ```
- **Clean Rebuild**:
  ```bat
  py packaging\build_exe.py --clean
  ```

---

## Output Structure
Upon successful compilation:
```
packaging/
├── build/                 # Temporary object and assembly cache (ignored by git)
├── dist/                  # Final distributable folder
│   ├── PUUMS.exe          # Standalone Windows application
│   ├── config.py          # Database configuration file (editable)
│   └── HOW_TO_RUN.txt     # End-user quickstart instructions
├── run_exe.py             # Runtime bootstrap wrapper
├── build_exe.py           # PyInstaller build automation script
├── build.bat              # Windows batch build helper
└── README.md              # This documentation
```
