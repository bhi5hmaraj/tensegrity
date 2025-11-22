# Experiment 02: Laplacian Early Warning Signal

## Status: ⊙ Design Complete, Implementation Pending

**Date designed**: 2025-11-22
**Implemented**: No
**Data collected**: No
**Analysis complete**: No

**Depends on**: Exp01 (baseline must PASS first)

---

## 1. Hypothesis

**H0 (Null)**: Local Dirichlet energy E_local at hub nodes does **not** predict incidents better than scalar metrics (health, complexity).

**H1 (Alternative)**: E_local at hub nodes provides **earlier warning** (~10 steps lead time) and **better predictive power** (higher AUC) than baseline metrics.

**Testable predictions**:
1. ROC AUC(E_local) > ROC AUC(health) with p < 0.05
2. ROC AUC(E_local) > ROC AUC(complexity) with p < 0.05
3. Mean lead time (E_local spike → incident) ≈ 8-12 steps
4. Mean lead time (health drop → incident) ≈ 2-5 steps

---

## 2. Purpose

**This is the CORE validation** of the software physics framework.

**Primary**: Test if structural tension (Laplacian-based) predicts failures better than scalar node properties.

**Why it matters**:
- If TRUE → Laplacian framework adds predictive value, not just mathematical elegance
- If FALSE → Framework is decorative, use simpler metrics instead

**Stakes**: If this experiment FAILS, most of the theory collapses. The phase space, Hamiltonian, thermodynamics—all rely on Laplacian being meaningful.

---

## 3. Starting State

### 3.1 Scenario: Competitor Shock

**Use**: Scenario 2 from `mvp-scenarios.md` (Competitor Shock)

**Why**: Creates incidents via external pressure, tests if E_local warns before failures manifest.

**Initial conditions**: Same as Baseline (Exp01), but with scheduled shock at t=20.

### 3.2 Scheduled Events

**t=20**: Competitor introduces competing feature
```python
events_t20 = [
    DemandShock('D_featureX', Δ=-0.4),      # Users migrate away
    NewRequirement('G_featureComp', demand=0.8, health=0.5, complexity=0.3),
]
```

**t=20**: Add new node G_featureComp, connect to A_core with w=0.6

**Expected dynamics**:
- Flow field rotates toward G_featureComp (high demand)
- Actors rush to build G
- A_core (hub) experiences stress (coupled to unhealthy new node)
- E_local[A_core] should spike ~t=25
- Incidents at A_core or neighbors ~t=35

### 3.3 Actors

**Unconstrained mode** (no governance):
```python
actors = [
    FeatureEngineer('Alice'),
    FeatureEngineer('Carol'),  # Two feature engineers (velocity pressure)
    RefactorEngineer('Bob'),
    AIAgent('Agent-1'),
]
```

**Justification**: More feature engineers → higher velocity → more stress → more incidents.

### 3.4 Run Parameters

- **n_steps**: 100
- **n_runs**: 30 (Monte Carlo to average over stochasticity)
- **random_seed**: different for each run

---

## 4. Measurement Protocol

### 4.1 What to Log (Every Step, Every Run)

**In addition to Exp01 logs**, track:

**Predictors** (potential early warning signals):
```python
predictors = {
    # Laplacian-based
    'E_local_A': E_local['A_core'],  # Hub node
    'E_local_max': max(E_local.values()),  # Any node
    'V_struct': V_struct,  # Global structural energy
    'grad_V_A': |grad_V['A_core']|,  # Gradient at hub

    # Scalar baselines
    'health_A': health['A_core'],
    'health_min': min(health.values()),
    'complexity_A': complexity['A_core'],
    'complexity_max': max(complexity.values()),
    'bad_A': bad['A_core'],
}
```

**Ground truth**:
```python
incidents_t = {
    'step': int,
    'node': str,
    'type': str,  # 'health_critical', 'complexity_overflow', etc.
}
```

