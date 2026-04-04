"""Generate all charts for the paper."""
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

DATA = Path(__file__).parent / "data"
CHARTS = Path(__file__).parent / "charts"
CHARTS.mkdir(exist_ok=True)

# Color scheme
COLORS = {
    "poet": "#2196F3",
    "critic": "#FF9800",
    "casino_host": "#9C27B0",
    "gambler": "#F44336",
    "advisor": "#4CAF50",
    "bootstrap": "#9E9E9E",
}
LABELS = {
    "poet": "Poet (30)",
    "critic": "Critic (25)",
    "casino_host": "Casino Host (5)",
    "gambler": "Gambler (50)",
    "advisor": "Advisor (39)",
}


def load_archetype_summary():
    rows = []
    with open(DATA / "archetype_summary.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["provided"] = int(r["provided"])
            r["consumed"] = int(r["consumed"])
            r["net_balance"] = float(r["net_balance"])
            r["num_peers"] = int(r["num_peers"])
            r["zero_provide"] = int(r["zero_provide"])
            rows.append(r)
    return rows


def chart_bilateral_by_archetype():
    """Grouped bar: provided vs consumed per archetype."""
    rows = load_archetype_summary()
    arch_agg = defaultdict(lambda: {"provided": 0, "consumed": 0, "nodes": 0})
    for r in rows:
        a = r["archetype"]
        if a == "bootstrap":
            continue
        arch_agg[a]["provided"] += r["provided"]
        arch_agg[a]["consumed"] += r["consumed"]
        arch_agg[a]["nodes"] += 1

    archetypes = ["poet", "critic", "casino_host", "gambler", "advisor"]
    provided = [arch_agg[a]["provided"] / arch_agg[a]["nodes"] for a in archetypes]
    consumed = [arch_agg[a]["consumed"] / arch_agg[a]["nodes"] for a in archetypes]

    x = np.arange(len(archetypes))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, provided, width, label="Skills Provided / node",
                   color=[COLORS[a] for a in archetypes], alpha=0.8)
    bars2 = ax.bar(x + width/2, consumed, width, label="Skills Consumed / node",
                   color=[COLORS[a] for a in archetypes], alpha=0.4,
                   edgecolor=[COLORS[a] for a in archetypes], linewidth=2)

    ax.set_ylabel("Skills per Node", fontsize=12)
    ax.set_title("Bilateral Trade: Providers vs Consumers", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([LABELS[a] for a in archetypes], fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    # Add value labels
    for bar in bars1:
        h = bar.get_height()
        if h > 1:
            ax.text(bar.get_x() + bar.get_width()/2, h + 1, f"{h:.0f}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
    for bar in bars2:
        h = bar.get_height()
        if h > 1:
            ax.text(bar.get_x() + bar.get_width()/2, h + 1, f"{h:.0f}",
                    ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    fig.savefig(CHARTS / "bilateral_by_archetype.png", dpi=150)
    plt.close(fig)
    print("  bilateral_by_archetype.png")


def chart_provide_consume_scatter():
    """Scatter: x=provided, y=consumed, color=archetype."""
    rows = load_archetype_summary()
    fig, ax = plt.subplots(figsize=(10, 8))

    for r in rows:
        a = r["archetype"]
        if a == "bootstrap":
            continue
        ax.scatter(r["provided"], r["consumed"],
                   c=COLORS.get(a, "#999"), alpha=0.6, s=50,
                   edgecolors="white", linewidth=0.5)

    # Diagonal line: provide = consume (balanced trade)
    max_val = max(max(r["provided"] for r in rows), max(r["consumed"] for r in rows))
    ax.plot([0, max_val], [0, max_val], "k--", alpha=0.3, label="Balanced trade line")

    # Legend
    patches = [mpatches.Patch(color=COLORS[a], label=LABELS[a])
               for a in ["poet", "critic", "casino_host", "gambler", "advisor"]]
    ax.legend(handles=patches, fontsize=10, loc="upper right")

    ax.set_xlabel("Skills Provided", fontsize=12)
    ax.set_ylabel("Skills Consumed", fontsize=12)
    ax.set_title("Provider vs Consumer: Each Node's Bilateral Trade Position", fontsize=13, fontweight="bold")
    ax.grid(alpha=0.3)

    # Annotate quadrants
    ax.text(max_val * 0.7, max_val * 0.05, "PRODUCERS\n(provide >> consume)",
            fontsize=9, alpha=0.5, ha="center")
    ax.text(max_val * 0.05, max_val * 0.7, "FREE-RIDERS\n(consume >> provide)",
            fontsize=9, alpha=0.5, ha="center")

    fig.tight_layout()
    fig.savefig(CHARTS / "provide_consume_scatter.png", dpi=150)
    plt.close(fig)
    print("  provide_consume_scatter.png")


def chart_net_balance_distribution():
    """Histogram of net balances by archetype."""
    rows = load_archetype_summary()
    fig, ax = plt.subplots(figsize=(10, 6))

    for a in ["poet", "casino_host", "critic", "gambler", "advisor"]:
        vals = [r["net_balance"] for r in rows if r["archetype"] == a]
        if vals:
            ax.hist(vals, bins=20, alpha=0.5, label=LABELS[a], color=COLORS[a])

    ax.axvline(x=0, color="black", linestyle="-", alpha=0.5)
    ax.set_xlabel("Net Credit Position", fontsize=12)
    ax.set_ylabel("Number of Nodes", fontsize=12)
    ax.set_title("Credit Distribution: Producers (left) vs Consumers (right)", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(CHARTS / "net_balance_distribution.png", dpi=150)
    plt.close(fig)
    print("  net_balance_distribution.png")


def chart_free_rider_fraction():
    """Stacked bar: zero-provide % by archetype."""
    rows = load_archetype_summary()
    arch_agg = defaultdict(lambda: {"total": 0, "zero": 0})
    for r in rows:
        a = r["archetype"]
        if a == "bootstrap":
            continue
        arch_agg[a]["total"] += 1
        arch_agg[a]["zero"] += r["zero_provide"]

    archetypes = ["poet", "critic", "casino_host", "gambler", "advisor"]
    zero_pct = [arch_agg[a]["zero"] / arch_agg[a]["total"] * 100 for a in archetypes]
    active_pct = [100 - z for z in zero_pct]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(archetypes))
    ax.bar(x, active_pct, label="Provided >= 1 skill", color=[COLORS[a] for a in archetypes], alpha=0.8)
    ax.bar(x, zero_pct, bottom=active_pct, label="Provided ZERO skills",
           color=[COLORS[a] for a in archetypes], alpha=0.25,
           edgecolor=[COLORS[a] for a in archetypes], linewidth=2, hatch="//")

    ax.set_ylabel("% of Nodes", fontsize=12)
    ax.set_title("Free-Riding Rate by Archetype (% providing zero skills)", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([LABELS[a] for a in archetypes], fontsize=10)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 105)

    # Add percentage labels
    for i, z in enumerate(zero_pct):
        if z > 5:
            ax.text(i, 100 - z/2 + z, f"{z:.0f}%", ha="center", va="center",
                    fontsize=11, fontweight="bold", color="white")

    fig.tight_layout()
    fig.savefig(CHARTS / "free_rider_fraction.png", dpi=150)
    plt.close(fig)
    print("  free_rider_fraction.png")


def chart_receipt_volume():
    """Bar chart of receipt types."""
    counts = defaultdict(int)
    with open(DATA / "receipts_summary.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            counts[r["document_type"]] += int(r["count"])

    types = sorted(counts.keys(), key=lambda t: -counts[t])
    vals = [counts[t] for t in types]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.barh(range(len(types)), vals, color="#1976D2", alpha=0.8)
    ax.set_yticks(range(len(types)))
    ax.set_yticklabels(types, fontsize=9)
    ax.set_xlabel("Count", fontsize=12)
    ax.set_title(f"Signed Receipt Volume ({sum(vals):,} total across 134 nodes)", fontsize=13, fontweight="bold")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)

    for bar, val in zip(bars, vals):
        ax.text(val + 20, bar.get_y() + bar.get_height()/2, f"{val:,}",
                va="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(CHARTS / "receipt_volume.png", dpi=150)
    plt.close(fig)
    print("  receipt_volume.png")


def chart_peer_connectivity():
    """Network connectivity: number of bilateral peers per node by archetype."""
    rows = load_archetype_summary()
    fig, ax = plt.subplots(figsize=(10, 6))

    for a in ["poet", "casino_host", "critic", "gambler", "advisor"]:
        vals = [r["num_peers"] for r in rows if r["archetype"] == a]
        if vals:
            positions = [{"poet": 1, "critic": 2, "casino_host": 3, "gambler": 4, "advisor": 5}[a]]
            vp = ax.violinplot([vals], positions=positions, showmeans=True, showmedians=True)
            for pc in vp["bodies"]:
                pc.set_facecolor(COLORS[a])
                pc.set_alpha(0.6)

    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels([LABELS[a] for a in ["poet", "critic", "casino_host", "gambler", "advisor"]], fontsize=9)
    ax.set_ylabel("Number of Bilateral Peers", fontsize=12)
    ax.set_title("Peer Connectivity by Archetype", fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(CHARTS / "peer_connectivity.png", dpi=150)
    plt.close(fig)
    print("  peer_connectivity.png")


def chart_economy_flow():
    """Sankey-style: credit flow between archetypes (simplified as stacked bar)."""
    # Load bilateral positions and aggregate by archetype pair
    def archetype(node_name):
        n = int(node_name.replace("node-", ""))
        if n == 1: return "bootstrap"
        if 2 <= n <= 31: return "poet"
        if 32 <= n <= 56: return "critic"
        if 57 <= n <= 61: return "casino_host"
        if 62 <= n <= 111: return "gambler"
        if 112 <= n <= 150: return "advisor"
        return "unknown"

    flows = defaultdict(lambda: {"provided": 0, "consumed": 0})
    with open(DATA / "bilateral_positions.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            a = archetype(r["node"])
            if a == "bootstrap":
                continue
            flows[a]["provided"] += int(r["tasks_provided"])
            flows[a]["consumed"] += int(r["tasks_consumed"])

    archetypes = ["poet", "casino_host", "critic", "gambler", "advisor"]
    fig, ax = plt.subplots(figsize=(10, 6))

    provided = [flows[a]["provided"] for a in archetypes]
    consumed = [flows[a]["consumed"] for a in archetypes]
    net = [p - c for p, c in zip(provided, consumed)]

    x = np.arange(len(archetypes))
    ax.bar(x, net, color=[COLORS[a] for a in archetypes], alpha=0.8,
           edgecolor="white", linewidth=1.5)

    ax.axhline(y=0, color="black", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([LABELS[a] for a in archetypes], fontsize=10)
    ax.set_ylabel("Net Skills (Provided - Consumed)", fontsize=12)
    ax.set_title("Economic Flow: Who Produces, Who Consumes", fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    for i, n in enumerate(net):
        ax.text(i, n + (20 if n >= 0 else -40), f"{n:+d}",
                ha="center", fontsize=11, fontweight="bold")

    fig.tight_layout()
    fig.savefig(CHARTS / "economy_flow.png", dpi=150)
    plt.close(fig)
    print("  economy_flow.png")


if __name__ == "__main__":
    print("Generating charts...")
    chart_bilateral_by_archetype()
    chart_provide_consume_scatter()
    chart_net_balance_distribution()
    chart_free_rider_fraction()
    chart_receipt_volume()
    chart_peer_connectivity()
    chart_economy_flow()
    print("Done.")
