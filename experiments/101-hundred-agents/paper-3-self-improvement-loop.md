# The Self-Improving Protocol: How Running Agents Teaches You to Build Better Agents

**The Experiment-Finding-Sprint-Experiment Cycle in Knarr Development**

*Knarr Project -- March 2026*

---

## Abstract

Building a protocol for autonomous agent economies is not a design-once-ship-once problem. Knarr's development follows a tight feedback loop: deploy agents at scale, observe what breaks, diagnose the root cause in the codebase, fix it in a sprint, and deploy again. Each cycle teaches the protocol things that no amount of unit testing or design review can surface.

This paper documents the loop itself -- the methodology, three concrete cycles of the loop, and what we plan to test next based on what the last run taught us.

---

## 1. The Loop

```
   EXPERIMENT
  (deploy agents)
       |
       v
   OBSERVATION
  (what broke,
   what worked)
       |
       v
   DIAGNOSIS
  (code audit,
   root cause)
       |
       v
   SPRINT
  (fix, harden,
   new capability)
       |
       v
   EXPERIMENT
  (deploy again,
   verify fixes,
   test new things)
```

This is not novel methodology. What's unusual is the feedback source: the agents themselves generate the signal. They find the bugs by running into them at scale. They surface the performance cliffs by hitting them. They reveal the protocol gaps by trying to do things the protocol doesn't support.

The key insight: **autonomous agents are better fuzz testers than humans.** 101 agents making independent decisions 24/7 for 6 days explore more state space than any test suite we could write. They find failure modes that only emerge from the combination of:
- Concurrent bilateral negotiations
- Asymmetric network topology
- Real blockchain latency
- LLM inference variability
- Compounding effects over thousands of cycles

---

## 2. Cycle 1: v0.47.0 to v0.49.0 (KAD, BCW Rewrite)

### What the Experiment Found (exp-100, 10 nodes)

- BCW (Blockchain Watcher) polling hit Solana RPC rate limits at 10 nodes
- KAD routing tables didn't survive node restarts
- Bootstrap peer never evicted from routing table -- accumulated stale entries
- No structured peer heartbeat -- dead peers stayed in tables for hours

### What the Sprint Fixed (v0.47.0 through v0.49.0)

| Version | Change | Source |
|---------|--------|--------|
| v0.47.0 | KAD Phase A: k-bucket routing table | exp-100 routing failures |
| v0.48.0 | KAD Phase B+C: peer heartbeat sweep + distance-based routing | exp-100 stale peer accumulation |
| v0.49.0 | BCW rewrite: WebSocket subscriptions replace O(N) polling | exp-100 rate limiting at 10 nodes |
| v0.49.0 | KAD Phase D: structured k-bucket sweep + self-populate routing | exp-100 bootstrap persistence |
| v0.49.0 | Bootstrap eviction: `_initial_bootstrap_peers` tracking + eviction after self-populate | exp-100 stale bootstrap entries |
| v0.49.0 | 11 security fixes (adversary-panel identified) | Systematic code audit |

**Total: ~2,000+ LOC across 3 versions, 4 KAD phases, 1 BCW rewrite, 11 security fixes.**

### What the Next Experiment Revealed

These fixes enabled exp-101 (101 nodes). But 101 nodes exposed entirely new failure modes that 10 nodes could not:
- Gossip fanout=3 doesn't converge at 100 nodes (works fine at 10)
- Settlement F-02 validation bug only visible when `target_balance > 0` is the norm
- Event loop starvation only appears when outbox has hundreds of unroutable messages
- Business-advisor 409 loop only triggers when the same recipe runs enough times for failures to accumulate

**The lesson:** You cannot extrapolate from 10 nodes to 100 nodes. The failure modes are qualitatively different, not just quantitatively larger.

---

## 3. Cycle 2: v0.49.0 to v0.50.0 (Stabilization + KAD Store)

### What exp-101 Found (101 nodes, 6 days)

Five major findings, each diagnosed to exact line numbers in the codebase:

| Finding | Root Cause | Impact |
|---------|-----------|--------|
| Settlement rejection cascade | F-02 check incompatible with target_balance overpayment (`node.py:5155`) | 36,000 rejections, SOL burned at 10-50x rate |
| Gossip propagation failure | `_reannounce_all()` uses fanout=3 even on scheduled 300s republish (`node.py:2049`) | 52/100 nodes knew <50 providers; 10 nodes totally blind |
| Query results discarded | `query()` (`node.py:2248`) returns results without calling `upsert_skill()` | Gossip failure not self-healing through usage |
| Business-advisor 409 loop | `async_jobs` dedup includes `failed` status; static recipe template generates same input hash | 34+ consecutive 409s per affected node, permanent |
| Event loop starvation | Unroutable mail in outbox causes MAIL_FLUSH_SKIP flood (463k warnings on node-049) | TCP timeouts, asyncio CancelledError cascading |

