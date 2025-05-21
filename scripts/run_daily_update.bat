@echo off
echo Starting Federal Register daily update at %TIME%
cd /d %~dp0\..
call env\Scripts\activate.bat
python scripts/daily_update.py
if errorlevel 1 (
    echo Update failed with error code %errorlevel%
    exit /b %errorlevel%
)
echo Update completed successfully at %TIME%
deactivate