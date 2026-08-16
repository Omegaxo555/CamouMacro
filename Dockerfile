FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEADLESS=true \
    TOR_PORT=9050

WORKDIR /app

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

COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir "camoufox[geoip]" && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m playwright install --with-deps firefox || true

COPY . .

RUN python -m camoufox fetch || true

EXPOSE 9050

CMD ["python", "main.py"]
