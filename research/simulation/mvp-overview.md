# MVP Simulator - Overview and Scope

## Document Status
- **Version**: 0.1.0
- **Date**: 2025-11-22
- **Status**: Design → Implementation

## Executive Summary

We are building a **small, interactive simulator** that models software systems as living tensegrity structures—where code modules act as compression elements under load and constraints (tests, contracts, architectural boundaries) act as tension elements holding the structure together.

**Goal**: Demonstrate that **structural tension at graph hubs** (measured via Laplacian-based Dirichlet energy) provides **earlier warning signals** for system instability than traditional per-node metrics like coverage or churn.

**Approach**: Toy universe with 6-8 modules, simple actors (2 humans + 1 AI agent), discrete-time event loop, explicit energy calculations at each step.

**Success**: If the simulator shows—even in a toy setting—that local energy spikes at hubs predict "incidents" 5-10 steps earlier than scalar metrics, we've validated the core physics intuition.

---

## The Problem We're Addressing

### Current State: Blind Metrics

Software teams track:
- **Churn**: Lines changed per week
- **Coverage**: Test coverage percentage
- **Complexity**: Cyclomatic complexity per module
- **Incidents**: Bugs, outages, SEVs

These are all **lagging or local** indicators. They tell you:
- "Something changed a lot" (churn) but not where stress concentrated
- "This module is complex" (complexity) but not how that affects coupled neighbors
- "We had an incident" (post-facto) but not which structural conditions led to it

**What's missing**: A structural view that shows how stress distributes through the dependency graph, where weak points are forming, and which areas are at risk **before** failures manifest.

### The Insight: Software as Physical Structure

Treat the codebase as a **graph with fields and energies**:

- **Nodes** = modules/services with scalar properties (health, complexity, risk)
- **Edges** = dependencies with weights (coupling strength)
- **Dirichlet energy** = ½ Σ w_ij (field[i] - field[j])²

This energy captures **gradients**: when neighboring nodes differ strongly in health or complexity, there's tension in the structure. That tension is where failures nucleate.

In a physical spring network or electrical circuit, the Laplacian governs how energy distributes. We're applying the same math to software.

### Why a Simulator?

We can't easily run controlled experiments on real production codebases. We need:

1. **Controlled environment**: Define initial conditions, inject shocks, observe dynamics
2. **Repeatability**: Run same scenario with different governance strategies, compare outcomes
3. **Safety**: Test ideas (like "block changes when local V_struct > threshold") without risking production
4. **Speed**: Compress months of development into minutes of simulation time
5. **Visibility**: Track every field, energy, event—full observability impossible in real systems

The simulator is a **conceptual microscope**: it won't match production reality in details, but it should capture the right qualitative dynamics and validate that the mathematical framework makes sense.

---

## Scope: What We Will Build

### MVP Includes

**Graph**:
- 6–8 technical nodes with synthetic names (e.g., `A_core`, `B_api`, `C_db`, `D_featureX`)
- Hub-and-spoke topology (2-3 core nodes, 3-5 feature leaves)
- Edge weights representing coupling strength
- No real code—just events that mutate node attributes

**Fields**:
- **Scalar**: health, complexity, risk, demand (all [0,1])
- **Derived**: badness = α(1-health) + β·complexity + γ·risk
- **Vector**: flow[i] ∈ ℝ² (feature pressure, refactor pressure)

**Energies**:
- **V_struct**: Dirichlet energy ½ bad^T L bad
- **V_bus**: Σ demand[i] · badness[i]
- **T**: Kinetic energy ½ Σ m_i (Δbad[i])²
- **H = T + V**: Total system stress
- **L = T - V**: Quality of motion

**Actors**:
- **Feature Engineer**: Prefers business direction, does FeatureChange
- **Refactor Engineer**: Prefers stability direction, does Refactor
- **AI Agent**: Follows largest ||flow[i]||, less nuanced

**Events**:
- **Field-only**: FeatureChange(i), Refactor(i), Patch(i)
- **Structural**: AddEdge(i,j), RemoveEdge(i,j), SplitNode, MergeNodes
- **Constraint**: AddConstraint(i), GovernanceChange(pattern)
- **Environment**: DemandShock(i, Δ), NewRequirement(zone)

**Simulation**:
- Discrete time loop: actors choose nodes, apply events, recompute energies, log
- ~100–500 steps per run
- Simple logging: CSV of all fields + energies per step
- Basic visualization: graph snapshots + time series plots (Matplotlib)

**Scenarios**:
1. **Baseline**: Stable demand, mixed actor actions, system in equilibrium
2. **Competitor shock**: Demand drops on one feature, new requirement appears, observe response
3. **Governance experiment**: Compare unconstrained vs. governed (e.g., "no changes when local V_struct > threshold at hubs")

### MVP Explicitly Excludes

**Not building**:
- Integration with real repos, VCS, or CI/CD
- Real LLMs in the loop (agents are scripted policies, not API calls)
- Calibration to real-world data or parameter fitting
- Fancy dashboards (Jupyter + Matplotlib is sufficient)
- System dynamics layer (PySD) for macro stocks/flows
- Full agent-based model framework (though Mesa is a natural next step)

