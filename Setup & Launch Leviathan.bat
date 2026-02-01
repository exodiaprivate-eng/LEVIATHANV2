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
if !errorlevel! neq 0 (
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
if !errorlevel! neq 0 (
    echo  pip not found. Installing pip...
    py -3.12 -m ensurepip --upgrade
    if !errorlevel! neq 0 (
        echo  ERROR: Could not install pip. Please install manually.
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%v in ('py -3.12 -m pip --version 2^>^&1') do set PIPVER=%%v
echo  OK: %PIPVER%
echo.

:: -----------------------------------------------
:: 3. INSTALL DEPENDENCIES
:: -----------------------------------------------
echo [3/4] Checking ^& installing dependencies...
echo.

set REQFILE=leviathan\requirements.txt

if not exist "%REQFILE%" (
    echo  ERROR: requirements.txt not found at %REQFILE%
    pause
    exit /b 1
)

py -3.12 -m pip install -r "%REQFILE%" --quiet 2>&1
if !errorlevel! neq 0 (
    echo  WARNING: Some packages may have had issues installing.
    echo  Attempting to continue anyway...
) else (
    echo  All dependencies satisfied.
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

if !errorlevel! neq 0 (
    echo.
    echo  Application exited with an error (code !errorlevel!).
    echo.
)

pause
