# MVP Simulator - Scenarios

## Overview

This document specifies three concrete scenarios for validating the software tensegrity simulator.

**Purpose**: Test the core hypothesis that Laplacian-based structural metrics provide earlier warning signals than traditional per-node metrics.

**For model details**, see `mvp-model.md`.

**For simulation mechanics**, see `mvp-simulation-design.md`.

---

## Scenario 1: Baseline (Healthy Equilibrium)

### Purpose

Establish baseline behavior: system in stable equilibrium with mixed actor activity, no external shocks.

**Expected outcome**: H stays moderate, gentle oscillations, no runaway dynamics.

### Initial Conditions

**Graph**: 6 nodes, hub-and-spoke topology

```
    A_core
    /  |  \
  /    |    \
B_api  C_db  F_util
  |     |
  |     |
D_feat  E_feat
```

**Edges and weights**:
```python
edges = [
    ('A_core', 'B_api', 0.9),      # Tight coupling
    ('A_core', 'C_db', 0.7),
    ('A_core', 'F_util', 0.4),
    ('B_api', 'D_featureX', 0.6),
    ('B_api', 'E_featureY', 0.5),
    ('C_db', 'D_featureX', 0.3),
]
```

**Fields** (initial values):
```python
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

risk = {  # All moderate
    node: 0.3 for node in nodes
}

demand = {
    'A_core': 0.4,
    'B_api': 0.5,
    'C_db': 0.3,
    'D_featureX': 0.7,  # Popular feature
    'E_featureY': 0.5,
    'F_util': 0.2,
}
```

**Computed initial state**:
- badness: ~0.35-0.40 across nodes (fairly uniform)
- V_struct: ~0.003 (low tension, neighbors similar)
- V_bus: ~0.9 (moderate business pressure)
- V: ~0.903
- T: 0 (no change yet)
- H: ~0.903

### Actors

```python
actors = [
    FeatureEngineer(name='Alice'),
    RefactorEngineer(name='Bob'),
    AIAgent(name='Agent-1'),
]
```

**Activity levels**:
- Each actor acts once per time step
- Actions chosen stochastically per policy

### Scheduled Events

**None**. Baseline has no external shocks.

### Run Parameters

- **n_steps**: 100
- **random_seed**: 42 (for reproducibility)

### Expected Dynamics

**H trajectory**:
- Starts ~0.9
- Gentle oscillations around 1.0 ± 0.2
- No monotonic increase
- No emergency spikes

**T vs V**:
- T: oscillates 0.01 – 0.05 (moderate change rate)
- V: oscillates 0.8 – 1.2 (stable structure)
- T/V ratio: ~0.03 (slightly bureaucratic, expected for stable system)

**Fields**:
- health: stays in [0.5, 0.9] range
- complexity: slow drift toward 0.5-0.6 (slight increase from features, offset by refactors)
- risk: stays in [0.25, 0.4] (no runaway)

**Incidents**:
- 0-3 total over 100 steps (low rate, p_incident ≈ 0.01 per node per step)

### Success Criteria

1. **Stability**: H(100) ≈ H(0) ± 20% (system in equilibrium)
2. **No runaway**: max(H) < 1.5 (no crisis)
3. **Moderate activity**: mean(T) ≈ 0.02-0.04 (actors doing things but not thrashing)
4. **Low incidents**: total incidents < 5

### Outputs

- `baseline_history.csv`: Time series of H, T, V, etc.
- `baseline_fields.json`: Per-node field values at each step
- `baseline_plot.png`: H, T, V vs time
- `baseline_graph_final.png`: Graph visualization at t=100

### Analysis

**Plot**:
- Time series: H, T, V on same figure (3 subplots)
- Phase space: scatter plot of (T, V) points colored by step

**Metrics**:
- Mean H, std(H), max(H), min(H)
- Mean T/V ratio
- Incident rate per 10 steps
- Node-level: which nodes have highest average E_local?

**Interpretation**:
If baseline behaves as expected, the model is sane. We can use this as reference for shock scenarios.

---

## Scenario 2: Competitor Shock

### Purpose

Test system response to sudden demand shift and new requirement. Validate that:
1. H spikes during scramble to respond
2. Local E at hubs warns earlier than global metrics
3. Governed mode stabilizes faster than unconstrained mode

### Initial Conditions

**Same as Baseline**: 6-node graph, same initial field values

### Actors

**Same as Baseline**: Alice (FE), Bob (RE), Agent-1 (LLMA)

### Scheduled Events

**t=20**: Competitor introduces feature

```python
events_t20 = [
    DemandShock('D_featureX', Δ=-0.4),  # Users migrate away
    NewRequirement('G_featureComp'),     # New node added
]
```

**Details of NewRequirement**:
```python
# Add new node G_featureComp
graph.add_node('G_featureComp')

# Initialize fields
health['G_featureComp'] = 0.5       # New code, moderate quality
complexity['G_featureComp'] = 0.3   # Simple to start
risk['G_featureComp'] = 0.4         # Risky (unproven)
demand['G_featureComp'] = 0.8       # High urgency

# Add edges to core
graph.add_edge('A_core', 'G_featureComp', weight=0.6)
graph.add_edge('B_api', 'G_featureComp', weight=0.5)
```

