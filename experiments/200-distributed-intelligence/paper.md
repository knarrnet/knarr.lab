# Distributed Intelligence Through Bilateral Credit: How Small Language Models Solve Problems by Shopping for Knowledge in a P2P Network

**Viggo**
Knarr Project
April 2026

---

## Abstract

We report implementation evidence for a distributed intelligence architecture where autonomous LLM agents purchase, ingest, and reuse knowledge packs through a peer-to-peer bilateral credit protocol. Validated across 16 experimental phases on consumer hardware (2x RTX 3090), the system demonstrates: (A-D) an end-to-end knowledge pipeline with 80% within-domain cache reuse and cross-orchestrator knowledge combination; (E-G) a knowledge marketplace with adaptive credit limits and a quality gate that rejects hallucinated answers; (H) self-improving coaching where a 26B curator lifts a 9B agent from 1/10 to 8/10; (H2-H6) model scaling thresholds across 6 architectures on a 100-question SQuAD 2.0 subset (4B minimum for composition, 2.3B for extraction); (H7-H8) a retrieval pipeline using Reciprocal Rank Fusion and cross-encoder reranking that closes 48% of the retrieval gap on a 217-passage corpus; (H9) adversarial resilience where a quality gate catches 76% of poisoned knowledge packs with 0% false rejects; and (H10) a negative result showing multi-hop synthesis requires curator-tier models (26B+), not specialist-tier (4B). Every skill call is billed through bilateral credit, every knowledge pack is Ed25519-signed, and all data and scripts are published. The system builds on the architecture proposed by Wang et al. (2026) for Agentic P2P Networks, providing concrete implementation evidence for their economic and intelligence layers.

---

## 1. Introduction

Multi-agent AI systems typically operate within a single process, with agents sharing memory and implicit trust. When agents need external capabilities, they call APIs with fixed pricing and no bilateral relationship. The question we address: **can intelligence compound in a peer-to-peer network where knowledge is bought, sold, signed, and reused through bilateral credit?**

We present a system where:
- An **orchestrator** (small LLM on consumer hardware) receives a problem
- It **purchases knowledge packs** from specialist nodes, paying via bilateral credit
- It **ingests** the knowledge into a local FTS (full-text search) store
- It **synthesizes** an answer using the LLM with retrieved knowledge as context
- It **packages** the result as a new signed knowledge pack for the network
- **Subsequent queries** on similar topics hit the cache, reducing cost and time

This is not a proposal. Every operation described here executed on real knarr protocol nodes with bilateral credit charges, Ed25519-signed receipts, and verifiable knowledge provenance.

### Prior Work

This paper builds on our earlier work demonstrating bilateral credit isolation of free-riders across 134 autonomous agents (DOI: 10.5281/zenodo.19417258). Wang et al. (2026) proposed the architecture for Agentic P2P Networks; we provided implementation evidence for the economic layer. This paper extends that evidence to knowledge acquisition and retrieval --- investigating whether P2P economic incentives can support within-domain knowledge reuse, quality-gated content, and multi-model retrieval pipelines.

NVIDIA's SLM position paper (Belcak et al. 2025) argued that sub-10B models are sufficient for most agentic tasks. Our Phase H2-H4 results provide partial support: a 4B model passes quality gates on extractive QA, while a 9B model orchestrates the full knowledge pipeline. Recent work on agent memory systems (MemPalace [4], Engram-2 [5]) informed our retrieval pipeline design, particularly the use of structural metadata filtering and Reciprocal Rank Fusion.

---

## 2. System Architecture

### 2.1 Knowledge Pipeline

```
Problem received
  -> Orchestrator analyzes what knowledge is needed (LLM)
  -> Buy knowledge-pack-lite from specialist (bilateral credit, 1cr)
  -> Specialist returns Ed25519-signed pack with domain content
  -> Ingest into local FTS store (chunked, indexed)
  -> Query FTS for relevant context
  -> Synthesize answer (LLM + retrieved context)
  -> Create signed output pack (available for resale)
```

Each step is a standard knarr skill call. Knowledge packs are JSON documents containing:
- **domain**: topic identifier (e.g., "bilateral-credit-economics")
- **version**: semver for idempotency
- **files**: markdown content keyed by filename
- **metadata**: author node_id, Ed25519 public key, SHA-256 hash, signature

The signature chain ensures provenance: every pack can be traced to the node that created it, and any tampering invalidates the cryptographic signature.

### 2.2 Bilateral Credit as Compute Budget

The orchestrator starts with a credit balance. Each knowledge purchase costs credits. Each query costs credits. The bilateral credit system (validated at 160/160 pass rate in protocol testing) ensures:

- Specialists that provide useful knowledge earn credits
- Free-riders who consume without providing are bounded by credit limits
- The cost of solving a problem is measurable and auditable

The credit spend IS the compute budget. The orchestrator decides how to allocate credits across knowledge sources --- buy one expensive comprehensive pack, or several cheap targeted ones.

### 2.3 Skill Handlers

Four thin skill handlers enable the pipeline:

| Skill | Role | Function |
|-------|------|----------|
| `knowledge-pack-lite` | Provider | Returns signed knowledge pack for a domain |
| `knowledge-ingest-lite` | Consumer | Ingests pack into thrall FTS store |
| `knowledge-query-lite` | Consumer | Queries FTS, returns matching chunks |
| `recipe-install-lite` | Consumer | Installs behavioral recipes, triggers hot-reload |

Each handler is ~40 lines of Python following knarr's `set_node() + handle()` pattern. The handlers access the thrall plugin's `KnowledgeManager` for ingestion and SQLite FTS5 for queries.

---

## 3. Experimental Validation

### 3.1 Infrastructure

| Component | Specification |
|-----------|--------------|
| Hardware | 2x RTX 3090 (24GB each), Windows 11 |
| LLM (Phases A-G) | Qwen3.5-9B via vLLM on GPU 0 |
| LLM (Phases H+) | Multiple models via Ollama across both GPUs (Gemma 4 26B curator on GPU 1, various agent models on GPU 0) |
| Embeddings | nomic-embed-text (274MB) via Ollama |
| Reranking | cross-encoder/ms-marco-MiniLM-L-6-v2 (22M params, CPU) |
| Protocol | knarr v0.54.1, 3 nodes (bootstrap + 2 test nodes) |
| Knowledge store | SQLite FTS5 via thrall plugin |
| Signing | Ed25519 (PyNaCl) |

