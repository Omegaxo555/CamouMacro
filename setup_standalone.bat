@echo off
title CamouMacro - Instalador Standalone Local
echo =======================================================
echo    CamouMacro Standalone Setup (Windows Nativo)
echo =======================================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado en el sistema.
    pause
    exit /b 1
)

echo [2/4] Creando entorno virtual .venv en python_engine...
cd python_engine
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo [3/4] Instalando dependencias de Python y Camoufox...
pip install --upgrade pip
pip install -r requirements.txt
python -m camoufox fetch
cd ..

echo [4/4] Compilando binarios de Go...
cd go_app
if not exist "bin" mkdir bin
go build -o bin/camoumacro-cli.exe ./cmd/camoumacro-cli
go build -o bin/camoumacro-tui.exe ./cmd/camoumacro-tui
cd ..

echo.
echo =======================================================
echo    Instalacion completada con exito!
echo =======================================================
echo Para iniciar el Dashboard interactivo: .\go_app\bin\camoumacro-tui.exe
echo Para iniciar en modo CLI: .\go_app\bin\camoumacro-cli.exe
echo.
pause
