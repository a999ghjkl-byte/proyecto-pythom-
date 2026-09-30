@echo off
title Compilador a Ejecutable EXE - Sistema de Ventas
color 0A
chcp 65001 >nul

echo ======================================================================
echo          GENERADOR DE EJECUTABLE AUTONOMO (.EXE PORTABLE)
echo ======================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado en este equipo.
    pause
    exit /b
)

echo [1/3] Asegurando PyInstaller y librerias...
pip install pyinstaller customtkinter >nul

echo [2/3] Empaquetando sistema en un archivo .EXE (esto puede tardar 1 o 2 minutos)...
pyinstaller --noconsole --onefile --name "SistemaVentas" --collect-all customtkinter main.py

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo  COMPILACION EXITOSA!
    echo ======================================================================
    echo  Tu programa ejecutable esta listo en:
    echo  Carpeta: dist\SistemaVentas.exe
    echo.
    echo  Puedes copiar ese unico archivo "SistemaVentas.exe" a cualquier
    echo  computadora o memoria USB y abrira sin instalar nada adicional.
    echo ======================================================================
) else (
    echo.
    echo [ERROR] Ocurrio un problema durante la compilacion.
)

echo.
pause
