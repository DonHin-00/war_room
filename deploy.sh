#!/bin/bash
echo "🚀 Deploying AI Cyber War Simulation..."

# Build the container
echo "🔨 Building Docker image..."
docker-compose build

# Run the container
echo "⚔️  Starting Simulation (2 Parallel War Zones)..."
docker-compose up -d

echo "✅ Deployment complete. Use 'docker-compose logs -f' to monitor."