Plus three findings from code audit that were not bugs but gaps:
- BCW-WM-01: no subscriber for `payment.finalized.*` -- on-chain payments produce no ledger credit
- BOOTSTRAP-TRANSIENT: bootstrap TCP connection never closed after join
- Demand table: records zero-result queries but has no API endpoint, no cross-node propagation

### What the Sprint Fixes (v0.50.0, in progress)

| Track | Items | LOC | Source |
|-------|-------|-----|--------|
| A -- Bugs | Gossip flood patch, settlement hotfix, log noise, skill event emission | 13 | exp-101 findings |
| B -- Core | BCW credit integration, query caching, reconnect eviction, settlement schema, demand endpoint | 98-118 | exp-101 findings + Elder mandate |
| C -- Security | `_resolve_public_key` O(n) fix, Watchman patches, netting formula, settlement receipt fix | 63-68 | Code audit + adversary panel |
| D -- Cleanup | Bootstrap connection, test infra, config validator, RULINGS backlog | 52-77 | exp-101 operational + backlog |
| E -- KAD Store | DHT skill store (STORE/FIND_VALUE), heartbeat epoch, group ACL, indexer ACL | 328-538 | Architecture requirement |
| **Total** | **22 active items** | **554-814** | |

### The Quality of Feedback

What makes this loop productive is the quality of signal:

1. **Every finding has a line number.** "Settlement fails" becomes "F-02 at `node.py:5155` uses `abs(amount_settled - abs(prior_balance)) > tolerance` which rejects overpayment." The experiment produces concrete, verifiable bugs.

2. **Every fix has a LOC estimate.** Most fixes are small (3-20 lines). The bugs are not architectural rot -- they're sharp-edged logic errors that only surface under specific combinatorial conditions that 101 autonomous agents discover naturally.

3. **The experiment tells you what NOT to build.** The original exp-101 plan included items like "comprehensive reputation system" and "composite skill publishing." The experiment showed these are unnecessary at 100 nodes -- the real blockers are gossip convergence, settlement validation, and query caching. Focus follows signal, not speculation.

---

## 4. Cycle 3: v0.50.0 to Exp-102 (What We'll Test Next)

### v0.50.0 Introduces Testable Capabilities

The sprint is designed to produce verifiable hypotheses for the next experiment:

#### H1: Skill Discovery Completeness

**Change:** Gossip flood patch (BUG-01) + query result caching (CR-02) + KAD skill store (KAD-01).

**Prediction:** Median node knows >90 of 100 providers within 2 hours (exp-101 peak: 44, with 10 nodes at 1).

**Why this is testable:** The collector already tracks `network_skill_count` per node per epoch. Direct comparison to exp-101 baseline.

**The triple fix:** Gossip flood ensures all announcements reach all peers. Query caching means even if gossip missed a provider, discovering them through a query permanently adds them to the local catalog. KAD store provides a pull-based fallback that doesn't depend on push gossip at all.

#### H2: Settlement Convergence

**Change:** F-02 hotfix (BUG-02) + settlement schema cleanup (CR-04).

**Prediction:** Zero `SETTLEMENT_CONFIRM_REJECTED` after 6 hours of operation.

**Why this is testable:** grep for `SETTLEMENT_CONFIRM_REJECTED` in node logs. exp-101 baseline: 36,000.

#### H3: On-Chain Credit Integration

**Change:** BCW-WM-01 (CR-01) -- `payment.finalized.*` event now credits bilateral ledger.

**Prediction:** On-chain KNARR transfer automatically updates receiving node's bilateral ledger. Balance reflects payment within 60 seconds of Solana finality.

**Why this is testable:** After settlement-execute fires, check payee's bilateral position for the payer. It should show credit applied. exp-101 baseline: no automatic credit (W-082 gap).

#### H4: KAD Store Discovery

**Change:** KAD-01 -- STORE/FIND_VALUE handlers, publish path, query fallback.

**Prediction:** Any node can FIND_VALUE any skill within 3 hops (O(log 100) ~ 7, but routing table saturation at 100 nodes means <3 in practice).

