#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

: "${GITHUB_PAT:?GITHUB_PAT is required}"

ARC_NAMESPACE="${ARC_NAMESPACE:-arc-systems}"
ARC_CONTROLLER_RELEASE="${ARC_CONTROLLER_RELEASE:-arc}"
ARC_RUNNER_RELEASE="${ARC_RUNNER_RELEASE:-arc-runner}"
GITHUB_CONFIG_URL="${GITHUB_CONFIG_URL:-https://github.com/Mikolgi/foodgram-st}"

helm upgrade --install "${ARC_CONTROLLER_RELEASE}" \
  --namespace "${ARC_NAMESPACE}" \
  --create-namespace \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller

kubectl apply -f "${REPO_ROOT}/k8s/arc-runner-rbac.yaml"

helm upgrade --install "${ARC_RUNNER_RELEASE}" \
  --namespace "${ARC_NAMESPACE}" \
  --create-namespace \
  -f "${SCRIPT_DIR}/github-runner-values.yaml" \
  --set "githubConfigUrl=${GITHUB_CONFIG_URL}" \
  --set "githubConfigSecret.github_token=${GITHUB_PAT}" \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set
