# Makefile for LangGraph Multi-Agent System
# Consolidates startup, cleanup, and maintenance commands

.PHONY: up down restart install-piston logs test dbshell

# Start the system (standard entry point)
up:
	@echo "Cleaning up old containers..."
	docker-compose down --remove-orphans
	@echo "Building and starting containers in detached mode..."
	docker-compose up --build -d
	@echo "Waiting for services to initialize..."
	sleep 5
	$(MAKE) install-piston

# Stop the system
down:
	docker-compose down

# Restart the system
restart: down up

# Pre-install common code runtimes into Piston sandbox
install-piston:
	@echo "Installing default Piston runtimes (Python, NodeJS, Go)..."
	./install_piston_packages.sh python node go

# Stream logs from the API container
logs:
	docker logs -f ai_piston_executor_api

# Run a sample agent command (Sanity check)
test:
	docker exec -it ai_piston_executor_api python scripts/run_agent.py "Write a Go program that prints Hello World"

# Open PostgreSQL shell inside the container
dbshell:
	docker exec -it demo_postgres psql -U user -d demo_db

# Clean up all docker resources related to this project
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker image prune -f
