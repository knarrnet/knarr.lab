"""Analyze collected experiment metrics and produce summary statistics.

Reads timeseries.csv and pairs.csv from the experiment data directory and
produces:
  - Terminal summary table (per-node balance, tasks, revenue, cost)
  - Network-level stats (Gini, density, peer entropy)
  - Top 5 producers / consumers
  - experiments/{id}/data/analysis/summary.json
  - experiments/{id}/data/analysis/timeseries_plot.png  (--plot flag, matplotlib required)

Usage:
    python -m scoring.analyze --experiment 002
    python -m scoring.analyze --experiment 002 --plot
"""

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Gini coefficient
# ---------------------------------------------------------------------------

def gini(values: list[float]) -> float:
    """Compute Gini coefficient on a list of (possibly negative) values.

    Uses absolute values so it measures spread regardless of sign.
    Returns 0 if all values are equal or the list is empty.
    """
    arr = sorted(abs(v) for v in values)
    n = len(arr)
    if n == 0:
        return 0.0
    total = sum(arr)
    if total == 0:
        return 0.0
    cumsum = sum((2 * i - n - 1) * v for i, v in enumerate(arr, 1))
    return cumsum / (n * total)


# ---------------------------------------------------------------------------
# Shannon entropy
# ---------------------------------------------------------------------------

def shannon_entropy(counts: list[float]) -> float:
    """Shannon entropy (bits) of a probability distribution derived from counts."""
    total = sum(counts)
    if total == 0:
        return 0.0
    probs = [c / total for c in counts if c > 0]
    return -sum(p * math.log2(p) for p in probs)


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

def load_timeseries(metrics_dir: Path) -> dict[str, dict[str, list[float]]]:
    """
    Load timeseries.csv into:
      { node: { metric: [value, ...] } }

    Values are ordered by timestamp (CSV is appended in order).
    """
    ts_path = metrics_dir / "timeseries.csv"
    if not ts_path.exists():
        return {}

    data: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    with open(ts_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            node = row["node"]
            metric = row["metric"]
            try:
                value = float(row["value"])
            except (ValueError, KeyError):
                continue
            data[node][metric].append(value)

    return data


def load_pairs(metrics_dir: Path) -> list[dict]:
    """Load pairs.csv into a list of row dicts."""
    pairs_path = metrics_dir / "pairs.csv"
    if not pairs_path.exists():
        return []

    rows = []
    with open(pairs_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "timestamp": row["timestamp"],
                    "node_a": row["node_a"],
                    "node_b": row["node_b"],
                    "bilateral_balance": float(row["bilateral_balance"]),
                    "trade_count": int(float(row["trade_count"])),
                    "utilization_pct": float(row["utilization_pct"]),
                })
            except (ValueError, KeyError):
                continue
    return rows


# ---------------------------------------------------------------------------
# Per-node summary
# ---------------------------------------------------------------------------

def last_value(series: list[float]) -> float:
    """Return the last recorded value, or 0.0 if empty."""
    return series[-1] if series else 0.0


def build_node_summary(ts_data: dict[str, dict[str, list[float]]]) -> list[dict]:
    """
    For each node return a dict with the last snapshot value for each metric.
    """
    summaries = []
    for node, metrics in sorted(ts_data.items()):
        summaries.append({
            "node": node,
            "balance": last_value(metrics.get("balance", [])),
            "tasks_provided": last_value(metrics.get("tasks_provided", [])),
            "tasks_consumed": last_value(metrics.get("tasks_consumed", [])),
            "revenue": last_value(metrics.get("revenue", [])),
            "cost": last_value(metrics.get("cost", [])),
            "credit_utilization": last_value(metrics.get("credit_utilization", [])),
            "peer_count": last_value(metrics.get("peer_count", [])),
            "snapshots": len(metrics.get("balance", [])),
        })
    return summaries


# ---------------------------------------------------------------------------
# Network statistics
# ---------------------------------------------------------------------------

