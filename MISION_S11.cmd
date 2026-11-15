@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m src.missions.g05 s11
) else (
  py -3.12 -m src.missions.g05 s11
)
if errorlevel 1 exit /b 1
echo S11 verificado. Abra index.html y entre a S11.
