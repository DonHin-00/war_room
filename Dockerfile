# Use official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
# gcc and python3-dev are often needed for psutil compilation if no wheel exists
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m sentinel
RUN chown -R sentinel:sentinel /app

# Copy project files
COPY . .

# Set permissions for simulation directories
RUN mkdir -p logs simulation_data simulation_data/persistence \
    && chown -R sentinel:sentinel logs simulation_data

# Switch to non-root user
USER sentinel

# Expose VNet Switch Port (internal, but good to document)
EXPOSE 10000

# Default Command: Run the Emulation
CMD ["python", "tools/run_emulation.py"]
