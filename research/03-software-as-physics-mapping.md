# Software as Physics: Detailed Mapping and Examples

## Overview

This document provides concrete mappings from software engineering concepts to physical/mathematical objects, with worked examples showing how to apply the framework in practice.

## The Complete Type System

### Layer 1: Graph Structure

**Technical Graph** G_tech(t) = (V_tech, E_tech, w)

**Nodes** (V_tech):
```python
Node = {
  id: string,              # "user-auth-service", "payment-api", "db-users"
  type: NodeType,          # MODULE | SERVICE | DATABASE | QUEUE | FEATURE
  metadata: {
    loc: int,              # lines of code
    age: days,             # time since creation
    contributors: [str],   # who has touched this
    criticality: float,    # 0-1, business importance
  }
}

NodeType = MODULE | SERVICE | DATABASE | QUEUE | FEATURE | LIBRARY | CONFIG
```

**Edges** (E_tech):
```python
Edge = {
  source: NodeID,
  target: NodeID,
  type: EdgeType,
  weight: float,          # coupling strength, 0-1
  metadata: {
    calls_per_day: int,   # API call volume
    data_flow_mb: float,  # data transferred
    change_coupling: float, # how often they change together
  }
}

EdgeType = IMPORT | CALL | DATA_FLOW | DEPLOY_COUPLING | TEST_COVERAGE
```

**Weight Calculation**:
```python
def calculate_edge_weight(edge: Edge) -> float:
    """
    Coupling strength from multiple signals.
    High weight = tight coupling = strong spring/cable in tensegrity.
    """
    # Normalize each component to [0,1]
    call_volume_norm = min(edge.metadata.calls_per_day / 10000, 1.0)
    data_flow_norm = min(edge.metadata.data_flow_mb / 1000, 1.0)
    change_coupling = edge.metadata.change_coupling  # already [0,1]

    # Weighted combination
    w = 0.4 * call_volume_norm + \
        0.3 * data_flow_norm + \
        0.3 * change_coupling

    return w
```

### Layer 2: Scalar Fields

**Health Field** h: V → [0,1]
```python
def compute_health(node: Node) -> float:
    """
    1.0 = pristine, well-tested, documented, no tech debt
    0.0 = broken, untested, undocumented, high debt
    """
    test_coverage = get_test_coverage(node)      # 0-1
    doc_coverage = has_documentation(node)       # 0-1
    recent_bugs = get_bug_count_30d(node)        # count
    code_smell_score = run_linter(node)          # 0-1, higher is worse

    health = 0.3 * test_coverage + \
             0.2 * doc_coverage + \
             0.3 * (1 - min(recent_bugs / 10, 1.0)) + \
             0.2 * (1 - code_smell_score)

    return max(0.0, min(1.0, health))
```

**Complexity Field** c: V → [0,1]
```python
def compute_complexity(node: Node) -> float:
    """
    0.0 = trivial
    1.0 = brain-melting
    """
    cyclomatic = get_cyclomatic_complexity(node)  # raw value
    cognitive = get_cognitive_complexity(node)    # raw value
    dependency_count = len(get_dependencies(node))

    # Normalize to [0,1] with soft saturation
    cyclo_norm = 1 - exp(-cyclomatic / 50)
    cogn_norm = 1 - exp(-cognitive / 30)
    dep_norm = 1 - exp(-dependency_count / 20)

    complexity = 0.4 * cyclo_norm + \
                 0.4 * cogn_norm + \
                 0.2 * dep_norm

    return complexity
```

**Risk Field** r: V → [0,1]
```python
def compute_risk(node: Node, history: ChangeHistory) -> float:
    """
    Emergent from health, complexity, change frequency, blast radius.
    """
    health = compute_health(node)
    complexity = compute_complexity(node)

    # Change velocity in last 30 days
    churn = len(history.commits_30d(node))
    churn_norm = 1 - exp(-churn / 20)

    # Blast radius: how many other nodes depend on this?
    dependents = len(get_reverse_dependencies(node))
    blast_norm = 1 - exp(-dependents / 15)

    # Risk increases with: low health, high complexity, high churn, high blast radius
    risk = 0.3 * (1 - health) + \
           0.3 * complexity + \
           0.2 * churn_norm + \
           0.2 * blast_norm

    return risk
```

