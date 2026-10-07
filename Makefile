.DEFAULT_GOAL := help

# Dynamic host-agnostic paths: resolves current repository root on any OS/host
ROOT_DIR := $(shell pwd -P 2>/dev/null || pwd)
export WORKSPACE_DIR ?= $(ROOT_DIR)/workspace
export REPO_DIR ?= $(ROOT_DIR)
export SANDBOX_USER_ID ?= $(shell id -u 2>/dev/null || echo 0)

# Load local .env if present
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

PORT ?= $(or $(OPENHANDS_PORT),8000)

.PHONY: help up down restart logs status shell clean workspace-dir

## Display available targets
help:
	@echo "Available commands:"
	@echo "  make up         Start OpenHands in Docker with bind mounts and open GUI link"
	@echo "  make down       Stop OpenHands container"
	@echo "  make restart    Restart OpenHands container"
	@echo "  make logs       Follow OpenHands container logs"
	@echo "  make status     Check status of containers"
	@echo "  make shell      Open a bash shell inside the OpenHands container"
	@echo "  make clean      Stop containers and remove orphans"

## Ensure workspace directory and config template exist on host
workspace-dir:
	@mkdir -p "$(WORKSPACE_DIR)"
	@if [ ! -f "openhands/config/settings.json" ] && [ -f "openhands/config/settings.example.json" ]; then \
		cp "openhands/config/settings.example.json" "openhands/config/settings.json"; \
	fi
## Start OpenHands in Docker with workspace and custom work bind-mounted
up: workspace-dir
	@echo "Starting OpenHands on http://localhost:$(PORT)..."
	@docker compose up -d
	@echo "Waiting for OpenHands server to become ready..."
	@for i in $$(seq 1 30); do \
		if curl -fs -o /dev/null "http://127.0.0.1:$(PORT)" 2>/dev/null; then \
			break; \
		fi; \
		sleep 1; \
	done
	@echo ""
	@echo "OpenHands is ready!"
	@echo "Access the Web GUI at: http://localhost:$(PORT)"
	@echo "Workspace bind-mounted from: $(WORKSPACE_DIR)"

## Stop OpenHands container
down:
	@docker compose down

## Restart OpenHands container
restart:
	@docker compose restart openhands

## Follow container logs
logs:
	@docker compose logs -f openhands

## Check container status
status:
	@docker compose ps

## Open interactive bash shell inside container
shell:
	@docker compose exec openhands /bin/bash

## Stop containers and remove orphan containers
clean:
	@docker compose down --remove-orphans
