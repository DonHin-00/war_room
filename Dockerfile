
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (sqlite3 for debugging, build-essential/gcc if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Permissions
RUN chmod +x *.py

# Expose ports
# 5000: Smart Target
# 8080: Web Dashboard
EXPOSE 5000 8080

# Environment variables
ENV PYTHONUNBUFFERED=1

# Entrypoint via supervisor approach or separate containers.
# For simplicity in this Task, we use simulation_runner.py
# but modified to launch the dashboard too.
# Or we can just run the runner, but we need the dashboard.
# Let's start the runner, which spawns the others.
# We will add dashboard to simulation_runner.py in next step.

CMD ["python3", "simulation_runner.py"]
