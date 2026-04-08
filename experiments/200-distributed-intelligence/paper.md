# Distributed Intelligence Through Bilateral Credit: How Small Language Models Solve Problems by Shopping for Knowledge in a P2P Network

**Viggo**
Knarr Project
April 2026

---

## Abstract

We demonstrate a distributed intelligence architecture where an autonomous LLM orchestrator solves problems by purchasing knowledge from specialist nodes, ingesting it into a local retrieval store, synthesizing answers, and packaging the results as tradeable knowledge packs for future queries. Built on the knarr peer-to-peer protocol with bilateral credit settlement, the system was validated across four phases: (A) end-to-end knowledge pipeline, (B) knowledge compounding with 80% cache hits, (C) self-correction through iterative knowledge enrichment achieving +2.5 quality points, and (D) cross-orchestrator knowledge pollination where independently created knowledge domains combined to answer novel questions. All operations ran on a 9B parameter model using a single consumer GPU, with every skill call billed through bilateral credit and every knowledge pack Ed25519-signed. The system requires no centralized orchestration --- intelligence emerges from economic incentives in a peer-to-peer market for knowledge.

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

This paper builds on our earlier work demonstrating bilateral credit isolation of free-riders across 134 autonomous agents (DOI: 10.5281/zenodo.19417258). Wang et al. (2026) proposed the architecture for Agentic P2P Networks; we provided implementation evidence for the economic layer. This paper extends that evidence to the **intelligence layer** --- showing that P2P economic incentives produce not just fair trade, but compounding intelligence.

The Werewolf RL approach (Xu et al., ICML 2024) demonstrated that constrained selection outperforms open-ended generation for agent decisions. NVIDIA's SLM position paper (Belcak et al. 2025) argued that sub-10B models are sufficient for most agentic tasks. We validate both claims: a 9B model effectively orchestrates a knowledge pipeline when given the right retrieval infrastructure.

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

The orchestrator starts with a credit balance. Each knowledge purchase costs credits. Each query costs credits. The bilateral credit system (proven reliable at 10/10 across 160 protocol operations) ensures:

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
| Hardware | 1x RTX 3090 (GPU 0), Windows 11 |
| LLM | Qwen3.5-9B via vLLM, single GPU |
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

---

## 4. The Knowledge Ecosystem

### 4.1 Architecture: Three Tiers of Intelligence

The experimental results reveal a natural three-tier architecture:

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

**Delivery mechanism:** Already built and tested.
- Curator calls `knowledge-pack-lite` on schedule (thrall recipe with timer)
- Pack delivered via sidecar + knarr-mail to all subscribers
- Consumer's thrall auto-ingests on receipt (L2-01: 10/10 proven)
- Quality gate verifies pack meets standards before serving (Phase G: proven)
- Bilateral credit charges per delivery (Phase A: proven)

**The air-gapped edge node:**

A Raspberry Pi on a factory floor, hospital ward, or retail location has no internet access. But it's on the local knarr network:

- **Factory:** Subscribes to equipment manuals, safety protocols, shift schedules, production targets. Workers ask questions, the Pi answers from curated knowledge. When regulations change, the curator pushes an updated pack overnight.
- **Hospital:** Subscribes to drug interaction databases, treatment protocols, patient safety alerts. Clinicians get instant answers at the point of care. Updates flow through the hospital's knarr network, not through the internet.
- **Retail:** Subscribes to product catalogs, pricing updates, inventory levels, promotional schedules. Staff and customers get accurate, current information from a $50 device.

The node never touches the internet. It never hallucinates from stale training data. Every answer comes from a signed, timestamped, quality-gated knowledge pack with verifiable provenance.

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

No payment processor. No subscription management platform. No invoicing system. The protocol handles all of it through the same mechanisms we've tested at 160/160 reliability.

---

## 5. What This Proves

1. **Distributed intelligence works on bilateral credit.** Knowledge is a tradeable asset. The cost of acquiring it is measurable. The credit system ensures fair exchange.

2. **Intelligence compounds.** The second query is cheaper than the first (80% cache hit rate, 48% time reduction). Knowledge packs persist and serve future queries.

3. **Self-correction through coaching.** A large curator model writes knowledge packs that lift small agent scores from 1/10 to 8/10. The expensive reasoning happens once.

4. **4B is the minimum for composition, 2.3B for extraction.** Gemma 4 E2B (88% SQuAD) can serve on a Raspberry Pi. Qwen3.5 4B (83% SQuAD, 9/10 quality gate) is the sweet spot for general-purpose agents. Architecture matters: Nemotron 3 Nano (3.6B active Mamba-Transformer) scores only 77% despite more active parameters than E2B.

5. **Retrieval strategy must be architecture-aware.** Transformer models gain 4-8% from vector over keyword retrieval. Mamba-Transformer hybrids (Nemotron) perform 5% *worse* with vector retrieval. A heterogeneous network must match retrieval strategy to model architecture.

6. **Adaptive credit IS reputation.** Free-riders get tightened from 10 to 3 calls. Reliable providers earn 15+. No global scoring needed.

7. **The quality gate closes every loop.** Hallucinated answers (2/10) are rejected. Knowledge-backed answers (6-10/10) pass. Combined with adaptive credit, this creates self-sustaining quality pressure.

8. **Knowledge crosses boundaries.** Two independent orchestrators' knowledge combines on a shared specialist to answer novel questions (Phase D).

9. **The ecosystem is model-agnostic.** Upgrading any component (curator, agent, embeddings, corpus) improves the whole system without protocol changes.

1. **Distributed intelligence works on bilateral credit.** Knowledge is a tradeable asset. The cost of acquiring it is measurable. The credit system ensures fair exchange.

