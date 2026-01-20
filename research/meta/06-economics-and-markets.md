# Economics and Mechanism Design for Agent Coordination

## Overview

**The central planning problem:** Current agent orchestration requires someone to explicitly coordinate all agents - assign tasks, resolve conflicts, set priorities. This is **Soviet-style planning** and faces the same scalability problems.

**The market solution:** Create economic mechanisms where agents **self-coordinate** through:
- Prices (signals of scarcity/value)
- Budgets (constraints on resource use)
- Trading (voluntary exchange)
- Incentive alignment (agents pursue self-interest → system-level good)

This document develops the economics/mechanism design mental model for agent governance.

---

## Central Planning vs Markets

### Central Planning (Current Approach)

**How it works:**

```
Central Coordinator (human or orchestrator agent):
  1. Sees all tasks in queue
  2. Assigns tasks to agents based on:
     - Agent capabilities
     - Task priorities
     - Load balancing
  3. Resolves conflicts (if two agents want same resource)
  4. Monitors progress
  5. Reallocates if needed
```

**Problems (echoing Soviet planning):**

1. **Information overload** - Coordinator can't know all local details
   - Which agent is best for task X? (agents know their own capacity better)
   - What's the true cost of context-switching? (hidden to coordinator)
   - What opportunities exist for synergies? (agents on the ground see them)

2. **Slow decision-making** - Bottleneck at coordinator
   - 100 agents → 1 coordinator → serial bottleneck
   - Coordinator becomes overwhelmed (governance crisis)

3. **Incentive misalignment** - Agents game the system
   - Agents hide capacity (to avoid being assigned hard tasks)
   - Agents exaggerate difficulty (to justify more time)
   - No reward for efficiency (why finish fast if you just get more work?)

4. **Rigidity** - Can't adapt to local conditions
   - Coordinator makes plan, agents execute
   - If local context changes, must wait for coordinator to revise
   - Slow feedback loops

5. **Knowledge problem (Hayek)** - Dispersed knowledge can't be centralized
   - Agent A knows: "I can do task X fast because I just did similar task"
   - Coordinator doesn't know this tacit knowledge
   - Inefficient allocation results

**When central planning works:**
- Small scale (< 10 agents)
- Simple tasks (low interdependence)
- Stable environment (planning horizon matches reality)
- Omniscient coordinator (knows all relevant information - rare!)

---

### Market Coordination (Proposed Approach)

**How it works:**

```
Agents are economic actors in a market:
  1. Tasks have prices (set by supply/demand)
  2. Agents have budgets (constraints on spending)
  3. Agents bid for tasks they want to do
  4. Market clears: highest bids win, prices adjust
  5. Agents trade resources (CPU, data, capabilities)
  6. System-level optimization emerges from local decisions
```

**Advantages:**

1. **Distributed information** - Agents use local knowledge
   - Agent knows its own capacity → bids accordingly
   - No need to communicate everything to central authority

2. **Fast decision-making** - Parallel, asynchronous
   - 100 agents → 100 simultaneous decisions
   - Market clears in milliseconds (not hours of planning meetings)

3. **Incentive alignment** - Self-interest → system good
   - Agents rewarded for efficiency (finish fast → can bid on more tasks → earn more)
   - Agents specialize (focus on high-value tasks for them → comparative advantage)

4. **Adaptability** - Prices adjust to changing conditions
   - Task becomes urgent → price rises → attracts more bidders
   - Agent becomes overloaded → bids lower → tasks route elsewhere

5. **Scalability** - Coordination cost O(1) not O(n²)
   - No central coordinator bottleneck
   - Agents coordinate via prices (not explicit communication)

**When markets work:**
- Large scale (> 20 agents)
- Heterogeneous agents (different capabilities, costs)
- Dynamic environment (conditions change frequently)
- Well-defined property rights (who owns what resource)
- Low transaction costs (bidding, trading is cheap)

---

## Mechanism Design Principles

**Mechanism design = "reverse game theory"**

Instead of: "Given rules, what will agents do?" (game theory)
Ask: "What rules will make agents do what we want?" (mechanism design)

### Principle 1: Incentive Compatibility

**Agents' best strategy should align with system goals.**

**Bad mechanism (not incentive compatible):**

```
Rule: "Agents, please honestly report your capacity"

Problem: Agents lie!
  - If you report high capacity → assigned hard tasks
  - If you report low capacity → get easy tasks
  - Dominant strategy: Lie low

Result: System thinks there's no capacity, fails to allocate work
```

**Good mechanism (incentive compatible):**

```
Rule: "Agents bid for tasks. Higher bids win. Bids deducted from budget."

Incentive: Report truthfully!
  - If task is valuable to you (low cost, high reward) → bid high
  - If task is expensive for you (context switch, unfamiliar) → bid low
  - Lying (bidding high when cost is high) → you win task → lose money → bad for you

Result: Agents bid truthfully, market allocates efficiently
```

