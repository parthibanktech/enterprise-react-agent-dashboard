# ==========================================
# STAGE 1: Build Vite + React Frontend App
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy dependencies first for caching
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy the rest of the frontend source code
COPY frontend/ ./

# Compile Vite static assets into frontend/dist
RUN npm run build

# ==========================================
# STAGE 2: Build Production Python Environment
# ==========================================
FROM python:3.11-slim AS production-runner

# Set system environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python dependencies and lockfiles
COPY pyproject.toml uv.lock* ./

# Install python dependencies
RUN pip install --no-cache-dir .

# Copy application source code and seed files
COPY app/ ./app/
COPY data/ ./data/
COPY lessons/ ./lessons/

# Copy compiled React static assets from Stage 1 into the designated FastAPI directory
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Run database seeder so the DB is ready on startup
RUN python -c "from data.seed import seed_database; seed_database()"

# Expose port
EXPOSE 7860

# Command to start the consolidated FastAPI application serving both backend and frontend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
