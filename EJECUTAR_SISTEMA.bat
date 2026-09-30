@echo off
title Sistema de Ventas PRO - Launcher
color 0B
chcp 65001 >nul

echo ======================================================================
echo          SISTEMA DE GESTION COMERCIAL Y FACTURACION (PYTHON)
echo ======================================================================
echo.

:: 1. Verificar si Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no se encuentra instalado o no esta en el PATH de Windows.
    echo.
    echo Por favor descarga e instala Python desde: https://www.python.org/downloads/
    echo Recuerda marcar la casilla: "Add python.exe to PATH" durante la instalacion.
    echo.
    pause
    exit /b
)

:: 2. Instalar dependencias si no estan presentes
echo [1/2] Verificando dependencias necesarias...
python -c "import customtkinter" >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando libreria CustomTkinter...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudieron instalar las dependencias. Verifica tu conexion a internet.
        pause
        exit /b
    )
)

:: 3. Iniciar la aplicación
echo [2/2] Iniciando aplicacion...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [AVISO] La aplicacion se cerro con un codigo de estado: %errorlevel%
    pause
)