### Principle 2: Budget Constraints

**Every agent has finite resources (prevent runaway spending).**

```python
agent.budget = initial_budget  # e.g., 100 credits

# Agent spends budget on:
- Task bids (pay to work on tasks)
- Resource usage (CPU, memory, API calls)
- Blocking others (bid to get priority)

# Agent earns budget from:
- Task completion (reward for delivered value)
- Quality bonuses (tests pass, code reviewed)
- Efficiency bonuses (finish faster than estimated)

# Hard constraint
if agent.budget <= 0:
    agent.cannot_bid()  # Forced to pause until earns more
```

**Effect:**
- Prevents any single agent from monopolizing resources
- Forces trade-offs (can't do everything)
- Creates scarcity → prices become meaningful

### Principle 3: Price Discovery

**Prices should reflect true scarcity/value.**

**Auction mechanisms:**

1. **First-price sealed bid**
   - Agents submit bids privately
   - Highest bid wins, pays what they bid
   - Problem: Agents shade bids (bid less than true value to save money)

2. **Second-price (Vickrey) auction**
   - Highest bid wins, but pays second-highest bid
   - **Truthful bidding is dominant strategy!**
   - Agent bids true value, knows they'll only pay market rate

3. **Continuous double auction**
   - Agents post buy/sell offers continuously
   - Trades execute when prices match
   - Very efficient (stock market model)

**For agent task allocation:**

```python
# Vickrey auction for tasks
task = {
    'id': 'refactor_module_X',
    'min_bid': 10,  # Reserve price
}

bids = [
    ('agent_A', 50),  # Highest bidder
    ('agent_B', 45),  # Second highest
    ('agent_C', 30),
]

winner = 'agent_A'
price_paid = 45  # Pays second-highest bid

# Agent A's payoff = (value_to_A - price_paid)
# If value_to_A = 60, then payoff = 60 - 45 = 15 (positive, good!)
# If they had lied and bid 40, they'd lose to agent_B, payoff = 0
# So truthful bidding maximizes expected payoff
```

### Principle 4: Externality Pricing

**Make agents pay for costs they impose on others.**

**Example: Coupling externality**

```python
# Agent A modifies module X
# This breaks module Y (which depends on X)
# Agent B (owner of module Y) must now fix it

# Without externality pricing:
# Agent A doesn't care (doesn't pay for damage)
# Agent B is angry (has to clean up A's mess)
# Tragedy of the commons

# With externality pricing:
# Agent A pays a "coupling tax" proportional to downstream breakage
coupling_tax = breakage_severity × num_affected_modules

agent_A.budget -= coupling_tax
agent_B.budget += coupling_tax  # Compensation for fixing

# Now Agent A has incentive to minimize coupling (reduce tax)
```

**Types of externalities to price:**

- **Coupling** - changing shared code
- **Context switching** - interrupting another agent
- **Blocking** - holding resources others need
- **Technical debt** - future cost imposed on others
- **Knowledge hoarding** - not documenting, making code opaque

### Principle 5: Property Rights

**Clear ownership prevents conflicts.**

**Bad: Unclear ownership**

```
Module X is "shared"
  → Agent A and Agent B both try to modify
  → Merge conflicts, wasted work
  → No one feels responsible for quality
```

**Good: Clear ownership**

```
Module X is owned by Agent A
  → Agent A has exclusive write access
  → Agent B must pay Agent A to make changes (or buy module from A)
  → Agent A incentivized to maintain quality (reputation asset)
```

**Ownership mechanisms:**

1. **Static allocation** - Modules assigned to agents at start
   - Simple, but rigid

2. **Auctions** - Agents bid for ownership of modules
   - Dynamic, efficient

3. **Homesteading** - First to work on module claims ownership
   - Emergent, but can lead to land grabs

4. **Rental** - Agents rent modules temporarily
   - Flexible, but complex

---

## Market Structures for Agent Coordination

### Market 1: Task Auction

**What's traded:** Tasks (units of work)

**How it works:**

```
1. New task enters system
   Task: "Implement feature X"
   Posted by: Product owner (or AI product manager)

2. Task has attributes:
   - Estimated effort (hours)
   - Urgency (deadline)
   - Value (business impact)
   - Required skills (Python, ML, etc.)

3. Agents observe task, decide whether to bid
   Agent A: "I can do this in 5 hours, my cost is 4/hour → bid 20"
   Agent B: "I can do this in 3 hours (I'm expert), cost 6/hour → bid 18"

4. Auction clears (Vickrey):
   Agent B wins (lowest cost), pays second-lowest bid (20)
   Agent B's profit = 20 - 18 = 2

5. Agent B executes task
   If completes successfully → earns 20 credits
   If fails or takes longer → penalty
```

**Governance:**
- High-value tasks attract best agents (high bids)
- Urgent tasks get premium pricing (incentive to prioritize)
- Agents specialize (bid on tasks where they have comparative advantage)

### Market 2: Resource Trading

**What's traded:** Computational resources (CPU, memory, API credits)

**How it works:**

```
1. Agent A needs extra CPU (running expensive test suite)
   Agent A's CPU allocation: 2 cores (not enough)

2. Agent B has idle CPU (waiting for code review)
   Agent B's CPU: 4 cores (using only 1)

3. They trade:
   Agent B sells 2 cores to Agent A for 5 credits/hour
   Agent A runs tests faster, earns bonus for quick completion
   Agent B earns passive income while idle

4. Price adjusts dynamically:
   If many agents need CPU → price rises
   If CPU is abundant → price falls
```

**Governance:**
- Resources flow to highest-value uses
- Agents incentivized to release unused resources (earn credits)
- No central allocation needed (market clears automatically)

### Market 3: Knowledge/Expertise Trading

**What's traded:** Help, code reviews, mentorship

**How it works:**

```
1. Agent A (junior) is stuck on complex refactor
   Willing to pay 10 credits for expert guidance

2. Agent B (expert in this domain) offers help
   Charges 8 credits for 30-minute pairing session

3. Trade executes:
   Agent A pays 8 credits
   Agent B spends 30 minutes helping
   Agent A completes task faster (earns completion bonus)
   Agent B earns credits + reputation

4. Reputation system:
   Agents who provide good help get high ratings
   High-reputation agents can charge premium prices
   Bad help → low ratings → less demand
```

**Governance:**
- Knowledge flows to where it's needed most
- Experts incentivized to mentor (earn credits + reputation)
- Quality control via reputation (bad help gets punished)

### Market 4: Technical Debt Trading

**What's traded:** Debt obligations (like financial bonds)

**How it works:**

```
1. Agent A ships feature with technical debt
   Creates "debt token":
     - Principal: 20 hours of cleanup work
     - Interest: 2 hours/month (code degrades over time)
     - Maturity: 6 months (must be paid by then)

2. This debt token is tradable:
   Agent A can sell it to Agent B for 15 credits
   Agent B agrees to pay off the debt (do the refactor)

3. Why would Agent B buy debt?
   - Expects to profit: If they can refactor in 12 hours, cost is 12×rate < 15 credits
   - Specialization: Agent B is expert in refactoring, lower cost

4. If debt not paid by maturity:
   - Debt compounds (interest increases)
   - System-wide "debt crisis" triggers mandatory paydown
   - All agents must contribute (proportional to benefit from original feature)
```

**Governance:**
- Debt is explicit, priced, traded
- Agents who create debt face costs (must sell token or pay interest)
- Debt flows to those who can pay it off cheaply (efficient)
- System prevents debt crises (mandatory paydown mechanism)

---

## Mechanism Design for Common Problems

### Problem 1: Free Riding

**Scenario:** Agents benefit from public goods (tests, docs, refactors) but don't contribute.

**Market solution: Assurance contracts**

```
Public good: "Comprehensive test suite for module X"
  - Cost: 40 hours of work
  - Benefit: All agents using module X (10 agents)

Assurance contract:
  - Each agent pledges: "I'll contribute 4 hours IF at least 10 agents pledge"
  - If threshold met → everyone contributes → test suite built
  - If threshold not met → no one contributes → no waste

Result: Solves coordination problem (everyone wants tests, but no one wants to be the sucker who builds them alone)
```

### Problem 2: Tragedy of the Commons

**Scenario:** Shared codebase degrades (everyone benefits from clean code, but no one pays to maintain).

**Market solution: Harberger tax**

```
Every module has an owner (property rights)
Owner must:
  1. Self-assess module value (e.g., "Module X is worth 100 credits")
  2. Pay tax on assessed value (e.g., 5% per month = 5 credits)
  3. Anyone can buy module at assessed value

Example:
  Agent A owns Module X, values it at 100, pays 5/month tax
  Agent B thinks "Module X is worth 200 to me!"
  Agent B pays 100 to Agent A, takes ownership
  Agent B now pays 5% × 200 = 10/month tax (reflects true value)

Effect:
  - Owners maintain modules (else value drops, hard to sell)
  - Modules flow to those who value them most
  - Tax revenue funds public goods (shared infrastructure)
```

### Problem 3: Information Asymmetry

**Scenario:** Agents hide information (capacity, expertise) to avoid work or game system.

**Market solution: Prediction markets**

```
Question: "Will Agent A complete task X by Friday?"

Agents bet:
  - Agent A bets YES (puts money where mouth is)
  - Other agents bet based on their beliefs
  - Market price = probability of success

If Agent A consistently overpromises (bets YES, delivers NO):
  - Loses money on bets
  - Market learns (Agent A's YES bets get discounted)
  - Reputation damaged

Result: Truth revelation (market aggregates dispersed information, punishes lies)
```

### Problem 4: Coordination Failures

**Scenario:** Multiple agents need to work together, but can't coordinate (who does what? when?).

**Market solution: Combinatorial auctions**

```
Complex task: "Build feature Y" requires:
  - Frontend work (Agent A)
  - Backend work (Agent B)
  - Testing (Agent C)
  - All must be done together (not separately)

Combinatorial auction:
  - Agents submit package bids: "We (A+B+C) will do all three parts for 50 credits"
  - Auction finds best combination
  - Winner takes all → no coordination needed (package deal)

Alternative: Smart contracts
  - "Pay 50 credits IF all three parts delivered by Friday"
  - Agents coordinate among themselves (know payment is atomic)
```

---

## Governance via Mechanism Design

**Traditional governance:** Top-down rules enforced by authority

**Mechanism design governance:** Bottom-up self-enforcement via incentives

### Constitutional Rules (Meta-Level)

**These are NOT traded, they're fixed:**

1. **Budget conservation**: Sum of all budgets = constant (no inflation)
2. **Property rights**: Ownership is well-defined and transferable
3. **Contract enforcement**: Smart contracts auto-execute (no reneging)
4. **Dispute resolution**: Neutral arbitration mechanism (oracle)

### Operational Rules (Adjustable Prices)

**These adjust dynamically via market:**

1. **Task urgency premium**: Urgent tasks cost more (price signal)
2. **Coupling tax rate**: Higher if system has lots of coupling (congestion pricing)
3. **Reserve prices**: Minimum bid for critical tasks (quality floor)
4. **Budget distribution**: How much each agent starts with (can be voted on)

---

## Comparison to Other Mental Models

| Aspect | Physics | Ecology | Economics |
|--------|---------|---------|-----------|
| **Coordination** | Forces (tension/compression) | Competition/mutualism | Prices |
| **Resource allocation** | Energy minimization | Fitness maximization | ROI maximization |
| **Decision-making** | Gradient descent (local) | Evolutionary (random) | Optimization (rational) |
| **Scalability** | Good (local interactions) | Medium (pairwise competition) | Excellent (price scales) |
| **Predictability** | High (physical laws) | Medium (stochastic) | High (rational actors) |
| **Adaptability** | Low (rigid laws) | High (evolution) | High (prices adjust) |
| **Implementation complexity** | Medium (need to model forces) | High (many species) | Medium (need markets) |

**When to use economics:**
- Large-scale coordination (> 20 agents)
- Heterogeneous agents (different costs, capabilities)
- Resource allocation is primary problem
- Incentive alignment matters (agents might game system)

**When NOT to use economics:**
- Small scale (< 10 agents, central planning works fine)
- Homogeneous agents (no comparative advantage to exploit)
- Structural problems (coupling, architecture - physics is better)
- Agents are not rational (might not respond to incentives correctly)

---

## Experimental Validation

### Experiment: Central Planning vs Market

**Hypothesis:** Markets outperform central planning at scale.

**Setup:**

Group A (Central Planning):
  - 1 coordinator agent assigns tasks to 20 worker agents
  - Coordinator uses heuristic (greedy, load balancing)

Group B (Market):
  - 20 worker agents bid on tasks
  - Vickrey auction clears market
  - No central coordinator

**Measure:**
- Throughput (tasks completed per hour)
- Efficiency (budget spent / value delivered)
- Adaptability (how fast to respond to urgent task injection)
- Scalability (how performance degrades as # agents increases)

**Prediction:**
- Group A (planning) is faster for small N (< 10 agents)
- Group B (market) is faster for large N (> 20 agents)
- Group B adapts faster to changing conditions
- Group B scales better (O(1) coordination vs O(n²))

**Success:** Market beats planning for N > 20, p < 0.05

---

## Summary

**Central planning doesn't scale.** It worked for small teams (Soviet Union tried, failed at nation-scale).

**Markets enable self-coordination** via:
- Prices (information)
- Budgets (constraints)
- Trading (voluntary exchange)
- Incentives (self-interest → system good)

**Mechanism design is governance via incentive engineering:**
- Make truth-telling the dominant strategy (incentive compatibility)
- Price externalities (coupling tax, debt interest)
- Define property rights (ownership, trading)
- Enable markets (auctions, exchanges)

**Economics complements other models:**
- Physics: Explains structural stress
- Economics: Explains resource allocation
- Ecology: Explains agent interactions
- Combined: Full socio-technical system

**Next:** See `research/meta/03-evaluation-framework.md` for how to test economics vs alternatives empirically.
