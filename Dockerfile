FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies and Google Chrome for the scraper
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirement files first to leverage Docker cache
COPY requirements.txt /app/
COPY medicine_scraper/requirements.txt /app/medicine_scraper/

# Install Python dependencies for both services
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r medicine_scraper/requirements.txt

# Copy project files
COPY . /app/

# Make the startup script executable
RUN chmod +x start.sh

# Expose the port that Render uses
EXPOSE 8000

# Run the startup script
CMD ["./start.sh"]
