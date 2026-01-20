# MVP Simulator - Mathematical Model

## Overview

This document defines the mathematical model for the software tensegrity simulator: fields, energies, and dynamics.

**For concrete code examples and worked calculations**, see `../03-software-as-physics-mapping.md`.

---

## 1. The Graph Structure

### 1.1 Technical Graph G_tech(t)

The core data structure is a time-varying weighted graph:

**Nodes** (V_tech):
- Modules, services, databases, features
- Example: `A_core`, `B_api`, `C_db`, `D_featureX`, `E_featureY`, `F_util`

**Edges** (E_tech):
- Dependencies: imports, calls, data flows, deployment coupling
- Each edge has type and weight

**Edge weights** w_ij ∈ [0,1]:
- Coupling strength—how tightly two components are bound
- Computed from: call volume, data flow, change coupling (co-change frequency)
- High weight = tight coupling = strong spring in tensegrity

**Representation**:
- NetworkX graph with node and edge attributes
- Laplacian matrix L = D - A (degree matrix - adjacency matrix)

### 1.2 Actor and Environment Layers (Future)

For MVP, we model only the technical graph. Future versions will include:

**Actor Layer** G_actor(t):
- Nodes: Human engineers, AI agents, PMs, SREs
- Edges: Team membership, code review relationships

**Environment Layer** G_env(t):
- Nodes: User cohorts, customers, competitors, funders
- Edges: Value flows, contracts, competitive pressure

**Cross-layer edges**:
- Ownership: Actor → Tech
- Usage: Environment → Tech
- Influence: Environment → Actor

---

## 2. Scalar Fields on Nodes

All fields map nodes to [0,1]:

### 2.1 Health h: V → [0,1]

**Definition**: Code quality, test coverage, documentation, absence of tech debt

**Components**:
- Test coverage (0-1)
- Documentation coverage (0-1)
- Bug density (inverted and normalized)
- Code smell score (inverted)

**Interpretation**:
- h = 1.0: Pristine, well-tested, documented, no debt
- h = 0.0: Broken, untested, undocumented, high debt

**Example computation** (see `03-software-as-physics-mapping.md` for code):
```
health = 0.3·coverage + 0.2·docs + 0.3·(1 - bugs/10) + 0.2·(1 - smells)
```

### 2.2 Complexity c: V → [0,1]

**Definition**: Structural and cognitive difficulty

**Components**:
- Cyclomatic complexity (normalized)
- Cognitive complexity (normalized)
- Dependency count (normalized)

**Interpretation**:
- c = 0.0: Trivial, easy to understand
- c = 1.0: Brain-melting, impossible to reason about

**Normalization**: Use soft saturation `1 - exp(-x/scale)` to map unbounded metrics to [0,1]

### 2.3 Risk r: V → [0,1]

**Definition**: Emergent from health, complexity, change velocity, blast radius

**Components**:
- (1 - health): Unhealthy code is risky
- complexity: Complex code is risky
- Churn (normalized): High change rate adds risk
- Blast radius (normalized): Many dependents add risk

**Interpretation**:
- r = 0.0: Safe, stable, isolated
- r = 1.0: Disaster waiting to happen

**Formula**:
```
risk = 0.3·(1-health) + 0.3·complexity + 0.2·churn_norm + 0.2·blast_norm
```

### 2.4 Demand d: V → [0,1]

**Definition**: User and business pressure on component

**Components**:
- Traffic volume (normalized)
- Product roadmap priority (0-1)
- User complaints (normalized)

**Interpretation**:
- d = 0.0: No one cares, unused
- d = 1.0: Critical, high-traffic, user pain

**Note**: Demand is **external** to the technical state—comes from environment layer

### 2.5 Composite Badness b: V → [0,1]

**Definition**: Single aggregated metric for energy calculations

**Formula**:
```
bad[i] = α·(1 - health[i]) + β·complexity[i] + γ·risk[i]
```

**Parameters** (default):
- α = 0.4 (health is most important)
- β = 0.3 (complexity matters)
- γ = 0.3 (risk matters)

**Tunable**: Adjust weights for different contexts

**Interpretation**: Higher badness → node is in worse state → contributes more to potential energy

---

## 3. Vector Field on Nodes

### 3.1 Flow Field f: V → ℝ²

**Definition**: 2D vector indicating direction of desired change

**Components**:
- x-component: Pressure for **feature work** (implement, extend)
- y-component: Pressure for **refactor/stabilization** (clean up, test)

