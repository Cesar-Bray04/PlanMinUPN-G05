@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m src.missions.g05 verificar
) else (
  py -3.12 -m src.missions.g05 verificar
)
exit /b %errorlevel%
