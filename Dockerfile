# ==============================================================================
# Stage 1: Compilación del Orquestador Go
# ==============================================================================
FROM golang:1.24-alpine AS builder

WORKDIR /build

COPY go_app/go.mod go_app/go.sum ./
RUN go mod download

COPY go_app/ ./
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-s -w" -o /build/camoumacro-cli ./cmd/camoumacro-cli && \
    CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-s -w" -o /build/camoumacro-tui ./cmd/camoumacro-tui

# ==============================================================================
# Stage 2: Runtime Completo (Python 3.12 + Tor + Camoufox/Firefox)
# ==============================================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    TOR_PORT=9050 \
    SPEED_FACTOR=1.0 \
    ALGO=allfeellove_auto \
    PYTHON_ENGINE_DIR=/app/python_engine \
    PYTHON_PATH=/usr/local/bin/python

WORKDIR /app

# Instalar Tor y librerías del sistema requeridas por Firefox/Camoufox
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    tor \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libdbus-glib-1-2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libnspr4 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxshmfence1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python y pre-descargar Camoufox Browser
COPY python_engine/requirements.txt ./python_engine/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "camoufox[geoip]" && \
    pip install --no-cache-dir -r ./python_engine/requirements.txt && \
    python -m camoufox fetch || true

# Copiar el código de Python Engine
COPY python_engine/ ./python_engine/

# Copiar los binarios compilados de Go desde el stage builder
COPY --from=builder /build/camoumacro-cli /usr/local/bin/camoumacro-cli
COPY --from=builder /build/camoumacro-tui /usr/local/bin/camoumacro-tui
RUN chmod +x /usr/local/bin/camoumacro-cli /usr/local/bin/camoumacro-tui

EXPOSE 9050

# Iniciar el orquestador híbrido Go
ENTRYPOINT ["/usr/local/bin/camoumacro-cli"]
CMD ["-loop=true"]
