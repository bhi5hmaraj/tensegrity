# Theoretical Foundations: The Geometry of Mental Models

## Overview

**Purpose:** Develop the foundational mathematical structures underlying all mental models.

**Philosophy:** Before we can compare models, we must understand: *What is a model?*

Not as a scoring function, but as a **mathematical object** - with state spaces, dynamics, observables, symmetries, and transformations.

**Analogy:**
- Physics → Symplectic manifolds (Hamiltonian mechanics)
- Quantum mechanics → Hilbert spaces (states, operators, observables)
- General relativity → Lorentzian manifolds (spacetime geometry)
- **Mental models → ?**

This document constructs that "?"

**Cross-references:**
- Provides theoretical foundation for `01-evaluation-dimensions.md`
- Formalizes model composition from `04-model-comparison.md`
- Underpins mathematical framework in `06-mathematical-framework.md`
- Connects to `../02-model-catalog.md` (specific instantiations)

---

## Part I: What is a Model?

### Definition 1.1: Model as Dynamical System

A **mental model** $M$ is a tuple:

$$M = (\mathcal{X}, \mathcal{O}, \Phi, \mu)$$

where:
- $\mathcal{X}$ : **State space** (configuration manifold)
- $\mathcal{O}$ : **Observable algebra** (what we can measure)
- $\Phi : \mathcal{X} \times \mathbb{R}_+ \to \mathcal{X}$ : **Flow** (dynamics)
- $\mu : \mathcal{O} \times \mathcal{X} \to \mathbb{R}$ : **Measurement map**

**Interpretation:**
- $\mathcal{X}$ = "states the system can be in"
- $\mathcal{O}$ = "things we can observe"
- $\Phi_t(x)$ = "state at time $t$ if started at $x$"
- $\mu(o, x)$ = "value of observable $o$ at state $x$"

### Example 1.1: Physics Model

**State space:**
$$\mathcal{X}_{\text{physics}} = \{(\mathbf{q}, \mathbf{p}) : \mathbf{q} \in \mathbb{R}^n, \mathbf{p} \in \mathbb{R}^n\}$$

where $\mathbf{q}$ = module properties (health, complexity), $\mathbf{p}$ = change rates

**Observable algebra:**
$$\mathcal{O}_{\text{physics}} = \{V_{\text{struct}}, T, H, E_{\text{local}}, \ldots\}$$

**Flow:** Hamiltonian dynamics
$$\Phi_t(\mathbf{q}, \mathbf{p}) = \exp(t \{H, \cdot\})(\mathbf{q}, \mathbf{p})$$

where $\{H, \cdot\}$ is Poisson bracket

**Measurement:**
$$\mu(V_{\text{struct}}, (\mathbf{q}, \mathbf{p})) = \frac{1}{2} \mathbf{q}^T L \mathbf{q}$$

### Example 1.2: Economics Model

**State space:**
$$\mathcal{X}_{\text{econ}} = \Delta^n \times \mathbb{R}^n_+$$

where:
- $\Delta^n$ = simplex (budget allocation: $\sum b_i = 1, b_i \geq 0$)
- $\mathbb{R}^n_+$ = prices (non-negative)

**Observable algebra:**
$$\mathcal{O}_{\text{econ}} = \{\text{Utility}, \text{Supply}, \text{Demand}, \text{ROI}, \ldots\}$$

**Flow:** Market dynamics (tatonnement process)
$$\dot{p}_i = \alpha (\text{Demand}_i - \text{Supply}_i)$$

**Measurement:**
$$\mu(\text{Utility}, (\mathbf{b}, \mathbf{p})) = \sum_i u_i(b_i)$$

### Remark 1.1: State Space Geometry

Different models have different geometric structures:
- **Physics:** $\mathcal{X}$ is symplectic manifold (has natural Poisson bracket)
- **Economics:** $\mathcal{X}$ is product of simplex and cone (constrained optimization)
- **Ecology:** $\mathcal{X} = \mathbb{R}^n_+$ (populations non-negative, Lotka-Volterra)
- **Cognitive:** $\mathcal{X} = \mathcal{G} \times [0, 1]^k$ (graph $\times$ understanding levels)

---

## Part II: The Space of Models

### Definition 2.1: Model Space

Let $\mathfrak{M}$ be the **space of all models**.

**Question:** What structure does $\mathfrak{M}$ have?

