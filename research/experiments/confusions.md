# Confusions: The Lab Notebook of Unresolved Concepts

## Purpose

*[Channeling Feynman's honesty]*

This is where we write down **what we don't understand yet**.

Not the polished equations. Not the beautiful diagrams. The **actual confusions** that arise when trying to implement the theory.

**Every experimentalist keeps this notebook.** When you can't make the apparatus work, when the measurement doesn't make sense, when two formulas contradict—you write it here.

Then you **resolve it**. Update the theory. Test again.

**This is where the real physics happens.**

---

## Status Legend

- **🔴 UNRESOLVED**: Active confusion, needs work
- **🟡 IN PROGRESS**: Working on resolution
- **🟢 RESOLVED**: Clarified, documented, tested

---

## Active Confusions

### 🔴 CONFUSION #1: What exactly is "mass"?

**Date raised**: 2025-11-22
**Raised by**: Implementation of kinetic energy formula

**The problem**:

In `mvp-model.md`, we define kinetic energy as:
```
T = ½ Σ_i m_i (Δbad_i)²
```

But **what is m_i**?

**Possibilities**:
1. m_i = demand[i] (nodes with high business demand have more "inertia")
2. m_i = 1 / health[i] (unhealthy nodes are "heavier", harder to change)
3. m_i = complexity[i] (complex nodes have more mass)
4. m_i = LOC[i] / LOC_max (literal code mass)
5. m_i = const = 1 (all nodes equal mass)

**Why it matters**:
- Affects T magnitude
- Changes which nodes dominate kinetic energy
- Impacts H = T + V balance

**Experiments affected**: All (T appears in every experiment)

**Resolution needed**: Pick one definition, justify it, test sensitivity.

**Status**: 🔴 UNRESOLVED

---

### 🔴 CONFUSION #2: How to compute "risk" field?

**Date raised**: 2025-11-22
**Raised by**: SimulationState initialization

**The problem**:

We have three primitive fields: health, complexity, demand.
We have one **derived** field: badness = f(health, complexity, risk).

But `risk` appears in the badness formula:
```python
bad[i] = α(1 - health[i]) + β·complexity[i] + γ·risk[i]
```

**How do we compute risk[i]**?

**Possibilities**:
1. risk = complexity × (1 - health) (interaction term)
2. risk = coupling × (1 - health) (structural vulnerability)
3. risk = incident_history[i] (learned from past failures)
4. risk = const (just a placeholder, set to 0.3 for all nodes)
5. risk is **primitive**, not derived (initialize it, update it via events)

**Why it matters**:
- Circular dependency if risk depends on badness, which depends on risk
- Affects gradient computations
- Changes actor decisions (flow field depends on badness)

**Experiments affected**: All

**Current workaround**: MVP docs use Option 5 (risk is primitive), but unclear what events modify it.

**Status**: 🔴 UNRESOLVED

---

### 🔴 CONFUSION #3: Edge weight semantics

**Date raised**: 2025-11-22
**Raised by**: Laplacian interpretation

**The problem**:

Edge weight w_ij means "coupling strength." But does that mean:

**Interpretation A**: Tight coupling (high w) → **more tension** when nodes disagree
- L = D - A (standard Laplacian)
- High w_ij amplifies energy when bad[i] ≠ bad[j]
- This is what we use

**Interpretation B**: Loose coupling (low w) → **more freedom** to disagree
- Inverse Laplacian L = D - A^(-1)?
- Or normalize weights differently?

**Why it matters**:
- Affects whether we want high or low w for resilience
- Changes how we interpret V_struct values
- Impacts governance rules (do we add or remove edges to reduce tension?)

**Experiments affected**: Exp02 (Laplacian early warning)

**Status**: 🔴 UNRESOLVED (currently using Interpretation A, but unvalidated)

---

### 🔴 CONFUSION #4: Incident probability function

**Date raised**: 2025-11-22
**Raised by**: Scenario expected outcomes

**The problem**:

We say "incidents occur when health is low and complexity is high," but **what's the exact formula**?

**Options**:
1. p_incident[i] = (1 - health[i]) × complexity[i] (multiplicative)
2. p_incident[i] = sigmoid(bad[i] - threshold) (logistic)
3. p_incident[i] = bad[i]^k / Z (power law with partition function)
4. p_incident[i] = 0 if health > 0.6, else 0.1 (step function)

**Why it matters**:
- Can't validate "E_local predicts incidents" without defining incidents precisely
- Affects calibration (too many/too few incidents changes signal-to-noise)

**Experiments affected**: Exp02 (core validation)

**Status**: 🔴 UNRESOLVED

---

### 🔴 CONFUSION #5: Flow field interpretation

**Date raised**: 2025-11-22
**Raised by**: Actor decision logic

**The problem**:

Flow field is defined as:
```python
flow[i] = (business_direction, stability_direction)
business_direction = demand[i]
stability_direction = -grad_V[i]
```

But actors choose actions based on flow. **How exactly**?

**Option A**: Sample node with probability ∝ ||flow[i]||
- Actors go where field magnitude is high
- But what's the action type? (Feature vs. Refactor?)

**Option B**: Sample node with probability ∝ flow_x, then choose feature; or ∝ flow_y, choose refactor
- Separates node choice from action choice

**Option C**: Flow is just a **visualization**, actors use raw demand and grad_V directly

**Why it matters**:
- Affects actor behavior
- Changes which nodes get attention
- Impacts simulation dynamics

**Experiments affected**: All (actors in every scenario)

**Status**: 🔴 UNRESOLVED

---

### 🔴 CONFUSION #6: Governance threshold calibration

**Date raised**: 2025-11-22
**Raised by**: Experiment 03 design

**The problem**:

We say "trigger emergency brake if H > 2.0," but **where does 2.0 come from**?

**Possibilities**:
1. Arbitrary (just pick something for MVP)
2. Calibrated from baseline (e.g., 2× mean(H) in baseline)
3. Derived from theory (e.g., when H > T_hot / T_cold...)
4. Learned from data (grid search for optimal threshold)

**Why it matters**:
- If threshold is too high → governance never triggers (useless)
- If threshold is too low → governance always triggers (bureaucracy)
- Need principled approach for real systems

**Experiments affected**: Exp03 (governance effectiveness)

**Status**: 🔴 UNRESOLVED

---

### 🔴 CONFUSION #7: Time units and scales

**Date raised**: 2025-11-22
**Raised by**: "10 steps earlier" prediction claim

**The problem**:

We claim "E_local warns 10 steps before incidents," but **what's a time step**?

**In simulation**:
- 1 step = 1 iteration of loop
- 3 actors act per step
- So 1 step = ~3 actions

**In real systems**:
- 1 step = 1 commit?
- 1 step = 1 day?
- 1 step = 1 PR merge?

**Why it matters**:
- Can't compare simulation to real git history without time mapping
- Affects how we interpret "early warning" (10 commits? 10 days?)

**Experiments affected**: All, especially Exp02

**Status**: 🔴 UNRESOLVED

---

## Resolved Confusions

### 🟢 CONFUSION #R1: Graph Laplacian normalization

**Date raised**: 2025-11-22
**Date resolved**: 2025-11-22
**Resolved by**: Mathematical foundations review

**The problem**:

Should we use:
- Combinatorial Laplacian: L = D - A
- Normalized Laplacian: L_norm = I - D^(-1/2) A D^(-1/2)
- Random walk Laplacian: L_rw = I - D^(-1) A

**Resolution**:

Use **combinatorial Laplacian L = D - A** for MVP.

**Reasons**:
1. Matches physics (spring networks, resistor networks)
2. Energy formula V = ½ f^T L f is exact
3. Simpler implementation (no degree normalization)
4. Post-MVP can compare normalized versions

**Documented in**: `02-mathematical-foundations.md:29-46`

**Status**: 🟢 RESOLVED

---

## Guidelines for Adding Confusions

**When to add**:
- Implementing code and don't know what value to use
- Two doc sections contradict each other
- Formula has undefined variable
- Edge case not handled
- Can't decide between multiple reasonable interpretations

**How to document**:
1. Give it a number (CONFUSION #N)
2. Date raised + who/what raised it
3. State the problem clearly
4. List possible resolutions
5. Explain why it matters
6. Mark status (🔴/🟡/🟢)

**How to resolve**:
1. Try each option experimentally (if fast)
2. Derive from first principles (if possible)
3. Pick simplest for MVP, mark for future testing (if unclear)
4. Update theory docs with the resolution
5. Move confusion to "Resolved" section

---

## Meta-Confusions (Confusions About Confusions)

**None yet. But we're watching for them.**

---

## Next Actions

**Before implementing Phase 1 code**:
1. Review confusions #1-#7
2. For each, pick an MVP resolution (even if temporary)
3. Mark as 🟡 IN PROGRESS
4. Implement, test
5. If it works, mark 🟢 RESOLVED
6. If it doesn't, try alternative, update confusion

**The rule**: Every confusion must be at least 🟡 before claiming "experiment works."

---

*"I would rather have questions that can't be answered than answers that can't be questioned."* — Richard Feynman
