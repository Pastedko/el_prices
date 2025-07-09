FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libgbm-dev \
    libxshmfence-dev \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxi6 \
    libatk1.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "main.py"]
