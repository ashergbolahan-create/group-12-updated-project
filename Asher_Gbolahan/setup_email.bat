@echo off
cd /d "%~dp0"
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto end
py -3 Great_Joseph2\setup_email.py
:end
pause
