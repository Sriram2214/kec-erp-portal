# ── Stage 1: Build React Frontend ──
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY frontend/package*.json ./
RUN npm install --silent
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Production Server ──
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

WORKDIR /app

# Install system dependencies (for PDF generation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Flask app
COPY app/ ./app/
COPY config.py wsgi.py ./

# Copy React build from frontend stage
# Based on your vite.config.js, build goes to ../app/static/dist
COPY --from=frontend-build /app/static/dist ./app/static/dist

# Create necessary folders
RUN mkdir -p logs instance

# Run as non-root user for security
RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && chown -R appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "wsgi.py"]