**Answer:** $\mathfrak{M}$ is a **category** where:
- Objects = Models $M = (\mathcal{X}, \mathcal{O}, \Phi, \mu)$
- Morphisms = Model transformations

### Definition 2.2: Model Morphism

A **morphism** $\phi: M_1 \to M_2$ is a triple $(\phi_X, \phi_O, \phi_\Phi)$ such that:

1. **State map:** $\phi_X : \mathcal{X}_1 \to \mathcal{X}_2$
2. **Observable pullback:** $\phi_O : \mathcal{O}_2 \to \mathcal{O}_1$
3. **Dynamics compatibility:**
   $$\phi_X \circ \Phi_1^t = \Phi_2^t \circ \phi_X$$

**Interpretation:**
- $\phi_X$ translates states from model 1 to model 2
- $\phi_O$ translates observables backwards (pullback)
- Compatibility: Dynamics commute with translation

### Example 2.1: Physics → Economics Translation

**State map:** $\phi_X : (\mathbf{q}, \mathbf{p}) \mapsto (\mathbf{b}, \mathbf{p}')$

where:
$$b_i = \frac{\text{Quality}(q_i)}{\sum_j \text{Quality}(q_j)}$$

(Convert module quality to budget allocation)

**Observable pullback:** $\phi_O(\text{ROI}) = \frac{V_{\text{business}}}{V_{\text{struct}}}$

(ROI in economics corresponds to business/structural tension ratio in physics)

**Compatibility check:**
Does budget allocation evolve consistently when projected from physics?

$$\frac{d}{dt}(b_i \circ \phi_X) = \phi_X \left(\frac{\partial H}{\partial p_i}\right)$$

### Proposition 2.1: Model Category Structure

$\mathfrak{M}$ forms a category with:

**Composition:** If $\phi: M_1 \to M_2$ and $\psi: M_2 \to M_3$, then:
$$(\psi \circ \phi)_X = \psi_X \circ \phi_X$$
$$(\psi \circ \phi)_O = \phi_O \circ \psi_O$$

**Identity:** $\text{id}_M = (\text{id}_\mathcal{X}, \text{id}_\mathcal{O}, \text{id})$

**This is NOT a trivial category** - not all models are comparable!

---

## Part III: Observables and Measurements

### Definition 3.1: Observable Algebra

For model $M$, the **observable algebra** $\mathcal{O}$ is a commutative $\mathbb{R}$-algebra:

$$\mathcal{O} = \{\text{functions } \mathcal{X} \to \mathbb{R}\}$$

with operations:
- Addition: $(f + g)(x) = f(x) + g(x)$
- Multiplication: $(f \cdot g)(x) = f(x) \cdot g(x)$
- Scalar: $(\lambda f)(x) = \lambda f(x)$

### Example 3.1: Physics Observable Algebra

Generators:
$$\mathcal{O}_{\text{physics}} = \langle q_i, p_i, V_{\text{struct}}, T, H \rangle$$

Relations:
- $H = T + V_{\text{struct}}$ (Hamiltonian is sum of kinetic + potential)
- $V_{\text{struct}} = \frac{1}{2} \sum_{ij} L_{ij} q_i q_j$ (quadratic in state)
- $T = \frac{1}{2} \sum_i p_i^2 / m_i$ (kinetic energy)

**This algebra is closed under Poisson bracket:**
$$\{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)$$

### Definition 3.2: Observability

An observable $o \in \mathcal{O}$ is **measurable** if there exists a procedure to compute $\mu(o, x)$ from empirical data.

**Measurability degree:**
$$\kappa(o) = \frac{1}{1 + \sigma^2(\mu(o, \cdot))}$$

where $\sigma^2$ is measurement noise variance.

**This connects to Dimension 5 (Measurability) from evaluation framework.**

---

## Part IV: Dynamics and Evolution

### Definition 4.1: Flow and Generator

The **flow** $\Phi_t : \mathcal{X} \to \mathcal{X}$ has infinitesimal generator:

$$\mathcal{L} = \lim_{t \to 0} \frac{\Phi_t - \text{id}}{t}$$

**Physics:** $\mathcal{L} = \{H, \cdot\}$ (Hamiltonian vector field)

**Economics:** $\mathcal{L} = \nabla U$ (gradient flow on utility landscape)

**Ecology:** $\mathcal{L} = \text{diag}(\mathbf{N}) (r - \alpha \mathbf{N})$ (Lotka-Volterra)

### Definition 4.2: Stationary Points

A state $x^* \in \mathcal{X}$ is **stationary** if:

$$\mathcal{L} x^* = 0$$

**Interpretation:** System doesn't evolve if started at $x^*$.

### Example 4.1: Physics Equilibria

Hamiltonian dynamics: $x^*$ is stationary if $\nabla H(x^*) = 0$

These are:
- Minima of $H$ → stable equilibria
- Maxima of $H$ → unstable equilibria
- Saddle points → critical transitions

### Proposition 4.1: Conservation Laws (Noether's Theorem Analog)

If flow $\Phi_t$ has continuous symmetry generated by $X$, then there exists a conserved quantity $C$ such that:

$$\frac{d}{dt} C(\Phi_t(x)) = 0$$

**Example (Physics):**
- **Time translation symmetry** → Energy conservation ($H$ constant)
- **Gauge symmetry** (reparameterization) → Coupling structure conserved

**Example (Economics):**
- **Budget conservation:** $\sum b_i = 1$ always
- **Walras' law:** $\sum p_i (\text{Demand}_i - \text{Supply}_i) = 0$

---

## Part V: Multi-Model Integration

### Definition 5.1: Fiber Bundle Structure

The **multi-model space** is a fiber bundle:

$$\pi: \mathcal{E} \to \mathcal{B}$$

where:
- $\mathcal{B}$ = base space (problem contexts)
- $\mathcal{E}$ = total space (models $\times$ contexts)
- Fiber $\pi^{-1}(c)$ = all models applicable to context $c$

**Interpretation:** Over each problem context, there's a space of applicable models.

### Definition 5.2: Model Composition (Monoidal Structure)

Two models $M_1, M_2$ can be **composed** via tensor product:

$$M_1 \otimes M_2 = (\mathcal{X}_1 \times \mathcal{X}_2, \mathcal{O}_1 \otimes \mathcal{O}_2, \Phi_1 \times \Phi_2, \mu_1 \otimes \mu_2)$$

**This is the mathematical foundation for multi-model integration.**

### Example 5.1: Physics $\otimes$ Economics

**State space:** $\mathcal{X}_{\text{phys}} \times \mathcal{X}_{\text{econ}}$
- Physics tracks: $(q_i, p_i)$ (module states, velocities)
- Economics tracks: $(b_i, p_i')$ (budgets, prices)

**Coupling:** Parameters of one model feed into the other

$$\text{Budget allocation } b_i = f(V_{\text{struct}, i})$$
$$\text{Refactor rate } \dot{q}_i = g(\text{ROI}_i)$$

**Observable algebra:**
$$\mathcal{O}_{\text{total}} = \mathcal{O}_{\text{phys}} \otimes \mathcal{O}_{\text{econ}}$$

Contains products like: $V_{\text{struct}} \times \text{Utility}$

### Definition 5.3: Hierarchical Composition (Pushforward)

Model $M_{\text{inner}}$ can be **pushed forward** to $M_{\text{outer}}$ via:

$$\pi_* : M_{\text{inner}} \to M_{\text{outer}}$$

**State space:** $\mathcal{X}_{\text{outer}} = \mathcal{X}_{\text{inner}} / \sim$

(Quotient by equivalence relation - coarse-graining)

**Dynamics:** Induced flow on quotient space

$$\Phi_{\text{outer}}^t = \pi \circ \Phi_{\text{inner}}^t \circ \pi^{-1}$$

### Example 5.2: Physics $\to$ System Dynamics (Coarse-Graining)

**Quotient:** Average over fast variables

$$\bar{q} = \langle q_i \rangle_{\text{modules in subsystem}}$$

**Induced dynamics:** Averaged Hamiltonian

$$\bar{H} = \langle H \rangle = \bar{T} + \bar{V}$$

**This is how System Dynamics emerges from Physics at larger scales.**

---

## Part VI: Symmetries and Invariants

### Definition 6.1: Symmetry Group

A **symmetry** of model $M$ is a transformation $g: \mathcal{X} \to \mathcal{X}$ such that:

1. $g$ preserves dynamics: $g \circ \Phi_t = \Phi_t \circ g$
2. $g$ preserves observables: $\mu(o, g(x)) = \mu(o, x)$

The set of all symmetries forms a group $G_M$.

### Example 6.1: Physics Symmetries

**Permutation symmetry:** If modules are interchangeable:

$$g: (q_1, q_2, \ldots) \mapsto (q_{\sigma(1)}, q_{\sigma(2)}, \ldots)$$

Then $V_{\text{struct}}$ must be symmetric:

$$V_{\text{struct}}(g(x)) = V_{\text{struct}}(x)$$

**Scaling symmetry:** If $V_{\text{struct}}$ is homogeneous:

$$V_{\text{struct}}(\lambda \mathbf{q}) = \lambda^2 V_{\text{struct}}(\mathbf{q})$$

### Theorem 6.1: Noether's Theorem for Models

If $M$ has continuous symmetry generated by vector field $X$, then there exists a conserved quantity $C$ such that:

$$\mathcal{L}_X C = 0$$

where $\mathcal{L}_X$ is Lie derivative along $X$.

**Proof sketch:**
- Symmetry ⇒ $\mathcal{L}_X H = 0$
- Flow preserves $H$ ⇒ $C = H$ is conserved along trajectories

**Application:** Identify hidden conservation laws in models!

---

## Part VII: Information Geometry

### Definition 7.1: Statistical Manifold

The space of probability distributions $\mathcal{P}(\mathcal{X})$ has natural Riemannian structure:

**Fisher information metric:**
$$g_{ij}(\theta) = \mathbb{E}\left[\frac{\partial \log p(x|\theta)}{\partial \theta_i} \frac{\partial \log p(x|\theta)}{\partial \theta_j}\right]$$

**This measures distinguishability of nearby distributions.**

### Definition 7.2: Model Divergence

Distance between models $M_1, M_2$ is given by **KL divergence** between their predictions:

$$D_{\text{KL}}(M_1 \| M_2) = \int p_1(x) \log \frac{p_1(x)}{p_2(x)} dx$$

where $p_i$ is probability distribution over outcomes predicted by model $i$.

### Proposition 7.1: Information Projection

Given models $M_1, \ldots, M_k$, the **optimal ensemble** is:

$$M^* = \arg\min_{M \in \text{span}(M_1, \ldots, M_k)} D_{\text{KL}}(M_{\text{true}} \| M)$$

This is an **information-geometric projection**.

**Connection to `06-mathematical-framework.md`: Ensemble optimal weights**

$$\mathbf{w}^* = \frac{\mathbf{\Sigma}^{-1} \mathbf{1}}{\mathbf{1}^T \mathbf{\Sigma}^{-1} \mathbf{1}}$$

is the projection in Fisher metric!

---

## Part VIII: Functorial Semantics

### Definition 8.1: Model Functor

A **model functor** $F: \mathfrak{C} \to \mathfrak{M}$ maps:
- Objects: Problem contexts $c \in \mathfrak{C}$
- Morphisms: Context changes $f: c_1 \to c_2$

to:
- Objects: Models $F(c) \in \mathfrak{M}$
- Morphisms: Model transformations $F(f): F(c_1) \to F(c_2)$

**Interpretation:** Functor picks "best model" for each context, consistently.

### Example 8.1: Context-Dependent Model Selection

**Context category $\mathfrak{C}$:**
- Objects: $\{\text{small-scale}, \text{medium-scale}, \text{large-scale}\}$
- Morphisms: Inclusions $\text{small} \hookrightarrow \text{medium} \hookrightarrow \text{large}$

**Model functor $F$:**
- $F(\text{small}) = \text{Physics}$ (detailed structural analysis)
- $F(\text{medium}) = \text{Physics} \otimes \text{Economics}$
- $F(\text{large}) = \text{Economics}$ (market coordination)

**Morphisms:** Coarse-graining maps (pushforward from definition 5.3)

### Theorem 8.1: Natural Transformations as Model Equivalences

If $F, G: \mathfrak{C} \to \mathfrak{M}$ are two model functors, a **natural transformation** $\eta: F \Rightarrow G$ assigns to each context $c$ a model morphism:

$$\eta_c : F(c) \to G(c)$$

such that for all $f: c_1 \to c_2$:

$$G(f) \circ \eta_{c_1} = \eta_{c_2} \circ F(f)$$

**Interpretation:** Two model selection strategies are "naturally equivalent" if they can be consistently translated.

---

## Part IX: Variational Principles

### Definition 9.1: Action Functional

For model $M$, define **action**:

$$S[x(\cdot)] = \int_0^T L(x(t), \dot{x}(t), t) dt$$

where $L$ is Lagrangian.

**Principle of stationary action:** Actual trajectories satisfy:

$$\delta S = 0$$

### Example 9.1: Physics Model

**Lagrangian:** $L = T - V_{\text{struct}}$

$$S[\mathbf{q}(\cdot), \mathbf{p}(\cdot)] = \int_0^T \left[\sum_i p_i \dot{q}_i - H(\mathbf{q}, \mathbf{p})\right] dt$$

**Euler-Lagrange equations:**
$$\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} = \frac{\partial L}{\partial q_i}$$

These are Hamilton's equations!

### Example 9.2: Economics Model

**Lagrangian:** $L = U(\mathbf{b}) - \lambda (\sum b_i - 1)$

(Utility minus budget constraint)

**Variational principle:** Maximize utility subject to constraints

$$\delta \int U(\mathbf{b}(t)) dt = 0$$

### Theorem 9.1: Least Action ⇒ Conservation Laws

If Lagrangian $L$ has symmetry (invariance under transformation $x \mapsto x + \epsilon \xi$), then:

$$C = \frac{\partial L}{\partial \dot{x}} \cdot \xi$$

is conserved along solutions.

**This unifies conservation laws across all models!**

---

## Part X: Towards a Universal Language

### Definition 10.1: Model Signature

Every model $M$ has a **signature** $\Sigma_M$ consisting of:

$$\Sigma_M = (\mathcal{X}, \mathcal{O}, \mathcal{L}, G_M, \{C_i\})$$

where:
- $\mathcal{X}$ = state space (manifold)
- $\mathcal{O}$ = observable algebra
- $\mathcal{L}$ = dynamics generator
- $G_M$ = symmetry group
- $\{C_i\}$ = conserved quantities

**This is the "DNA" of a model.**

### Example 10.1: Model Signatures

**Physics:**
$$\Sigma_{\text{phys}} = (\mathbb{R}^{2n}, \langle q, p, H \rangle, \{H, \cdot\}, \text{Sp}(2n), \{H\})$$

- Symplectic manifold
- Hamiltonian algebra
- Poisson bracket dynamics
- Symplectic group
- Energy conserved

**Economics:**
$$\Sigma_{\text{econ}} = (\Delta^n \times \mathbb{R}^n_+, \langle U, \text{ROI} \rangle, \nabla U, S_n, \{\sum b_i\})$$

- Simplex $\times$ cone
- Utility algebra
- Gradient flow
- Permutation group
- Budget conserved

### Theorem 10.1: Model Comparison via Signature Distance

Define **signature distance**:

$$d(\Sigma_1, \Sigma_2) = d_{\text{Hausdorff}}(\mathcal{X}_1, \mathcal{X}_2) + d_{\text{algebra}}(\mathcal{O}_1, \mathcal{O}_2) + d_{\text{generator}}(\mathcal{L}_1, \mathcal{L}_2)$$

Models are "similar" if $d(\Sigma_1, \Sigma_2)$ is small.

**This provides geometric intuition for model space $\mathfrak{M}$!**

---

## Part XI: Effective Field Theory Perspective

### Definition 11.1: Scale Hierarchy

Models exist at different **scales**:

$$\text{Microscopic} \xrightarrow{\text{coarse-grain}} \text{Mesoscopic} \xrightarrow{\text{coarse-grain}} \text{Macroscopic}$$

**Example:**
- Microscopic: Individual functions/classes (too detailed)
- Mesoscopic: Modules (Physics model lives here)
- Macroscopic: Business outcomes (System Dynamics lives here)

### Definition 11.2: Effective Action

At scale $\Lambda$, the **effective model** $M_{\text{eff}}^\Lambda$ has action:

$$S_{\text{eff}}^\Lambda = S_{\text{micro}} + \text{corrections from integrated-out degrees of freedom}$$

**Renormalization group flow:** How models change as we zoom out.

### Example 11.1: Physics → System Dynamics

**Microscopic:** Physics model with $n = 100$ modules

**Coarse-grain:** Group into $k = 5$ subsystems

**Effective model:** System Dynamics on 5 stocks

$$S_{\text{eff}} = \int \left[\sum_{i=1}^5 \text{Stock}_i \cdot \text{Flow}_i\right] dt$$

with effective parameters (emergent from physics):
- Flow rates = averaged change rates
- Coupling = inter-subsystem dependencies

### Theorem 11.1: Renormalization Group Fixed Points

Under coarse-graining transformation $\mathcal{R}_\Lambda : M_\Lambda \to M_{\Lambda'}$ ($\Lambda' < \Lambda$), a model $M^*$ is a **fixed point** if:

$$\mathcal{R}_\Lambda(M^*) = M^*$$

**Interpretation:** Model structure is scale-invariant (self-similar).

**Example:** Power law models (CAS) are often near fixed points.

---

## Part XII: Synthesis and Open Problems

### Theorem 12.1: Universal Model Theorem (Conjectured)

There exists a **universal model** $\mathcal{U}$ such that any model $M$ can be embedded:

$$\iota_M : M \hookrightarrow \mathcal{U}$$

with $\mathcal{U}$ having the structure of an **∞-category** (higher category theory).

**Status:** Open conjecture. If true, provides ultimate unification.

### Open Problem 12.1: Model Cohomology

Define **cohomology groups** $H^k(\mathfrak{M})$ of model space.

**Question:** What do these measure?
- $H^0$ = disconnected components (fundamentally different model types?)
- $H^1$ = "holes" in model space (missing intermediate models?)
- $H^2$ = obstructions to model composition?

### Open Problem 12.2: Quantum Models

Can we define **quantum mental models** where:

$$\mathcal{X} \rightsquigarrow \mathcal{H} \text{ (Hilbert space)}$$
$$\mathcal{O} \rightsquigarrow \mathcal{A} \text{ (operator algebra, non-commutative!)}$$

**Interpretation:** Observables don't commute (Heisenberg uncertainty for models?)

Example: Measuring "coupling" changes "complexity" (complementarity)

### Open Problem 12.3: Model Machine Learning

Can we **learn** the optimal model $M^*$ for a given context via:

$$M^* = \arg\min_{M \in \mathfrak{M}} \mathbb{E}[\ell(M, \text{data})]$$

where $\ell$ is loss functional on model space?

This is **meta-learning on the space of models**.

---

## Summary: The Mathematical Architecture

**We've constructed:**

1. **Definition of model** as tuple $(\mathcal{X}, \mathcal{O}, \Phi, \mu)$
2. **Model space** $\mathfrak{M}$ as category with morphisms
3. **Observable algebras** with Poisson/commutative structure
4. **Dynamical flows** with generators and conservation laws
5. **Composition operations** (monoidal, hierarchical)
6. **Symmetries and invariants** (Noether's theorem)
7. **Information geometry** (Fisher metric, KL divergence)
8. **Functorial semantics** (context $\to$ model selection)
9. **Variational principles** (action functionals)
10. **Model signatures** (geometric characterization)
11. **Effective field theory** (renormalization, scale hierarchy)
12. **Open problems** (cohomology, quantum, learning)

**This provides:**
- **Vocabulary:** States, observables, flows, morphisms
- **Grammar:** How to compose, transform, compare models
- **Theorems:** Conservation laws, Noether, information projection
- **Geometry:** Manifolds, symmetries, fiber bundles
- **Unification:** All models as instances of $(\mathcal{X}, \mathcal{O}, \Phi, \mu)$

**The framework is:**
- **Rigorous:** Definitions, theorems, proofs
- **General:** Subsumes all specific models (Physics, Economics, etc.)
- **Practical:** Connects to evaluation framework (dimensions = observables)
- **Deep:** Uses advanced mathematics (categories, differential geometry, information theory)

**Cross-references:**
- `../02-model-catalog.md`: Specific models are *instances* of framework
- `01-evaluation-dimensions.md`: Dimensions are *observables* on model space
- `06-mathematical-framework.md`: Statistical methods are *induced* from geometry
- `../business/`: Hierarchical composition applied to business+software

**Next:** Use this foundation to:
1. Derive evaluation dimensions from first principles
2. Prove theorems about optimal model selection
3. Construct new models via symmetry principles
4. Develop model learning algorithms

---

*"The miracle of the appropriateness of the language of mathematics for the formulation of the laws of physics is a wonderful gift which we neither understand nor deserve."* — Eugene Wigner

**We seek the same miracle for mental models.**
