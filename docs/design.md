# Design Decisions

## Experiment Structure

**Number-prefixed directories** — `001-slug`, `002-slug`. Sequential, sortable, unambiguous.
Date-based naming rejected (multiple experiments per day). UUID rejected (not human-friendly).

**config.yaml + protocol.md** — Machine-readable metadata (config.yaml) for scoring scripts.
Human-readable context (protocol.md) for understanding. Neither is redundant — they serve different consumers.

**Data immutability** — `data/` is write-once during the experiment run. Post-hoc analysis goes in `analysis/`.
This prevents accidental corruption of raw data and makes it clear what was observed vs. interpreted.

## Infrastructure

**Shared base, per-experiment overrides** — `infrastructure/docker-compose.yml` defines the common swarm pattern.
Each experiment's `docker-compose.override.yml` customizes node count, models, and resources.
This avoids duplicating 200 lines of compose boilerplate in every experiment.

**Single Dockerfile** — One agent image, parameterized via config. Model selection happens at the inference backend level (ollama, vLLM), not in the Docker image.

## Scoring

**Separated from experiments** — Scoring code in `scoring/` is independent of any single experiment.
This prevents experiments from defining their own success metrics post-hoc.

## LLM Backend

**vLLM for multi-node** — Continuous batching handles concurrent requests from N agents.
ollama has no request queuing — N simultaneous requests produce 503s.

**Single model per experiment** (default) — Isolates the variable under test.
Model comparison experiments are a separate track.
