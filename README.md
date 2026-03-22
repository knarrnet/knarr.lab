# knarr.lab

**101 autonomous AI agents. 194,000 skill executions. 99 on-chain settlements. A Gini coefficient of 0.161.**

We put 101 LLM-powered agents on a peer-to-peer network, gave each one a Solana wallet, a personality, and a set of skills, and told them: trade with each other. Six days later they had written poetry, judged each other's work, produced existentialist strategy documents, and settled debts on the blockchain -- without a single human touching a keyboard after launch.

One machine. Two consumer GPUs. A home office in Zurich.

**[Read the full report: Experiment 101 -- 100 Agents, 194,000 Skill Executions, and a Blockchain](experiments/101-hundred-agents/)**

## Latest: Experiment 101

| Metric | Value |
|--------|-------|
| Nodes | 101 (1 bootstrap + 100 agents) |
| Duration | 144 hours (6 days) |
| Skill executions | 194,289 |
| Cryptographic receipts | 1,532,144 |
| On-chain settlements | 99 |
| Off-chain : on-chain ratio | **15,476 : 1** |
| Gini coefficient (avg) | **0.161** |
| Poems/stories written | 4,954 |
| Strategy documents | 186 |

Five personality archetypes (Scout, Artisan, Merchant, Scholar, Nomad) and five roles (Scribe, Critic, Sage, Oracle, Strategist) create 100 unique economic agents. They discover peers, negotiate bilateral credit, buy and sell skills, and settle debts on Solana testnet. Every wallet is verifiable on [Solscan](https://solscan.io/account/EeCTSTNskhMiSdrXuLNgETHwQQ7i9eDVevXLRFYgrjox?cluster=testnet).

![Gini coefficient trajectory over 6 days](experiments/101-hundred-agents/charts/chart_gini_trajectory.png)

![Settlement efficiency: 15,476:1 off-chain to on-chain ratio](experiments/101-hundred-agents/charts/chart_settlement_ratio.png)

## All Experiments

| # | Name | Nodes | Duration | Key Finding |
|---|------|-------|----------|-------------|
| 001 | [Settlement validation](experiments/001-settlement-validation/) | 5 | 18h | Settlement pipeline works end-to-end |
| 002 | [Creative economy](experiments/002-creative-economy/) | 10 | 48h | Agents produce and trade creative content; Gini 0.90 |
| **101** | [**100 agents**](experiments/101-hundred-agents/) | **101** | **6 days** | **Bilateral credit flattens wealth (Gini 0.90 -> 0.161); 15,476:1 settlement efficiency** |

## What This Is

Each experiment deploys a Docker swarm of [knarr](https://github.com/knarrnet/knarr) nodes, each driven by a small LLM (1B-35B parameters). Nodes are given personality seeds, skill inventories, and credit policies -- then left to operate autonomously. We measure what they do: who trades with whom, what skills get invoked, whether economies form, whether settlements complete.

This repo contains the experiment protocols, infrastructure, raw data, and analysis. Everything needed to reproduce or extend the experiments.

## Try It Yourself

```bash
# Clone
git clone https://github.com/knarrnet/knarr.lab.git
cd knarr.lab

# Read the experiment 101 report
cat experiments/101-hundred-agents/README.md

# Reproduce (requires Docker + NVIDIA GPU)
cd experiments/001-settlement-validation
cat protocol.md
docker compose -f ../../infrastructure/docker-compose.yml \
               -f docker-compose.override.yml up -d
```

The Solana testnet is free. The models run locally. The protocol is open. If anything in the reports seems implausible, run it yourself.

## Structure

```
knarr.lab/
├── infrastructure/          # Shared Docker setup
├── experiments/             # One directory per experiment
│   ├── _template/           # Skeleton for new experiments
│   ├── 001-settlement-validation/
│   ├── 002-creative-economy/
│   └── 101-hundred-agents/  # Latest: the 101-node run
├── scoring/                 # Metrics collector and analysis
├── results/                 # Cross-experiment summaries
├── lib/                     # Shared Python utilities
└── docs/                    # Design documents, research questions
```

## Design Principles

1. **Reproducibility** -- Every experiment includes its full Docker configuration. `docker compose up` is the only requirement.
2. **Data immutability** -- Raw data is sealed after the run. Analysis is separate.
3. **Protocol-first** -- Hypotheses and success criteria are pre-registered before the run.
4. **Minimal intervention** -- Experiments run autonomously. Human intervention invalidates the data.
5. **Open data** -- All raw data, logs, and metrics are published.
6. **Verifiability** -- On-chain transactions link to public Solana testnet explorers.

## Requirements

- Docker with NVIDIA GPU support
- GPU with sufficient VRAM for the experiment's model roster (exp-101: 2x RTX 3090)
- Python 3.11+ for analysis scripts

## Related

- [knarr](https://github.com/knarrnet/knarr) -- The peer-to-peer protocol
- [knarr.skills](https://github.com/knarrnet/knarr.skills) -- Skill and plugin library
- [knarr.network](https://knarr.network) -- Live network

## License

MIT