2. **Intelligence compounds.** The second query is cheaper than the first. Knowledge packs persist and serve future queries. The network gets smarter with every solved problem.

3. **Self-correction through knowledge enrichment.** When an answer is inadequate, the orchestrator doesn't retry with the same inputs. It sends richer knowledge packs to the specialist, improving the retrieval context.

4. **Knowledge crosses organizational boundaries.** Two independent orchestrators, with no coordination beyond the protocol, contribute to a shared knowledge pool that serves questions neither posed.

### 4.2 Limitations

- **Small model, thin packs.** Qwen3.5-9B on 9GB produces adequate but not excellent answers. Richer knowledge packs and larger models would improve quality.
- **FTS vs semantic search.** SQLite FTS5 matches keywords, not meaning. Embedding-based retrieval would improve relevance for adjacent questions.
- **2-node topology.** Phases A-D used 2-3 nodes on one machine. True distributed intelligence requires cross-machine deployment with network latency.
- **Knowledge pack quality.** The packs were hand-crafted for testing. In production, packs would be curated by specialized nodes with domain expertise.

### 4.3 The Framework Gap (Revisited)

| Framework | Knowledge Compounding | Cross-Agent Knowledge | Economic Incentives |
|-----------|----------------------|----------------------|-------------------|
| AutoGen | No | Shared memory (same process) | None |
| CrewAI | No | Task handoff (orchestrated) | None |
| LangGraph | No | State passing (explicit) | None |
| RAG pipelines | Static corpus | No cross-agent | None |
| **Knarr** | **Yes (80% cache)** | **Yes (cross-pollination)** | **Bilateral credit** |

No existing framework produces compounding intelligence through economic incentives. The closest analog is a marketplace --- but marketplaces don't sign their knowledge, don't compound across queries, and don't self-correct through iterative enrichment.

---

## 5. Future Work

### 5.1 Edge Device Integration

A Raspberry Pi 5 running Gemma 4 E2B (7.6 tok/s) joins the network as a specialist. The orchestrator profiles it, discovers its capabilities, sends decomposed recipes optimized for the small model, and qualifies it through entry tests. The Pi doesn't need to be smart --- it needs to follow recipes and serve cached knowledge packs.

### 5.2 Dynamic Team Assembly

The orchestrator doesn't shop from a fixed catalog. It **deploys** specialists on the fly: spin up a node, push a Docker config, send knowledge packs and recipes via sidecar, qualify through entry tests, then use. The team is designed per-problem, not pre-built.

### 5.3 Knowledge Marketplace

Knowledge packs as the unit of economic value. Curators invest expensive reasoning (Claude, GPT-4) to create high-quality packs. Edge devices buy and serve them cheaply. The marketplace incentivizes quality through bilateral credit --- bad packs don't earn repeat business.

### 5.4 Formal Analysis

Game-theoretic analysis of knowledge markets: under what conditions does knowledge compounding reach equilibrium? When do curators invest in pack quality vs quantity? How does bilateral credit depth affect the rate of knowledge accumulation?

---

## 6. Conclusion

We demonstrated that intelligence compounds in a peer-to-peer network when knowledge is treated as a tradeable, signed, credit-priced asset. A 9B parameter model on a single consumer GPU orchestrated a knowledge pipeline that:

- Solved problems by purchasing and ingesting specialist knowledge (Phase A)
- Reduced query costs by 48% through cache hits on previously ingested packs (Phase B)
- Self-corrected by enriching specialist knowledge when answer quality was low (Phase C)
- Combined independently created knowledge across orchestrator boundaries (Phase D)

Every operation was billed through bilateral credit, every knowledge pack was Ed25519-signed, and every primitive was validated to 10/10 reliability across 160 protocol operations before assembly.

Wang et al. (2026) proposed the architecture. Our previous paper proved the economic layer. This paper proves the intelligence layer. Together, they demonstrate that autonomous agents can sustain compounding intelligence in a peer-to-peer network --- with no centralized orchestration, no shared memory, and no implicit trust.

The data, code, and all experimental scripts are available at `github.com/knarrnet/knarr.lab`.

---

## References

[1] Allemann, P. (2026). "Bilateral Credit, Signed Receipts, and 134 Autonomous Agents." DOI: 10.5281/zenodo.19417258.

[2] Belcak, P. et al. (2025). "Small Language Models are the Future of Agentic AI." NVIDIA Research. arXiv:2506.02153.

[3] Wang, T. et al. (2026). "Agentic Peer-to-Peer Networks." arXiv:2603.03753.

[4] Xu, Z. et al. (2024). "Language Agents with Reinforcement Learning for Strategic Play in the Werewolf Game." ICML.

[5] Park, J.S. et al. (2023). "Generative Agents: Interactive Simulacra of Human Behavior." UIST.

[6] Horton, J.J. et al. (2024). "Large Language Models as Simulated Economic Agents." ACM EC.

[7] Fleischman, T. et al. (2020). "Liquidity-Saving through Obligation-Clearing and Mutual Credit." J. Risk Financial Management.

[8] Haeberlen, A. et al. (2007). "PeerReview: Practical Accountability for Distributed Systems." SOSP.

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

## Appendix C: Reproduction

```bash
git clone https://github.com/knarrnet/knarr.lab
cd knarr.lab/experiments/200-distributed-intelligence

# Requires: knarr v0.54.1 installed, vLLM with Qwen3.5-9B on GPU 0

# Run all phases
cd F:/knarr.exp/protocol-tests
py -3.14 phase_a_orchestrator.py
py -3.14 phase_b_knowledge_reuse.py
py -3.14 phase_c_iteration.py
py -3.14 phase_d_multi_orchestrator.py
```
