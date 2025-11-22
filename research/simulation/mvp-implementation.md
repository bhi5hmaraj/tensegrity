# MVP Simulator - Implementation Guide

## Overview

This document provides the technical plan for implementing the software tensegrity simulator in Python.

**For the model** (fields, energies), see `mvp-model.md`.

**For simulation design** (actors, events, loop), see `mvp-simulation-design.md`.

---

## 1. Technology Stack

### 1.1 Core Dependencies

**Language**: Python 3.10+

**Required libraries**:
```bash
networkx>=3.0       # Graph structure, Laplacian computation
numpy>=1.24         # Vectorized field operations, matrix math
matplotlib>=3.7     # Visualization (graphs and time series)
scipy>=1.10         # Sparse linear algebra, optional for scaling
```

**Install**:
```bash
pip install networkx numpy matplotlib scipy
```

### 1.2 Optional/Future

**Agent-based modeling**:
```bash
mesa>=2.1  # ABM framework with browser visualization
```

**System dynamics**:
```bash
pysd>=3.0  # Translate Vensim/XMILE to Python
```

**Interactive UI**:
```bash
streamlit>=1.28     # Quick dashboards
jupyter>=1.0        # Notebooks for exploration
```

### 1.3 Development Tools

```bash
pytest>=7.0         # Unit testing
black>=23.0         # Code formatting
mypy>=1.0           # Type checking (optional)
```

---

## 2. Project Structure

```
tensegrity/research/
├── simulation/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph_model.py      # Graph, fields, Laplacian
│   │   ├── energy.py           # V_struct, V_bus, T, H calculations
│   │   └── state.py            # SimulationState class
│   ├── actors/
│   │   ├── __init__.py
│   │   ├── base.py             # BaseActor abstract class
│   │   ├── feature_engineer.py
│   │   ├── refactor_engineer.py
│   │   ├── ai_agent.py
│   │   └── product_manager.py
│   ├── events/
│   │   ├── __init__.py
│   │   ├── base.py             # Event base class
│   │   ├── field_events.py     # FeatureChange, Refactor, Patch
│   │   ├── structural_events.py # AddEdge, RemoveEdge, etc.
│   │   ├── constraint_events.py # AddConstraint, GovernanceChange
│   │   └── environment_events.py # DemandShock, NewRequirement
│   ├── scenarios/
│   │   ├── __init__.py
│   │   ├── baseline.py
│   │   ├── competitor_shock.py
│   │   └── governance_experiment.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging_utils.py
│   │   ├── visualization.py
│   │   └── metrics.py
│   ├── simulation.py           # Main simulation loop
│   └── config.py              # Parameters, constants
├── notebooks/
│   └── mvp_demo.ipynb
├── tests/
│   ├── test_energy.py
│   ├── test_events.py
│   └── test_actors.py
└── data/
    └── outputs/                # Simulation results
```

---

## 3. Implementation Plan - Phased Approach

### Phase 1: Core Infrastructure (Week 1)

**Goal**: Graph model, fields, energy calculations working and tested

#### Task 1.1: Graph Model (`core/graph_model.py`)

```python
import networkx as nx
import numpy as np

class TensegrityGraph:
    """Wrapper around NetworkX with software-specific methods."""

    def __init__(self, nodes: list, edges: list):
        self.G = nx.Graph()
        self._initialize_nodes(nodes)
        self._initialize_edges(edges)
        self.L = None  # Laplacian matrix
        self._update_laplacian()

    def _initialize_nodes(self, nodes):
        for node_id in nodes:
            self.G.add_node(node_id)

    def _initialize_edges(self, edges):
        for (i, j, weight) in edges:
            self.G.add_edge(i, j, weight=weight)

    def _update_laplacian(self):
        """Compute and cache Laplacian matrix."""
        self.L = nx.laplacian_matrix(self.G).toarray()

    def add_edge_weighted(self, i, j, weight):
        """Add or update edge, recompute Laplacian."""
        self.G.add_edge(i, j, weight=weight)
        self._update_laplacian()

    def remove_edge_safe(self, i, j):
        """Remove edge if exists, recompute Laplacian."""
        if self.G.has_edge(i, j):
            self.G.remove_edge(i, j)
            self._update_laplacian()

    def get_neighbors(self, node):
        return list(self.G.neighbors(node))

    def edges_touching(self, node):
        return list(self.G.edges(node, data=True))
```