**Not trying to**:
- Predict actual bugs or incidents in real systems (yet)
- Replace existing metrics (complement, not replace)
- Model every detail of software development
- Achieve numerical accuracy (care about qualitative regimes, not exact numbers)

The MVP is **proof of concept**, not production tool.

---

## Success Criteria

The MVP succeeds if it demonstrates:

### 1. Expressiveness
Can we model realistic scenarios (feature pressure, competitive shock, governance) purely as sequences of events on this toy graph?

**Test**: Competitor shock scenario feels "right"—demand shifts, agents respond, tensions spike, system adapts or breaks.

### 2. Differentiation
Do different governance strategies produce qualitatively different trajectories?

**Test**: Compare two runs of competitor shock:
- **Unconstrained**: Agents can make arbitrary changes
- **Governed**: Changes blocked when local V_struct at core nodes exceeds threshold

We expect: unconstrained → H spikes, stays elevated, eventual "incidents"; governed → H spikes briefly, stabilizes, fewer incidents.

### 3. Predictive Signal
Does local Dirichlet energy at hubs warn earlier than global metrics?

**Test**: In unconstrained run, measure:
- Time when `local_V_struct[A_core]` first exceeds threshold: t₁
- Time when average health drops below threshold: t₂
- Time when first "incident" fires: t₃

Hypothesis: t₁ < t₂ < t₃ (local energy warns first).

If true, we've validated the core physics insight even in a toy setting.

### 4. Interpretability
Can someone unfamiliar with the code look at a phase-space plot (H vs. time, T vs. V) and identify regime transitions (stable → chaotic, frozen → thrashy)?

**Test**: Show plots to colleague without context, ask them to label "healthy" vs. "crisis" periods. If they can, the visualization is working.

### 5. Extensibility
Can we easily add new event types, actor policies, or governance rules without rewriting core logic?

**Test**: Add a new event "TechnicalDebtRepayment(i)" and a new actor "TechDebtBot" in < 50 lines. If yes, architecture is modular enough.

---

## Why This Scope?

### Small Enough to Build Quickly
6-8 nodes, 3 actors, discrete-time loop → can implement in 1-2 weeks of focused work.

Python + NetworkX + NumPy + Matplotlib → mature, well-documented stack.

No LLM integration, no real repos → avoid complexity and API costs.

### Large Enough to Be Interesting
Hub-and-spoke topology creates non-trivial dynamics (stress concentrates at hubs).

Multiple actor types create competing forces (velocity vs. quality).

Competitor shock scenario mirrors real-world product development shocks.

### Focused on Core Hypothesis
Everything is designed to test: "Does Laplacian-based local energy predict trouble earlier than scalar metrics?"

If yes → publish research note, prototype real integration.

If no → understand why, refine model, iterate.

---

## Relation to Broader Tensegrity Vision

This MVP is **theoretical validation** for the Tensegrity governance layer.

**Tensegrity (the product)** will:
- Monitor real codebases
- Enforce invariants and gates
- Provide active learning primitives
- Tune equilibrium forces (velocity, quality, coherence, learning, scope)

**Software physics (this research)** provides:
- Mathematical vocabulary ("equilibrium", "stress", "stability")
- Diagnostic metrics (H, V, T, local Dirichlet energy)
- Design principles (keep system in viable basin, shape energy landscapes)
- Simulation tools for testing governance before deployment

Think of it as:
- **Tensegrity** = the engineered system users interact with
- **Physics simulator** = the lab bench where we test ideas before shipping

This MVP is the first artifact from the "lab bench".

---

## What Comes After MVP?

### If MVP Validates Core Insight

**Immediate (0-3 months)**:
- Publish research note / blog post on "software physics" approach
- Prototype real integration: parse actual dependency graph from repo, compute energies
- Compare historical V_struct at hubs vs. incident timing on a real project

**Medium-term (3-12 months)**:
- Integrate into Tensegrity governance layer as diagnostic dashboard
- Add LLM-in-the-loop for richer agent policies
- Expand to multi-layer graphs (tech + social + environment)
- Develop "software Reynolds numbers" and other dimensionless diagnostics

**Long-term (1-3 years)**:
- Ship as part of Tensegrity product
- Publish academic paper on graph-based software dynamics
- Explore thermodynamic / control-theoretic extensions

### If MVP Reveals Flaws

**Debug and iterate**:
- Which assumptions broke? (e.g., Dirichlet energy doesn't correlate with incidents?)
- Alternative metrics? (e.g., spectral gap, effective resistance, betweenness × badness?)
- Different dynamics? (e.g., treat as active inference system, not Hamiltonian?)

Science is iterative. A "negative result" (simulator doesn't work as expected) is still valuable—it tells us where the model needs refinement.

---

## Next Steps: Implementing the MVP

See:
- **[mvp-model.md](./mvp-model.md)**: Detailed field and energy definitions
- **[mvp-simulation-design.md](./mvp-simulation-design.md)**: Actor policies, event types, loop
- **[mvp-implementation.md](./mvp-implementation.md)**: Code structure and tech stack
- **[mvp-scenarios.md](./mvp-scenarios.md)**: Baseline, competitor shock, governance experiments

**Start**: `mvp-implementation.md` → set up Python environment → build `graph_model.py`
