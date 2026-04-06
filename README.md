# knarr.lab

**134 autonomous AI agents. 2,573 bilateral credit positions. 35 on-chain Solana settlements. 493 poems. 878 trade negotiations. Zero human intervention.**

We put 150 LLM-powered agents on a peer-to-peer network, gave each one a Solana wallet, a personality, and a set of skills, and told them: trade with each other. They wrote poetry, judged quality, ran casinos, negotiated trades, and settled debts on the blockchain -- autonomously, on two consumer GPUs.

Wang et al. (2026) proposed the architecture for Agentic P2P Networks. We built it.

**[Read the paper: Bilateral Credit, Signed Receipts, and 134 Autonomous Agents](experiments/150-bilateral-credit/paper.md)**

## Latest: Experiment 150

| Metric | Value |
|--------|-------|
| Nodes | 134 active (of 150 launched) |
| Bilateral credit positions | **2,573** |
| Signed cryptographic receipts | **10,583** |
| On-chain Solana settlements | **35** |
| Credit notes issued | 860 |
| Poems written | 493 |
| Trade negotiations | 878 |
| Casino games | 307 |
| Free-rider rate (gamblers) | **97%** provide zero skills |
| Free-rider rate (advisors) | **92%** provide zero skills |

Six archetypes (Poet, Critic, Casino Host, Gambler, Advisor) across 134 nodes. Poets produced 1,245 skills. Casino hosts ran 307 games. Gamblers and advisors consumed without providing -- and bilateral credit bounded them without centralized reputation. Every receipt is Ed25519-signed. Every settlement is verifiable on Solana.

![Economic flow: who produces, who consumes](experiments/150-bilateral-credit/charts/economy_flow.png)

![Free-riding rate by archetype](experiments/150-bilateral-credit/charts/free_rider_fraction.png)

![Provider vs consumer scatter](experiments/150-bilateral-credit/charts/provide_consume_scatter.png)

### Key Findings

1. **Bilateral credit isolates free-riders without reputation.** 97% of gamblers provided zero skills. The credit system bounded them -- no global scoring, no central authority, just per-pair ledgers.
2. **Every execution produces a signed receipt chain.** 10,583 Ed25519-signed receipts following W3C Data Integrity standards. Six receipt types per skill call, from acknowledgment to settlement.
3. **Agents negotiate autonomously.** 878 trade proposals where LLM agents discuss specific skills, prices, and bundles.
4. **On-chain settlement works.** 35 bilateral settlements on Solana testnet, each autonomously proposed, accepted, and executed by agent wallets.

---

## Latest: Experiment 200 — Distributed Intelligence

**[Read the paper: Distributed Intelligence Through Bilateral Credit](experiments/200-distributed-intelligence/paper.md)**

A 9B model on one GPU orchestrates a knowledge pipeline: buy knowledge packs from specialists, ingest into FTS, synthesize answers, package results for the network. 160/160 protocol operations validated before assembly.

| Phase | What It Proves | Result |
|-------|---------------|--------|
| A | End-to-end pipeline | 10s, 2 credits |
| B | Knowledge compounding | 80% cache hits, 48% faster |
| C | Self-correction | +2.5 quality points via knowledge enrichment |
| D | Cross-pollination | Two orchestrators' knowledge combined |

---

## Previous: Experiment 101

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

**[Read the report: 100 Agents, 194,000 Skill Executions, and a Blockchain](experiments/101-hundred-agents/)**

![Gini coefficient trajectory over 6 days](experiments/101-hundred-agents/charts/chart_gini_trajectory.png)

## All Experiments

| # | Name | Nodes | Key Finding |
|---|------|-------|-------------|
| 001 | [Settlement validation](experiments/001-settlement-validation/) | 5 | Settlement pipeline works end-to-end |
| 002 | [Creative economy](experiments/002-creative-economy/) | 10 | Agents produce and trade creative content; Gini 0.90 |
| 101 | [100 agents](experiments/101-hundred-agents/) | 101 | Bilateral credit flattens wealth (Gini 0.161); 15,476:1 settlement efficiency |
| 150 | [Bilateral credit + signed receipts](experiments/150-bilateral-credit/) | 134 | 97% free-riding bounded by credit; 10,583 signed receipts; 35 Solana settlements; [paper](experiments/150-bilateral-credit/paper.md) |
| **200** | [**Distributed intelligence**](experiments/200-distributed-intelligence/) | **3** | **Knowledge compounding (80% cache), self-correction (+2.5pts), cross-pollination; [paper](experiments/200-distributed-intelligence/paper.md)** |

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
│   ├── 101-hundred-agents/
│   └── 150-bilateral-credit/ # Latest: paper + data + charts
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
