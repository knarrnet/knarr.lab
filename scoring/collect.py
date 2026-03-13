"""Collect per-node and per-pair economic metrics from a running swarm cluster.

Polls each node's /api/status and /api/economy endpoints, writes rolling
timeseries CSVs, and handles connection failures gracefully.

Usage:
    python -m scoring.collect --experiment 002 --loop 300 --token knarr-cluster-local
    python -m scoring.collect --experiment 001 --once
"""

import argparse
import csv
import json
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Port range: node-001 → 8301 … node-100 → 8400
BASE_PORT = 8300
NODE_COUNT = 100
TOKEN_DEFAULT = "knarr-cluster-local"

# SSL context — cluster uses self-signed certs
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def node_port(node_name: str) -> int:
    """Map 'node-NNN' to external cockpit port (8301-8400)."""
    try:
        n = int(node_name.split("-")[-1])
        return BASE_PORT + n
    except (ValueError, IndexError):
        raise ValueError(f"Cannot parse node number from '{node_name}'")


def all_node_names() -> list[str]:
    return [f"node-{i:03d}" for i in range(1, NODE_COUNT + 1)]


def _get(url: str, token: str, timeout: int = 5) -> dict | None:
    """GET JSON from cockpit URL. Returns None on any error."""
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urlopen(req, timeout=timeout, context=_ssl_ctx) as resp:
            return json.loads(resp.read())
    except HTTPError as exc:
        print(f"  WARN  {url} → HTTP {exc.code}", file=sys.stderr)
        return None
    except URLError as exc:
        # Connection refused / timeout — node is down, silently skip
        return None
    except Exception as exc:
        print(f"  WARN  {url} → {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Per-node metric extraction
# ---------------------------------------------------------------------------

def extract_node_metrics(status: dict, economy: dict) -> dict:
    """
    Combine /api/status and /api/economy into a flat metric dict.

    Returns metrics keyed by metric name, values are floats.
    All keys in the spec:
      balance, tasks_provided, tasks_consumed, revenue, cost,
      credit_utilization, peer_count
    """
    metrics: dict[str, float] = {}

    # From /api/status
    metrics["peer_count"] = float(status.get("peer_count", 0))
    metrics["task_count"] = float(status.get("task_count", 0))

    # From /api/economy — summary gives net_position (= balance from node POV)
    summary = economy.get("summary", {})
    metrics["balance"] = float(summary.get("net_position", 0.0))

    # Aggregate peer-ledger data to get totals
    tasks_provided_total = 0
    tasks_consumed_total = 0
    revenue_total = 0.0
    cost_total = 0.0
    max_utilization = 0.0

    for peer in economy.get("peers", []):
        tp = int(peer.get("tasks_provided", 0))
        tc = int(peer.get("tasks_consumed", 0))
        bal = float(peer.get("balance", 0.0))
        util = float(peer.get("utilization_pct", 0.0))

        tasks_provided_total += tp
        tasks_consumed_total += tc

        # balance on the peer ledger entry is positive when they owe us
        # (we provided to them) and negative when we owe them (we consumed).
        # Revenue = sum of positive balances; cost = sum of negative balances.
        if bal > 0:
            revenue_total += bal
        else:
            cost_total += abs(bal)

        if util > max_utilization:
            max_utilization = util

    # Supplement revenue/cost from skill-level breakdowns if available
    rev_by_skill = economy.get("revenue_by_skill", [])
    cost_by_skill = economy.get("cost_by_skill", [])
    if rev_by_skill:
        revenue_total = sum(float(s.get("total", 0)) for s in rev_by_skill)
    if cost_by_skill:
        cost_total = sum(float(s.get("total", 0)) for s in cost_by_skill)

    metrics["tasks_provided"] = float(tasks_provided_total)
    metrics["tasks_consumed"] = float(tasks_consumed_total)
    metrics["revenue"] = revenue_total
    metrics["cost"] = cost_total
    metrics["credit_utilization"] = max_utilization

    return metrics


# ---------------------------------------------------------------------------
# Per-pair bilateral metric extraction
# ---------------------------------------------------------------------------

def extract_bilateral_metrics(node_name: str, economy: dict) -> list[dict]:
    """
    Return one row per (node_a, node_b) pair from this node's economy data.

    Each row:
      node_a, node_b, bilateral_balance, trade_count, utilization_pct
    """
    rows = []
    for peer in economy.get("peers", []):
        peer_id = peer.get("node_id", "unknown")[:16]
        bilateral_balance = float(peer.get("balance", 0.0))
        trade_count = int(peer.get("tasks_provided", 0)) + int(peer.get("tasks_consumed", 0))
        utilization_pct = float(peer.get("utilization_pct", 0.0))

        # Only record pairs that have actually traded
        if trade_count > 0:
            rows.append({
                "node_a": node_name,
                "node_b": peer_id,
                "bilateral_balance": bilateral_balance,
                "trade_count": trade_count,
                "utilization_pct": utilization_pct,
            })
    return rows


# ---------------------------------------------------------------------------
# Snapshot collection
# ---------------------------------------------------------------------------

def collect_snapshot(
    metrics_dir: Path,
    token: str,
    nodes: list[str] | None = None,
    verbose: bool = True,
) -> tuple[int, int]:
    """
    Collect one snapshot from all nodes. Writes to timeseries.csv and pairs.csv.

    Returns (nodes_ok, nodes_failed).
    """
    metrics_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ts_label = datetime.now(timezone.utc).strftime("%H:%M:%S")

    ts_path = metrics_dir / "timeseries.csv"
    pairs_path = metrics_dir / "pairs.csv"

    write_ts_header = not ts_path.exists()
    write_pairs_header = not pairs_path.exists()

    nodes_ok = 0
    nodes_failed = 0

    if nodes is None:
        nodes = all_node_names()

    with (
        open(ts_path, "a", newline="") as ts_f,
        open(pairs_path, "a", newline="") as pairs_f,
    ):
        ts_writer = csv.writer(ts_f)
        pairs_writer = csv.writer(pairs_f)

        if write_ts_header:
            ts_writer.writerow(["timestamp", "node", "metric", "value"])

        if write_pairs_header:
            pairs_writer.writerow([
                "timestamp", "node_a", "node_b",
                "bilateral_balance", "trade_count", "utilization_pct",
            ])

        for node in nodes:
            try:
                port = node_port(node)
            except ValueError as exc:
                print(f"  WARN  {exc}", file=sys.stderr)
                nodes_failed += 1
                continue

            base = f"https://localhost:{port}"

            # Fetch both endpoints
            status = _get(f"{base}/api/status", token)
            economy = _get(f"{base}/api/economy", token)

            if status is None and economy is None:
                if verbose:
                    print(f"  {ts_label}  {node}  DOWN")
                nodes_failed += 1
                continue

            # Use empty dicts if one endpoint fails
            status = status or {}
            economy = economy or {}

            # Per-node metrics
            node_metrics = extract_node_metrics(status, economy)
            for metric, value in node_metrics.items():
                ts_writer.writerow([ts, node, metric, value])

            # Per-pair bilateral rows
            bilateral = extract_bilateral_metrics(node, economy)
            for row in bilateral:
                pairs_writer.writerow([
                    ts,
                    row["node_a"],
                    row["node_b"],
                    row["bilateral_balance"],
                    row["trade_count"],
                    row["utilization_pct"],
                ])

            nodes_ok += 1
            if verbose:
                bal = node_metrics.get("balance", 0.0)
                tp = int(node_metrics.get("tasks_provided", 0))
                tc = int(node_metrics.get("tasks_consumed", 0))
                peers = int(node_metrics.get("peer_count", 0))
                print(
                    f"  {ts_label}  {node}  "
                    f"bal={bal:+.1f}  tp={tp}  tc={tc}  peers={peers}"
                )

    return nodes_ok, nodes_failed


# ---------------------------------------------------------------------------
# Experiment directory resolution
# ---------------------------------------------------------------------------

def find_experiment_dir(experiment_id: str) -> Path:
    """Find experiment directory by ID prefix (e.g. '002' → '002-creative-economy')."""
    experiments = Path(__file__).parent.parent / "experiments"
    for d in sorted(experiments.iterdir()):
        if d.is_dir() and d.name.startswith(experiment_id):
            return d
    raise FileNotFoundError(
        f"No experiment directory matching '{experiment_id}' under {experiments}"
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Collect economic metrics from a knarr swarm cluster"
    )
    parser.add_argument(
        "--experiment", required=True,
        help="Experiment ID prefix (e.g. 002)",
    )
    parser.add_argument(
        "--loop", type=int, default=0,
        help="Collection interval in seconds; 0 = collect once and exit",
    )
    parser.add_argument(
        "--token", default=TOKEN_DEFAULT,
        help="Cockpit auth token (default: knarr-cluster-local)",
    )
    parser.add_argument(
        "--nodes", default=None,
        help="Comma-separated node names to poll (default: node-001 … node-100)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-node output lines",
    )
    args = parser.parse_args()

    experiment_dir = find_experiment_dir(args.experiment)
    metrics_dir = experiment_dir / "data" / "metrics"

    node_list = None
    if args.nodes:
        node_list = [n.strip() for n in args.nodes.split(",") if n.strip()]

    print(f"Experiment : {experiment_dir.name}")
    print(f"Metrics dir: {metrics_dir}")
    print(f"Nodes      : {len(node_list) if node_list else NODE_COUNT} targets")
    print(f"Token      : {args.token[:8]}...")
    print(f"Interval   : {'once' if args.loop == 0 else f'{args.loop}s'}")
    print()

    iteration = 0
    while True:
        iteration += 1
        print(f"[snapshot #{iteration}]  {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
        ok, failed = collect_snapshot(
            metrics_dir,
            token=args.token,
            nodes=node_list,
            verbose=not args.quiet,
        )
        print(f"  => {ok} OK, {failed} failed")
        print()

        if args.loop == 0:
            break
        try:
            time.sleep(args.loop)
        except KeyboardInterrupt:
            print("Interrupted — stopping collection loop.")
            break


if __name__ == "__main__":
    main()
