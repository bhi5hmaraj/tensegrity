# Experiments: Testing the Software Physics Framework

## Overview

This directory contains **experimental designs** for validating the software tensegrity framework.

**Status**: Design phase → Implementation starting

**Purpose**: Convert the simulation MVP into rigorous scientific experiments with:
- Testable hypotheses
- Measurement protocols
- Statistical analysis plans
- Success/failure criteria

---

## Philosophy: Theory → Experiment Loop

*[The experimentalist's discipline]*

We have **theory** (6 research docs, ~3200 lines of mathematics).
We have **simulation design** (5 MVP docs, ~2700 lines of implementation specs).

Now we need **experiments** that:
1. **Test specific hypotheses** (not just "does it work")
2. **Measure quantitatively** (p-values, AUC scores, confidence intervals)
3. **Fail gracefully** (know what to do if hypothesis is rejected)
4. **Clarify confusions** (formalization reveals hidden assumptions)

**The pact**: Every equation we write must face measurement. Every prediction must be tested.

---

## Experiments Catalog

### Experiment 01: Baseline Validation
**File**: `exp01-baseline-validation.md`

**Hypothesis**: The simulation reaches stable equilibrium (H oscillates around constant mean).

**Tests**:
- Statistical stationarity of H time series
- Absence of monotonic trends
- Energy conservation properties

**Purpose**: Sanity check - does the model behave reasonably?

---

### Experiment 02: Laplacian Early Warning
**File**: `exp02-laplacian-early-warning.md`

**Hypothesis**: Local Dirichlet energy E_local at hub nodes predicts incidents ~10 steps earlier than scalar metrics (health, complexity).

**Tests**:
- ROC curves: E_local vs. health vs. complexity as predictors
- Lead time analysis (time from spike to incident)
- Statistical significance (p < 0.05)

**Purpose**: **Core validation** - is Laplacian-based metric actually better?

---

### Experiment 03: Governance Effectiveness
**File**: `exp03-governance-effectiveness.md`

**Hypothesis**: Governed systems (H-threshold, E_local gates) recover from shocks faster with fewer incidents.

**Tests**:
- A/B comparison: governed vs ungoverned
- Metrics: H_peak, incident_count, recovery_time
- Effect size and significance

**Purpose**: Validate that governance rules **actually help**.

---

### Experiment 04: Phase Space Regimes
**File**: `exp04-phase-space-regimes.md`

**Hypothesis**: System states cluster into distinct (T, V) regimes with qualitatively different behaviors.

**Tests**:
- K-means clustering in (T, V) space
- Regime transition detection
- Behavioral differences (incident rate, field stability)

**Purpose**: Validate phase space as diagnostic tool.

---

### Experiment 05: Efficiency and Thermodynamics
**File**: `exp05-efficiency-thermodynamics.md`

**Hypothesis**: Development efficiency η is bounded by a Carnot-like limit based on quality "temperatures."

**Tests**:
- Measure η = Value / Effort across scenarios
- Test if η < η_Carnot = 1 - T_cold / T_hot
- Identify violators and explain

**Purpose**: Validate thermodynamic analogy.

---

## Confusions Document

**File**: `confusions.md`

**Purpose**: Running log of concepts that are **still nebulous** and need clarification.

When implementing experiments, we'll discover:
- Undefined parameters (what is "mass"?)
- Ambiguous formulas (how exactly to compute "risk"?)
- Missing links (how does flow field affect actor sampling?)
- Edge cases (what if Laplacian is singular?)

**This is where the real science happens.** Track confusions → resolve them → update theory.

---

## Experiment Design Template

Each experiment doc follows this structure:

```markdown
# Experiment N: Title

## 1. Hypothesis
[Specific, testable, falsifiable statement]

## 2. Starting State
[Precise initial conditions: graph, fields, actors]

## 3. Protocol
[What to measure, when, how]

## 4. Analysis Plan
[Statistical tests, metrics, visualizations]

## 5. Success Criteria
[Quantitative thresholds for accept/reject]

## 6. Implementation Notes
[Code to write, tests to add]

## 7. Failure Modes
[What if hypothesis is rejected? Next steps.]
```

---

## Relationship to MVP Docs

**MVP docs** (`simulation/mvp-*.md`):
- Define the **apparatus** (code structure, classes, methods)
- Specify **scenarios** (initial conditions, events)
- Provide **implementation guide** (phases, tech stack)

**Experiment docs** (`experiments/exp*.md`):
- Define **hypotheses** (what we're testing)
- Specify **measurements** (what to log, how to analyze)
- Provide **success criteria** (quantitative thresholds)
- Track **confusions** (what's still unclear)

**Think of it as**:
- MVP docs = Building the particle accelerator
- Experiment docs = Designing the collision experiments

---

## Implementation Status

| Experiment | Design | Code | Data | Analysis | Status |
|------------|--------|------|------|----------|--------|
| 01: Baseline | ✓ | ☐ | ☐ | ☐ | Design complete |
| 02: Early Warning | ✓ | ☐ | ☐ | ☐ | Design complete |
| 03: Governance | ✓ | ☐ | ☐ | ☐ | Design complete |
| 04: Phase Space | ⊙ | ☐ | ☐ | ☐ | In progress |
| 05: Efficiency | ⊙ | ☐ | ☐ | ☐ | In progress |

Legend: ✓ = Done, ⊙ = In progress, ☐ = Not started

---

## Next Steps

### Immediate (This session)
1. Create experiment design docs (exp01-exp05)
2. Create confusions.md
3. Review with user, iterate

### Next session
1. Implement Phase 1 of MVP (core infrastructure)
2. Run Experiment 01 (baseline validation)
3. Update confusions as issues arise

### Following sessions
1. Implement remaining experiments
2. Analyze results
3. Update theory based on findings

---

## The Experimentalist's Checklist

Before claiming "the theory works":

- [ ] All 5 experiments designed with testable hypotheses
- [ ] Statistical tests specified (not just eyeballing plots)
- [ ] Failure modes identified (what if we're wrong?)
- [ ] Confusions documented (what's still unclear?)
- [ ] Code implemented and tested
- [ ] Data collected and analyzed
- [ ] Results interpreted honestly
- [ ] Theory updated based on findings

**Science is not done until the last checkbox is marked.**

---

## References

- **Simulation MVP**: `../simulation/mvp-*.md` for implementation details
- **Theory docs**: `../01-06-*.md` for mathematical foundations
- **Vision**: `../../docs/design/vision_architecture.md` for product context

---

*"It doesn't matter how beautiful your theory is, it doesn't matter how smart you are. If it doesn't agree with experiment, it's wrong."* — Richard Feynman
