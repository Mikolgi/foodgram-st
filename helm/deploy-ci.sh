#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

: "${VAULT_ADDR:?VAULT_ADDR is required}"
: "${VAULT_TOKEN:?VAULT_TOKEN is required}"
: "${BACKEND_IMAGE_TAG:?BACKEND_IMAGE_TAG is required}"
: "${FRONTEND_IMAGE_TAG:?FRONTEND_IMAGE_TAG is required}"

export VAULT_AUTH_METHOD="${VAULT_AUTH_METHOD:-token}"
export HELM_SECRETS_BACKEND="${HELM_SECRETS_BACKEND:-vals}"
export HELM_SECRETS_DRIVER="${HELM_SECRETS_DRIVER:-vals}"

helm dependency update app

vals eval -f app/values.yaml | helm upgrade --install foodgram app \
  -n "${HELM_NAMESPACE:-foodgram}" \
  --create-namespace \
  -f - \
  --set "back.deployment.image.tag=${BACKEND_IMAGE_TAG}" \
  --set "worker.deployment.image.tag=${BACKEND_IMAGE_TAG}" \
  --set "flower.deployment.image.tag=${BACKEND_IMAGE_TAG}" \
  --set "front.deployment.image.tag=${FRONTEND_IMAGE_TAG}"
