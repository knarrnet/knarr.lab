# knarr.lab

Autonomous agent swarm experiments on the [knarr](https://github.com/knarrnet/knarr) peer-to-peer protocol.

Small language models operate independent network nodes — discovering peers, trading skills, negotiating prices, and settling debts. No human intervention during runs. We observe what emerges.

## What This Is

Each experiment deploys a Docker swarm of knarr nodes, each driven by a small LLM (1B–4B parameters). Nodes are given personality seeds, skill inventories, and credit policies — then left to operate autonomously. We measure what they do: who trades with whom, what skills get invoked, whether economies form, whether settlements complete.

This repo contains the experiment protocols, infrastructure, raw data, and analysis. Everything needed to reproduce or extend the experiments.

## Experiments

| # | Name | Status | Duration | Nodes | Key Finding |
|---|------|--------|----------|-------|-------------|
| — | — | — | — | — | *First experiment in progress* |

## Quick Start

### Reproduce an experiment

```bash
# Clone
git clone https://github.com/knarrnet/knarr.lab.git
cd knarr.lab

# Pick an experiment
cd experiments/001-settlement-validation

# Review the protocol
cat protocol.md

# Launch (requires Docker + NVIDIA GPU)
docker compose -f ../../infrastructure/docker-compose.yml \
               -f docker-compose.override.yml up -d

# Collect data
python ../../scoring/collect.py --experiment 001
```

### Add a new experiment

```bash
cp -r experiments/_template experiments/NNN-your-experiment
# Edit protocol.md — define hypothesis, design, success criteria
# Edit config.yaml — set parameters
# Edit docker-compose.override.yml — configure nodes, models, resources
# Run and collect data
# Write analysis in analysis/
# Submit PR
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full process.

## Structure

```
knarr.lab/
├── infrastructure/          # Shared Docker setup (base images, configs)
├── experiments/             # One directory per experiment
│   ├── _template/           # Copyable skeleton for new experiments
│   └── NNN-slug/            # Numbered experiments with data + analysis
├── scoring/                 # Analysis and scoring framework
├── results/                 # Auto-generated cross-experiment summaries
├── lib/                     # Shared Python utilities
└── docs/                    # Design documents, research questions
```

## Design Principles

1. **Reproducibility** — Every experiment includes its full Docker configuration. `docker compose up` is the only requirement.
2. **Data immutability** — Raw data in `data/` is sealed after the run. Analysis is separate.
3. **Protocol-first** — The experiment protocol (`protocol.md`) is written *before* the run. Hypotheses and success criteria are pre-registered.
4. **Minimal intervention** — Experiments run autonomously. Human intervention during a run invalidates the data.
5. **Open data** — All raw data, logs, and metrics are published. Cherry-picking results defeats the purpose.

## Requirements

- Docker with NVIDIA GPU support
- A GPU with sufficient VRAM for the experiment's model roster (see each experiment's `config.yaml`)
- Python 3.11+ for analysis scripts

## Related

- [knarr](https://github.com/knarrnet/knarr) — The peer-to-peer protocol
- [knarr.skills](https://github.com/knarrnet/knarr.skills) — Skill and plugin library

## License

MIT