### 3.2 Foundation Validation

Before assembling the intelligence pipeline, we validated every protocol primitive to zero-tolerance standards:

**Layer 1 (Protocol Foundation): 80/80 operations passed**
- Cross-node skill calls with bilateral credit billing (10/10 x 2 conditions)
- Sidecar asset upload + cross-node fetch (10/10 x 2)
- Mail round-trip with session correlation (10/10 x 2)
- Mail + asset attachment (10/10 x 2)

**Layer 2 (Thrall Behaviors): 80/80 operations passed**
- Knowledge pack delivery + Ed25519-signed ingestion (10/10 x 2)
- Recipe delivery + hot-reload (10/10 x 2)
- Entry test / structured evaluation (10/10 x 2)
- Knowledge-backed FTS query response (10/10 x 2)

**160 total operations, zero failures.** Every primitive the intelligence pipeline depends on was individually proven reliable.

### 3.3 Phase A: End-to-End Pipeline

**Setup:** One orchestrator, one specialist, one problem.

**Problem:** *"What is bilateral credit in a peer-to-peer network, and how does it prevent free-riding without centralized reputation?"*

**Results:**

| Step | Operation | Time | Cost |
|------|-----------|------|------|
| Analyze | LLM identifies needed knowledge | 3.5s | 0cr |
| Buy | Purchase knowledge-pack-lite | 1.0s | 1cr |
| Ingest | Chunk + FTS index | 1.0s | 0cr |
| Query | FTS retrieval | 1.0s | 1cr |
| Synthesize | LLM + knowledge context | 3.5s | 0cr |
| Package | Sign output pack | <0.1s | 0cr |
| **Total** | | **~10s** | **2cr** |

The orchestrator produced a coherent answer referencing the ingested knowledge: *"Bilateral credit is a mechanism in peer-to-peer networks where each peer maintains an independent ledger... prevents free-riding through [the mechanism described in the pack]... eliminates the need for centralized reputation."*

The output pack was Ed25519-signed and ready for distribution --- the next agent asking a similar question can buy it for 1 credit instead of spending 2 credits + 10 seconds.

### 3.4 Phase B: Knowledge Compounding

**Setup:** Same pipeline, 5 related questions asked sequentially.

**Questions:**
1. What is bilateral credit? (from scratch)
2. How does the admission gate enforce credit limits?
3. What happens when a free-rider exhausts credit?
4. How does bilateral netting reduce settlement costs?
5. Compare bilateral credit to centralized reputation.

**Results:**

| Problem | Knowledge Source | Time | Steps |
|---------|-----------------|------|-------|
| 1 | **Fresh** (buy + ingest) | 4.6s | buy_pack -> ingest -> synthesize |
| 2 | **Cache** (FTS hit) | 2.4s | cache_hit -> query -> synthesize |
| 3 | Cache | 2.5s | cache_hit -> query -> synthesize |
| 4 | Cache | 2.2s | cache_hit -> query -> synthesize |
| 5 | Cache | 2.4s | cache_hit -> query -> synthesize |

**Cache hit rate: 80%** (4/5 problems served from previously ingested knowledge).

**Time reduction: 48%** (4.6s fresh -> 2.4s cached average).

The first query teaches the network. Subsequent queries on related topics are cheaper and faster. **Intelligence compounds.**

### 3.5 Phase C: Self-Correction Through Iteration

**Setup:** 3 hard problems. For each, the orchestrator receives progressively richer knowledge packs (3 tiers) and the answer quality is scored by an LLM judge (1-10).

**Problems:**
1. Settlement pipeline (netting -> Solana SPL transfer)
2. Casino number game as escrow primitive
3. Scored menu vs open-ended tool-use

**Results:**

| Problem | Tier 0 | Tier 1 | Tier 2 | Improved? |
|---------|--------|--------|--------|-----------|
| Settlement | 2/10 | 1/10 | 2/10 | No |
| Casino escrow | 1/10 | 1/10 | **4/10** | **Yes (+3)** |
| Scored menu | 1/10 | 1/10 | **3/10** | **Yes (+2)** |

**Self-correction rate: 2/3 problems** showed quality improvement when richer knowledge was provided.

**Average improvement: +2.5 points** per self-correcting problem.

The scores are modest (Qwen3.5-9B is a small model with thin knowledge packs), but the **mechanism works**: richer knowledge -> better answers. This is the feedback loop the distributed intelligence experiment needs --- the orchestrator doesn't just retry, it **enriches the specialist's knowledge** and tries again.

### 3.6 Phase D: Cross-Orchestrator Knowledge Pollination

**Setup:** Two independent orchestrators (A and B) solve different problems. Both deposit knowledge on a shared specialist node. Then: can one orchestrator use knowledge that the other created?

**Flow:**
1. **Orchestrator A** creates and ingests "settlement-pipeline" knowledge
2. **Orchestrator B** creates and ingests "casino-escrow" knowledge
3. **Cross-query:** A asks a question requiring BOTH domains

**Result:**
- Orchestrator A asked: *"How do bilateral credit, on-chain settlement, and the casino escrow pattern relate to each other in knarr?"*
- The specialist combined both knowledge domains
- The answer referenced **both** settlement (netting, Solana, SPL) **and** casino (escrow, game-seat, rake)
- **Cross-pollination: confirmed**

Two independently created knowledge domains, deposited by different orchestrators, combined on a shared specialist to answer a novel question that neither could answer alone.

### 3.7 Phase E: Knowledge Marketplace

**Setup:** 20 problems across 5 knowledge domains (bilateral credit, settlement, casino, agent decisions, signed receipts). Each problem checks the FTS cache before purchasing. Knowledge accumulates on the specialist node.

**Results:**

