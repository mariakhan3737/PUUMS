@echo off
setlocal
echo ========================================================
echo PUUMS Standalone Executable Builder
echo ========================================================
echo.

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=py
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set PY_CMD=python
    ) else (
        echo [ERROR] Neither 'py' nor 'python' was found in PATH.
        echo Please ensure Python is installed and available in your environment.
        pause
        exit /b 1
    )
)

echo Using Python launcher: %PY_CMD%
%PY_CMD% "%~dp0build_exe.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [BUILD FAILED] Review the error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Build finished successfully! Check packaging\dist for the executable.
pause
