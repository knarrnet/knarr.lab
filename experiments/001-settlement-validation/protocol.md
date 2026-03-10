# Experiment 001: Settlement Pipeline Validation — 5-Node Autonomous Swarm

## Objective

Determine whether LLM-driven autonomous agents can (a) form a functioning credit-based trade economy and (b) complete the full settlement pipeline end-to-end, including netting document generation, dual-signature verification, and balance reconciliation.

## Hypothesis

**H1:** Autonomous agents running swarm-probe will discover peers, invoke cross-node skills, and generate sustained trade activity resulting in non-trivial credit imbalances across the network.

**H2:** The settlement pipeline (commerce engine imbalance detection, netting document generation with eddsa-jcs-2022, dual-signature validation, balance reconciliation) completes end-to-end without human intervention.

**H0:** No meaningful trade patterns emerge — agents fail to discover or invoke cross-node skills, credit balances remain near initial values.

## Lineage

First formal knarr.lab experiment. Builds on informal swarm-cluster experiments 1-7 (Docker swarm testbed development, thrall integration, commerce engine tuning). The swarm-cluster infrastructure and swarm-probe treatment were iterated across those prior runs.

## Setup

- **Nodes:** 5 agent nodes (alpha, bravo, charlie, delta, echo) + 1 bootstrap
- **Models:** Qwen/Qwen3.5-4B via single vLLM instance (bfloat16, max_model_len=4096, gpu_memory_utilization=0.7)
- **GPU:** 1x RTX 3090 (24 GB VRAM), shared across all nodes via networked vLLM
- **Runtime:** knarr v0.41.0, thrall v3.7.0 (commerce engine + gather engine)
- **Skill distribution:**
  - All nodes: `echo-lite` (1 cr), `swarm-probe-lite` (0 cr), `concierge-faq-lite` (0 cr), `settlement-check-lite` (0 cr), `settlement-execute-lite` (0 cr), `knarr-mail` (0 cr)
  - Charlie, delta: additional skills copied from shared skills directory at boot
- **Credit policy:** `initial_credit=15`, `min_balance=-8`
- **Settlement policy:** `soft_threshold=0.8`, `soft_target=0.5`, `min_settlement_amount=1.0`
- **Network:** Docker bridge (exp8), all nodes bootstrap against each other and the bootstrap node
- **Duration:** 18h

## Procedure

1. **T+0m:** Start vLLM container, wait for health check (model load ~2 min).
2. **T+2m:** Start bootstrap node, wait for cockpit health check.
3. **T+3m:** Start all 5 agent nodes simultaneously. Each node loads thrall plugin, discovers peers via bootstrap mesh, and begins autonomous swarm-probe cycles.
4. **T+3m onward (autonomous):** Each node's thrall engine:
   - Runs swarm-probe-lite on a periodic tick (LLM decides which peer skill to invoke)
   - Invokes cross-node skills (echo-lite, concierge-faq-lite, etc.) as decided by the LLM
   - Commerce engine monitors credit utilization per peer
   - When utilization exceeds `soft_threshold` (80%), commerce engine generates a netting document
   - Netting documents are signed with eddsa-jcs-2022 and submitted for settlement execution
5. **T+18h:** Collect data — status, economy, and ledger snapshots from each node's cockpit API; copy decision logs, settlement logs, and full node logs.
6. **No manual interventions during the run.** All activity is autonomous.

## Data Collection

- **Metrics:** Node status (peer count, skill count, task count, uptime), economy snapshots (per-peer balance, utilization, tasks provided/consumed, net position), ledger dumps
- **Logs:** Full node logs, LLM decision logs (one line per decision), settlement-specific logs (netting docs + execution attempts)
- **Frequency:** Single collection at T+18h (end of run)
- **Storage:**
  - `data/metrics/` — JSON status, economy, and ledger snapshots per node
  - `data/logs/` — Full logs and filtered decision/settlement logs per node
  - `data/artifacts/` — Reserved for netting documents and signed settlement payloads (none successfully completed)

## Success Criteria

Pre-registered before the run:

1. **H1 supported:** More than 100 cross-node skill invocations occur across the network.
2. **H2 supported:** At least one settlement completes end-to-end (netting doc generated, dual-signature validated, balances reconciled).
3. **H0 rejected:** Credit balances diverge meaningfully from initial values (net position > 50 for at least one node).

## Known Risks

| Risk | Mitigation |
|------|------------|
| vLLM OOM or throughput bottleneck (5 nodes, 1 GPU) | `gpu_memory_utilization=0.7`, `max_model_len=4096`, bfloat16 dtype |
| Event loop blocking from synchronous HTTP in gather.py | Known issue; monitor error rates, fix post-experiment |
| Settlement key mismatch (thrall_identity.key vs node key.pem) | Suspected from code review; this experiment validates whether it manifests |
| Node isolation (Docker DNS resolution) | Full mesh bootstrap list; all nodes reference each other by hostname |
| Credit exhaustion halting trade | `min_balance=-8` allows deficit operation; monitor utilization levels |

## Duration

- **Target:** 18h
- **Checkpoints:** T+1h (verify all 5 nodes connected and trading), T+6h (verify netting documents being generated), T+18h (collect all data)
- **Actual:** 18h 2m (64,976s uptime reported by nodes)