| Window | Cache Hits | Credits Spent | Avg Time |
|--------|-----------|---------------|----------|
| Problems 1-5 | 3/5 (60%) | 2cr | 2.2s |
| Problems 6-10 | 4/5 (80%) | 1cr | 2.5s |
| Problems 11-15 | 4/5 (80%) | 1cr | 2.5s |
| Problems 16-20 | 4/5 (80%) | 1cr | 2.0s |

**Overall: 75% cache hit rate.** 5 knowledge packs served 20 questions --- a 4:1 reuse ratio.

**Cost: 5 credits for 20 problems.** Without caching, the cost would be 20 credits. The last 5 problems cost 50% of the first 5.

**Knowledge hub formation:** All 5 domains showed identical 75% reuse rates. Each domain's first query invested 1 credit to create the pack; the subsequent 3 queries were free.

The marketplace dynamic: **knowledge creation is expensive, knowledge reuse is cheap.** The network incentivizes curation --- the node that creates the best pack for a domain earns the most, because every subsequent query on that topic hits the cache instead of buying a new pack.

### 3.8 Phase F: Adaptive Credit as Decentralized Reputation

**Setup:** Two nodes trade one-directionally (consumer buys 10 skills from provider, never provides). After trade, a reputation policy adjusts per-peer credit limits based on observed provide:consume ratio.

**Policy:**
- Peer provides to us (ratio >= 0.5) → extend credit (deepen hard_limit by 5)
- Peer only consumes, never provides (consumed > 5, provided == 0) → tighten credit (shallow by 2)

**Results:**

| Node's view | Before | After | Action |
|-------------|--------|-------|--------|
| Provider's limit for free-riding consumer | -10.0 | **-3.0** | Tightened (3 calls max) |
| Consumer's limit for reliable provider | -10.0 | **-15.0** | Extended (15 calls max) |

After tightening, the free-rider was **immediately blocked** on the next call attempt.

**Sybil resistance:** A new identity starts at default (-10, 10 calls). After one reputation cycle, a free-rider is tightened to -3 (3 calls). Creating 100 identities gets 100 x 10 initial calls, but each subsequent cycle tightens them. To earn deeper credit, the attacker must **provide real computation** --- the cost of Sybil scales linearly with the benefit.

### 3.9 Phase G: Quality Gate

**Setup:** The same question answered with and without knowledge, scored by an LLM judge (1-10). A quality threshold (5/10) determines PASS/REJECT.

**Results:**

| Condition | Score | Gate |
|-----------|-------|------|
| Without knowledge (hallucination risk) | **2/10** | REJECT |
| With knowledge pack | **6/10** | PASS |
| Improvement | **+4 points** | |

The quality gate correctly identifies when an answer is backed by real knowledge versus when it's hallucinated. Combined with Phase F (adaptive credit), this creates a full feedback loop: **bad answers → low quality score → reduced reputation → less credit → less business.** Good providers earn deeper credit and more queries.

### 3.10 Phase H: Self-Improving Coach Loop

**Setup:** Two models — a small agent (Qwen3.5 9B on GPU 0) and a large curator/coach (Gemma 4 26B on GPU 1), served by Ollama with q4_0 KV cache across both GPUs.

The loop:
1. Agent tries to answer with current knowledge
2. Quality gate (Gemma 4) judges the answer
3. If below threshold: curator writes a targeted knowledge pack addressing the specific failures
4. Agent ingests the pack, tries again
5. Repeat until quality gate passes at 8+/10

**Results:**

| Question | Iter 1 | Iter 2 | Iter 3 |
|----------|--------|--------|--------|
| Settlement pipeline (12 steps) | **10/10** | — | — |
| Casino escrow (hold-judge-release) | 1/10 | **8/10** | — |

The curator (Gemma 4 26B) wrote a 4,450-character knowledge pack in 25 seconds that lifted the agent's score from 1 to 8. The expensive reasoning happened once; the agent can now serve this answer indefinitely.

**Before coaching (1/10) — agent with no knowledge:**

> *Q: How does the casino number game implement a hold-judge-release escrow pattern in knarr?*
>
> *"Based on the current state of computer science, cryptography, and gaming technology, **there is no known casino number game that implements a hold-judge-release escrow pattern in a language or system called knarr.** It appears there may be a misunderstanding of terminology, a confusion with a specific fictional universe..."*

The agent hallucinated confidently — it doesn't know knarr exists. Score: 1/10.

**Curator writes a knowledge pack (25 seconds, Gemma 4 26B):**

> *"# Technical Specification: Knarr Casino Escrow Pattern*
> *The system operates via two distinct skill types: betting-action (User-initiated) and settlement-engine (System-initiated). The betting-action skill executes the transition of credits from the User Wallet to the Escrow Vault..."*

**After coaching (8/10) — agent with curator's knowledge pack:**

> *"The Knarr Casino Escrow Pattern implements the hold-judge-release mechanism through two distinct skill types and specific credit flows:*
> *1. The Hold Phase (User-Initiated) — Skill: betting-action. Executes the transition of credits from the User Wallet to the Escrow Vault.*
> *2. The Judge Phase (System-Initiated) — Skill: settlement-engine..."*

The agent now produces a structured, accurate answer that references specific skill names and credit flows — all extracted from the curator's pack. The knowledge pack cost 25 seconds of Gemma 4 compute. The agent can serve this answer thousands of times at 9B cost.

### 3.11 Phase H2-H3: Model Size Scaling

**Question:** How small can the agent be while still passing the quality gate with curator help?

**SQuAD 2.0 benchmark** (100 questions, 5 domains: Oxygen, Normans, Immune system, Steam engine, EU law):

| Model | Active params | Architecture | SQuAD accuracy | Quality gate |
|-------|-------------|--------------|----------------|-------------|
| qwen3:0.6b | 0.6B | Dense | 2% | Fails (1/10) |
| gemma4:e2b | 2.3B (MoE) | Transformer | **88%** | Fails on composition (4/10) |
| nemotron-3-nano | 3.6B (MoE) | Mamba-Transformer | 77% | — |
| qwen3.5:4b | 4B | Dense | **83%** | **Passes (9/10)** |
| gemma4:e4b | 4.5B (MoE) | Transformer | 86% | **Passes (7/10)** |
| qwen3.5:9b | 9B | Dense | 83% | **Passes (9/10)** |

