@echo off
echo OpenSuperWhisper Launcher
echo ======================
echo.
echo Choose launch method:
echo 1. Run EXE file (fastest)
echo 2. Run from Python source
echo.
set /p choice="Enter choice (1 or 2): "

REM Check if OPENAI_API_KEY is set (optional now)
if not "%OPENAI_API_KEY%"=="" (
    echo API Key found in environment: %OPENAI_API_KEY:~0,10%...
) else (
    echo No environment API key found. You can set it via Settings menu in the app.
)
echo.

if "%choice%"=="1" (
    echo Launching EXE version...
    start dist\OpenSuperWhisper.exe
) else if "%choice%"=="2" (
    echo Launching Python version...
    python run.py
) else (
    echo Invalid choice. Launching EXE by default...
    start dist\OpenSuperWhisper.exe
)

echo Application launched. Check if the window opened successfully.
pause