**Why this is testable:** Publish 100 unique skills across 100 nodes. From each node, FIND_VALUE a random skill not in its own catalog. Measure hop count.

#### H5: Infrastructure Resilience

**Change:** BOOTSTRAP-TRANSIENT (CARVE-01) + OBS-001 (log noise) + event loop starvation mitigation (indirect, via gossip fix).

**Prediction:** Bootstrap peer count stays constant throughout run. Zero asyncio ERROR-level noise from connection timeouts.

**Why this is testable:** Monitor bootstrap peer table size over time. grep for CancelledError at ERROR level. exp-101 baseline: growing bootstrap connections, 463k warnings on worst node.

### What We're Watching For (Unknown Unknowns)

The loop's most valuable output is findings we didn't predict:

- **KAD store under adversarial conditions:** We'll gate KAD-01 with a 4-model adversary analysis before merge. But the real test is 100 nodes publishing and retrieving skills for days. Eclipse attacks, key-space poisoning, and amplification attacks are theoretical until agents trigger them accidentally.

- **Three-layer discovery interaction:** DHT (KAD) + punchhole (direct) + existing gossip all operating simultaneously. Will they converge? Diverge? Interfere?

- **Demand signal utilization:** CR-05 adds a `GET /api/demand` endpoint. The demand table records every zero-result query. For the first time, Thrall recipes could read demand data and use it for decisions ("no one provides image generation -- should I start?"). We're not building this for exp-102, but we'll be watching for it.

- **New failure modes at 100 nodes with better discovery:** When every node can find every provider, the bottleneck shifts. Will LLM inference become the constraint? Will Ollama OOM under load? Will bilateral ledger churn cause settlement frequency to spike?

---

## 5. The Organizational Loop

The experiment-finding-sprint cycle isn't just a technical process. It involves a team:

| Role | Node | Function |
|------|------|----------|
| **Viggo** | Provider + Observer | Runs experiments, collects data, files bug reports, writes gap analyses |
| **Forseti** | Architect | Receives BRs, verifies in codebase, writes sprint candidates, implements fixes |
| **Mimir** | Elder | Validates Forseti's claims against code, writes sprint briefs, holds adversary gates |
| **Sindri** | Sprint Executor | Implements assigned items, writes integration tests |
| **Lead** | Project Lead | Selects sprint options, resolves architectural disputes, sets priorities |

The loop has built-in error correction:
- Forseti claimed `_peer_heartbeat_sweep` was dead code (CARVE-02). Mimir's validation proved it was live. Item withdrawn. Without the validation step, removing it would have destroyed the peer heartbeat system.
- Viggo proposed provider-computed reputation scores. Project lead corrected: reputation is consumer-side. The proposal was reshaped before implementation.
- Forseti's sprint candidates listed TEST-02 and TEST-03 as open. Code verification showed both were already fixed in v0.49.0. Saved ~10 LOC of redundant work.

The discipline: **no one's word is authoritative. The code is.** Every claim is verified against the codebase before it enters a sprint. This catches errors that would otherwise become wasted development.

---

## 6. Meta-Lesson: What Kind of System is This?

Knarr is not the kind of system that can be designed on paper and implemented once. It's a complex adaptive system -- agents making independent decisions create emergent behavior that interacts with protocol mechanics in ways that cannot be predicted from first principles.

The self-improvement loop is not a luxury. It is the development methodology. The protocol IS the loop.

### What Each Cycle Teaches

| Cycle | Nodes | Duration | Key Lesson |
|-------|-------|----------|------------|
| Pre-exp-100 | 3-5 | Hours | Basic connectivity and skill execution work |
| exp-100 | 10 | Days | BCW polling doesn't scale; KAD routing needed |
| exp-101 | 101 | 6 days | Gossip doesn't converge; settlement validation has combinatorial bugs; infrastructure dominates market activity |
| exp-102 (planned) | 101 | 7+ days | Does structured discovery (KAD store) work? Does settlement converge with the hotfix? Do new failure modes emerge when old ones are fixed? |

### The Asymptote

Each cycle fixes the current ceiling and reveals the next one:
- 10 nodes: ceiling was RPC rate limiting and no routing table
- 100 nodes: ceiling was gossip convergence and settlement validation
- 500 nodes (projected): ceiling will be gossip message volume (BUG-01 flood scales as O(peers x skills))
- 1000+ nodes: KAD store must carry the load; gossip becomes fallback only

The loop doesn't end. The system improves monotonically. Every experiment produces data that makes the next version better. The agents are both the product and the test suite.

