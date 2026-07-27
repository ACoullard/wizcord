#!/usr/bin/env bash
# Pull the latest pre-built images, recreate changed containers, and prune old images.
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"

docker compose -f "$COMPOSE_FILE" pull
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans
docker image prune -f
