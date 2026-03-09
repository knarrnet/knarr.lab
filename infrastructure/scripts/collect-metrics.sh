#!/usr/bin/env bash
# Collect metrics from a running knarr.lab swarm
#
# Usage: ./collect-metrics.sh <experiment-dir> [interval-seconds]
#
# Polls each node's cockpit API and writes metrics to the experiment's data/ dir.

set -euo pipefail

EXPERIMENT_DIR="${1:?Usage: $0 <experiment-dir> [interval-seconds]}"
INTERVAL="${2:-60}"
TOKEN="${AUTH_TOKEN:-lab-token}"
DATA_DIR="${EXPERIMENT_DIR}/data/metrics"

mkdir -p "$DATA_DIR"

METRICS_FILE="${DATA_DIR}/timeseries.csv"

# Write header if file doesn't exist
if [ ! -f "$METRICS_FILE" ]; then
    echo "timestamp,node,metric,value" > "$METRICS_FILE"
fi

echo "Collecting metrics every ${INTERVAL}s to ${METRICS_FILE}"
echo "Press Ctrl+C to stop"

while true; do
    TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Discover running nodes from docker compose
    NODES=$(docker compose ps --format '{{.Name}}' 2>/dev/null | grep -v bootstrap | grep -v vllm || true)

    for NODE in $NODES; do
        # Get node status via cockpit
        STATUS=$(docker exec "$NODE" curl -sk \
            -H "Authorization: Bearer $TOKEN" \
            "https://localhost:8081/api/status" 2>/dev/null || echo "{}")

        if [ "$STATUS" != "{}" ]; then
            # Extract key metrics (jq required)
            PEERS=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('peer_count',0))" 2>/dev/null || echo 0)
            SKILLS=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('skill_count',0))" 2>/dev/null || echo 0)

            echo "${TS},${NODE},peer_count,${PEERS}" >> "$METRICS_FILE"
            echo "${TS},${NODE},skill_count,${SKILLS}" >> "$METRICS_FILE"
        fi
    done

    sleep "$INTERVAL"
done
