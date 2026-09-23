@echo off
title Starbound: The Lost Realms
echo Launching Starbound: The Lost Realms...
cd /d "%~dp0"
if exist "builds\windows\StarboundLostRealms\StarboundLostRealms.exe" (
    start "" "builds\windows\StarboundLostRealms\StarboundLostRealms.exe"
) else (
    echo Executable not found in builds\windows. Running via python launcher...
    py run_game.py
)
exit