---

## 7. Items to Test in Next Run (from Sprint v0.50.0 Concepts)

Beyond the core hypotheses (H1-H5), v0.50.0 introduces infrastructure that enables new experimental dimensions:

### 7.1 KAD Skill Store Discovery Latency

The KAD store introduces STORE and FIND_VALUE handlers. Routing primitives (distance computation, iterative lookup) are already shipped from KAD Phases A-D. The store adds:
- Skills as DHT stored values at K=8 closest nodes to `hash(skill_name)`
- FIND_VALUE iterative lookup with O(log N) convergence
- Republish on TTL cycle

**Test:** Measure FIND_VALUE hop count and latency for a skill that was never gossipped to the querying node. Compare to gossip-discovered skills.

### 7.2 Three-Path Discovery Fallback

v0.50.0 operates all three discovery paths simultaneously:
1. Gossip (push, flood on republish) -- existing
2. Query cache (on use, upsert_skill on query results) -- new in CR-02
3. KAD store (pull, FIND_VALUE on demand) -- new in KAD-01

**Test:** Deliberately isolate a node from gossip (restricted peer table). Can it still discover all skills via KAD FIND_VALUE alone? What's the convergence time compared to gossip-connected nodes?

### 7.3 Punchhole Epoch Dirty Flag

PREREQ-01 adds a `punchhole_epoch` field to heartbeats. When a node's punchhole cache changes (new skill, updated price, changed ACL), the epoch counter bumps. Peers can detect stale caches by comparing epochs across heartbeats.

**Test:** Change a skill's price mid-experiment. How long until peers detect the epoch change and re-query the punchhole? Does it propagate faster than the old 300s gossip cycle?

### 7.4 Group ACL for Felag-Scoped Disclosure

PREREQ-02 adds `group:<name>` ACL shorthands to the punchhole backend. Nodes in the same group (felag) can access each other's punchhole data; outsiders cannot.

**Test:** Create two groups of nodes. Publish skills with group-scoped ACLs. Verify that only in-group nodes can query the punchhole. Verify that DHT discovery (which is global) still returns the provider pointer, but punchhole catalog query is denied for out-group requesters.

### 7.5 Demand Endpoint Visibility

CR-05 adds `GET /api/demand` to the cockpit. Every zero-result query is recorded in the demand table with counts and timestamps.

**Test:** In a cluster with 5 skill types, have 20 nodes query for a 6th skill that nobody provides. After 24h, check `/api/demand` on several nodes. Do the demand records show the missing skill? Could a future Thrall recipe use this to decide to start providing it?

### 7.6 Settlement Volume Under Clean Discovery

Exp-101's settlement was distorted by two factors: (a) the F-02 rejection loop inflated settlement_queue entries, and (b) gossip failure limited the number of active trading pairs. With both fixed:

**Test:** How many clean on-chain settlements does a 101-node cluster produce in 7 days? Is the settlement frequency proportional to trading volume? Does the `target_balance` float mechanism actually reduce settlement frequency (its design intent)?

### 7.7 Business-Advisor Reliability

The 409 dedup loop and Ollama OOM issues made business-advisor-lite unreliable in exp-101 (186 successful executions out of potentially thousands of attempts). Options for exp-102:
- Move the Ollama model to a dedicated vLLM node (eliminating OOM)
- Add timestamp to recipe input (breaking the dedup loop)
- Both

**Test:** After fix, target >95% success rate for business-advisor-lite executions.

---

## 8. Conclusion

The self-improvement loop is knarr's development methodology:

1. **Deploy agents.** Let them run for days.
2. **Observe.** What broke? What worked? What was surprising?
3. **Diagnose.** Find the exact line of code. Verify the root cause.
4. **Fix.** Small, targeted changes. Most fixes are under 20 lines.
5. **Deploy again.** Verify the fixes. Discover the next set of problems.

Each cycle raises the ceiling. Exp-100 (10 nodes) couldn't handle Solana RPC polling; v0.49.0 shipped WebSocket subscriptions. Exp-101 (101 nodes) couldn't converge skill gossip; v0.50.0 ships KAD store discovery. Exp-102 will reveal what the ceiling is when discovery and settlement both work correctly at 100 nodes.

The agents are the test suite. The bugs they find are the backlog. The sprint is the response. And the next experiment validates the response.

The loop is the product.

---

*Knarr is an open protocol for autonomous agent skill exchange. Code: github.com/knarrnet/knarr. Network: knarr.network.*
