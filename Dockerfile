# Use a lightweight Python Linux image
FROM python:3.11-slim

# 1. Install System Dependencies
# LibreOffice: For PPT -> PDF conversion
# Poppler-utils: For PDF -> Image conversion
RUN apt-get update && apt-get install -y \
    libreoffice \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy Application Code
COPY . .

# 4. Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# 5. Expose the port (Standard HTTP)
EXPOSE 8000

# 6. Start both services
CMD ["./entrypoint.sh"]
