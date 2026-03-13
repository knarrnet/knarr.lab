# Experiment 002: 100 Agents Build a Creative Economy

**Author:** Tyr (spec) / Viggo (implementation)
**Date:** 2026-03-13
**Status:** planned
**Protocol version:** v0.45.0+ (requires x402, meter, settlement hooks, WM, netting cycle)

---

## Objective

Does quality of LLM creative output propagate as an economic signal in a 100-node knarr cluster?

Nodes generate poems and stories, other nodes judge quality and issue credit-denominated payments. We measure whether higher-quality generators earn disproportionately more credits, whether settlement occurs autonomously on testnet KNARR, and whether stable trading-partner preferences emerge from zero initial configuration.

---

## Hypothesis

**H1:** Nodes specializing in high-quality creative output earn disproportionately more credits. The quality signal (meter + imagery + originality scores from quality-judge-lite) propagates through the bilateral credit economy, rewarding better generators.

**H2:** Settlement occurs autonomously when credit utilization exceeds the configured threshold (0.8), with real testnet KNARR tokens transferred on-chain without human intervention.

**H3:** Nodes develop stable trading-partner preferences. Trade clusters emerge organically from quality reputation — critics return to reliable sage nodes, and sage nodes cultivate preferred critic relationships.

**H0:** No meaningful differentiation. All nodes earn similar credits regardless of creative output quality. Quality scores show no correlation with revenue (Pearson r < 0.3).

---

## Lineage

- **Exp-001** (settlement validation, 10 nodes): Validated settlement hooks end-to-end on testnet. This experiment reuses the same settlement config and scales 10x.
- **Tyr exp-100-economy-spec.md** (Exp6/Exp7 lineage): Tyr's base spec proved economic activity is measurable; Exp7 fixed the `is_own` bug. This experiment adds quality-differentiated demand to the basic economy design.
- **Key change from Tyr's original spec**: Tyr's design used generic skill types (summarization, Q&A, code review). Exp-002 replaces these with a quality-differentiated creative loop — generate → judge → pay — so output quality directly drives credit flow, making the economy observable and narratively compelling.

---

## Setup

- **Nodes:** 100 agent nodes + 1 bootstrap + 1 vLLM service
- **Duration:** 72 hours minimum
- **Snapshot interval:** every 5 minutes
- **Node identity:** fresh keys per run (no cross-run carryover)
- **Human intervention:** zero after boot — whatever happens is data

### Node Roles

| Role | Count | Skill offered | Model backend | Price |
|------|-------|--------------|---------------|-------|
| Sage | 30 | creative-gen-lite | Ollama / gemma3:12b | 3 cr |
| Critic | 20 | quality-judge-lite | Ollama / qwen3:14b | 2 cr |
| Scribe | 40 | text-summarize-lite | vLLM / Qwen3.5-4B | 2 cr |
| Oracle | 10 | cluster-state-query | Ollama / qwen3:14b | 1 cr |

All 100 nodes also offer `echo` (free, health ping).

### GPU Assignment

- **GPU 0** — vLLM serving Qwen/Qwen3.5-4B: Scribe nodes (text-summarize-lite). High-volume, commodity throughput.
- **GPU 1** — Ollama serving gemma3:12b + qwen3:14b: Sage nodes (creative-gen-lite via gemma3:12b) and Critic/Oracle nodes (quality-judge-lite, cluster-state-query via qwen3:14b). Ollama multi-model, sequential.

### Credit Policy

- `initial_credit = 15` for all nodes (including bootstrap)
- `min_balance = -10` (nodes can go 10 credits negative before transactions are blocked)
- `settlement_threshold = 0.8` (trigger at 80% credit utilization)
- `settlement_min_interval = 300s` (max one settlement per pair per 5 minutes)
- `netting_interval = 60s`

### Workload Generator (demand loop)

Every 2–5 minutes (jittered), each node executes a "need cycle":

1. Select a skill type the node does NOT offer locally
2. Discover providers via DHT
3. Evaluate cost vs. current credit position
4. Execute (buy) or decline based on economic state
5. Log decision: `bought / declined / no_provider_found`

Sage nodes consume: quality-judge-lite, text-summarize-lite, cluster-state-query
Critic nodes consume: creative-gen-lite, text-summarize-lite, cluster-state-query
Scribe nodes consume: creative-gen-lite, quality-judge-lite, cluster-state-query
Oracle nodes consume: creative-gen-lite, quality-judge-lite, text-summarize-lite

This creates organic cross-role demand without scripted transaction pairs. No node can self-serve its full workload.

---

## The Creative Economy Loop

