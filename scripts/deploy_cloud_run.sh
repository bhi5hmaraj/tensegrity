#!/usr/bin/env bash
set -euo pipefail

# Deploy PadAI to Cloud Run using gcloud directly (no Terraform).
# - Builds the image via Cloud Build
# - Pushes to Artifact Registry (creates repo on first push)
# - Deploys to Cloud Run service
#
# Usage:
#   scripts/deploy_cloud_run.sh [-d|--debug] <project> <region> <service>
#
# Examples:
#   scripts/deploy_cloud_run.sh my-proj us-central1 tensegrity
#   scripts/deploy_cloud_run.sh my-proj us-central1 tensegrity-preview
#
# Optional env:
#   ENV_VARS   Comma-separated env vars for the service
#              (default: WORKSPACE_PATH=/workspace,LOG_LEVEL=INFO)

DEBUG=0
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--debug) DEBUG=1; shift ;;
    *) ARGS+=("$1"); shift ;;
  esac
done

if [[ ${#ARGS[@]} -lt 3 ]]; then
  echo "Usage: $0 [-d|--debug] <project> <region> <service>" >&2
  exit 2
fi

PROJECT="${ARGS[0]}"
REGION="${ARGS[1]}"
SERVICE="${ARGS[2]}"

ENV_VARS="${ENV_VARS:-WORKSPACE_PATH=/workspace,LOG_LEVEL=INFO}"

if [[ $DEBUG -eq 1 ]]; then
  set -x
  export CLOUDSDK_CORE_VERBOSITY=debug
  export CLOUDSDK_CORE_LOG_HTTP=true
fi

echo "→ Project: $PROJECT  Region: $REGION  Service: $SERVICE  Debug: $DEBUG"

echo "→ Ensuring required APIs (best-effort)"
set +e
for SVC in run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com; do
  gcloud services enable "$SVC" --project "$PROJECT" \
    || echo "WARN: could not enable $SVC (missing permission or already enabled)"
done
set -e

REPO="tensegrity"
IMAGE_PATH="$REGION-docker.pkg.dev/$PROJECT/$REPO/$SERVICE"
TAG=$(date +%Y%m%d-%H%M%S)
if git rev-parse --short HEAD >/dev/null 2>&1; then GIT_SHA=$(git rev-parse --short HEAD); TAG="$TAG-$GIT_SHA"; fi
IMAGE="$IMAGE_PATH:$TAG"

echo "→ Building image with Cloud Build: $IMAGE"
gcloud builds submit --project "$PROJECT" --tag "$IMAGE" .

echo "→ Deploying to Cloud Run: $SERVICE ($REGION)"
gcloud run deploy "$SERVICE" \
  --project "$PROJECT" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "$ENV_VARS"

URL=$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format='value(status.url)')
echo "✓ Deployed: $URL"
