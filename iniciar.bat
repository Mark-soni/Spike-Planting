@echo off
:: Ejecuta el countdown como Administrador (requerido para hook global de teclado)
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Solicitando permisos de Administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Iniciando Countdown Overlay...
python "%~dp0countdown.py"
pause