**Deliverable**: `TensegrityGraph` class with Laplacian computation

**Test**: Create 6-node graph, verify Laplacian properties (row sums = 0, symmetric, PSD)

#### Task 1.2: Energy Calculations (`core/energy.py`)

```python
import numpy as np

def compute_structural_potential(L: np.ndarray, bad: np.ndarray) -> float:
    """
    V_struct = ½ bad^T L bad
    """
    return 0.5 * bad.T @ L @ bad

def compute_business_potential(demand: dict, health: dict,
                                complexity: dict, λ1=0.6, λ2=0.4) -> float:
    """
    V_bus = Σ demand[i] · [λ1(1-health[i]) + λ2·complexity[i]]
    """
    V = 0.0
    for i in demand.keys():
        V += demand[i] * (λ1 * (1 - health[i]) + λ2 * complexity[i])
    return V

def compute_kinetic_energy(bad_curr: np.ndarray, bad_prev: np.ndarray,
                           mass: np.ndarray) -> float:
    """
    T = ½ Σ m_i (Δbad[i])²
    """
    delta_bad = bad_curr - bad_prev
    return 0.5 * np.sum(mass * delta_bad**2)

def compute_local_dirichlet_energy(G, bad: dict, node: str) -> float:
    """
    E_local[i] = ½ Σ_j∈neighbors(i) w_ij (bad[i] - bad[j])²
    """
    E = 0.0
    for neighbor in G.neighbors(node):
        w = G[node][neighbor]['weight']
        diff = bad[node] - bad[neighbor]
        E += 0.5 * w * diff**2
    return E
```

**Deliverable**: Energy calculation functions

**Test**: Hand-calculate energies for 3-node graph, verify code matches

#### Task 1.3: State Management (`core/state.py`)

```python
from dataclasses import dataclass, field
import numpy as np

@dataclass
class SimulationState:
    """Complete state of the simulation at one time step."""

    # Graph
    graph: TensegrityGraph

    # Scalar fields (dict[node_id, float])
    health: dict
    complexity: dict
    risk: dict
    demand: dict

    # Derived
    bad: dict = field(default_factory=dict)
    bad_prev: dict = field(default_factory=dict)

    # Vector field (dict[node_id, tuple])
    flow: dict = field(default_factory=dict)
    grad_V: dict = field(default_factory=dict)

    # Energies
    V_struct: float = 0.0
    V_bus: float = 0.0
    V: float = 0.0
    T: float = 0.0
    H: float = 0.0
    L: float = 0.0  # Lagrangian

    # Diagnostics
    E_local: dict = field(default_factory=dict)

    # Incidents
    incidents: list = field(default_factory=list)

    def update_derived_fields(self, α=0.4, β=0.3, γ=0.3):
        """Compute badness, gradient, flow."""
        # Badness
        for node in self.graph.G.nodes:
            self.bad[node] = (α * (1 - self.health[node]) +
                             β * self.complexity[node] +
                             γ * self.risk[node])

        # Gradient (discrete Laplacian)
        for node in self.graph.G.nodes:
            grad = 0.0
            for neighbor in self.graph.get_neighbors(node):
                w = self.graph.G[node][neighbor]['weight']
                grad += w * (self.bad[node] - self.bad[neighbor])
            self.grad_V[node] = grad

        # Flow (business + stability)
        for node in self.graph.G.nodes:
            business_x = self.demand[node]
            stability_y = -self.grad_V[node]

            α_flow, β_flow = 0.6, 0.4
            flow_x = α_flow * business_x
            flow_y = β_flow * stability_y

            self.flow[node] = (flow_x, flow_y)

    def update_energies(self):
        """Recompute all energies."""
        bad_array = np.array([self.bad[n] for n in self.graph.G.nodes])
        bad_prev_array = np.array([self.bad_prev[n] for n in self.graph.G.nodes])
        mass_array = np.array([self.demand[n] for n in self.graph.G.nodes])

        self.V_struct = compute_structural_potential(self.graph.L, bad_array)
        self.V_bus = compute_business_potential(self.demand, self.health,
                                                 self.complexity)
        self.V = self.V_struct + self.V_bus

        self.T = compute_kinetic_energy(bad_array, bad_prev_array, mass_array)

        self.H = self.T + self.V
        self.L = self.T - self.V

        # Local energies
        for node in self.graph.G.nodes:
            self.E_local[node] = compute_local_dirichlet_energy(
                self.graph.G, self.bad, node
            )
```