```
Sage node                    Critic node
──────────────────────────────────────────
1. Generate poem/haiku/story
   [creative-gen-lite]
   theme="trust in networks"
   format=haiku
   → content, model, format

2. Call quality-judge-lite
   on a Critic node
   → meter, imagery, originality
      (1-10 each), total, verdict

3. Credit transfer:
   Critic earns 2 cr
   Sage pays 2 cr

4. Sage reputation accumulates:
   high-total poems → more
   repeat business from Critics
```

Quality signal propagation: Critics track which Sage nodes produce high-scoring work. The bilateral credit ledger reflects this — Sages with high average scores accumulate positive balances from repeated invocations; low-scoring Sages bleed credits until they can't afford to generate.

---

## Data Collection

### Per-node (every 5 minutes)
- Balance (current)
- Tasks provided (cumulative)
- Tasks consumed (cumulative)
- Revenue (cumulative credits earned)
- Cost (cumulative credits spent)
- Credit utilization (% of limit used)
- Held balance (settlement holds pending)
- Meter readings (per-skill execution counts)
- Average quality score received (for Sage nodes)

### Per-pair (bilateral)
- Bilateral balance
- Trade count (tasks exchanged between pair)
- Credit utilization between pair
- Direction of trade (who provides, who consumes)
- Average quality score (for Sage→Critic pairs)

### Network-level (aggregate)
- Total transactions completed
- Total transactions refused (credit exhaustion / admission gate)
- Unique bilateral pairs with at least 1 trade
- Gini coefficient of final balances (wealth distribution)
- Network graph density (pairs with trade / total possible pairs)
- Netting cycles completed
- Settlements submitted / confirmed on testnet

### Quality-economics correlation
- Per-Sage: average `total` score from quality-judge-lite vs. revenue
- Pearson r of quality vs. revenue across all Sage nodes
- Top-10 Sage nodes by quality vs. top-10 by revenue (overlap metric)

---

## Procedure

### Before boot
1. Build image: `docker build -t knarr-node:v045-exp002 .` in provider root
2. Generate compose: `python gen_compose.py --nodes 100 --base-port 9300 --image knarr-node:v045-exp002 --output docker/swarm-cluster/compose/cluster-002.yml`
3. Verify compose: `docker compose -f cluster-002.yml config --quiet`
4. Ensure Ollama is running on GPU 1 with gemma3:12b and qwen3:14b pulled
5. Ensure vLLM can load Qwen/Qwen3.5-4B on GPU 0

### Boot
```
cd docker/swarm-cluster
docker compose -f compose/cluster-002.yml up -d
```
Expected boot time: ~90 seconds for 100 nodes.

### T+0 (boot)
- Tyr's airdrop node fires `welcome-airdrop-lite` for each new DHT peer
- Each node receives 5 testnet KNARR to their Ed25519 wallet
- Airdrop ledger at `plugin_state/airdrop/airdrop_ledger.json` serves as operational registry

### T+1h checkpoint
- Verify all 100 nodes appear in bootstrap peer table
- Verify cross-node skill invocations are occurring (check cockpit metrics)
- Verify at least 1 quality-judge-lite invocation logged
- If zero activity: check workload generator and DHT discovery

### T+4h checkpoint
- Verify Gini > 0.1 (some differentiation emerging)
- Verify at least 1 settlement trigger (credit utilization >80% on any pair)
- Check quality-revenue correlation: early signal expected

### T+24h / T+48h / T+72h
- Run `python collect_results.py` snapshot
- Export bilateral graph for topology analysis
- Log any anomalies (crashed nodes, stuck settlements)

### T+72h (collect)
```
python collect_results.py    # snapshots → CSV
python analyze.py            # Gini, topology graph, quality-revenue correlation
```

---

## Airdrop Integration (Tyr's Node)

Tyr's node runs separately from the Docker cluster. It listens on DHT for `peer_joined` events and invokes `welcome-airdrop-lite` for each new node ID.

