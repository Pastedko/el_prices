FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y wget unzip chromium chromium-driver xvfb libxi6 libgconf-2-4 libnss3 libxss1 libappindicator3-1 libasound2 && \
    rm -rf /var/lib/apt/lists/*

ENV DISPLAY=:99

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["xvfb-run", "--server-args=-screen 0 1920x1080x24", "python", "main.py"]