**Deliverable**: `SimulationState` class with update methods

**Test**: Create state, apply field changes, verify energies update correctly

---

### Phase 2: Events and Actors (Week 1-2)

#### Task 2.1: Event Base Class (`events/base.py`)

```python
from abc import ABC, abstractmethod

class Event(ABC):
    """Base class for all events."""

    @abstractmethod
    def apply(self, state: SimulationState) -> SimulationState:
        """Apply this event to state, return modified state."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Human-readable description."""
        pass
```

#### Task 2.2: Field Events (`events/field_events.py`)

```python
class FeatureChange(Event):
    def __init__(self, node: str, magnitude: float = 0.1):
        self.node = node
        self.magnitude = magnitude

    def apply(self, state: SimulationState) -> SimulationState:
        state.complexity[self.node] = min(1.0,
            state.complexity[self.node] + self.magnitude)
        state.health[self.node] = max(0.0,
            state.health[self.node] - 0.5 * self.magnitude)
        state.risk[self.node] = min(1.0,
            state.risk[self.node] + 0.3 * self.magnitude)
        return state

    def __str__(self):
        return f"FeatureChange({self.node})"

class Refactor(Event):
    # Similar structure...
```

**Deliverable**: All field event classes

**Test**: Apply event, verify fields change as specified

#### Task 2.3: Actor Base Class (`actors/base.py`)

```python
class BaseActor(ABC):
    """Base class for all actors."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def choose_action(self, state: SimulationState) -> Event:
        """Observe state, return chosen event."""
        pass
```

#### Task 2.4: Concrete Actors

Implement `FeatureEngineer`, `RefactorEngineer`, `AIAgent` per design in `mvp-simulation-design.md`.

**Deliverable**: Actor classes with policies

**Test**: Mock state, call `choose_action`, verify action type matches policy

---

### Phase 3: Simulation Loop (Week 2)

#### Task 3.1: Main Loop (`simulation.py`)

```python
def run_simulation(initial_state: SimulationState,
                   actors: list,
                   scheduled_events: dict,
                   n_steps: int,
                   config: dict) -> list:
    """
    Run simulation for n_steps, return history.
    """
    state = initial_state
    history = []

    for k in range(n_steps):
        # Apply scheduled environment events
        for event in scheduled_events.get(k, []):
            state = event.apply(state)

        # Actors act
        for actor in actors:
            action = actor.choose_action(state)
            state = action.apply(state)

        # Update derived fields and energies
        state.update_derived_fields()
        state.update_energies()

        # Check for incidents
        state.incidents = check_incidents(state)

        # Log
        history.append(snapshot_state(state, k))

        # Update prev for next step
        state.bad_prev = state.bad.copy()

    return history

def snapshot_state(state: SimulationState, step: int) -> dict:
    """Extract key metrics for logging."""
    return {
        'step': step,
        'H': state.H,
        'T': state.T,
        'V': state.V,
        'V_struct': state.V_struct,
        'V_bus': state.V_bus,
        'fields': {node: {'bad': state.bad[node],
                          'E_local': state.E_local[node]}
                   for node in state.graph.G.nodes},
        'incidents': state.incidents,
    }
```

**Deliverable**: Working simulation loop

**Test**: Run 10-step sim with dummy actors, verify history length = 10

#### Task 3.2: Logging (`utils/logging_utils.py`)

```python
import json
import csv

def save_history_csv(history: list, filename: str):
    """Save time series to CSV."""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['step', 'H', 'T', 'V',
                                                 'V_struct', 'V_bus'])
        writer.writeheader()
        for entry in history:
            writer.writerow({
                'step': entry['step'],
                'H': entry['H'],
                'T': entry['T'],
                'V': entry['V'],
                'V_struct': entry['V_struct'],
                'V_bus': entry['V_bus'],
            })

def save_history_json(history: list, filename: str):
    """Save full history to JSON."""
    with open(filename, 'w') as f:
        json.dump(history, f, indent=2)
```

**Deliverable**: Logging utilities

**Test**: Run sim, save CSV and JSON, verify files are valid

---

### Phase 4: Scenarios (Week 2-3)

See `mvp-scenarios.md` for detailed scenario definitions.

#### Task 4.1: Baseline Scenario (`scenarios/baseline.py`)