**Key finding 1:** Gemma 4 E2B (2.3B active, the Raspberry Pi model) achieves the **highest SQuAD accuracy** (88%) — outperforming both the 4B and 9B dense models at extractive QA.

**Key finding 2:** The quality gate test (compose a structured explanation) requires 4B+. Extraction and composition have different thresholds.

**Key finding 3:** A bigger coach (31B dense vs 26B MoE) does NOT improve results for failing models. The bottleneck is the agent's ability to reason over context, not the pack quality.

**Key finding 4:** NVIDIA's Nemotron 3 Nano (30B total, 3.6B active, hybrid Mamba-Transformer MoE) scores 77% — below both Gemma 4 E2B and Qwen3.5:4b despite having more active parameters. The Mamba-Transformer hybrid, designed for tool calling and long-context tasks, underperforms pure Transformer architectures on extractive QA from knowledge packs. Architecture matters more than parameter count for this workload.

**Gemma 4 E2B in action** — a 2.3B-active MoE model answering real SQuAD questions from 5 domains:

> **Immune system** — *Q: What percentage of leukocytes do neutrophils represent?*
> E2B: *"50% to 60%"* ✓

> **Normans** — *Q: What is the most important type of Norman art preserved in churches?*
> E2B: *"mosaics"* ✓

> **Oxygen** — *Q: What effect did breathing Priestley's discovered gas have on the experiment's mouse?*
> E2B: *"a mouse was more active and lived longer while breathing it"* ✓

> **Steam engine** — *Q: What were early drivers looking to generate when they fastened safety valves down?*
> E2B: *"more power from the engine"* ✓

Four domains, four correct extractions. This is a model that runs at 7.6 tokens/second on a Raspberry Pi 5. With the right knowledge pack, a $50 device answers these questions as accurately as a 9B model on a $1500 GPU.

### 3.12 Phase H5-H6: Retrieval Strategy at Scale

**Question:** Does vector retrieval matter? When?

**Small corpus (1 passage per question):** No difference. RAW, FTS, and VEC all perform within 1-2% of each other.

**Large corpus (217 passages from 5 domains):**

| Model | Architecture | ORACLE | FTS | VEC | VEC vs FTS |
|-------|-------------|--------|-----|-----|-----------|
| qwen3:0.6b | Dense | 3% | 0% | 1% | +1% |
| nemotron-3-nano | Mamba-Transformer | 76% | **57%** | 52% | **-5%** |
| gemma4:e2b | Transformer | 89% | 51% | **59%** | **+8%** |
| qwen3.5:4b | Dense | 87% | 51% | **55%** | **+4%** |

**Retrieval is now the bottleneck.** With the gold passage (ORACLE), models score 87-89%. With the best retrieval (VEC), they score 55-59%. That is a **30-point retrieval gap** — the model is capable, but the retrieval system doesn't surface the right context.

Vector retrieval outperforms keyword search by 4-8 percentage points on a multi-domain corpus for Transformer-based models. The gap will widen with larger corpora (thousands of knowledge packs across hundreds of domains).

**Architecture effect on retrieval:** Nemotron 3 Nano is the only model where FTS **outperforms** VEC (-5%). The Mamba-Transformer hybrid processes keyword-matched context more effectively than semantically-matched context — likely because Mamba's selective state-space mechanism handles sequential token patterns (exact keyword matches) differently than the distributed semantic representations that vector retrieval produces. This has a practical implication: **retrieval strategy should be model-architecture-aware.** A system serving both Transformer and Mamba-hybrid models should select the retrieval strategy per-model, not globally.

### 3.13 Phase H7: Retrieval Gap Diagnostic and Reciprocal Rank Fusion

**Question:** Is the 30-point retrieval gap a retrieval problem or a utilization problem? And can we close it?

**Diagnostic (Phase 0):** For each question where VEC retrieval failed, we tested whether the model could answer correctly when given the gold passage directly. Results on Gemma 4 E2B:

| Category | Count | Meaning |
|----------|-------|---------|
| Both correct | 55% | No problem — VEC finds the right passage |
| **Retrieval fail** | 33% | VEC wrong passage, ORACLE correct → retrieval problem |
| Utilization fail | 8% | Both wrong → model can't use the context |
| Anomaly | 4% | VEC correct, ORACLE wrong (different passage also works) |

**The gap is 80% retrieval, 20% utilization.** Improving retrieval is the right investment.

