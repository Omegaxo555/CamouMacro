@echo off
title CamouMacro - 1-Click Docker Runner
echo =======================================================
echo    CamouMacro Hybrid - Despliegue Zero-Dependency
echo =======================================================
echo.

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta instalado o no se encuentra en el PATH.
    echo Por favor instala Docker Desktop y vuelve a ejecutar este script.
    echo.
    pause
    exit /b 1
)

echo [1/2] Construyendo imagen de Docker (esto puede tardar unos minutos en el primer inicio)...
docker compose build

if %errorlevel% neq 0 (
    echo [ERROR] Fallo al construir la imagen Docker.
    pause
    exit /b 1
)

echo.
echo [2/2] Iniciando contenedor con Docker Compose...
echo.
docker compose up
pause
