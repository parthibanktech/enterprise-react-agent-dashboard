# Use a lightweight official Python image
FROM python:3.11-slim

# Set system environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Install system dependencies (needed for SQLite or network operations)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first (leverage Docker build cache)
COPY pyproject.toml uv.lock* ./

# Install dependencies using 'pip' based on pyproject.toml
RUN pip install --no-cache-dir .

# Copy application source code and seed files
COPY app/ ./app/
COPY data/ ./data/

# Run database seeder so the DB is ready on startup
RUN python -c "from data.seed import seed_database; seed_database()"

# Expose the Gradio container port
EXPOSE 7860

# Command to start the Gradio dashboard web app on host 0.0.0.0
CMD ["python", "-m", "app.ui.dashboard"]