def compute_network_stats(
    node_summaries: list[dict],
    pairs_rows: list[dict],
) -> dict:
    """
    Compute network-level aggregate statistics.

    Returns a dict with:
      total_transactions, unique_trading_pairs, total_nodes,
      gini_balance, network_density, peer_entropy_median,
      net_producer_count, net_consumer_count,
      max_utilization, mean_utilization,
      peak_bilateral_utilization
    """
    n = len(node_summaries)
    if n == 0:
        return {}

    # Final balances for Gini
    balances = [s["balance"] for s in node_summaries]

    # Total tasks from last snapshot
    total_tasks_provided = sum(s["tasks_provided"] for s in node_summaries)
    total_tasks_consumed = sum(s["tasks_consumed"] for s in node_summaries)
    # Each transaction is counted once on the provider side
    total_transactions = int(total_tasks_provided)

    # Unique trading pairs: use the latest snapshot's pairs
    # Normalise (node_a, node_b) → frozenset so (A,B) == (B,A)
    # Group by latest timestamp
    if pairs_rows:
        # Find the latest timestamp
        latest_ts = max(r["timestamp"] for r in pairs_rows)
        latest_pairs = [r for r in pairs_rows if r["timestamp"] == latest_ts]

        trading_pairs: set[frozenset] = set()
        for row in latest_pairs:
            if row["trade_count"] > 0:
                trading_pairs.add(frozenset([row["node_a"], row["node_b"]]))

        unique_pairs = len(trading_pairs)
        peak_bilateral_util = max(
            (r["utilization_pct"] for r in latest_pairs), default=0.0
        )
    else:
        unique_pairs = 0
        peak_bilateral_util = 0.0

    # Network density: actual pairs / max possible pairs
    max_possible = n * (n - 1) / 2 if n > 1 else 1
    network_density = unique_pairs / max_possible

    # Gini on final balances
    gini_val = gini(balances)

    # Net producers/consumers (based on final balance)
    net_producers = sum(1 for s in node_summaries if s["balance"] > 0)
    net_consumers = sum(1 for s in node_summaries if s["balance"] < 0)

    # Credit utilization stats
    utils = [s["credit_utilization"] for s in node_summaries if s["credit_utilization"] > 0]
    max_util = max(utils) if utils else 0.0
    mean_util = sum(utils) / len(utils) if utils else 0.0

    # Peer entropy per node: distribution of trade_count across trading partners
    # Use all pair rows (latest snapshot)
    if pairs_rows:
        latest_ts = max(r["timestamp"] for r in pairs_rows)
        latest_pairs = [r for r in pairs_rows if r["timestamp"] == latest_ts]

        node_trade_volumes: dict[str, list[float]] = defaultdict(list)
        for row in latest_pairs:
            if row["trade_count"] > 0:
                node_trade_volumes[row["node_a"]].append(float(row["trade_count"]))

        entropies = [
            shannon_entropy(vols)
            for vols in node_trade_volumes.values()
            if vols
        ]
        peer_entropy_median = sorted(entropies)[len(entropies) // 2] if entropies else 0.0
        peer_entropy_mean = sum(entropies) / len(entropies) if entropies else 0.0
    else:
        peer_entropy_median = 0.0
        peer_entropy_mean = 0.0

    return {
        "total_nodes": n,
        "total_transactions": total_transactions,
        "total_tasks_provided": int(total_tasks_provided),
        "total_tasks_consumed": int(total_tasks_consumed),
        "unique_trading_pairs": unique_pairs,
        "max_possible_pairs": int(max_possible),
        "network_density": round(network_density, 4),
        "gini_balance": round(gini_val, 4),
        "net_producer_count": net_producers,
        "net_consumer_count": net_consumers,
        "max_credit_utilization": round(max_util, 1),
        "mean_credit_utilization": round(mean_util, 1),
        "peak_bilateral_utilization": round(peak_bilateral_util, 1),
        "peer_entropy_median": round(peer_entropy_median, 4),
        "peer_entropy_mean": round(peer_entropy_mean, 4),
    }


# ---------------------------------------------------------------------------
# Terminal output
# ---------------------------------------------------------------------------

def print_node_table(node_summaries: list[dict], top_n: int = 100):
    """Print a formatted per-node summary table."""
    headers = ["Node", "Balance", "Provided", "Consumed", "Revenue", "Cost", "Util%", "Peers"]
    col_w = [10, 9, 10, 10, 9, 8, 7, 6]

    def row_str(cols):
        return "  ".join(str(c).rjust(w) for c, w in zip(cols, col_w))

    print(row_str(headers))
    print("  ".join("-" * w for w in col_w))
    for s in node_summaries[:top_n]:
        print(row_str([
            s["node"],
            f"{s['balance']:+.1f}",
            int(s["tasks_provided"]),
            int(s["tasks_consumed"]),
            f"{s['revenue']:.1f}",
            f"{s['cost']:.1f}",
            f"{s['credit_utilization']:.0f}%",
            int(s["peer_count"]),
        ]))


def print_network_stats(stats: dict):
    """Print network-level statistics."""
    print(f"  Total nodes observed     : {stats.get('total_nodes', 0)}")
    print(f"  Total transactions       : {stats.get('total_transactions', 0):,}")
    print(f"  Total tasks provided     : {stats.get('total_tasks_provided', 0):,}")
    print(f"  Total tasks consumed     : {stats.get('total_tasks_consumed', 0):,}")
    print(f"  Unique trading pairs     : {stats.get('unique_trading_pairs', 0)}"
          f"  /  {stats.get('max_possible_pairs', 0)} possible")
    print(f"  Network density          : {stats.get('network_density', 0):.4f}")
    print(f"  Gini (final balances)    : {stats.get('gini_balance', 0):.4f}")
    print(f"  Net producers            : {stats.get('net_producer_count', 0)}")
    print(f"  Net consumers            : {stats.get('net_consumer_count', 0)}")
    print(f"  Max credit utilization   : {stats.get('max_credit_utilization', 0):.1f}%")
    print(f"  Mean credit utilization  : {stats.get('mean_credit_utilization', 0):.1f}%")
    print(f"  Peak bilateral util      : {stats.get('peak_bilateral_utilization', 0):.1f}%")
    print(f"  Peer entropy (median)    : {stats.get('peer_entropy_median', 0):.4f} bits")
    print(f"  Peer entropy (mean)      : {stats.get('peer_entropy_mean', 0):.4f} bits")


# ---------------------------------------------------------------------------
# Plot generation
# ---------------------------------------------------------------------------

def generate_plot(ts_data: dict, analysis_dir: Path):
    """Generate a balance-over-time line chart per node. Requires matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        import numpy as np
    except ImportError:
        print("  matplotlib not available — skipping plot generation")
        return

    fig, ax = plt.subplots(figsize=(14, 7))

    nodes = sorted(ts_data.keys())
    colors = cm.tab20(np.linspace(0, 1, max(len(nodes), 1)))

    for idx, node in enumerate(nodes):
        balance_series = ts_data[node].get("balance", [])
        if not balance_series:
            continue
        x = list(range(len(balance_series)))
        ax.plot(x, balance_series, linewidth=0.8, alpha=0.7,
                color=colors[idx % len(colors)], label=node)

    ax.axhline(0, color="black", linewidth=0.5, linestyle="--", alpha=0.5)
    ax.set_xlabel("Snapshot index")
    ax.set_ylabel("Balance (credits)")
    ax.set_title("Node balances over time")

    # Legend only if reasonable number of nodes
    if len(nodes) <= 20:
        ax.legend(fontsize=6, loc="upper left", ncol=2)

    plt.tight_layout()
    plot_path = analysis_dir / "timeseries_plot.png"
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Plot saved: {plot_path}")


# ---------------------------------------------------------------------------
# Experiment directory resolution
# ---------------------------------------------------------------------------

def find_experiment_dir(experiment_id: str) -> Path:
    experiments = Path(__file__).parent.parent / "experiments"
    for d in sorted(experiments.iterdir()):
        if d.is_dir() and d.name.startswith(experiment_id):
            return d
    raise FileNotFoundError(
        f"No experiment directory matching '{experiment_id}' under {experiments}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Analyze collected experiment metrics"
    )
    parser.add_argument(
        "--experiment", required=True,
        help="Experiment ID prefix (e.g. 002)",
    )
    parser.add_argument(
        "--plot", action="store_true",
        help="Generate timeseries_plot.png (requires matplotlib)",
    )
    parser.add_argument(
        "--top", type=int, default=20,
        help="Number of nodes to show in full table (default: 20)",
    )
    args = parser.parse_args()

    experiment_dir = find_experiment_dir(args.experiment)
    metrics_dir = experiment_dir / "data" / "metrics"
    analysis_dir = experiment_dir / "data" / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    print(f"Experiment : {experiment_dir.name}")
    print(f"Metrics dir: {metrics_dir}")
    print()

    # Load data
    ts_data = load_timeseries(metrics_dir)
    pairs_rows = load_pairs(metrics_dir)

    if not ts_data:
        print("No timeseries data found. Run collect.py first.")
        sys.exit(1)

    print(f"Loaded {len(ts_data)} nodes, {len(pairs_rows)} bilateral pair rows")
    print()

    # Build summaries
    node_summaries = build_node_summary(ts_data)
    net_stats = compute_network_stats(node_summaries, pairs_rows)

    # --- Per-node table ---
    print("=" * 72)
    print("PER-NODE SUMMARY  (last snapshot values)")
    print("=" * 72)
    print_node_table(node_summaries, top_n=args.top)
    if len(node_summaries) > args.top:
        print(f"  ... ({len(node_summaries) - args.top} more nodes not shown, use --top N)")
    print()

    # --- Top 5 providers ---
    print("TOP 5 PROVIDERS (by revenue)")
    print("-" * 40)
    by_rev = sorted(node_summaries, key=lambda s: s["revenue"], reverse=True)
    for i, s in enumerate(by_rev[:5], 1):
        print(f"  {i}. {s['node']}  revenue={s['revenue']:.1f}  tasks_provided={int(s['tasks_provided'])}")
    print()

    # --- Top 5 consumers ---
    print("TOP 5 CONSUMERS (by cost)")
    print("-" * 40)
    by_cost = sorted(node_summaries, key=lambda s: s["cost"], reverse=True)
    for i, s in enumerate(by_cost[:5], 1):
        print(f"  {i}. {s['node']}  cost={s['cost']:.1f}  tasks_consumed={int(s['tasks_consumed'])}")
    print()

    # --- Network stats ---
    print("=" * 72)
    print("NETWORK STATISTICS")
    print("=" * 72)
    print_network_stats(net_stats)
    print()

    # --- Spec target comparison ---
    print("SPEC TARGETS (from Tyr's design)")
    print("-" * 72)
    targets = [
        ("Total transactions",       net_stats.get("total_transactions", 0),         "10000-50000",  ""),
        ("Unique bilateral pairs",   net_stats.get("unique_trading_pairs", 0),       "200-500",      ""),
        ("Gini coefficient",         net_stats.get("gini_balance", 0),               "0.30-0.60",    ".4f"),
        ("Network density",          net_stats.get("network_density", 0),            ">0.04",        ".4f"),
        ("Peer entropy (median)",    net_stats.get("peer_entropy_median", 0),        "1.5-2.5 bits", ".4f"),
        ("Peak bilateral util",      net_stats.get("peak_bilateral_utilization", 0), ">50%",         ".1f"),
    ]
    for label, value, target, fmt in targets:
        val_str = f"{value:{fmt}}" if fmt else str(value)
        print(f"  {label:<30} current={val_str:<12}  target={target}")
    print()

    # --- Write summary.json ---
    summary = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "experiment": experiment_dir.name,
        "network": net_stats,
        "nodes": node_summaries,
        "top_providers": [
            {"node": s["node"], "revenue": s["revenue"],
             "tasks_provided": int(s["tasks_provided"])}
            for s in by_rev[:5]
        ],
        "top_consumers": [
            {"node": s["node"], "cost": s["cost"],
             "tasks_consumed": int(s["tasks_consumed"])}
            for s in by_cost[:5]
        ],
    }
    summary_path = analysis_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON written: {summary_path}")

    # --- Optional plot ---
    if args.plot:
        print("Generating plot...")
        generate_plot(ts_data, analysis_dir)

    print()
    print("Done.")


if __name__ == "__main__":
    main()
