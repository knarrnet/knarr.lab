"""Collect and structure experiment data from a running or completed swarm.

Usage:
    python -m scoring.collect --experiment 001
    python -m scoring.collect --experiment 001 --loop 60
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def find_experiment_dir(experiment_id: str) -> Path:
    """Find experiment directory by ID prefix."""
    experiments = Path(__file__).parent.parent / "experiments"
    for d in sorted(experiments.iterdir()):
        if d.is_dir() and d.name.startswith(experiment_id):
            return d
    raise FileNotFoundError(f"No experiment matching '{experiment_id}'")


def collect_snapshot(experiment_dir: Path, token: str = "lab-token"):
    """Collect a single metrics snapshot from all nodes."""
    metrics_dir = experiment_dir / "data" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    csv_path = metrics_dir / "timeseries.csv"
    write_header = not csv_path.exists()

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["timestamp", "node", "metric", "value"])

        # Read config.yaml for node list
        config_path = experiment_dir / "config.yaml"
        if config_path.exists():
            try:
                import yaml
                with open(config_path) as cf:
                    config = yaml.safe_load(cf)
                # Extract node names from skill_distribution keys
                nodes = list(config.get("parameters", {}).get("skill_distribution", {}).keys())
            except Exception:
                nodes = []
        else:
            nodes = []

        if not nodes:
            print(f"  No nodes found in config.yaml, skipping snapshot")
            return

        for node in nodes:
            try:
                req = Request(
                    f"https://localhost:8081/api/status",
                    headers={"Authorization": f"Bearer {token}"},
                )
                # In Docker context, would need to route to correct container
                # This is a placeholder — real collection uses docker exec or per-node ports
                print(f"  {ts} {node}: collection stub (implement per-experiment)")
            except Exception as e:
                print(f"  {ts} {node}: error - {e}")


def main():
    parser = argparse.ArgumentParser(description="Collect experiment metrics")
    parser.add_argument("--experiment", required=True, help="Experiment ID (e.g., 001)")
    parser.add_argument("--loop", type=int, default=0, help="Collection interval in seconds (0=once)")
    parser.add_argument("--token", default="lab-token", help="Cockpit auth token")
    args = parser.parse_args()

    experiment_dir = find_experiment_dir(args.experiment)
    print(f"Experiment: {experiment_dir.name}")

    if args.loop > 0:
        print(f"Collecting every {args.loop}s (Ctrl+C to stop)")
        while True:
            collect_snapshot(experiment_dir, args.token)
            time.sleep(args.loop)
    else:
        collect_snapshot(experiment_dir, args.token)


if __name__ == "__main__":
    main()