**Demand Field** d: V → [0,1]
```python
def compute_demand(node: Node, business: BusinessContext) -> float:
    """
    User/business pressure on this component.
    """
    # From telemetry
    traffic = get_traffic_volume(node)           # requests/day
    traffic_norm = 1 - exp(-traffic / 100000)

    # From product roadmap
    feature_priority = business.get_priority(node)  # 0-1

    # From customer feedback
    user_pain = get_user_complaints(node)        # count
    pain_norm = 1 - exp(-user_pain / 50)

    demand = 0.4 * traffic_norm + \
             0.3 * feature_priority + \
             0.3 * pain_norm

    return demand
```

**Composite "Badness" Field** b: V → [0,1]
```python
def compute_badness(node: Node, α=0.4, β=0.3, γ=0.3) -> float:
    """
    Single scalar aggregating multiple concerns.
    Used as input to Laplacian energy calculations.
    """
    health = compute_health(node)
    complexity = compute_complexity(node)
    risk = compute_risk(node)

    bad = α * (1 - health) + β * complexity + γ * risk
    return bad
```

### Layer 3: Vector Fields

**Flow Field** f: V → ℝ²
```python
def compute_flow(node: Node,
                 G: Graph,
                 bad: Dict[Node, float],
                 demand: Dict[Node, float]) -> np.array:
    """
    2D vector: (feature_pressure, refactor_pressure)

    Actors use this to decide what to do where.
    """
    # Compute local gradient of V via Laplacian
    grad_V = compute_laplacian_gradient(G, bad, node)

    # Business direction: proportional to demand
    business_dir = np.array([demand[node], 0])

    # Stability direction: opposite of gradient (go downhill in V)
    stability_dir = np.array([0, -grad_V]) if grad_V > 0 else np.array([0, 0])

    # Weighted combination
    α_flow = 0.6  # weight for business
    β_flow = 0.4  # weight for stability

    flow = α_flow * business_dir + β_flow * stability_dir
    return flow
```

### Layer 4: Energies

**Structural Potential Energy** V_struct
```python
def compute_structural_potential(G: Graph, bad: Dict[Node, float]) -> float:
    """
    Dirichlet energy: tension from neighbors disagreeing.

    V_struct = ½ Σ_(i,j)∈E w_ij * (bad[i] - bad[j])²
    """
    V = 0.0
    for edge in G.edges:
        i, j = edge.source, edge.target
        w_ij = edge.weight
        diff = bad[i] - bad[j]
        V += 0.5 * w_ij * diff**2

    return V

# Alternative: using Laplacian matrix (faster for large graphs)
def compute_structural_potential_matrix(L: np.array, bad: np.array) -> float:
    """
    V_struct = ½ bad^T L bad
    """
    return 0.5 * bad.T @ L @ bad
```

**Business Potential Energy** V_bus
```python
def compute_business_potential(nodes: List[Node],
                                bad: Dict[Node, float],
                                demand: Dict[Node, float],
                                λ1=0.6, λ2=0.4) -> float:
    """
    High-demand modules that are in bad state cost a lot.

    V_bus = Σ_i demand[i] * (λ1*(1-health[i]) + λ2*complexity[i])
    """
    V = 0.0
    for node in nodes:
        health = compute_health(node)
        complexity = compute_complexity(node)
        d = demand[node]

        V += d * (λ1 * (1 - health) + λ2 * complexity)

    return V
```

**Kinetic Energy** T
```python
def compute_kinetic_energy(bad_prev: Dict[Node, float],
                           bad_curr: Dict[Node, float],
                           mass: Dict[Node, float]) -> float:
    """
    Rate of change energy.

    T = ½ Σ_i m_i * (Δbad[i])²
    """
    T = 0.0
    for node in bad_curr.keys():
        Δbad = bad_curr[node] - bad_prev[node]
        m = mass[node]
        T += 0.5 * m * Δbad**2

    return T
```

**Lagrangian and Hamiltonian**
```python
def compute_lagrangian(T: float, V: float) -> float:
    """L = T - V"""
    return T - V

def compute_hamiltonian(T: float, V: float) -> float:
    """H = T + V (total system stress)"""
    return T + V
```