**Incident definition** (resolve CONFUSION #4):
```python
# Option: Stochastic based on badness
p_incident[i] = sigmoid(bad[i] - 0.6, steepness=10)

# If random() < p_incident[i]: trigger incident
```

### 4.2 Output Files

**Per run**:
- `shock_run{n}_timeseries.csv`
- `shock_run{n}_incidents.csv`

**Aggregated**:
- `shock_aggregated_predictors.csv`: All predictor time series, all runs
- `shock_aggregated_incidents.csv`: All incidents, all runs
- `shock_roc_curves.png`: ROC curves for each predictor
- `shock_lead_time_analysis.json`: Lead time statistics

---

## 5. Analysis Plan

### 5.1 ROC Curve Analysis

**For each predictor**, build binary classifier:
- **Positive class**: Incident occurs in next N steps (N = 10)
- **Negative class**: No incident in next N steps

**Method**:
```python
from sklearn.metrics import roc_curve, auc

# For E_local_A as predictor
y_true = []  # Binary: incident in next 10 steps?
y_score = []  # E_local_A value

for run in runs:
    for t in range(len(run) - 10):
        # Check if incident happens in [t+1, t+10]
        incident_soon = any(incidents between t+1 and t+10)
        y_true.append(1 if incident_soon else 0)

        # Predictor value at t
        y_score.append(E_local_A[t])

# Compute ROC
fpr, tpr, thresholds = roc_curve(y_true, y_score)
roc_auc = auc(fpr, tpr)

print(f"E_local_A AUC: {roc_auc:.3f}")

# Repeat for health_A, complexity_A, etc.
```

**Comparison**:
```python
predictors_auc = {
    'E_local_A': 0.78,
    'E_local_max': 0.75,
    'V_struct': 0.65,
    'health_A': 0.62,
    'complexity_A': 0.58,
    'bad_A': 0.68,
}

# Statistical test: DeLong test for AUC comparison
from scipy.stats import bootstrap

# Compare E_local_A vs health_A
p_value = compare_auc(E_local_A, health_A, y_true)

# Hypothesis: AUC(E_local_A) > AUC(health_A), p < 0.05
```

**Plot**:
```python
plt.figure(figsize=(8, 6))
for name, (fpr, tpr, auc_val) in roc_curves.items():
    plt.plot(fpr, tpr, label=f'{name} (AUC={auc_val:.2f})')

plt.plot([0, 1], [0, 1], 'k--', label='Random')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves: Early Warning Signals')
plt.legend()
plt.grid(True)
plt.savefig('shock_roc_curves.png')
```

### 5.2 Lead Time Analysis

**Method**: For each incident, find when predictors crossed thresholds.

```python
# For each incident
for incident in incidents:
    t_incident = incident['step']
    node = incident['node']

    # Find when E_local_A first exceeded threshold (e.g., 0.5)
    t_warning_E_local = first_crossing(E_local_A, threshold=0.5, before=t_incident)

    # Find when health_A first dropped below threshold (e.g., 0.5)
    t_warning_health = first_crossing(health_A, threshold=0.5, before=t_incident, direction='down')

    # Lead times
    lead_time_E_local = t_incident - t_warning_E_local if t_warning_E_local else None
    lead_time_health = t_incident - t_warning_health if t_warning_health else None

    # Log
    lead_times.append({
        'incident_t': t_incident,
        'lead_E_local': lead_time_E_local,
        'lead_health': lead_time_health,
    })

# Statistics
mean_lead_E_local = np.mean([lt['lead_E_local'] for lt in lead_times if lt['lead_E_local']])
mean_lead_health = np.mean([lt['lead_health'] for lt in lead_times if lt['lead_health']])

print(f"Mean lead time E_local: {mean_lead_E_local:.1f} steps")
print(f"Mean lead time health: {mean_lead_health:.1f} steps")

# Hypothesis: mean_lead_E_local ≈ 10, mean_lead_health ≈ 3
```

**Visualization**:
```python
plt.figure(figsize=(8, 6))
plt.hist([lt['lead_E_local'] for lt in lead_times], bins=20, alpha=0.5, label='E_local')
plt.hist([lt['lead_health'] for lt in lead_times], bins=20, alpha=0.5, label='health')
plt.xlabel('Lead Time (steps)')
plt.ylabel('Count')
plt.title('Distribution of Lead Times')
plt.legend()
plt.savefig('shock_lead_time_distribution.png')
```

### 5.3 Time Series Visualization

**Plot**: Overlay predictor and incident markers

```python
fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

# E_local_A
axes[0].plot(steps, E_local_A, label='E_local[A_core]', color='blue')
axes[0].axhline(0.5, color='red', linestyle='--', label='Threshold')
for incident in incidents_at_A:
    axes[0].axvline(incident['step'], color='red', alpha=0.3)
axes[0].set_ylabel('E_local[A_core]')
axes[0].legend()
axes[0].grid(True)

# Health_A
axes[1].plot(steps, health_A, label='health[A_core]', color='green')
axes[1].axhline(0.5, color='red', linestyle='--', label='Threshold')
for incident in incidents_at_A:
    axes[1].axvline(incident['step'], color='red', alpha=0.3)
axes[1].set_ylabel('health[A_core]')
axes[1].legend()
axes[1].grid(True)

# Incidents count
axes[2].bar(steps, incidents_per_step, color='red', alpha=0.5)
axes[2].set_ylabel('Incidents')
axes[2].set_xlabel('Time Step')
axes[2].grid(True)

plt.suptitle('Early Warning Signals: E_local vs health')
plt.savefig('shock_early_warning_comparison.png')
```

---

## 6. Success Criteria

### 6.1 Quantitative Thresholds

**STRONG SUCCESS (H1 strongly supported)**:
1. AUC(E_local_A) > AUC(health_A) + 0.1, p < 0.01
2. AUC(E_local_A) > AUC(complexity_A) + 0.1, p < 0.01
3. Mean lead time (E_local) > 8 steps
4. Mean lead time (health) < 5 steps
5. Lead time difference > 5 steps, p < 0.05

**MODERATE SUCCESS**:
1. AUC(E_local_A) > AUC(health_A), p < 0.05
2. Mean lead time (E_local) > mean lead time (health), p < 0.05

**FAILURE (H0 not rejected)**:
1. AUC(E_local_A) ≈ AUC(health_A) (difference < 0.05)
2. No significant lead time difference

### 6.2 Interpretation

**If STRONG SUCCESS**:
- Laplacian framework validated
- E_local is a useful early warning signal
- Proceed with confidence to Exp03-05
- Write up results for publication

**If MODERATE SUCCESS**:
- Laplacian adds value but not dramatically
- May need calibration (threshold tuning)
- Proceed to Exp03, but cautiously
- Consider alternative formulations (normalized Laplacian?)

**If FAILURE**:
- Laplacian doesn't predict better than scalars
- Either:
  - Model is wrong (back to theory)
  - Implementation has bugs (debug)
  - Confusions unresolved correctly (revisit CONFUSION #1-7)
- Do NOT proceed to Exp03-05 until this is fixed

---

## 7. Implementation Notes

### 7.1 Code to Write

**New components** (beyond Exp01):
```python
# events/environment_events.py
class DemandShock(Event):
    def __init__(self, node, delta):
        self.node = node
        self.delta = delta

    def apply(self, state):
        state.demand[self.node] += self.delta
        state.demand[self.node] = np.clip(state.demand[self.node], 0, 1)
        return state

class NewRequirement(Event):
    def __init__(self, node_id, demand, health, complexity):
        self.node_id = node_id
        self.demand = demand
        self.health = health
        self.complexity = complexity

    def apply(self, state):
        # Add node to graph
        state.graph.G.add_node(self.node_id)
        state.graph._update_laplacian()

        # Initialize fields
        state.health[self.node_id] = self.health
        state.complexity[self.node_id] = self.complexity
        state.risk[self.node_id] = 0.3  # Default
        state.demand[self.node_id] = self.demand

        return state
```

```python
# scenarios/competitor_shock.py
def create_competitor_shock_scenario():
    # Same as baseline for t < 20
    graph, fields, actors = create_baseline_components()

    # Scheduled shock at t=20
    scheduled = {
        20: [
            DemandShock('D_featureX', delta=-0.4),
            NewRequirement('G_featureComp', demand=0.8, health=0.5, complexity=0.3),
            # Also add edge: G_featureComp <-> A_core
            AddEdge('G_featureComp', 'A_core', weight=0.6),
        ]
    }

    return {
        'graph': graph,
        'fields': fields,
        'actors': actors,
        'scheduled': scheduled,
        'n_steps': 100,
    }
```

```python
# analysis/roc_analysis.py
def compute_roc_for_predictor(predictor_values, incidents, lookahead=10):
    """Build ROC curve for predictor."""
    y_true = []
    y_score = []

    for t in range(len(predictor_values) - lookahead):
        # Label: incident in next lookahead steps?
        incident_soon = any(inc['step'] in range(t+1, t+lookahead+1)
                           for inc in incidents)
        y_true.append(1 if incident_soon else 0)

        # Score: predictor value at t
        y_score.append(predictor_values[t])

    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)

    return fpr, tpr, roc_auc, thresholds

def compare_aucs_statistically(auc1, auc2, y_true, y_score1, y_score2):
    """DeLong test for comparing two AUCs."""
    from scipy.stats import mannwhitneyu
    # Simplified: use bootstrap
    # TODO: Implement proper DeLong test
    pass
```

### 7.2 Confusions to Resolve

**CRITICAL**:
- **CONFUSION #4**: Incident probability function (defines ground truth!)

**Important**:
- **CONFUSION #7**: Time units (affects "10 steps" prediction)

**Nice to have**:
- **CONFUSION #6**: Optimal threshold for E_local warning

---

## 8. Failure Modes and Contingencies

### Failure Mode 1: No incidents occur

**Symptoms**: 0 incidents in all runs

**Diagnosis**:
- Incident probability too low
- System too stable (shock not strong enough)
- Actors too good at preventing problems

**Fix**:
1. Increase incident probability (steeper sigmoid)
2. Stronger shock (Δdemand = -0.6 instead of -0.4)
3. Remove one RefactorEngineer (less mitigation)

### Failure Mode 2: Too many incidents (noise)

**Symptoms**: Incidents every few steps, no clear pattern

**Diagnosis**:
- Incident probability too high
- System too chaotic
- Can't distinguish signal from noise

**Fix**:
1. Decrease incident probability
2. Add RefactorEngineer
3. Longer lookahead window (N=20 instead of 10)

### Failure Mode 3: All predictors equally bad (AUC ≈ 0.5)

**Symptoms**: No predictor does better than random

**Diagnosis**:
- Incidents are truly random (no structural causes)
- Lookahead window wrong
- Labels mislabeled

**Fix**:
1. Check incident definition (is it actually related to badness?)
2. Vary lookahead (try N=5, 10, 15, 20)
3. Debug labeling logic

### Failure Mode 4: Scalar metrics win

**Symptoms**: AUC(health) > AUC(E_local)

**Diagnosis**:
- Laplacian doesn't add value
- E_local threshold wrong
- Hub node isn't actually stressed

**Implications**: **Theory may be wrong**. Consider:
1. Normalized Laplacian instead of combinatorial
2. Different badness formula
3. Alternative model (ecology, CAS) from `06-future-directions.md`

---

## 9. Expected Outcomes

**If model is correct** (based on theory):

**Competitor shock timeline**:
- t=20: Shock applied, demand shifts
- t=22-25: E_local[A_core] rises (hub stressed by new coupling)
- t=26-28: health[A_core] starts dropping (incidents brewing)
- t=30-35: First incidents manifest

**Lead times**:
- E_local warning: ~8-12 steps before incident
- health drop: ~2-5 steps before incident
- **Difference**: ~5-8 steps (E_local earlier)

**AUC scores**:
- E_local[A_core]: 0.75-0.80
- health[A_core]: 0.60-0.65
- complexity[A_core]: 0.55-0.60

**Interpretation**: Laplacian-based metrics provide **meaningful** early warning.

---

## 10. Timeline

**Estimated effort**: 2-3 weeks (including Exp01)

**Breakdown**:
- Implement DemandShock, NewRequirement events: 1 day
- Implement competitor shock scenario: 1 day
- Run 30 Monte Carlo simulations: 1 day (or overnight)
- ROC analysis code: 2 days
- Lead time analysis: 1 day
- Visualization and writeup: 2 days
- Debugging/iteration: 3-5 days

**Deliverable**: ROC curves, lead time distributions, statistical tests, write-up.

**Decision point**: If PASS → We have validated the core framework. If FAIL → Deep debugging or theory revision.

---

## 11. References

- **MVP Scenarios**: `../simulation/mvp-scenarios.md` (Scenario 2: Competitor Shock)
- **Future Directions**: `../06-future-directions.md` (Experiment 2 in critical experiments)
- **Confusions**: `confusions.md` (#4 is critical)

---

**This is the experiment that matters most.** Everything else is setup or followup.

If E_local predicts incidents earlier than scalar metrics, **we have something real**.

If not, we're just collecting stamps.
