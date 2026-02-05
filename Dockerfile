FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create working directory
WORKDIR /app

# Install system dependencies (procps for pgrep/pkill/ps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (if any, though we are mostly stdlib)
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security (though pgrep/kill might need permissions depending on setup)
# For this simulation, running as root inside the container simplifies process management.
# If we wanted strict security, we'd use a non-root user and capabilities.
# USER 1000

# Default command: Run the orchestrator with 2 parallel zones
CMD ["python3", "orchestrator.py", "--instances", "2"]