## Worked Example: Small System

### Initial Setup

```python
# 6-node system
nodes = {
    'A_core': Node(type=MODULE, criticality=0.9),
    'B_api': Node(type=SERVICE, criticality=0.8),
    'C_db': Node(type=DATABASE, criticality=1.0),
    'D_featureX': Node(type=FEATURE, criticality=0.6),
    'E_featureY': Node(type=FEATURE, criticality=0.5),
    'F_util': Node(type=LIBRARY, criticality=0.3),
}

edges = [
    Edge('A_core', 'B_api', weight=0.9),      # tight coupling
    Edge('A_core', 'C_db', weight=0.7),
    Edge('B_api', 'D_featureX', weight=0.6),
    Edge('B_api', 'E_featureY', weight=0.5),
    Edge('A_core', 'F_util', weight=0.4),
    Edge('D_featureX', 'C_db', weight=0.3),
]

# Initial state: moderately healthy
health = {
    'A_core': 0.8,
    'B_api': 0.8,
    'C_db': 0.7,
    'D_featureX': 0.6,
    'E_featureY': 0.6,
    'F_util': 0.7,
}

complexity = {
    'A_core': 0.7,
    'B_api': 0.6,
    'C_db': 0.5,
    'D_featureX': 0.4,
    'E_featureY': 0.4,
    'F_util': 0.3,
}

risk = {
    'A_core': 0.3,
    'B_api': 0.3,
    'C_db': 0.3,
    'D_featureX': 0.3,
    'E_featureY': 0.3,
    'F_util': 0.2,
}

demand = {
    'A_core': 0.4,
    'B_api': 0.5,
    'C_db': 0.3,
    'D_featureX': 0.9,  # hot feature!
    'E_featureY': 0.5,
    'F_util': 0.2,
}
```

### Step 1: Compute Badness

```python
α, β, γ = 0.4, 0.3, 0.3

bad = {}
for node_id in nodes:
    h = health[node_id]
    c = complexity[node_id]
    r = risk[node_id]
    bad[node_id] = α*(1-h) + β*c + γ*r

# Results:
bad = {
    'A_core': 0.4*0.2 + 0.3*0.7 + 0.3*0.3 = 0.08 + 0.21 + 0.09 = 0.38,
    'B_api': 0.4*0.2 + 0.3*0.6 + 0.3*0.3 = 0.08 + 0.18 + 0.09 = 0.35,
    'C_db': 0.4*0.3 + 0.3*0.5 + 0.3*0.3 = 0.12 + 0.15 + 0.09 = 0.36,
    'D_featureX': 0.4*0.4 + 0.3*0.4 + 0.3*0.3 = 0.16 + 0.12 + 0.09 = 0.37,
    'E_featureY': 0.4*0.4 + 0.3*0.4 + 0.3*0.3 = 0.37,
    'F_util': 0.4*0.3 + 0.3*0.3 + 0.3*0.2 = 0.12 + 0.09 + 0.06 = 0.27,
}
```

System is fairly uniform in badness—good sign, no extreme outliers.

### Step 2: Compute Structural Potential

```python
V_struct = 0.5 * sum(
    w_ij * (bad[i] - bad[j])**2
    for (i, j, w_ij) in edges
)

# Edge by edge:
A-B: 0.5 * 0.9 * (0.38 - 0.35)² = 0.45 * 0.0009 = 0.0004
A-C: 0.5 * 0.7 * (0.38 - 0.36)² = 0.35 * 0.0004 = 0.0001
B-D: 0.5 * 0.6 * (0.35 - 0.37)² = 0.30 * 0.0004 = 0.0001
B-E: 0.5 * 0.5 * (0.35 - 0.37)² = 0.25 * 0.0004 = 0.0001
A-F: 0.5 * 0.4 * (0.38 - 0.27)² = 0.20 * 0.0121 = 0.0024
D-C: 0.5 * 0.3 * (0.37 - 0.36)² = 0.15 * 0.0001 = 0.00002

V_struct ≈ 0.0031
```

Most edges have low tension. The A-F edge has the most (0.0024) because F_util has much lower badness than A_core.

### Step 3: Compute Business Potential

