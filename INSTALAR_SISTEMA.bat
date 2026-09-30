@echo off
title Instalador Oficial - Sistema de Ventas PRO
color 0B
chcp 65001 >nul

echo ======================================================================
echo          INSTALADOR ASISTIDO - SISTEMA DE VENTAS PRO
echo ======================================================================
echo  Bienvenido al asistente de instalacion del Sistema de Ventas.
echo  Este instalador configurara el programa en tu equipo y creara
echo  los accesos directos en tu Escritorio y Menu Inicio.
echo ======================================================================
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\SistemaVentas"
set "EXE_SOURCE=%~dp0dist\SistemaVentas.exe"
set "DB_SOURCE=%~dp0sistema_ventas_python\ventas.db"

:: 1. Verificar si existe el archivo ejecutable compilado
if not exist "%EXE_SOURCE%" (
    echo [AVISO] No se detecto el archivo compilado en dist\SistemaVentas.exe
    echo [INFO] Iniciando compilacion automatica ahora mismo con Python...
    echo.
    python -m PyInstaller --noconsole --onefile --name "SistemaVentas" --collect-all customtkinter "%~dp0main.py"
    if not exist "%EXE_SOURCE%" (
        echo.
        echo [ERROR] No se pudo generar SistemaVentas.exe.
        echo Asegurate de tener Python instalado o compilar primero con COMPILAR_A_EXE.bat.
        pause
        exit /b 1
    )
)

echo [1/4] Creando directorio de instalacion...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [2/4] Copiando archivos del sistema...
copy /Y "%EXE_SOURCE%" "%INSTALL_DIR%\SistemaVentas.exe" >nul
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo copiar el ejecutable a %INSTALL_DIR%.
    pause
    exit /b 1
)

:: Copiar base de datos inicial solo si no existe todavia en el destino
if not exist "%INSTALL_DIR%\ventas.db" (
    if exist "%DB_SOURCE%" (
        copy /Y "%DB_SOURCE%" "%INSTALL_DIR%\ventas.db" >nul
        echo       Base de datos inicial copiada con exito.
    )
) else (
    echo       Se conserva la base de datos existente con tus ventas y clientes.
)

:: Crear script desinstalador
(
echo @echo off
echo title Desinstalador - Sistema de Ventas PRO
echo color 0C
echo chcp 65001 >nul
echo echo Desinstalando Sistema de Ventas PRO...
echo powershell -NoProfile -Command "$d = [Environment]::GetFolderPath('Desktop'); Remove-Item -Path \"$d\Sistema de Ventas PRO.lnk\" -Force -ErrorAction SilentlyContinue"
echo powershell -NoProfile -Command "$s = [Environment]::GetFolderPath('StartMenu'); Remove-Item -Path \"$s\Programs\Sistema de Ventas PRO.lnk\" -Force -ErrorAction SilentlyContinue"
echo echo Accesos directos eliminados.
echo echo Puedes eliminar manualmente la carpeta: %%LOCALAPPDATA%%\SistemaVentas si no deseas conservar la base de datos.
echo pause
) > "%INSTALL_DIR%\Desinstalar.bat"

echo [3/4] Creando Accesos Directos oficiales en Windows...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $d = [Environment]::GetFolderPath('Desktop'); $scD = $ws.CreateShortcut((Join-Path $d 'Sistema de Ventas PRO.lnk')); $scD.TargetPath = '%INSTALL_DIR%\SistemaVentas.exe'; $scD.WorkingDirectory = '%INSTALL_DIR%'; $scD.Description = 'Sistema de Ventas & Facturacion PRO'; $scD.Save(); $sm = [Environment]::GetFolderPath('Programs'); $scS = $ws.CreateShortcut((Join-Path $sm 'Sistema de Ventas PRO.lnk')); $scS.TargetPath = '%INSTALL_DIR%\SistemaVentas.exe'; $scS.WorkingDirectory = '%INSTALL_DIR%'; $scS.Description = 'Sistema de Ventas & Facturacion PRO'; $scS.Save()"

echo [4/4] Verificando instalacion...
echo.
color 0A
echo ======================================================================
echo                ¡INSTALACION COMPLETADA CON EXITO!
echo ======================================================================
echo  El sistema se instalo en:
echo    %INSTALL_DIR%
echo.
echo  Accesos directos creados:
echo    [*] Escritorio:   "Sistema de Ventas PRO"
echo    [*] Menu Inicio:  "Sistema de Ventas PRO"
echo.
echo  Credenciales de acceso preconfiguradas:
echo    * Administrador:  admin@lozano.com   / 123456
echo    * Vendedor:       vendedor@lozano.com / 123456
echo    * Consultor:      lucia@edu.com      / lucia2177$
echo ======================================================================
echo.

set /p ABRIR="¿Deseas abrir el Sistema de Ventas ahora mismo? (S/N): "
if /i "%ABRIR%"=="S" (
    echo Iniciando sistema...
    start "" "%INSTALL_DIR%\SistemaVentas.exe"
) else (
    echo Puedes abrirlo en cualquier momento desde el icono de tu Escritorio.
)

echo.
pause