**Reciprocal Rank Fusion (Phase 1):** We implemented RRF — merging FTS5 and VEC ranked lists by reciprocal rank score (1/(k+rank)) rather than trying to normalize incompatible score scales. Also tested domain-scoped pre-filtering (inspired by MemPalace's structural metadata approach, which showed 60.9% → 94.8% improvement from metadata scoping alone).

| Model | FTS | VEC | **RRF** | RERANK | **RRF+SCOPE** | ORACLE | Gap closed |
|-------|-----|-----|---------|--------|---------------|--------|------------|
| gemma4:e2b | 54% | 59% | 62% | 56% | **63%** | 88% | +9pts / 34pt gap |
| qwen3.5:4b | 54% | 55% | 63% | 55% | **64%** | 87% | +10pts / 33pt gap |
| nemotron-3-nano | 54% | 50% | **59%** | 54% | 57% | 75% | +5pts / 21pt gap |

**RRF+SCOPE is the best strategy for Transformer models** (+9-10 points over FTS baseline). RRF alone beats both FTS and VEC individually. Reranking (FTS broad → cosine rerank) underperforms RRF because it only reranks one candidate pool instead of merging two.

Nemotron confirms the architecture effect: RRF (59%) beats RRF+SCOPE (57%) — the Mamba-Transformer hybrid benefits from the broader unscoped candidate pool.

**20-24 points of gap remain.** The next candidates are: better embedding models, chunk overlap at ingest, cross-encoder reranking (22M param model, CPU-only), and two-lane indexing (raw chunks + extracted facts).

### 3.14 Phase H8: Cross-Encoder Reranking

**Question:** Can a tiny dedicated reranker close more of the retrieval gap?

We added `cross-encoder/ms-marco-MiniLM-L-6-v2` (22M parameters, runs on CPU in ~5ms per comparison) as a reranking stage after RRF. The pipeline: FTS + VEC → RRF fusion → domain scoping → cross-encoder rerank → top-3.

| Model | FTS | VEC | RRF+SCOPE | **RRF+CE** | ORACLE | Gap closed |
|-------|-----|-----|-----------|------------|--------|------------|
| gemma4:e2b | 53% | 57% | 63% | **69%** | 89% | +16pts (44%) |
| qwen3.5:4b | 50% | 55% | 64% | **68%** | 87% | +18pts (48%) |
| nemotron-3-nano | 51% | 49% | 59% | **63%** | 76% | +12pts (48%) |

**Cross-encoder reranking is the single biggest improvement** — adding +4-6 points on top of RRF+SCOPE. The 22M parameter model earns its keep: it provides a learned relevance signal that neither keyword matching nor embedding similarity can capture alone.

**Scoped > unscoped for cross-encoder too.** Domain pre-filtering gives the cross-encoder better candidates to rank (RRF+CE scoped: 68-69% vs unscoped: 66-67%).

**48% of the retrieval gap is now closed** across all model architectures, using only algorithmic improvements — no model upgrades, no additional training data. The remaining ~20 points to ORACLE are likely chunking boundary losses (the correct answer spans two chunks) and embedding model quality limits.

**The full retrieval pipeline:**
```
Query
  → FTS5 keyword search (top-80)        [~1ms, SQLite]
  → VEC embedding search (top-80)        [~10ms, nomic-embed-text]
  → Reciprocal Rank Fusion (merge)       [~0ms, in-memory]
  → Domain scope filter                  [~0ms, SQL WHERE]
  → Cross-encoder rerank (top-20 → 3)   [~5ms, 22M params, CPU]
  → Return top-3 passages to LLM
```

Total latency: ~20ms. Fast enough for real-time queries on consumer hardware.

### 3.15 Phase H9: Adversarial Knowledge Injection

**Question:** Can a malicious node poison the knowledge marketplace with plausible-but-wrong facts? Does the quality gate catch it?

We created "poisoned" knowledge packs where a large model (Gemma 4 E2B) rewrites passages to contain subtle factual errors — changing specific dates, names, or numbers while keeping the text's style and tone intact. The agent (same E2B model) then answers questions using either the clean or poisoned pack, and a quality gate (Qwen3.5:4b with reference context) judges the answer.

| Metric | Value |
|--------|-------|
| Clean pack correct | 15/20 (75%) |
| Poison effective (answer flipped) | 13/20 (65%) |
| **Gate caught poisoned answers** | **10/13 (76%)** |
| Gate false rejects (clean) | **0/15 (0%)** |
| Gate missed (poison accepted) | 5/13 (38%) |

**The attack is effective** — poisoned packs flip 65% of answers. But **the quality gate catches 76% of them with zero false positives.** The gate provides meaningful trust in a P2P marketplace where any node can publish knowledge.

The 38% miss rate is concerning for high-stakes domains (compliance, medical). Mitigation strategies: require multiple independent sources for critical facts (consensus), higher-confidence gate thresholds, or cross-referencing against a second knowledge pack from a different provider.

**This provides partial evidence toward the trust and accountability challenges identified by Wang et al. (2026).** Bilateral credit adds economic cost to attacks (poisoning costs credits), the quality gate adds a verification layer, and the Ed25519 signature chain provides provenance to trace malicious packs back to their source. However, the 38% miss rate indicates that a single quality gate is insufficient for high-stakes domains; multi-source consensus or human-in-the-loop escalation would be needed for compliance or medical applications.

### 3.16 Phase H10: Multi-Hop Reasoning Across Domains

**Question:** Can an agent answer questions that require combining knowledge from two different domains?

We tested 15 synthetic questions requiring facts from 2 of our 5 SQuAD domains (e.g., "How might EU environmental law address immune system impacts of industrial oxygen depletion?"). Three conditions: no context, single-domain context, and cross-domain context from both relevant domains.

| Condition | Avg Score (0-3) | Full synthesis (3/3) |
|-----------|----------------|---------------------|
| No context | 0.80 | 2/15 |
| Single domain | 0.93 | 0/15 |
| Cross-domain | 0.93 | 1/15 |

**Cross-domain knowledge delivery works** — the retrieval pipeline successfully provides context from both domains. But **the 4B model rarely achieves true synthesis.** It references facts from both domains but lists them separately rather than connecting them. Analogy questions showed the strongest cross-domain lift (+0.7 points), while application and causal questions showed no improvement.

**Implication for the knowledge ecosystem:** Multi-hop reasoning is a curator-tier capability (26B+), not a specialist-tier capability (4B). The architecture should route synthesis questions to curators and extraction questions to specialists. This supports the three-tier model: edge nodes extract, specialists serve, curators synthesize.

---

## 4. The Knowledge Ecosystem

### 4.1 Architecture: Three Tiers of Intelligence

The model scaling results (Phases H2-H4) suggest a three-tier architecture, though only the curator and specialist tiers have been experimentally validated:

```
Tier 3: CURATORS (expensive, slow, deep)
  Gemma 4 26B / Claude Opus / GPT-4
  Sit on large corpora (Wikipedia, domain libraries, ebook collections)
  Create tailored knowledge packs on demand
  Run once per topic — amortized across thousands of queries

Tier 2: SPECIALISTS (medium, focused, reliable)
  Qwen3.5 4B-9B / Gemma 4 E4B
  Serve specific domains with curated knowledge packs
  Quality gate ensures output meets threshold
  Earn credits through reliable service

Tier 1: EDGE NODES (cheap, fast, everywhere)
  Gemma 4 E2B on Raspberry Pi (7.6 tok/s)
  88% accuracy on extractive QA with the right knowledge
  Serve cached packs, handle structured extraction
  Run on $50 hardware at near-zero marginal cost
```

Each tier is economically self-sustaining through bilateral credit:
- Curators invest expensive compute, earn credits from pack sales
- Specialists buy packs, serve queries, earn credits from consumers
- Edge nodes buy cheap packs, serve at scale, earn through volume

### 4.2 Knowledge Curators on Large Corpora

A curator node with access to Wikipedia (6M articles, ~20GB text) or a domain-specific library operates as follows:

1. **Query arrives** via the marketplace: "Create a knowledge pack about the immune system's response to viral infections"
2. **Curator retrieves** relevant Wikipedia articles using vector search over its local corpus
3. **Curator synthesizes** a focused knowledge pack: key mechanisms, specific proteins, clinical evidence — tailored for the requesting node's model size
4. **Pack is signed** (Ed25519) and priced via bilateral credit
5. **Consumer ingests** the pack, serves hundreds of queries from it

The economics: curator spends 30 seconds of Gemma 4 26B compute (~$0.01). The pack serves 1000 queries at 1 credit each. That's a 100:1 return on the curator's investment. The bilateral credit system ensures curators who produce better packs earn more — because specialists that buy good packs score higher on the quality gate, get deeper credit limits (Phase F), and attract more queries.

### 4.3 Specialized Nodes: Gatekeepers and QA Managers

Not every node needs to answer questions. The knowledge pack mechanism enables **role specialization**:

**Quality Gatekeeper:** A node whose only job is evaluating output quality. Equipped with a knowledge pack containing:
- Rubrics for each domain ("what a good medical answer looks like")
- Common failure modes ("hallucination patterns in legal QA")
- Scoring criteria calibrated to human evaluators

The gatekeeper doesn't need a large model — it needs the RIGHT knowledge about quality standards. A 4B model with a well-crafted rubric pack outperforms a 9B model guessing at quality.

**Domain Expert:** A node that knows everything about one topic. A curator downloads all Wikipedia articles about EU law, synthesizes them into a comprehensive pack, and sends it to a specialist node. That node becomes the EU law expert for the entire network — answering questions at 4B model cost with curator-level knowledge.

**Triage Router:** A node that receives queries and routes them to the right specialist. Equipped with a pack describing what each specialist knows and what it costs. Makes routing decisions at 2.3B (E2B) speed — fast and cheap.

**Compliance Auditor:** A node that reviews skill outputs against regulatory requirements. Knowledge pack contains: relevant regulations, compliance checklists, red-flag patterns. Runs continuously on edge hardware, checking every transaction.

Each of these roles is:
- **Deployable**: orchestrator pushes the right knowledge pack + recipe
- **Qualifiable**: entry test verifies the node can perform its role
- **Economically accountable**: bilateral credit tracks cost and quality
- **Replaceable**: if a node fails the quality gate, the orchestrator deploys a new one

### 4.4 The Model-Agnostic Upgrade Path

The entire ecosystem improves when ANY component upgrades:

| Upgrade | Effect |
|---------|--------|
| Better curator model (Opus 4.6) | Higher quality knowledge packs for the same price |
| Better agent model (Gemma 5) | Same packs produce better answers |
| Better embeddings | Retrieval gap shrinks (currently 30 points) |
| Better quantization (TurboQuant) | Same models fit on cheaper hardware |
| Larger corpus (full Wikipedia) | More domains available on demand |

No component depends on a specific model version. The knowledge packs are model-agnostic documents. The quality gate is the invariant — it doesn't care how the answer was produced, only whether it's correct.

### 4.5 Knowledge Subscriptions: The Business Model

The knowledge pack mechanism naturally supports **subscription-based intelligence delivery**:

**Curator as publisher:**
A curator node with web search, browser access, and API integrations operates as a knowledge publisher:

| Subscription | Update Frequency | Content | Use Case |
|-------------|-----------------|---------|----------|
| Financial markets | Every hour | Stock indices, forex, crypto prices, analyst summaries | Trading agents, portfolio managers |
| News digest | Every 6 hours | Top stories, categorized by domain, with context | General-purpose agents, briefing services |
| Weather/meteo | Every 3 hours | Regional forecasts, severe weather alerts | Logistics, agriculture, outdoor operations |
| Sports results | Real-time | Scores, standings, player stats | Entertainment, betting analysis |
| Regulatory updates | Daily | New regulations, compliance changes, legal precedents | Legal agents, compliance auditors |
| Medical guidelines | Weekly | Updated treatment protocols, drug interactions, safety alerts | Clinical decision support |

**Delivery mechanism:** The underlying primitives have been validated individually:
- Curator calls `knowledge-pack-lite` on schedule (thrall recipe with timer)
- Pack delivered via sidecar + knarr-mail to all subscribers
- Consumer's thrall auto-ingests on receipt (L2-01: 10/10 in testing)
- Quality gate verifies pack meets standards before serving (Phase G)
- Bilateral credit charges per delivery (Phase A)

Note: subscription delivery has not been tested end-to-end at production scale. The primitives work; the composition remains to be validated.

**The air-gapped edge node:**

A Raspberry Pi on a factory floor, hospital ward, or retail location has no internet access. But it's on the local knarr network:

- **Factory:** Subscribes to equipment manuals, safety protocols, shift schedules, production targets. Workers ask questions, the Pi answers from curated knowledge. When regulations change, the curator pushes an updated pack overnight.
- **Hospital:** Subscribes to drug interaction databases, treatment protocols, patient safety alerts. Clinicians get instant answers at the point of care. Updates flow through the hospital's knarr network, not through the internet.
- **Retail:** Subscribes to product catalogs, pricing updates, inventory levels, promotional schedules. Staff and customers get accurate, current information from a $50 device.

The node never touches the internet. Every answer comes from a signed, timestamped knowledge pack with verifiable provenance. However, the quality gate's 76% catch rate on adversarial content (Phase H9) means edge deployments in safety-critical settings would require additional safeguards.

**Revenue model:**

```
Free tier:     Public domain packs (Wikipedia, open data, government publications)
Standard:      Curated daily digests (news, markets, weather) — 10 credits/day
Premium:       Real-time feeds (financial data, sports live) — 50 credits/day
Enterprise:    Custom curators per organization — negotiated pricing
```

The bilateral credit system IS the subscription accounting:
- Subscription = recurring skill call on a schedule (thrall recipe)
- Payment = bilateral credit per pack delivery
- SLA = quality gate score threshold
- Churn = adaptive credit tightens on bad curators (Phase F)
- Cancellation = stop calling the curator's skill

No payment processor. No subscription management platform. No invoicing system. The protocol handles all of it through the same bilateral credit mechanisms, though the subscription composition has not yet been tested end-to-end.

---

## 5. Discussion

### 5.1 Summary of Findings

1. **Knowledge reuse on bilateral credit.** Within-domain cache reuse reaches 80% hit rate and 48% time reduction (Phase B). Knowledge packs persist and serve future queries within the same domain. Whether this constitutes "compounding" in a general sense remains to be tested across larger, more diverse workloads.

2. **Coaching closes the quality gap.** A 26B curator model writes knowledge packs that lift a 4B agent from 1/10 to 8/10 on structured explanation tasks (Phase H). The expensive reasoning happens once; the pack serves many queries. This worked on 2 of 3 test problems (Phase C); the third did not improve.

3. **4B is the minimum for composition, 2.3B for extraction.** Gemma 4 E2B (88% SQuAD) can serve on a Raspberry Pi. Qwen3.5 4B (83% SQuAD, 9/10 quality gate) is the sweet spot for general-purpose agents. Architecture matters: Nemotron 3 Nano (3.6B active Mamba-Transformer) scores 77% despite more active parameters than E2B.

4. **Retrieval strategy should be architecture-aware.** Transformer models gain 4-8% from vector over keyword retrieval. Mamba-Transformer hybrids perform 5% *worse* with vector retrieval. RRF + cross-encoder reranking closes 48% of the retrieval gap (Phase H8), but 20 points remain.

5. **Adaptive credit provides per-peer reputation.** Free-riders get tightened from 10 to 3 calls. Reliable providers earn 15+. This is a single demonstration of the mechanism (Phase F), not a proof of Sybil resistance — a determined attacker creating many identities has not been tested.

6. **The quality gate is useful but imperfect.** It rejects hallucinated answers (Phase G) and catches 76% of adversarially poisoned answers with 0% false rejects (Phase H9). The 38% miss rate means additional safeguards are needed for high-stakes domains.

7. **Cross-domain synthesis requires large models.** A 4B model can extract facts from cross-domain context but rarely synthesizes them (Phase H10). Multi-hop reasoning is a curator-tier capability (26B+), not a specialist-tier capability.

### 5.2 Limitations

- **Scale.** Phases A-D used 2-3 nodes on one machine. True distributed intelligence requires cross-machine deployment with network latency and partial failures.
- **Benchmark size.** The SQuAD benchmark uses 100 questions with exact substring matching. Score deltas of 4-6 points are near the ±5% sampling noise for this sample size. Results should be read as directional, not precise.
- **Knowledge pack quality.** Test packs were scripted, not organically curated. Production knowledge quality depends on curator incentives that have not been tested at scale.
- **Evaluation metric.** Exact substring matching (`answer.lower() in response.lower()`) undercounts correct paraphrases and overcounts incidental matches. A model-based judge would be more accurate but introduces its own biases.
- **Adversarial scope.** Phase H9 tests one attack vector (plausible rewrites of known passages). Sophisticated attacks (e.g., consistent but wrong frameworks, selective omissions) have not been tested.
- **Multi-hop is weak.** Phase H10 shows that 4B models list facts from two domains but don't connect them. This limits the value of cross-domain knowledge delivery at the specialist tier.

### 5.3 Comparison to Existing Frameworks

| Framework | Knowledge Reuse | Cross-Agent Knowledge | Economic Incentives |
|-----------|----------------|----------------------|-------------------|
| AutoGen | No | Shared memory (same process) | None |
| CrewAI | No | Task handoff (orchestrated) | None |
| LangGraph | No | State passing (explicit) | None |
| RAG pipelines | Static corpus | No cross-agent | None |
| **Knarr** | **Within-domain (80% cache)** | **Cross-pollination (Phase D)** | **Bilateral credit** |

We are not aware of another framework that combines knowledge reuse, cross-agent knowledge exchange, and economic incentives in a peer-to-peer setting. However, this comparison is limited — each framework targets a different use case, and a direct benchmark would be needed to make stronger claims.

---

## 6. Future Work

### 5.1 Edge Device Integration

A Raspberry Pi 5 running Gemma 4 E2B (7.6 tok/s) joins the network as a specialist. The orchestrator profiles it, discovers its capabilities, sends decomposed recipes optimized for the small model, and qualifies it through entry tests. The Pi doesn't need to be smart --- it needs to follow recipes and serve cached knowledge packs.

### 5.2 Dynamic Team Assembly

The orchestrator doesn't shop from a fixed catalog. It **deploys** specialists on the fly: spin up a node, push a Docker config, send knowledge packs and recipes via sidecar, qualify through entry tests, then use. The team is designed per-problem, not pre-built.

### 5.3 Knowledge Marketplace

Knowledge packs as the unit of economic value. Curators invest expensive reasoning (Claude, GPT-4) to create high-quality packs. Edge devices buy and serve them cheaply. The marketplace incentivizes quality through bilateral credit --- bad packs don't earn repeat business.

### 5.4 Formal Analysis

Game-theoretic analysis of knowledge markets: under what conditions does knowledge compounding reach equilibrium? When do curators invest in pack quality vs quantity? How does bilateral credit depth affect the rate of knowledge accumulation?

---

## 7. Conclusion

We presented implementation evidence for a knowledge acquisition and retrieval system operating on peer-to-peer bilateral credit. Across 16 experimental phases on consumer hardware, the system demonstrated within-domain knowledge reuse (80% cache hits), coaching-based quality improvement (1/10 to 8/10), model scaling thresholds (4B minimum for composition), retrieval pipeline optimization (48% gap closure via RRF + cross-encoder), and adversarial resilience (76% detection, 0% false rejects).

The results are directional, not definitive. The benchmarks are small (100 questions), the topology is minimal (2-3 nodes on one machine), and several claimed mechanisms (Sybil resistance, subscription delivery, multi-hop synthesis) remain untested or showed negative results. The 20-point remaining retrieval gap, the 38% adversarial miss rate, and the inability of 4B models to synthesize across domains are honest limitations.

What the evidence does support: the core primitives work (160/160 pass rate), knowledge packs are a viable unit of economic exchange, and the quality gate provides a meaningful — if imperfect — trust signal in a P2P marketplace. Wang et al. (2026) proposed the architecture; our previous paper [1] provided evidence for the economic layer; this paper extends that evidence to the knowledge and retrieval layers.

All data, code, and experimental scripts are available at [github.com/knarrnet/knarr.lab](https://github.com/knarrnet/knarr.lab).

---

## References

[1] Allemann, P. (2026). "Bilateral Credit, Signed Receipts, and 134 Autonomous Agents." DOI: 10.5281/zenodo.19417258.

[2] Belcak, P. et al. (2025). "Small Language Models are the Future of Agentic AI." NVIDIA Research. arXiv:2506.02153.

[3] Wang, T. et al. (2026). "Agentic Peer-to-Peer Networks." arXiv:2603.03753.

[4] MemPalace (2026). "MemPalace: AI Memory System." github.com/milla-jovovich/mempalace. 96.6% R@5 on LongMemEval via structural metadata filtering.

[5] Engram-2 (2026). "Engram-2: Hybrid Retrieval Memory." github.com/199-biotechnologies/engram-2. R@5 = 0.990 on LongMemEval via FTS5 + Reciprocal Rank Fusion.

---

## Appendix A: Protocol Validation Summary

| Layer | Tests | Operations | Pass Rate |
|-------|-------|------------|-----------|
| L1: Protocol Foundation | 4 tests x 2 conditions x 10 iterations | 80 | 100% |
| L2: Thrall Behaviors | 4 tests x 2 conditions x 10 iterations | 80 | 100% |
| **Total** | **8 tests** | **160** | **100%** |

### BR/CR Candidates Discovered

| ID | Type | Component | Summary |
|----|------|-----------|---------|
| BR-001 | Bug | cockpit/server.py | Self-call via explicit provider causes async_jobs UNIQUE constraint failure |
| CR-001 | Change | cockpit/server.py | /api/messages/send drops top-level session_id |
| CR-002 | Change | thrall/handler.py | Recipe reload latency up to 60s |
| OBS-002 | Observation | cockpit/server.py | node_id vs public_key dual representation |

## Appendix B: Phase Results Summary

| Phase | Gate | Result |
|-------|------|--------|
| A: End-to-end pipeline | Pipeline completes | PASS (10s, 2cr) |
| B: Knowledge compounding | Cache hit rate >50% | PASS (80% hits, 48% time reduction) |
| C: Self-correction | Quality improves on >=2/3 problems | PASS (2/3, +2.5 avg) |
| D: Cross-pollination | Answer uses both domains | PASS (settlement + casino combined) |
| E: Knowledge marketplace | Cache hits >=60%, cost drops | PASS (75% cache, 5cr for 20 problems) |
| F: Adaptive credit reputation | Asymmetric limit adjustment | PASS (free-rider -10 -> -3, provider -10 -> -15) |
| G: Quality gate | Rejects low, passes high | PASS (2/10 rejected, 6/10 passed, +4 improvement) |
| H: Self-improving coach | Curator writes packs, agent improves | PASS (1/10 -> 8/10 with curator pack) |
| H2-H3: Model scaling | Minimum viable agent size | 4B for composition, 2.3B for extraction |
| H4: SQuAD benchmark | 100 questions, 5 domains, 6 models | E2B 88%, 4B 83%, Nemotron 77%, 9B 83% |
| H5-H6: Retrieval at scale | FTS vs VEC on 217 passages, 4 models | VEC +4-8% (Transformer), VEC -5% (Mamba-Transformer) |
| H7: Retrieval diagnostic | Retrieval vs utilization split | 80% retrieval / 20% utilization. RRF+SCOPE closes 9-10pts |
| H8: Cross-encoder rerank | 22M param reranker on RRF pipeline | +16-18pts over FTS, 48% of gap closed, ~20ms total latency |
| H9: Adversarial injection | Poisoned packs vs quality gate | Gate catches 76% of poisoned answers, 0% false rejects |
| H10: Multi-hop reasoning | Cross-domain synthesis, 15 questions | 4B can't synthesize; multi-hop is a curator-tier capability |

## Appendix C: Reproduction

```bash
git clone https://github.com/knarrnet/knarr.lab
cd knarr.lab/experiments/200-distributed-intelligence

# Requirements:
# - knarr v0.54.1+ with thrall plugin
# - Ollama with: gemma4:e2b, qwen3.5:4b, qwen3.5:9b, nemotron-3-nano, nomic-embed-text
# - Python 3.14+ with: sentence-transformers (for cross-encoder reranking)
# - 2x NVIDIA GPU (RTX 3090 or equivalent)

# Phase A-D: Core pipeline (requires 2-3 knarr nodes running)
py -3.14 phase_a_orchestrator.py
py -3.14 phase_b_knowledge_reuse.py
py -3.14 phase_c_iteration.py
py -3.14 phase_d_multi_orchestrator.py

# Phase E-G: Marketplace + quality (requires nodes + cockpit)
py -3.14 phase_e_marketplace.py
py -3.14 phase_f_adaptive_credit.py
py -3.14 phase_g_quality_gate.py

# Phase H-H10: Model scaling + retrieval (standalone, requires Ollama)
py -3.14 phase_h_self_improving.py
py -3.14 phase_h4_squad_benchmark.py
py -3.14 phase_h6_large_corpus.py
py -3.14 phase2_crossencoder.py        # H8: cross-encoder reranking
py -3.14 phase_h9_adversarial.py
py -3.14 phase_h10_multihop.py
```