**Trigger:** New peer appears in DHT (detected by Tyr's thrall recipe `welcome-airdrop`)
**Action:** `welcome-airdrop-lite` executes:
1. Validates the 64-char hex node_id
2. Dedup check against `airdrop_ledger.json` (skip if already airdropped)
3. Derives recipient Solana wallet from node_id (node_id IS the Ed25519 pubkey, base58-encoded)
4. Checks BCW master wallet balance (abort if < 10 KNARR)
5. Builds + submits SPL Token-2022 transfer of 5 KNARR on Solana testnet
6. Records tx in `airdrop_ledger.json`
7. Sends welcome mail to the new node via cockpit `/api/messages/send`

**Auth:** BCW master seed loaded from Tyr's vault (`bcw/bcw_master_seed`). No token injection into skill input.

**The airdrop ledger** (`plugin_state/airdrop/airdrop_ledger.json`) serves as the operational registry of all cluster nodes: each entry maps `node_id → {recipient_wallet, tx_hash, amount_knarr, timestamp}`. This doubles as proof-of-participation for the testnet settlement trail.

**BCW-01 gap note:** SPL Token-2022 ATA creation may fail if recipient ATA does not exist. See `thing/briefs/2026-03-12-bcw-ata-gap.md`. If airdrop tx fails with ATA error, this is expected and tracked as OPEN.

---

## Bonus Track: Moltbook Integration

No `moltbook` skill was found in `F:/knarr.tyr/skills/`. Tyr's skills directory contains only:
`welcome_airdrop_lite.py`, `payment_alert_lite.py`, `proton_fetch_lite.py`, `proton_inbox_lite.py`, `proton_send_lite.py`, `proton_session_lite.py`, `tyr_ops.py`

If a moltbook skill is built later, the intended integration is:
- After each quality-judged poem, a nominated Sage node posts the poem + scores to moltbook
- Input would be: `content` (poem text), `total_score` (float), `author_node_id` (16-char prefix), `format` (haiku/poem/story)
- This creates a public artifact trail of the best poems the economy produced
- Gate: only post if `total >= 7.0` (top-quality output only)

---

## Success Criteria (pre-registered)

| # | Criterion | Target | Measurement |
|---|-----------|--------|-------------|
| SC-1 | Cross-node skill invocations | ≥ 10,000 in 72h | `meter_reads` aggregate in snapshots |
| SC-2 | End-to-end settlement on testnet | ≥ 1 confirmed tx | `settlement_confirmed` in node logs |
| SC-3 | Economic differentiation | Gini coefficient of final balances ≥ 0.3 | `analyze.py` output |
| SC-4 | Specialization emergence | ≥ 1 node earns >3× median revenue | Revenue distribution in `collect_results.py` |
| SC-5 | Quality-revenue correlation | Pearson r ≥ 0.3 (Sage quality vs. revenue) | Correlation script in `analyze.py` |

All criteria are binary (met / not met) and measurable from exported snapshots. Pre-registered 2026-03-13.

---

## Known Risks

| Risk | Mitigation |
|------|------------|
| Ollama serializes inference — Critic/Oracle nodes queue up | Allocate qwen3:14b exclusively to GPU 1; limit concurrent requests via Ollama concurrency settings |
| BCW-01 ATA gap causes all airdrop txs to fail | Expected; tracked as OPEN. Airdrop failure does not block economy experiment — nodes function on bilateral credit alone |
| Low Gini even with quality differentiation | May indicate credit limits are too high (nodes never feel scarcity). Mitigation: reduce `min_balance` to -5 in a follow-up run |
| vLLM OOM with 40+ concurrent Scribe nodes | Qwen3.5-4B at 0.85 GPU util handles ~256 concurrent sequences per spec. If OOM: reduce `--max-num-seqs` |
| Workload generator not yet built | Critical path. This is a gap — see below |
| quality-judge-lite returns `json_parse` errors | Extract logic has fallback but qwen3:14b sometimes wraps in markdown. Monitor `error` field in snapshots |
| Network graph density too low (nodes don't discover each other) | All nodes bootstrap from the same bootstrap node; DHT propagation should reach full mesh within T+30min |

---

## Known Gaps (must resolve before run)

1. **Workload generator not built.** The periodic "need cycle" (select → discover → evaluate → execute/decline) is the critical path. Without it, nodes sit idle. Owner: Viggo. Status: NOT BUILT.
2. **Moltbook skill absent.** No moltbook integration possible until Tyr builds the skill.
3. **Analysis scripts not built.** `collect_results.py` (extended from Exp6) and `analyze.py` (Gini, topology, quality-revenue correlation) need to be written. Owner: Viggo / Tyr. Status: NOT BUILT.
4. **cluster-002.yml not generated.** Run the gen_compose.py command below to produce it.
5. **knarr-node:v045-exp002 image not built.** Needs creative_gen_lite.py + quality_judge_lite.py baked into the cluster image.

---

## Duration

- **Target:** 72h minimum, 168h ideal
- **Checkpoints:** T+1h (connectivity), T+4h (activity), T+24h (early patterns), T+48h (mid-run), T+72h (collect)
- **Zero-intervention policy:** do not restart nodes, adjust configs, or fix bugs mid-run

---

## Reproducibility Payload

```
git clone https://github.com/knarrnet/knarr
cd docker/swarm-cluster
docker compose -f compose/cluster-002.yml up -d
# ... wait 72 hours ...
python collect_results.py   # snapshots → CSV
python analyze.py           # Gini, topology, quality-revenue correlation chart
```
