#!/bin/bash

# LangGraph Agent System Runner

# 1. Clean up potential old container states to avoid 'ContainerConfig' errors
echo "Cleaning up old containers..."
docker-compose down --remove-orphans

# 2. Build and start containers
echo "Starting system..."
docker-compose up --build -d

# 3. Wait for DB to be ready
echo "Waiting for PostgreSQL to initialize..."
sleep 5

# 4. Install default Piston runtimes
echo "Installing code execution runtimes..."
./install_piston_packages.sh python node go

echo "------------------------------------------------"
echo "SYSTEM READY!"
echo "API: http://localhost:8001"
echo "Postgres (Host): localhost:5433"
echo "------------------------------------------------"
echo "Try a test command:"
echo "docker exec -it ai_piston_executor_api python scripts/run_agent.py \"Get all users from database\""
