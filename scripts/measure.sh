#!/usr/bin/env bash
set -euo pipefail
IMAGE="${1:-data-processing-api:baseline}"
echo "Image: ${IMAGE}"
docker image inspect "$IMAGE" --format 'Size in bytes: {{.Size}}'
docker image ls "$IMAGE"
docker history "$IMAGE"
