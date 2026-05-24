@echo off
:: Ejecuta el countdown como Administrador (requerido para hook global de teclado)
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: pythonw corre sin ventana de consola — se puede cerrar este cmd tranquilo
start "" pythonw "%~dp0countdown.py"
exit