```python
def create_baseline_scenario():
    """Stable system with mixed actor activity."""
    graph = create_6node_graph()
    fields = initialize_healthy_fields()
    actors = [FeatureEngineer(), RefactorEngineer(), AIAgent()]
    scheduled = {}  # No shocks

    return {
        'graph': graph,
        'fields': fields,
        'actors': actors,
        'scheduled': scheduled,
        'n_steps': 100,
    }

if __name__ == '__main__':
    scenario = create_baseline_scenario()
    state = SimulationState(scenario['graph'], **scenario['fields'])
    history = run_simulation(state, scenario['actors'],
                            scenario['scheduled'], scenario['n_steps'])

    save_history_csv(history, 'baseline_results.csv')
    plot_timeseries(history)
```

**Deliverable**: Baseline scenario script

**Test**: Run, verify H stays in moderate range

#### Task 4.2: Competitor Shock Scenario

Implement per `mvp-scenarios.md`.

#### Task 4.3: Governance Experiment

Implement constrained vs unconstrained comparison.

---

### Phase 5: Visualization and Analysis (Week 3)

#### Task 5.1: Time Series Plots (`utils/visualization.py`)

```python
import matplotlib.pyplot as plt

def plot_timeseries(history: list):
    """Plot H, T, V vs time."""
    steps = [h['step'] for h in history]
    H = [h['H'] for h in history]
    T = [h['T'] for h in history]
    V = [h['V'] for h in history]

    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    ax[0].plot(steps, H, label='H = T + V')
    ax[0].set_ylabel('Hamiltonian H')
    ax[0].legend()
    ax[0].grid(True)

    ax[1].plot(steps, T, label='T (kinetic)', color='orange')
    ax[1].set_ylabel('Kinetic Energy T')
    ax[1].legend()
    ax[1].grid(True)

    ax[2].plot(steps, V, label='V (potential)', color='red')
    ax[2].set_ylabel('Potential Energy V')
    ax[2].set_xlabel('Time Step')
    ax[2].legend()
    ax[2].grid(True)

    plt.tight_layout()
    plt.show()
```

#### Task 5.2: Graph Visualization

```python
def visualize_graph(state: SimulationState):
    """Draw graph with node colors = badness."""
    import networkx as nx
    import matplotlib.pyplot as plt

    G = state.graph.G
    pos = nx.spring_layout(G)

    node_colors = [state.bad[node] for node in G.nodes]
    node_sizes = [1000 * state.demand[node] for node in G.nodes]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=node_sizes, cmap='RdYlGn_r',
                           vmin=0, vmax=1)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, width=2)

    plt.title('Software Tensegrity Graph')
    plt.colorbar(label='Badness')
    plt.axis('off')
    plt.show()
```

**Deliverable**: Visualization utilities

**Test**: Plot baseline results, verify they make sense

---

## 4. Configuration Management

**File**: `config.py`

```python
# Field weight parameters
BADNESS_ALPHA = 0.4  # Health weight
BADNESS_BETA = 0.3   # Complexity weight
BADNESS_GAMMA = 0.3  # Risk weight

# Business potential parameters
LAMBDA_1 = 0.6  # Health vs demand
LAMBDA_2 = 0.4  # Complexity vs demand

# Flow field parameters
ALPHA_FLOW = 0.6  # Business direction weight
BETA_FLOW = 0.4   # Stability direction weight

# Governance thresholds
H_EMERGENCY = 2.0         # Trigger emergency brake
LOCAL_E_WARNING = 0.5     # Hub stress alert
T_FROZEN = 0.01           # System frozen alert

# Simulation parameters
DEFAULT_N_STEPS = 100
RANDOM_SEED = 42
```

**Use**: Import in all modules, easy tuning

---

## 5. Testing Strategy

### Unit Tests

**`tests/test_energy.py`**:
- Test Laplacian computation for known graphs
- Test energy formulas against hand calculations
- Test energy is non-negative, bounded

**`tests/test_events.py`**:
- Test each event modifies fields correctly
- Test events clamp fields to [0,1]
- Test structural events update Laplacian

**`tests/test_actors.py`**:
- Test actor policies choose sensible actions
- Test weighted sampling works
- Test flow-following logic

### Integration Tests

**`tests/test_simulation.py`**:
- Run 10-step sim, verify no crashes
- Check energy conservation properties (if applicable)
- Verify logging produces valid output

