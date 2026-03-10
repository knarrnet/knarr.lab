# Experiment 001: Settlement Pipeline Validation — 5-Node Autonomous Swarm

> **Status:** concluded
> **Protocol:** [protocol.md](protocol.md)
> **Config:** [config.yaml](config.yaml)

## Summary

Five autonomous LLM-driven knarr nodes (Qwen3.5-4B via vLLM) ran unsupervised for 18 hours in a Docker swarm. The agents autonomously discovered peers, made trade decisions, and invoked cross-node skills, generating 4,656 tasks and 2,445 LLM decisions. A functioning credit-based economy emerged with significant balance differentiation across all nodes.

The settlement pipeline failed at 100% — every netting document was correctly generated and signed, but dual-signature validation rejected all settlement execution attempts due to a key mismatch between thrall's signing identity and the node identity expected by core.

## Results

### Hypothesis Outcomes

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| **H1** — Agents form a functioning trade economy | **Supported** | 4,656 cross-node tasks, net positions ranging +65 to +124 |
| **H2** — Settlement pipeline completes end-to-end | **Rejected** | 0/55 settlement attempts succeeded |
| **H0** — No meaningful trade patterns emerge | **Rejected** | All 5 nodes exceeded net position +50 |

### Activity Summary

| Metric | Value |
|--------|-------|
| Total tasks executed | 4,656 |
| LLM decisions made | 2,445 |
| Netting documents generated | 34 |
| Settlement attempts | 55 |
| Settlements completed | 0 |
| Error rate (cockpit API timeouts) | ~25% |
| Run duration | 18h 2m |

### Credit Positions at T+18h

| Node | Net Position | Green | Amber | Red | Highest Peer Balance | Lowest Peer Balance |
|------|-------------|-------|-------|-----|---------------------|---------------------|
| alpha | +65 | 4 | 1 | 2 | +36 | -8 |
| bravo | +121 | 5 | 1 | 1 | +34 | -6 |
| charlie | +104 | 5 | 1 | 1 | +38 | -5 |
| delta | +65 | 3 | 2 | 2 | +38 | -8 |
| echo | +124 | 6 | 1 | 0 | +35 | 0 |

Credit floor reached -8 (hard limit) for several peer relationships. Ceiling reached +38. The `min_balance=-8` policy effectively constrained deficit accumulation while allowing sustained trade.

### Error Categorization

| Category | Count | Cause | Status |
|----------|-------|-------|--------|
| Cockpit API timeout | ~25% of tasks | `gather.py` uses synchronous `urllib` from async context, blocking the event loop | Fix committed (`asyncio.to_thread` wrapper) |
| Settlement signature rejection | 55/55 attempts | `thrall_identity.key` used for eddsa-jcs-2022 signing; core validates against `key.pem` (`#key-1`) | Bug — requires key unification |
| Netting doc generation | 34 docs, all valid | Commerce engine correctly detects imbalances above 80% threshold | Working as designed |

### Settlement Failure Detail

The settlement pipeline works correctly through four of five stages:

1. **Imbalance detection** — Commerce engine monitors per-peer credit utilization and triggers at 80% threshold.
2. **Netting document generation** — 34 netting documents generated across all 5 nodes with correct amounts.
3. **Document signing** — eddsa-jcs-2022 signatures applied using thrall's `thrall_identity.key`.
4. **Dual-signature validation** — **FAILS HERE.** Core expects `#key-1` (derived from `key.pem`, the node's transport identity) but thrall signs with its own plugin-level key. Every attempt produces: `Node signature (#key-1) verification failed`.
5. **Balance reconciliation** — Never reached.

The root cause is an architectural mismatch: thrall maintains a separate identity (`thrall_identity.key`) for plugin-level cryptographic operations, but the core settlement execution path validates signatures against the node's transport key (`key.pem`). These are different key pairs.

## Key Observations

1. **Autonomous economy formation is robust.** With no human intervention, 5 nodes running a 4B parameter model formed a differentiated economy. Nodes specialized organically — some became net providers (bravo: +121, echo: +124), others ran balanced books (alpha: +65, delta: +65). This was not programmed; it emerged from LLM decision-making.

2. **The commerce engine works.** Imbalance detection, threshold-based triggering, and netting document generation all functioned correctly. The 80% soft threshold produced 34 netting attempts — appropriately timed relative to balance growth.

3. **Small models can drive meaningful agent behavior.** Qwen3.5-4B (4 billion parameters) produced 2,445 coherent trade decisions over 18 hours. Decision quality was sufficient for skill discovery, peer selection, and invocation — the core agent loop.

4. **Event loop blocking is the dominant error source.** The ~25% error rate is entirely attributable to synchronous HTTP calls inside async context in `gather.py`. This is a known issue with a straightforward fix (`asyncio.to_thread`), not a fundamental limitation.

5. **Settlement is the critical gap.** The entire pipeline from imbalance detection through netting document generation works. The single failure point — key identity mismatch — is a fixable integration bug, not a design flaw.

## Limitations

- **Single model:** All nodes ran the same model (Qwen3.5-4B). Heterogeneous model configurations were not tested.
- **Closed network:** All 5 nodes are cooperative. Adversarial or non-participating nodes were not present.
- **Single GPU:** vLLM served all 5 nodes from one RTX 3090. Under contention, inference latency may have influenced trade patterns.
- **No baseline comparison:** There is no control group (e.g., random-decision agents) to isolate LLM contribution from protocol-level mechanics.
- **End-of-run snapshot only:** Metrics were collected at T+18h. Time-series data (trade rate over time, balance trajectories) was not captured.

## Data

- `data/metrics/` — Per-node JSON snapshots: `{node}-status.json`, `{node}-economy.json`, `{node}-ledger.json`
- `data/logs/` — Full node logs (`{node}.log`), LLM decision logs (`{node}-decisions.log`), settlement logs (`{node}-settlement.log`), bootstrap log
- `data/artifacts/` — Reserved (no completed settlement artifacts)

## Follow-up

- **BUG-001:** Unify thrall signing identity with node transport key, or extend core dual-signature validation to accept plugin-level keys. This is the prerequisite for experiment 002.
- **FIX-001:** Wrap `gather.py` synchronous HTTP calls with `asyncio.to_thread` to eliminate the 25% error rate. Already committed.
- **EXP-002:** Re-run with key unification fix to validate complete settlement pipeline.
- **EXP-003:** Heterogeneous model experiment — different models per node to test cross-model trade dynamics.