```python
λ1, λ2 = 0.6, 0.4

V_bus = sum(
    demand[i] * (λ1*(1-health[i]) + λ2*complexity[i])
    for i in nodes
)

# Node by node:
A: 0.4 * (0.6*0.2 + 0.4*0.7) = 0.4 * (0.12 + 0.28) = 0.4 * 0.40 = 0.16
B: 0.5 * (0.6*0.2 + 0.4*0.6) = 0.5 * (0.12 + 0.24) = 0.5 * 0.36 = 0.18
C: 0.3 * (0.6*0.3 + 0.4*0.5) = 0.3 * (0.18 + 0.20) = 0.3 * 0.38 = 0.114
D: 0.9 * (0.6*0.4 + 0.4*0.4) = 0.9 * (0.24 + 0.16) = 0.9 * 0.40 = 0.36
E: 0.5 * (0.6*0.4 + 0.4*0.4) = 0.5 * 0.40 = 0.20
F: 0.2 * (0.6*0.3 + 0.4*0.3) = 0.2 * (0.18 + 0.12) = 0.2 * 0.30 = 0.06

V_bus = 0.16 + 0.18 + 0.114 + 0.36 + 0.20 + 0.06 = 1.074
```

D_featureX contributes most (0.36) because it has high demand but mediocre health.

### Step 4: Total Potential and Initial Hamiltonian

```python
V = V_struct + V_bus = 0.0031 + 1.074 = 1.077

# At t=0, no changes yet, so T = 0
T = 0

H_0 = T + V = 0 + 1.077 = 1.077
L_0 = T - V = 0 - 1.077 = -1.077
```

**Baseline**: H ≈ 1.08, dominated by business potential (V_bus >> V_struct).

### Step 5: Simulate Event - FeatureChange at D

Agent does `FeatureChange(D_featureX)`:
- complexity[D] increases: 0.4 → 0.5
- health[D] decreases: 0.6 → 0.55
- risk[D] increases: 0.3 → 0.35

New badness:
```python
bad[D] = 0.4*(1-0.55) + 0.3*0.5 + 0.3*0.35
       = 0.4*0.45 + 0.15 + 0.105
       = 0.18 + 0.15 + 0.105 = 0.435
```

Changed from 0.37 to 0.435, so Δbad[D] = +0.065

### Step 6: Recompute Energies at t=1

**Structural potential**:
```python
# Only edges touching D changed:
# B-D: was 0.0001, now 0.5*0.6*(0.35-0.435)² = 0.3*(0.085)² = 0.3*0.007225 = 0.0022
# D-C: was 0.00002, now 0.5*0.3*(0.435-0.36)² = 0.15*(0.075)² = 0.15*0.005625 = 0.00084

# New V_struct ≈ 0.0004 + 0.0001 + 0.0022 + 0.0001 + 0.0024 + 0.00084 = 0.0060
```

Doubled from 0.0031 → 0.0060. The B-D and D-C edges are now more stressed.

**Business potential**:
```python
# Only D's contribution changed:
# Old: 0.36, New: 0.9 * (0.6*0.45 + 0.4*0.5) = 0.9 * (0.27 + 0.20) = 0.9*0.47 = 0.423

V_bus_new = 1.074 - 0.36 + 0.423 = 1.137
```

Increased from 1.074 → 1.137

**Kinetic energy**:
```python
# Only D changed
# Assume mass[D] = demand[D] = 0.9 (critical feature)
T = 0.5 * 0.9 * (0.065)² = 0.45 * 0.004225 = 0.0019
```

**New Hamiltonian**:
```python
V = 0.0060 + 1.137 = 1.143
H_1 = T + V = 0.0019 + 1.143 = 1.145
```

**ΔH** = 1.145 - 1.077 = +0.068

The system became slightly more stressed. The change was localized to D, but it increased both structural tension (neighbors now disagree more) and business potential (D is now worse but still under high demand).

### Step 7: Interpretation

**Local Dirichlet energy at B_api**:
```python
# Sum over edges touching B
E_local[B] = 0.5 * sum(w_ij * (bad[B] - bad[j])² for j in neighbors(B))

# B's neighbors: A, D, E
# At t=0: already computed as 0.0004 + 0.0001 + 0.0001 = 0.0006
# At t=1: 0.0004 + 0.0022 + 0.0001 = 0.0027

# Increased 4.5x!
```