**t=50**: Users start returning as feature ships

```python
events_t50 = [
    DemandShock('G_featureComp', Δ=+0.2),  # Demand increases
]
```

### Run Parameters

- **n_steps**: 100
- **random_seed**: 42
- **Two modes**: Unconstrained vs Governed

### Mode 1: Unconstrained

**Governance**: None. Actors can do anything.

**Expected dynamics**:

**t=0-20 (baseline)**:
- H ≈ 0.9-1.0, stable

**t=20 (shock)**:
- New node G with high demand added
- V_bus spikes: new term demand[G] × badness[G] ≈ 0.8 × 0.4 = 0.32
- H jumps to ~1.3-1.5

**t=21-50 (scramble)**:
- Alice and Agent-1 hammer G with FeatureChange
- G's complexity rises, health drops
- A_core and B_api under stress (coupled to G)
- Local E_local[A] and E_local[B] spike (neighbors disagree)
- T rises (lots of motion)
- V_struct rises (neighbors diverge in badness)
- H continues climbing: peak ~2.0-2.5

**t=50-80 (stabilization or not)**:
- If G is healthy: demand satisfied, V_bus drops, H starts relaxing
- If G is unhealthy: incidents fire, V_bus stays high, H stays elevated

**t=80-100 (aftermath)**:
- System may or may not return to baseline
- If unconstrained thrash occurred, H stays high, E_local at hubs remains elevated

### Mode 2: Governed

**Governance rules**:

1. **Hub protection**: If `E_local[hub] > 0.5`, only Refactor or AddConstraint allowed at hub until E_local drops
2. **Health floor**: If `health[i] < 0.4`, block FeatureChange(i)
3. **Emergency brake**: If `H > 2.0`, pause all feature work for 5 steps

**Expected dynamics**:

**t=0-20**: Same as unconstrained

**t=20**: Same shock

**t=21-50**:
- Alice and Agent-1 still target G
- But: when E_local[A] or E_local[B] exceeds 0.5, hub protection kicks in
- Bob is forced to Refactor(A) and Refactor(B)
- This keeps core healthy, preventing V_struct blowup
- T still high (lots of activity) but V capped by governance
- H peaks lower: ~1.7-1.9 instead of 2.5

**t=50-80**:
- Demand returns to G
- G is in better shape (governance prevented health from cratering)
- Fewer incidents
- V_bus drops as G becomes healthy
- H relaxes back toward 1.0-1.2

**t=80-100**:
- System returns to near-baseline equilibrium
- H ≈ 1.1, only slightly higher than initial

### Key Metrics to Compare

| Metric | Unconstrained | Governed | Interpretation |
|--------|---------------|----------|----------------|
| **max(H)** | ~2.3 | ~1.8 | Governance caps peak stress |
| **H at t=100** | ~1.7 | ~1.1 | Governed recovers faster |
| **Total incidents** | ~8-12 | ~3-5 | Fewer failures with governance |
| **max(E_local[A])** | ~0.8 | ~0.6 | Hub less stressed |
| **Time when E_local[A] > 0.5** | t≈25 | t≈27 | **Early warning** |
| **Time when avg(health) < 0.6** | t≈35 | t≈40 | Local energy warns ~10 steps earlier |
| **Time when first incident** | t≈38 | t≈45 | Incidents lag local energy by ~10-15 steps |

### Success Criteria

1. **Differentiation**: Unconstrained and governed modes produce visibly different H trajectories
2. **Early warning**: `E_local[hub] > threshold` occurs 5-10 steps before first incident
3. **Governance benefit**: Governed mode has lower max(H), faster recovery, fewer incidents

### Outputs

- `shock_unconstrained_history.csv`
- `shock_governed_history.csv`
- `shock_comparison_plot.png`: Overlay H(t) for both modes
- `shock_early_warning_plot.png`: Time series of E_local[A], avg(health), incident markers

### Analysis

**Early warning validation**:
```python
t_local_spike = first_time(E_local[A_core] > 0.5)
t_health_drop = first_time(avg(health) < 0.6)
t_first_incident = first_time(incident occurred)

assert t_local_spike < t_health_drop < t_first_incident
```

If true, we've validated the core hypothesis.

**Governance effectiveness**:
```python
assert max(H_governed) < max(H_unconstrained)
assert incidents_governed < incidents_unconstrained
```

If true, governance is working as intended.

---

## Scenario 3: Governance Experiment (A/B Test)

### Purpose

Systematic comparison of multiple governance strategies to find optimal balance.

### Setup

**Same initial condition as baseline.**

**Run multiple variants**:

1. **Variant A**: No governance (baseline)
2. **Variant B**: Health floor only (`health[i] < 0.4` blocks features)
3. **Variant C**: Hub protection only (`E_local[hub] > 0.5` requires refactor)
4. **Variant D**: Emergency brake only (`H > 2.0` pauses features)
5. **Variant E**: All three gates active

