#!/bin/bash
# manage_scaling.sh
# Usage: ./manage_scaling.sh LIVE (or ECO)

MODE=$1
PROJECT_ID="stately-lambda-495113-j3"
REGION="us-central1"
SERVICES=("backend" "axiom")

if [ "$MODE" == "LIVE" ]; then
    echo "🚀 Switching to LIVE Mode (Always-on, High Performance)..."
    for service in "${SERVICES[@]}"; do
        gcloud run services update $service --region=$REGION --min-instances=1 --no-cpu-throttling --quiet
    done
elif [ "$MODE" == "ECO" ]; then
    echo "🌿 Switching to ECO Mode (Scale-to-zero, Cost Saving)..."
    for service in "${SERVICES[@]}"; do
        gcloud run services update $service --region=$REGION --min-instances=0 --cpu-throttling --quiet
    done
else
    echo "Usage: ./manage_scaling.sh [LIVE|ECO]"
    exit 1
fi

echo "✅ Mode applied: $MODE"