**Computation**:
```python
grad_V[i] ≈ Σ_j w_ij · (bad[i] - bad[j])  # Discrete Laplacian gradient

business_dir[i] = demand[i] · x̂          # Push toward features
stability_dir[i] = -grad_V[i] · ŷ         # Push toward energy reduction

flow[i] = α_flow · business_dir[i] + β_flow · stability_dir[i]
```

**Parameters** (default):
- α_flow = 0.6 (business has more weight)
- β_flow = 0.4 (stability is secondary)

**Interpretation**:
- Large ||flow[i]|| → high pressure to act at node i
- Direction of flow → what kind of action (feature vs refactor)
- Actors use flow to guide decisions

**Dynamic**: Flow field **changes every step** as bad and demand evolve

---

## 4. Energies - The Core Physics

### 4.1 Structural Potential Energy V_struct

**Definition**: Dirichlet energy of badness field over graph

**Formula**:
```
V_struct = ½ Σ_(i,j)∈E w_ij · (bad[i] - bad[j])²
         = ½ bad^T · L · bad
```

Where L is the **graph Laplacian** (L = D - A).

**Physical interpretation**:
- Like springs stretched between masses of different heights
- Like power dissipation in resistor network with voltage differences
- High V_struct → neighbors disagree strongly → **tension in structure**

**Units**: Dimensionless, proportional to squared differences

**Why it matters**: Captures **gradients**, not just local values. A clean module tightly coupled to a mess creates high tension.

### 4.2 Business Potential Energy V_bus

**Definition**: Cost of bad state weighted by business demand

**Formula**:
```
V_bus = Σ_i demand[i] · [λ₁·(1 - health[i]) + λ₂·complexity[i]]
```

**Parameters** (default):
- λ₁ = 0.6 (unhealthy high-demand modules hurt most)
- λ₂ = 0.4 (complex high-demand modules also hurt)

**Interpretation**: High-demand modules that are in bad state create **business pain**

**Units**: Dimensionless, summed over nodes

**Why it matters**: Even if structural tension is low, high V_bus means users are suffering

### 4.3 Total Potential V

```
V(t) = V_struct(t) + V_bus(t)
```

Total "stress" in the system—both structural and business.

### 4.4 Kinetic Energy T

**Definition**: Rate of change of badness

**Formula** (discrete time):
```
Δbad[i]_k = bad[i]_k - bad[i]_(k-1)

T_k = ½ Σ_i m_i · (Δbad[i]_k)²
```

**Mass** m_i:
- Importance weight for node i
- Can be demand[i], or criticality, or user impact
- Higher mass → changes at this node contribute more to T

**Interpretation**: Rapid changes in critical modules → high kinetic energy

**Units**: Dimensionless, like V

**Why it matters**: High T means lots of motion; T=0 means frozen

### 4.5 Lagrangian L

```
L = T - V
```

**Interpretation**: "Quality of motion"

- High T, low V: Good! Rapid change in a well-constrained system
- High T, high V: Bad! Thrashing, chaotic motion under stress
- Low T, low V: Stable equilibrium (can be good or stuck)
- Low T, high V: Frozen under stress (bureaucracy)

**Use**: Not directly, but conceptually useful for understanding regimes

### 4.6 Hamiltonian H

```
H = T + V
```

**Interpretation**: **Total system "stress load"**

- H = 0: No stress, no motion (theoretical minimum)
- H moderate: Healthy flow
- H high and rising: Crisis energy building
- H spiking: Emergency

**Primary diagnostic**: Track H(t) over time

**Regimes**:
- **Healthy flow**: H ∈ [0.5, 1.5], stable or gentle oscillation
- **Frozen bureaucracy**: H > 1.0, T ≈ 0 (all potential, no motion)
- **Chaotic thrash**: H > 2.0, both T and V high
- **Runaway**: H increasing monotonically

---

## 5. Derived Metrics

### 5.1 Local Dirichlet Energy E_local[i]

**Definition**: Contribution of node i to structural potential

**Formula**:
```
E_local[i] = ½ Σ_j∈neighbors(i) w_ij · (bad[i] - bad[j])²
```

**Interpretation**: How much tension is concentrated at node i

**Why critical**: **Hub nodes** with high centrality and high E_local are where failures nucleate

**Use case**: Alert when `E_local[hub] > threshold`

### 5.2 Gradient of V at Node i

**Definition**: Discrete derivative of potential

**Formula**:
```
∇V[i] ≈ (L · bad)[i] = Σ_j w_ij · (bad[i] - bad[j])
```

