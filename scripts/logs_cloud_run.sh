#!/usr/bin/env bash
set -euo pipefail

# logs_cloud_run.sh — Convenience wrapper to fetch Cloud Run service logs
#
# Usage:
#   scripts/logs_cloud_run.sh <project_id> <region> <service> [-n N] [--errors] [--follow]
#
# Examples:
#   scripts/logs_cloud_run.sh personal-457416 us-central1 tensegrity
#   scripts/logs_cloud_run.sh personal-457416 us-central1 tensegrity -n 500 --errors
#   scripts/logs_cloud_run.sh personal-457416 us-central1 tensegrity --follow

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <project_id> <region> <service> [-n N] [--errors] [--follow]" >&2
  exit 2
fi

PROJECT="$1"; REGION="$2"; SERVICE="$3"; shift 3
LIMIT=200
FILTER_ERRORS=0
FOLLOW=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n) LIMIT="$2"; shift 2 ;;
    --errors) FILTER_ERRORS=1; shift ;;
    --follow) FOLLOW=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

cmd=(gcloud run services logs read "$SERVICE" --region "$REGION" --project "$PROJECT" --limit "$LIMIT")
if [[ $FOLLOW -eq 1 ]]; then
  cmd+=(--stream)
fi

echo "[logs] Running: ${cmd[*]}"
if [[ $FILTER_ERRORS -eq 1 ]]; then
  "${cmd[@]}" | rg -i "error|exception|traceback|bd failed|timed out" --color=never || true
else
  "${cmd[@]}"
fi