### Run Tests

```bash
pytest tests/ -v
```

---

## 6. Development Workflow

### Initial Setup

```bash
# Clone repo
cd tensegrity/research/simulation

# Create venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

### Development Cycle

1. **Implement feature** (e.g., new event type)
2. **Write test** for that feature
3. **Run tests**: `pytest tests/`
4. **Commit**: `git commit -m "feat: add SplitNode event"`
5. **Repeat**

### Running Scenarios

```bash
# Baseline
python scenarios/baseline.py

# Competitor shock
python scenarios/competitor_shock.py

# Compare outputs
python analysis/compare_scenarios.py baseline_results.csv shock_results.csv
```

---

## 7. Deliverables Checklist

### Phase 1: Core
- [ ] `TensegrityGraph` class
- [ ] Energy calculation functions
- [ ] `SimulationState` class
- [ ] Unit tests passing

### Phase 2: Actors & Events
- [ ] All event classes (field, structural, constraint, environment)
- [ ] All actor classes (FE, RE, LLMA, PM)
- [ ] Unit tests for events and actors

### Phase 3: Simulation
- [ ] Main simulation loop
- [ ] Logging utilities
- [ ] Integration tests

### Phase 4: Scenarios
- [ ] Baseline scenario working
- [ ] Competitor shock scenario working
- [ ] Governance experiment working

### Phase 5: Analysis
- [ ] Time series plotting
- [ ] Graph visualization
- [ ] Comparison tools

---

## 8. Extension Points (Post-MVP)

### Easy Additions
- New event types (just subclass `Event`)
- New actor types (just subclass `BaseActor`)
- New governance rules (add to config, check in actor logic)

### Medium Additions
- **Mesa integration**: Wrap actors as Mesa agents, use built-in viz
- **Jupyter widgets**: Interactive parameter tuning
- **Sensitivity analysis**: Vary α, β, γ, see how results change

### Hard Additions
- **LLM-in-the-loop**: Call GPT API for AI agent decisions
- **Real repo integration**: Parse actual dependency graph
- **Continuous time**: Replace discrete loop with ODEs (use `scipy.integrate`)

---

## 9. Quick Start Guide

### For First-Time Users

```bash
# 1. Install
pip install networkx numpy matplotlib

# 2. Run baseline
cd tensegrity/research/simulation
python scenarios/baseline.py

# 3. View results
open baseline_results.csv  # Or Excel, etc.

# 4. Explore in notebook
jupyter notebook notebooks/mvp_demo.ipynb
```

### For Developers

```bash
# 1. Clone and setup
git clone <repo>
cd tensegrity/research/simulation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run tests
pytest tests/ -v

# 3. Implement a feature
# Edit core/graph_model.py, add method
# Write test in tests/test_graph_model.py
# Run: pytest tests/test_graph_model.py

# 4. Run scenario
python scenarios/baseline.py

# 5. Commit
git add .
git commit -m "feat: your feature"
git push
```

---

## 10. Performance Considerations

### For MVP (6-8 nodes, 100-500 steps)
- **NetworkX is fine**: Small graphs, no performance issues
- **NumPy arrays**: Fast enough for energies
- **Matplotlib**: Adequate for basic plots

### For Scaling (50+ nodes, 1000+ steps)
- **Use scipy.sparse**: Sparse Laplacian matrices
- **Vectorize more**: Avoid Python loops, use NumPy broadcasting
- **Mesa for parallelism**: If many actor instances
- **Cython or Numba**: JIT-compile hot loops (energy calculations)

### Profiling

```bash
python -m cProfile -o profile.stats scenarios/baseline.py
python -m pstats profile.stats
# (pstats) sort cumtime
# (pstats) stats 10
```

Identify bottlenecks, optimize as needed.

---

## Summary

**Phases**:
1. Core infrastructure: graph, energies, state (Week 1)
2. Events and actors (Week 1-2)
3. Simulation loop and logging (Week 2)
4. Scenarios (Week 2-3)
5. Visualization and analysis (Week 3)

**Tech stack**: Python + NetworkX + NumPy + Matplotlib

**Output**: Working simulator with 3 scenarios, CSV logs, time series plots

**Success**: If baseline runs, competitor shock shows qualitative regime change, and governed mode stabilizes H

**Next**: See `mvp-scenarios.md` for detailed scenario specs