Even though B_api didn't change, its **local energy spiked** because its neighbor D got worse. This is the early warning signal: B is now under more structural stress, making it more vulnerable to failures.

### Step 8: Flow Field Update

At node D after the change:
```python
# Gradient of V at D (simplified discrete version):
grad_V[D] = sum(w_ij * (bad[D] - bad[j]) for j in neighbors(D))
          = 0.6*(0.435 - 0.35) + 0.3*(0.435 - 0.36)  # B and C
          = 0.6*0.085 + 0.3*0.075
          = 0.051 + 0.0225 = 0.0735

# Flow at D:
business_dir = [0.9, 0]  # high demand
stability_dir = [0, -0.0735]  # downhill in V

flow[D] = 0.6*[0.9, 0] + 0.4*[0, -0.0735]
        = [0.54, 0] + [0, -0.0294]
        = [0.54, -0.0294]
```

The vector points **strongly right** (feature pressure still high) but **slightly down** (system wants to refactor D to reduce gradient).

At node B_api:
```python
# B's gradient increased because D got worse
grad_V[B] = sum(w_ij * (bad[B] - bad[j]) for j in neighbors(B))
          = 0.9*(0.35-0.38) + 0.6*(0.35-0.435) + 0.5*(0.35-0.37)
          = 0.9*(-0.03) + 0.6*(-0.085) + 0.5*(-0.02)
          = -0.027 - 0.051 - 0.01 = -0.088

# Negative gradient → B is "downhill" from neighbors
# Stability direction points UP (increase B's badness would reduce global V?!)
# This is counterintuitive, but it happens when you're the "good" node surrounded by "bad" neighbors
# In practice, you'd want to refactor the neighbors, not make B worse

# More nuanced flow computation would recognize B is a hub under stress and prioritize
# refactoring its neighbors or adding constraints (tests) around B
```

This illustrates why **local Dirichlet energy** at hubs is more useful than raw gradients: it tells you "this area has high tension" without the sign ambiguity.

## Mapping Agent Actions to Transformations

### FeatureChange(node)

**Effect on fields**:
```python
def apply_feature_change(node: Node, magnitude=0.1):
    complexity[node] += magnitude
    health[node] -= magnitude * 0.5
    risk[node] += magnitude * 0.3

    # Clamp to [0,1]
    complexity[node] = min(1.0, complexity[node])
    health[node] = max(0.0, health[node])
    risk[node] = min(1.0, risk[node])
```

**Effect on graph**: None (topology unchanged)

**Typical ΔH**: +0.05 to +0.15 depending on node centrality

### Refactor(node)

**Effect on fields**:
```python
def apply_refactor(node: Node, magnitude=0.1):
    complexity[node] -= magnitude
    health[node] += magnitude * 0.8
    risk[node] -= magnitude * 0.5

    # Clamp
    complexity[node] = max(0.0, complexity[node])
    health[node] = min(1.0, health[node])
    risk[node] = max(0.0, risk[node])
```

**Effect on graph**: None

**Typical ΔH**: -0.03 to -0.10 (energy decreases—good!)

### AddEdge(i, j)

**Effect on graph**: New edge with initial weight based on type
```python
def apply_add_edge(i: Node, j: Node, edge_type: EdgeType):
    w_init = 0.5  # medium coupling initially
    G.add_edge(Edge(i, j, edge_type, w_init))

    # Side effects on fields:
    risk[i] += 0.05  # new dependency adds risk
    risk[j] += 0.05
```

**Effect on Laplacian**: L changes—new row sums, new off-diagonal entries

**Typical ΔH**: +0.02 to +0.08 (adding coupling usually increases V_struct)

### RemoveEdge(i, j)

**Effect on graph**: Edge removed
```python
def apply_remove_edge(i: Node, j: Node):
    G.remove_edge(i, j)

    # Temporarily increase complexity as boundaries are redrawn
    complexity[i] += 0.03
    complexity[j] += 0.03

    # But risk might decrease (decoupling can be good long-term)
    # This creates a transient spike in H, then relaxation
```

**Typical ΔH**: +0.05 initially, then -0.08 after a few steps (worth it for decoupling)

