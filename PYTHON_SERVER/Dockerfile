# Builder stage
FROM python:3.12-slim as builder

# GPG anahtarlarını güncelle ve sistem paketlerini yükle
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    gnupg \
    && apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-server-dev-all \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Tüm Python paketlerini tek komutta yükle
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    psycopg2-binary \
    scrapy-rotating-proxies \
    uvicorn \
    celery \
    redis \
    flower \
    pika \
    -r requirements.txt && \
    playwright install-deps chromium && \
    playwright install chromium

# Final stage
FROM python:3.12-slim

# GPG anahtarlarını güncelle ve sistem paketlerini yükle
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    xvfb \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python paketlerini builder'dan kopyala
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# ✅ Playwright browser'larını builder'dan kopyala
COPY --from=builder /root/.cache/ms-playwright/ /root/.cache/ms-playwright/

# Sadece gerekli dosyaları kopyala (önce değişmeyen dosyalar)
COPY app/ ./app/

# Environment variables
ENV DISPLAY=:99
ENV CHROME_OPTIONS='--headless --no-sandbox --disable-dev-shm-usage'
ENV SERVER_PATH=/app
ENV TZ=Europe/Istanbul

# Timezone ayarla
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Permissions
RUN chmod +x /app/app/services/CrawlerService.py