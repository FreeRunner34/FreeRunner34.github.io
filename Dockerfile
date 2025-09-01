# Simple production Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
ENV GUNICORN_CMD_ARGS="--bind 0.0.0.0:$PORT --workers 2 --threads 4"
RUN pip install --no-cache-dir gunicorn

CMD ["gunicorn", "app:app"]
