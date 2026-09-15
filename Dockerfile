# ==============================================================================
# DMC Operations Command Platform - Production Dockerfile
# ==============================================================================
FROM python:3.12-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Install system utilities (curl for healthchecks, chromium for headless PDF if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Initialize SQLite database schema and seed contract tariffs
RUN python db.py

# Expose server port
EXPOSE 8080

# Healthcheck to ensure REST API is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/kpis || exit 1

# Start the DMC server without opening a local web browser
CMD ["python", "server.py", "--no-browser"]
