# Osnovni image sa Python-om
FROM python:3.10-slim

# Instaliraj sistemske zavisnosti za Chromium i ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Podesi radni direktorijum
WORKDIR /app

# Kopiraj requirements.txt i instaliraj Python zavisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiraj ceo projekat
COPY . .

# Pokreni glavni fajl
CMD ["python", "main.py"]