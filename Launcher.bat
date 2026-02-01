@echo off
setlocal enabledelayedexpansion
title Leviathan V2 - Setup ^& Launch
color 0A
cd /d "%~dp0"

echo.
echo  =============================================
echo   LEVIATHAN V2 - Autonomous Trading Platform
echo  =============================================
echo.

:: -----------------------------------------------
:: 1. CHECK PYTHON 3.12
:: -----------------------------------------------
echo [1/4] Checking Python 3.12...

py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python 3.12 is NOT installed or not found.
    echo  Leviathan requires Python 3.12 specifically.
    echo  Download from: https://www.python.org/downloads/release/python-3120/
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('py -3.12 --version 2^>^&1') do set PYVER=%%v
echo  OK: %PYVER% detected.
echo.

:: -----------------------------------------------
:: 2. CHECK PIP
:: -----------------------------------------------
echo [2/4] Checking pip...

py -3.12 -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  pip not found. Installing pip...
    py -3.12 -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo  ERROR: Could not install pip. Please install manually.
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%v in ('py -3.12 -m pip --version 2^>^&1') do set PIPVER=%%v
echo  OK: %PIPVER%
echo.

:: -----------------------------------------------
:: 3. CHECK & INSTALL DEPENDENCIES
:: -----------------------------------------------
echo [3/4] Checking dependencies...
echo.

set MISSING=0
set REQFILE=leviathan\requirements.txt

if not exist "%REQFILE%" (
    echo  ERROR: requirements.txt not found at %REQFILE%
    pause
    exit /b 1
)

:: Check each package
for /f "usebackq tokens=1 delims=>=" %%p in ("%REQFILE%") do (
    set "PKG=%%p"
    :: Skip empty lines
    if not "!PKG!"=="" (
        py -3.12 -c "import importlib; importlib.import_module('!PKG!'.replace('-','_').strip())" >nul 2>&1
        if !errorlevel! neq 0 (
            echo  MISSING: !PKG!
            set /a MISSING+=1
        ) else (
            echo  OK: !PKG!
        )
    )
)

echo.

if %MISSING% gtr 0 (
    echo  %MISSING% package(s) need to be installed.
    echo  Installing all requirements...
    echo.
    py -3.12 -m pip install -r "%REQFILE%" --quiet
    if %errorlevel% neq 0 (
        echo.
        echo  WARNING: Some packages may have failed to install.
        echo  Attempting to continue anyway...
        echo.
    ) else (
        echo  All packages installed successfully.
    )
) else (
    echo  All dependencies are already installed.
)

echo.

:: -----------------------------------------------
:: 4. LAUNCH LEVIATHAN
:: -----------------------------------------------
echo [4/4] Launching Leviathan V2...
echo.
echo  =============================================
echo   Starting application...
echo  =============================================
echo.

py -3.12 -m leviathan.gui.app

if %errorlevel% neq 0 (
    echo.
    echo  Application exited with an error (code %errorlevel%).
    echo.
)

pause
