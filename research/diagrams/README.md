# Diagrams

This directory contains GraphViz diagrams explaining the software tensegrity framework and simulation design.

## Generating SVGs

The diagrams are stored as `.dot` (GraphViz) source files. To generate SVG images:

```bash
# Run the generation script
./generate-diagrams.sh
```

This requires graphviz to be installed:
- **macOS**: `brew install graphviz`
- **Ubuntu/Debian**: `sudo apt-get install graphviz`
- **Fedora**: `sudo dnf install graphviz`

## Diagram Catalog

### Architecture and Relationships

**`overall-architecture.dot`** / `overall-architecture.svg`
- Shows relationship between PadAI (Layer 1: Coordination), Tensegrity (Layer 2: Governance), and Software Physics Research (theoretical foundation)
- Illustrates how the three layers connect: research → governance metrics → coordination infrastructure
- Referenced in: `../simulation/README.md`, `../../docs/design/vision_architecture.md`

**`five-forces-equilibrium.dot`** / `five-forces-equilibrium.svg`
- Visualizes the five forces (Velocity, Quality, Coherence, Learning, Scope) in equilibrium
- Shows common imbalance scenarios (Cowboy mode, Bureaucracy, Drift, Mystery codebase, Scope sprawl)
- Demonstrates how Tensegrity governance detects and corrects imbalances
- Referenced in: `../../docs/design/vision_architecture.md`, `../01-motivation-and-core-insight.md`

**`knowledge-representation-gap.dot`** / `knowledge-representation-gap.svg`
- Illustrates divergence over time between ground truth (codebase), AI mental model, and human mental model
- Shows why active learning primitives are necessary to maintain governance capacity
- Referenced in: `../../docs/design/vision_architecture.md`, `../01-motivation-and-core-insight.md`

### Mathematical Foundations

**`graph-laplacian-energy.dot`** / `graph-laplacian-energy.svg`
- Concrete example of 4-node graph with badness values
- Shows computation flow: Graph → Laplacian (L = D - A) → Dirichlet energy
- Visualizes per-edge tension contributions and local energy decomposition
- Referenced in: `../02-mathematical-foundations.md`, `../03-software-as-physics-mapping.md`

**`phase-space-regimes.dot`** / `phase-space-regimes.svg`
- 2×2 phase space showing T (kinetic) vs V (potential) quadrants
- Four regimes: Healthy Flow, Chaotic Thrash, Stable Equilibrium, Frozen Bureaucracy
- Governance interventions for each quadrant
- Common trajectories and real-world examples
- Referenced in: `../03-software-as-physics-mapping.md`, `../simulation/mvp-scenarios.md`

### Simulation Design

**`simulation-loop.dot`** / `simulation-loop.svg`
- Flowchart of discrete-time simulation loop
- Six steps per iteration: scheduled events → actor actions → update derived fields → compute physics → apply governance → log
- Referenced in: `../simulation/mvp-simulation-design.md`, `../simulation/mvp-implementation.md`

**`actor-decision-flow.dot`** / `actor-decision-flow.svg`
- Decision-making process for three actor types: FeatureEngineer, RefactorEngineer, AIAgent
- Shows how actors observe state, apply strategy, and choose actions constrained by governance
- Detailed breakdown of FeatureEngineer and RefactorEngineer decision trees
- Referenced in: `../simulation/mvp-simulation-design.md`

## Usage in Markdown

To embed diagrams in documentation:

```markdown
![Diagram Title](diagrams/filename.svg)
```

Or with relative paths from different locations:

```markdown
# From research/*.md files
![Diagram](diagrams/filename.svg)

# From research/simulation/*.md files
![Diagram](../diagrams/filename.svg)

# From docs/design/*.md files
![Diagram](../../research/diagrams/filename.svg)
```

## Editing Diagrams

The `.dot` files use GraphViz DOT language. To edit:

1. Open the `.dot` file in any text editor
2. Modify the graph structure, labels, or styling
3. Run `./generate-diagrams.sh` to regenerate SVGs
4. View the SVG in a browser or image viewer

### Useful Resources

- [GraphViz Documentation](https://graphviz.org/documentation/)
- [DOT Language Quick Reference](https://graphviz.org/doc/info/lang.html)
- [Node, Edge, and Graph Attributes](https://graphviz.org/doc/info/attrs.html)

## Design Principles

All diagrams follow these principles:

1. **Clarity over complexity**: Diagrams should illuminate, not obscure
2. **Consistent terminology**: Use the same terms as the written docs
3. **Color coding**: Use colors meaningfully (green = healthy, red = problem, blue = structure)
4. **Self-contained**: Each diagram should be understandable on its own with labels and legends
5. **Complementary to text**: Diagrams illustrate concepts explained in prose

## Maintenance

When adding new diagrams:

1. Create `.dot` file in this directory
2. Follow naming convention: `kebab-case-description.dot`
3. Add entry to this README under appropriate section
4. Reference from relevant markdown files
5. Run `./generate-diagrams.sh` to generate SVG
6. Commit both `.dot` and `.svg` files (so diagrams work on GitHub)