**Common shock**: Same competitor shock at t=20 as Scenario 2

**n_steps**: 100 for each variant

### Metrics to Track

For each variant, compute:

- **max(H)**: Peak stress
- **mean(H, t=50-100)**: Long-term stress level
- **total incidents**: Count
- **total FeatureChange events**: Velocity proxy
- **total Refactor events**: Quality investment proxy
- **mean(health, t=80-100)**: Final health state
- **recovery time**: Steps from max(H) back to H < 1.2

### Expected Results

| Variant | max(H) | Recovery Time | Incidents | Feature Events | Refactors |
|---------|--------|---------------|-----------|----------------|-----------|
| **A: None** | 2.3 | Never (stays high) | 10 | 70 | 20 |
| **B: Health floor** | 2.1 | 40 steps | 7 | 60 | 28 |
| **C: Hub protection** | 1.9 | 30 steps | 5 | 65 | 25 |
| **D: Emergency brake** | 2.0 (capped) | 35 steps | 6 | 55 | 30 |
| **E: All gates** | 1.8 | 25 steps | 4 | 50 | 35 |

**Interpretation**:

- **Variant C (hub protection)** is most effective at preventing stress concentration
- **Variant E (all gates)** is safest but slowest (most refactors, fewest features)
- **Variant B (health floor)** helps but doesn't address structural tension
- **Variant D (emergency brake)** is reactive, not proactive

**Tradeoff curve**: Plot `(feature_events, max(H))` for all variants

- Upper right: high velocity, high stress (Variant A)
- Lower left: low velocity, low stress (Variant E)
- Sweet spot: Variant C or D (moderate velocity, controlled stress)

### Success Criteria

1. **Differentiation**: Clear differences in max(H) and incidents across variants
2. **Tradeoff visible**: Can plot Pareto frontier of velocity vs. stress
3. **Best practice identified**: One variant clearly superior (likely C or E)

### Outputs

- `governance_comparison.csv`: Table of metrics per variant
- `governance_tradeoff.png`: Scatter plot of (velocity, max(H))
- `governance_timeseries.png`: H(t) for all variants overlaid

### Analysis

**Statistical test**: Is difference in mean(H) between variants significant?

```python
from scipy.stats import ttest_ind

H_A = extract_H(variant_A)
H_C = extract_H(variant_C)

t_stat, p_value = ttest_ind(H_A, H_C)

if p_value < 0.05:
    print("Variant C significantly better than A")
```

**Recommendation**: Based on results, which governance strategy to use in Tensegrity?

---

## Implementation Checklist

### For Each Scenario

- [ ] Define `create_scenario()` function returning config dict
- [ ] Implement in `scenarios/<name>.py`
- [ ] Run simulation, save results
- [ ] Generate plots
- [ ] Export CSV and JSON
- [ ] Document findings in scenario-specific README

### Example Template

```python
# scenarios/competitor_shock.py

from simulation import run_simulation
from core.state import SimulationState
from actors import FeatureEngineer, RefactorEngineer, AIAgent
from events import DemandShock, NewRequirement
from utils.visualization import plot_timeseries, save_csv

def create_competitor_shock_unconstrained():
    """Competitor shock with no governance."""
    # Graph setup
    graph = create_6node_graph()

    # Initial fields
    fields = create_baseline_fields()

    # Actors
    actors = [
        FeatureEngineer('Alice'),
        RefactorEngineer('Bob'),
        AIAgent('Agent-1'),
    ]

    # Scheduled events
    scheduled = {
        20: [
            DemandShock('D_featureX', -0.4),
            NewRequirement('G_featureComp'),
        ],
        50: [
            DemandShock('G_featureComp', +0.2),
        ],
    }

    return {
        'graph': graph,
        'fields': fields,
        'actors': actors,
        'scheduled': scheduled,
        'n_steps': 100,
        'governance': None,
    }

if __name__ == '__main__':
    config = create_competitor_shock_unconstrained()

    state = SimulationState(config['graph'], **config['fields'])

    history = run_simulation(
        state,
        config['actors'],
        config['scheduled'],
        config['n_steps'],
        config
    )

    # Save
    save_csv(history, 'shock_unconstrained.csv')

    # Plot
    plot_timeseries(history)
    plt.savefig('shock_unconstrained_plot.png')
    plt.show()

    # Report
    print(f"max(H) = {max(h['H'] for h in history)}")
    print(f"Total incidents = {sum(len(h['incidents']) for h in history)}")
```

---

## Summary

**Three scenarios**:

1. **Baseline**: Stable equilibrium, no shocks → validates model sanity
2. **Competitor shock**: External shock → validates early warning and governance effectiveness
3. **Governance experiment**: A/B test → finds optimal governance strategy

**Key hypothesis to validate**:

> Local Dirichlet energy at hubs (E_local) provides earlier warning (5-10 steps) than global scalar metrics (avg health, coverage) or incidents.

**Success**:
- If baseline is stable: model works
- If shock differentiates governed vs unconstrained: governance works
- If E_local spikes before incidents: hypothesis validated

**Next**: Implement scenarios, run experiments, analyze results, publish findings.
