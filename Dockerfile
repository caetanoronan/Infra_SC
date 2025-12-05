FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para Playwright/Chromium
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates \
    libnss3 libxss1 libatk1.0-0 libatk-bridge2.0-0 \
    libdrm2 libxkbcommon0 libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libffi-dev \
 && rm -rf /var/lib/apt/lists/*

# Instala as dependências Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && playwright install --with-deps chromium

# Copia o restante do código
COPY . .

ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

CMD ["python", "app_gerador_mapas_final.py"]
