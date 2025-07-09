FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y wget unzip gnupg2 \
    # Install Chromium and Chromedriver dependencies
    fonts-liberation libnss3 libatk-bridge2.0-0 libgtk-3-0 libasound2 \
    libgbm-dev libxshmfence-dev libxrandr2 libxss1 libxcursor1 \
    libxi6 libatk1.0-0 libxcomposite1 libxdamage1 libxext6 \
    chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable for Chrome/Chromium
ENV CHROME_BIN=chromium
ENV CHROMEDRIVER_BIN=chromium-driver

# Set up working directory
WORKDIR /app

# Copy requirements (if any) and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script and .env
COPY . .

# Make downloads folder
RUN mkdir -p downloads

# Run the script
CMD ["python", "main.py"]
