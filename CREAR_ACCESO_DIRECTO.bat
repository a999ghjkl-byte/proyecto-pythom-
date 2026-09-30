@echo off
title Crear Acceso Directo en el Escritorio - Sistema de Ventas
color 0A
chcp 65001 >nul

echo ======================================================================
echo       CREAR ACCESO DIRECTO EN EL ESCRITORIO (MODO PORTABLE)
echo ======================================================================
echo.

set "EXE_TARGET=%~dp0dist\SistemaVentas.exe"

if not exist "%EXE_TARGET%" (
    echo [AVISO] No se encontro "%EXE_TARGET%".
    echo [INFO] Compilando el ejecutable SistemaVentas.exe primero...
    call "%~dp0COMPILAR_A_EXE.bat"
)

if not exist "%EXE_TARGET%" (
    echo [ERROR] No se pudo encontrar ni compilar SistemaVentas.exe.
    pause
    exit /b 1
)

echo Creando acceso directo en el Escritorio...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $d = [Environment]::GetFolderPath('Desktop'); $sc = $ws.CreateShortcut((Join-Path $d 'Sistema de Ventas PRO.lnk')); $sc.TargetPath = '%EXE_TARGET%'; $sc.WorkingDirectory = '%~dp0dist'; $sc.Description = 'Sistema de Ventas & Facturacion PRO'; $sc.Save()"

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo  ¡ACCESO DIRECTO CREADO EXITOSAMENTE EN TU ESCRITORIO!
    echo ======================================================================
    echo  Ahora puedes ir a tu Escritorio y hacer doble clic sobre:
    echo  "Sistema de Ventas PRO" para abrir el programa directamente.
    echo ======================================================================
) else (
    echo [ERROR] No se pudo crear el acceso directo.
)

echo.
pause
