# Use an official Python runtime as a parent image
FROM python:3.9-slim-bullseye

# Set environment variables
# PYTHONUNBUFFERED=1: Forces stdout/stderr to be flushed immediately
# PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install system dependencies (procps for ps/kill used by watchdog/runner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories for runtime data
RUN mkdir -p simulation_data battlefield network_bus

# Define volumes for persistence
VOLUME ["/app/simulation_data", "/app/battlefield"]

# Run the simulation orchestrator
CMD ["python3", "simulation_runner.py"]
