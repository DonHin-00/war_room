#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🛡️  SENTINEL CYBER WAR EMULATION DEPLOYMENT 🛡️${NC}"
echo "==================================================="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  docker-compose not found, checking 'docker compose'...${NC}"
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed.${NC}"
        exit 1
    fi
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${GREEN}✅ Prerequisites checked.${NC}"

# Setup Directories
echo -e "${YELLOW}📂 Setting up directories...${NC}"
mkdir -p logs simulation_data simulation_data/persistence
chmod 700 logs simulation_data simulation_data/persistence

# Build
echo -e "${YELLOW}🏗️  Building Sentinel Container...${NC}"
$DOCKER_COMPOSE build

# Deploy
echo -e "${GREEN}🚀 Launching Emulation...${NC}"
$DOCKER_COMPOSE up -d

echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "   - View Logs:      $DOCKER_COMPOSE logs -f"
echo -e "   - Attach Dashboard: $DOCKER_COMPOSE exec -it sentinel /usr/local/bin/python tools/dashboard.py"
echo -e "   - Stop Simulation: $DOCKER_COMPOSE down"
