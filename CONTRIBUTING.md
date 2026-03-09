# Contributing to knarr.lab

## Adding an Experiment

### 1. Create from template

```bash
cp -r experiments/_template experiments/NNN-your-slug
```

Use the next available number. Keep the slug short and descriptive.

### 2. Write the protocol

Edit `protocol.md` **before** running anything. This is pre-registration — it forces you to commit to hypotheses and success criteria before seeing data.

Required sections:
- **Objective** — What question are you answering?
- **Hypothesis** — What do you expect to happen? Include a null hypothesis.
- **Setup** — Node count, models, skill distribution, credit policy.
- **Procedure** — What happens during the run. Manual interventions (if any) must be documented.
- **Data collection** — What metrics, how often, where stored.
- **Success criteria** — Measurable, binary. "At least 3 nodes invoke cross-node skills" not "nodes trade a lot."
- **Duration** — How long the experiment runs.

### 3. Configure

Edit `config.yaml` with machine-readable parameters. This is what scoring scripts consume.

Edit `docker-compose.override.yml` to define your swarm topology, model assignments, and resource limits. This file extends `infrastructure/docker-compose.yml`.

### 4. Run

```bash
docker compose -f ../../infrastructure/docker-compose.yml \
               -f docker-compose.override.yml up -d
```

Do not intervene during the run unless documenting the intervention in `protocol.md`.

### 5. Collect data

Raw data goes in `data/`. This directory is immutable after the run — never modify raw data.

```
data/
├── logs/        # Node logs, mail transcripts
├── metrics/     # Structured metrics (JSON, CSV)
└── artifacts/   # Generated files, screenshots
```

### 6. Analyze

Post-hoc analysis goes in `analysis/`. Jupyter notebooks, scripts, figures.

### 7. Write results

Update `README.md` in your experiment directory with a summary: what happened, whether hypotheses were supported, key observations, limitations.

### 8. Submit PR

PRs should include:
- Complete protocol (written before the run)
- Raw data
- Analysis with reproducible notebooks
- Results summary

## Experiment Numbering

Sequential integers, zero-padded to 3 digits: `001`, `002`, `003`. The slug after the number is for human readability — the number is the canonical identifier.

## Data Format

### Metrics CSV

Standard columns for time-series metrics:

```csv
timestamp,node,metric,value
2026-03-09T22:00:00Z,alpha,credit_balance,15.0
2026-03-09T22:00:00Z,alpha,peer_count,4
```

### Mail transcripts

JSON lines format, one message per line:

```jsonl
{"timestamp":"2026-03-09T22:01:00Z","from":"alpha","to":"bravo","type":"text","body":"..."}
```

## Code Style

- Python: black, no type stubs for simple scripts
- YAML: 2-space indent
- Markdown: one sentence per line (for clean diffs)

## Questions?

Open an issue or start a discussion.
