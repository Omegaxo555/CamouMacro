#!/usr/bin/env bash
set -e

echo "======================================================="
echo "   CamouMacro Hybrid - Despliegue Zero-Dependency      "
echo "======================================================="
echo ""

if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker no está instalado o no se encuentra en el PATH."
    echo "Por favor instala Docker y vuelve a ejecutar este script."
    exit 1
fi

echo "[1/2] Construyendo imagen de Docker..."
docker compose build

echo ""
echo "[2/2] Iniciando contenedor con Docker Compose..."
echo ""
docker compose up