**Interpretation**: Direction and magnitude of "force" on node i

- Positive ∇V[i]: Node i is "worse" than neighbors → refactoring reduces V
- Negative ∇V[i]: Node i is "better" than neighbors → improving i increases V (counterintuitive but happens)

**Use**: Feed into flow field computation

### 5.3 Ratio T/V

**Definition**: Kinetic to potential ratio

**Regimes**:
- T/V ≈ 1: Balanced (ideal)
- T/V >> 1: Lots of motion, low constraint (cowboy mode)
- T/V << 1: Lots of constraint, no motion (frozen)

**Use**: Governance tuning—adjust to keep ratio near 1

---

## 6. Parameter Summary

### Field Weights
- **Badness**: α=0.4, β=0.3, γ=0.3 (health, complexity, risk)
- **Business potential**: λ₁=0.6, λ₂=0.4 (health vs complexity)

### Flow Weights
- **Business vs stability**: α_flow=0.6, β_flow=0.4

### Mass Weights
- **Default**: m_i = demand[i] (critical nodes have more mass)
- **Alternative**: m_i = 1.0 (all nodes equal)

### Thresholds (governance)
- **High H**: > 2.0 (emergency brake)
- **High local E**: > 0.5 at hubs (require refactor before feature work)
- **Low T**: < 0.01 (system frozen, relax constraints)

---

## 7. Units and Normalization

**All fields are dimensionless** [0,1].

**Energies are dimensionless** but have consistent scaling:
- V_struct ∝ number of edges × (typical Δbad)²
- V_bus ∝ number of nodes × demand × badness
- T ∝ number of nodes × mass × (Δbad)²

**Typical ranges** (for 6-8 node system):
- V_struct: 0.001 – 0.01 (low tension to high tension)
- V_bus: 0.5 – 2.0 (depends on demand distribution)
- T: 0.0 – 0.3 (frozen to chaotic)
- H: 0.5 – 2.5 (healthy to crisis)

**Normalization strategy**: System-relative, not absolute. Compare H(t) to H_baseline for this project, not to other projects.

---

## 8. Why This Model?

### 8.1 Grounded in Established Math

Graph Laplacians appear in:
- **Spring networks**: Elastic potential energy
- **Electrical circuits**: Kirchhoff's laws, power dissipation
- **Random walks**: Commute times, mixing rates
- **Spectral clustering**: Module boundaries

We're applying the **same quadratic form** used in physics and network science.

### 8.2 Captures Structure, Not Just Scalars

Traditional metrics (coverage, complexity) are **local**—per-node values.

Laplacian energy captures **relationships**—how nodes differ from neighbors.

That's where failures propagate: along edges with high tension.

### 8.3 Predictive, Not Just Descriptive

High local V_struct at a hub **predicts** future incidents before they manifest.

Traditional metrics are **lagging indicators**; structural energy is **leading**.

### 8.4 Compositional

You can drill down:
- Global H → per-subsystem H → per-edge contributions
- Identify which edges are stressed, which nodes are hot

Not possible with scalar metrics alone.

---

## 9. Limitations and Assumptions

### What We're NOT Claiming

- Exact numeric accuracy (this is a toy model)
- Calibration to real-world units (no "Joules" or "Kelvin")
- Complete representation of all software dynamics

### What We ARE Claiming

- Structural validity (qualitative regimes are correct)
- Relative predictive power (earlier warnings than scalar metrics)
- Extensibility (can add more fields, layers, dynamics)

### Key Assumptions

1. **Badness is composable**: α(1-h) + βc + γr is meaningful
2. **Laplacian captures tension**: Neighbors differing strongly → problems
3. **Discrete time is adequate**: Don't need continuous ODEs for MVP
4. **Small graph generalizes**: Insights from 6-8 nodes apply to larger systems

These are testable. If the MVP works, assumptions validated. If not, refine.

---

## 10. Next Steps

**Use this model to**:
1. Implement `graph_model.py` (see `mvp-implementation.md`)
2. Compute energies at each simulation step
3. Log fields and energies for analysis
4. Visualize phase space trajectories (H vs time, T vs V)

**Validate by**:
- Running baseline scenario: H should stay moderate
- Running competitor shock: H should spike, then stabilize or diverge
- Comparing local E at hubs to global metrics as early warning

**See also**:
- `../02-mathematical-foundations.md` - Deep dive on Laplacians
- `../03-software-as-physics-mapping.md` - Worked examples with code
- `mvp-simulation-design.md` - How actors and events use this model