### AddConstraint(node)

**Effect on graph**: Increase weights on edges touching node (stiffer springs)
```python
def apply_add_constraint(node: Node):
    for edge in G.edges_touching(node):
        edge.weight *= 1.2  # 20% stiffer

    # Improve health slightly (more tests/contracts)
    health[node] += 0.05
```

**Effect on V_struct**: Can increase (tighter coupling) but reduces variance (neighbors pulled together)

**Typical ΔH**: +0.01 short-term, -0.05 long-term (constraints pay off)

## Diagnostic Patterns

### Pattern 1: Hub Under Stress

**Symptom**: Local Dirichlet energy at a high-centrality node spikes

**Calculation**:
```python
def local_dirichlet_energy(G: Graph, bad: Dict, node: Node) -> float:
    E_local = 0.0
    for edge in G.edges_touching(node):
        neighbor = edge.other_end(node)
        w = edge.weight
        E_local += 0.5 * w * (bad[node] - bad[neighbor])**2
    return E_local

# Alert condition:
if local_dirichlet_energy(G, bad, hub_node) > threshold:
    alert("Hub under stress: " + hub_node.id)
```

**Interpretation**: The hub is either much better or much worse than its neighbors, creating tension. Failures are likely to propagate through this hub.

**Action**: Refactor hub or its neighbors to smooth the gradient. Add constraints (tests) around hub.

### Pattern 2: Runaway Hamiltonian

**Symptom**: H increasing monotonically over many steps

**Detection**:
```python
def detect_runaway(H_history: List[float], window=10) -> bool:
    if len(H_history) < window:
        return False

    recent = H_history[-window:]
    # Check if strictly increasing
    return all(recent[i] < recent[i+1] for i in range(len(recent)-1))
```

**Interpretation**: System is accumulating stress faster than it's being relieved. Either too much change (high T) or accumulating structural/business debt (rising V).

**Action**: Pause feature work. Force refactors. Increase constraints.

### Pattern 3: Frozen System

**Symptom**: T ≈ 0 for extended period, but V high

**Detection**:
```python
def detect_frozen(T: float, V: float, T_threshold=0.01) -> bool:
    return T < T_threshold and V > 0.5
```

**Interpretation**: Lots of structural tension (V high) but no motion (T low). System is "stuck"—too constrained, bureaucratic, or risk-averse to move.

**Action**: Relax some constraints. Remove blocker. Inject energy (new feature, refactor initiative).

### Pattern 4: Chaotic Thrash

**Symptom**: Both T and V high, H spiking

**Detection**:
```python
def detect_chaos(T: float, V: float) -> bool:
    return T > 0.3 and V > 0.8
```

**Interpretation**: Lots of motion AND lots of stress. Changes are happening but making things worse, not better. Likely unconstrained agents or poor coordination.

**Action**: Emergency brake. Pause all agents. Require approval for changes. Add governance gates.

## Summary: The Physics → Software Dictionary

| Physics Concept | Software Analogue | How to Measure |
|----------------|-------------------|----------------|
| **Graph nodes** | Modules, services, features | Static analysis, service registry |
| **Graph edges** | Dependencies, calls, data flows | Imports, API traces, change coupling |
| **Edge weights w_ij** | Coupling strength | Call volume, data flow, co-change freq |
| **Scalar field f[i]** | Health, complexity, risk | Test coverage, linters, bug history |
| **Dirichlet energy** | Structural tension | ½ Σ w_ij (f[i]-f[j])² via Laplacian |
| **Potential V** | Structural + business stress | V_struct + V_bus |
| **Kinetic T** | Rate of change | ½ Σ m_i (Δf[i])² |
| **Hamiltonian H** | Total system load | T + V |
| **Lagrangian L** | Quality of motion | T - V |
| **Gradient ∇V** | Direction of stress | (L · f)[i] at node i |
| **Vector field** | Guidance for actions | Combine demand + -∇V |
| **Harmonic function** | Equilibrium state | Minimizer of Dirichlet energy |
| **Effective resistance** | Modularity / isolation | R_eff(i,j) via L pseudoinverse |

**Next**: Use this mapping to build the MVP simulator, run scenarios, validate that the diagnostics work.
