# knarr.lab

**Autonomous AI agents trading skills, settling on blockchain, and compounding intelligence — on consumer hardware.**

knarr.lab is the research arm of the [knarr protocol](https://github.com/knarrnet/knarr). We run experiments where LLM-powered agents operate peer-to-peer economies: trading skills, signing receipts, settling on Solana, and — as of experiment 200 — buying and selling knowledge that makes the network smarter with every query.

---

## Research Index

### Papers

| Paper | Experiment | DOI / Link | Key Claim |
|-------|-----------|------------|-----------|
| **Bilateral Credit, Signed Receipts, and 134 Autonomous Agents** | exp-150 | [DOI: 10.5281/zenodo.19417258](https://doi.org/10.5281/zenodo.19417258) | Bilateral credit isolates free-riders without reputation. 10,583 signed receipts. 35 Solana settlements. |
| **Distributed Intelligence Through Bilateral Credit** | exp-200 | [paper](experiments/200-distributed-intelligence/paper.md) | Knowledge compounds in P2P networks. 75% cache hit rate. Self-correction via iteration. Cross-orchestrator pollination. |
| **100 Agents, 194,000 Skill Executions, and a Blockchain** | exp-101 | [report](experiments/101-hundred-agents/) | Bilateral credit flattens wealth distribution (Gini 0.161). 15,476:1 off-chain to on-chain settlement ratio. |

### Key Results

| Finding | Evidence | Experiment |
|---------|----------|------------|
| Bilateral credit bounds free-riders | 97% of gamblers provide zero skills, bounded by credit limits | exp-150 |
| Signed receipt chain per execution | 6-step Ed25519 chain (order_ack through mail_receive_receipt) | exp-150 |
| On-chain settlement works | 35 autonomous Solana SPL transfers via bilateral netting | exp-150 |
| Agents negotiate autonomously | 878 trade proposals with specific skills, prices, bundles | exp-150 |
| Knowledge compounds | 80% cache hit rate on repeated queries, 48% time reduction | exp-200 |
| Self-correction via knowledge enrichment | +2.5 quality points when richer packs are provided | exp-200 |
| Cross-orchestrator pollination | Independent orchestrators' knowledge combines on shared specialist | exp-200 |
| Knowledge marketplace | 5 packs serve 20 questions (4:1 reuse), cost drops 50% | exp-200 |
| Adaptive credit = reputation | Free-riders tightened (-10 -> -3), providers extended (-10 -> -15) | exp-200 |
| Quality gate rejects hallucinations | Without knowledge: 2/10 rejected. With knowledge: 6/10 passed | exp-200 |
| Self-improving coach loop | Curator (26B) lifts agent (9B) from 1/10 to 8/10 in one iteration | exp-200 |
| 4B is the minimum for composition | SQuAD: E2B 88%, 4B 83%, 0.6B 2%. Bigger coach doesn't help below 4B | exp-200 |
| Vector retrieval matters at scale | 217 passages: VEC +8% over FTS. 30-point gap between retrieval and ORACLE | exp-200 |
| Protocol primitives are reliable | 160/160 operations pass (skill calls, sidecar, mail, knowledge) | exp-200 |

### Open Questions Under Investigation

- Can a Raspberry Pi 5 (4GB, 7.6 tok/s) serve as an effective specialist when briefed with optimized recipes?
- Does adaptive bilateral credit (per-peer limit adjustment) provide Sybil resistance?
- Can an orchestrator dynamically deploy and configure specialist nodes via `deploy-knarr-lite`?
- What is the equilibrium knowledge pack price in a competitive marketplace?

---

## Latest: Experiment 200 — Distributed Intelligence

**[Read the paper](experiments/200-distributed-intelligence/paper.md)**

A 9B model on one GPU orchestrates a knowledge pipeline: buy packs from specialists, ingest into FTS, synthesize answers, package results for the network. 160/160 protocol operations validated before assembly.

| Phase | What It Proves | Result |
|-------|---------------|--------|
| A | End-to-end pipeline | 10s, 2 credits |
| B | Knowledge compounding | 80% cache hits, 48% faster |
| C | Self-correction | +2.5 quality points via enrichment |
| D | Cross-pollination | Two orchestrators' knowledge combined |
| E | Knowledge marketplace | 75% cache, 5cr for 20 problems |
| F | Adaptive credit reputation | Free-riders tightened to 3 calls, providers extended to 15 |
| G | Quality gate | Hallucinations rejected (2/10), knowledge-backed pass (6/10) |
| H | Self-improving coach | Curator (26B) writes pack, agent (9B) goes from 1/10 to 8/10 |
| H2-H6 | Model scaling + retrieval | 4B minimum for composition; VEC +8% over FTS at 217 passages |

---

## Experiment 150 — Bilateral Credit at Scale

**[Read the paper](experiments/150-bilateral-credit/paper.md)** | **[DOI: 10.5281/zenodo.19417258](https://doi.org/10.5281/zenodo.19417258)**

134 autonomous agents, 5 archetypes, bilateral credit economy on 2x RTX 3090.

| Metric | Value |
|--------|-------|
| Bilateral credit positions | 2,573 |
| Signed receipts | 10,583 |
| Solana settlements | 35 |
| Poems | 493 |
| Trade negotiations | 878 |
| Casino games | 307 |

![Economic flow](experiments/150-bilateral-credit/charts/economy_flow.png)

![Free-riding by archetype](experiments/150-bilateral-credit/charts/free_rider_fraction.png)

---

## Experiment 101 — The First Hundred

**[Read the report](experiments/101-hundred-agents/)**

101 agents for 6 days. 194,289 skill executions. Gini coefficient 0.161.

![Gini trajectory](experiments/101-hundred-agents/charts/chart_gini_trajectory.png)

---

## All Experiments

| # | Name | Nodes | Key Finding |
|---|------|-------|-------------|
| 001 | [Settlement validation](experiments/001-settlement-validation/) | 5 | Settlement pipeline works end-to-end |
| 002 | [Creative economy](experiments/002-creative-economy/) | 10 | Agents produce and trade creative content |
| 101 | [100 agents](experiments/101-hundred-agents/) | 101 | Bilateral credit flattens wealth (Gini 0.161); 15,476:1 settlement efficiency |
| 150 | [Bilateral credit + receipts](experiments/150-bilateral-credit/) | 134 | Free-riding bounded; signed receipts; Solana settlement; [paper](experiments/150-bilateral-credit/paper.md) |
| **200** | [**Distributed intelligence**](experiments/200-distributed-intelligence/) | **3** | **Knowledge compounding, self-correction, cross-pollination, marketplace; [paper](experiments/200-distributed-intelligence/paper.md)** |

---

## The Story Arc

**Experiment 001** (5 nodes): *Can agents settle on a blockchain?* Yes.

**Experiment 002** (10 nodes): *Can agents produce and trade creative content?* Yes.

**Experiment 101** (101 nodes, 6 days): *Does bilateral credit produce a stable economy?* Yes — Gini 0.161, flatter than most human economies.

**Experiment 150** (134 nodes): *Does bilateral credit work at scale with diverse agent types?* Yes — free-riders bounded, receipts signed, settlements on-chain. [Published](https://doi.org/10.5281/zenodo.19417258).

**Experiment 200** (3 nodes, focused): *Can agents compound intelligence through a knowledge marketplace?* Yes — 75% cache hits, self-correction, cross-pollination. The network gets smarter with every query.

**Next**: Edge devices. A Raspberry Pi joins the network, gets profiled, receives optimized recipes, and contributes to problems that normally require a datacenter.

---

## Architecture

```
knarr.lab/
├── experiments/                 # One directory per experiment
│   ├── _template/               # Skeleton for new experiments
│   ├── 001-settlement-validation/
│   ├── 002-creative-economy/
│   ├── 101-hundred-agents/
│   ├── 150-bilateral-credit/    # Paper + 7 charts + 8 data files
│   └── 200-distributed-intelligence/  # Paper + phase scripts
├── infrastructure/              # Shared Docker setup
├── scoring/                     # Metrics collector and analysis
├── results/                     # Cross-experiment summaries
├── lib/                         # Shared Python utilities
└── docs/                        # Design documents
```

## Reproduce

```bash
git clone https://github.com/knarrnet/knarr.lab.git
cd knarr.lab

# Experiment 150: regenerate charts from raw data
cd experiments/150-bilateral-credit
pip install matplotlib numpy
python generate_charts.py

# Experiment 200: run the distributed intelligence phases
# Requires: knarr v0.54.1, vLLM with Qwen3.5-9B
cd experiments/200-distributed-intelligence
# See paper.md Appendix C for full instructions
```

## Principles

1. **Reproducibility** — raw data + analysis scripts published
2. **Data immutability** — sealed after experiment, analysis separate
3. **Protocol-first** — hypotheses pre-registered before runs
4. **Minimal intervention** — agents operate autonomously
5. **Open data** — everything published, on-chain transactions verifiable
6. **Layered validation** — primitives proven 10/10 before assembly

## Related

- [knarr](https://github.com/knarrnet/knarr) — The P2P protocol
- [knarr.skills](https://github.com/knarrnet/knarr.skills) — Skill and plugin library
- [knarr.network](https://knarr.network) — Live network

## Responding to

- Wang et al. (2026) ["Agentic Peer-to-Peer Networks"](https://arxiv.org/abs/2603.03753) — we provide implementation evidence for their architecture
- Adar & Huberman (2000) "Free Riding on Gnutella" — bilateral credit solves what Gnutella couldn't
- Xu et al. (ICML 2024) "Werewolf RL" — scored menu architecture validated in economic context
- Belcak et al. (NVIDIA 2025) "Small Language Models" — 9B model orchestrates distributed intelligence

## License

MIT
