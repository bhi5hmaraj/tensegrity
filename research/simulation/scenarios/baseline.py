"""
Baseline scenario for Experiment 01.

See research/experiments/exp01-baseline-validation.md for full specification.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulation.core import TensegrityGraph, SimulationState
from simulation.actors import FeatureEngineer, RefactorEngineer, AIAgent
from simulation.simulation import run_simulation, SimulationConfig


def create_baseline_scenario():
    """
    Create initial state for baseline experiment.

    Returns:
        dict with 'state' and 'actors' keys
    """

    # 1. Create graph topology
    nodes = ['A_core', 'B_api', 'C_db', 'D_featureX', 'E_featureY', 'F_util']

    edges = [
        ('A_core', 'B_api', 0.9),      # Tight coupling
        ('A_core', 'C_db', 0.7),
        ('A_core', 'F_util', 0.4),
        ('B_api', 'D_featureX', 0.6),
        ('B_api', 'E_featureY', 0.5),
        ('C_db', 'D_featureX', 0.3),
    ]

    graph = TensegrityGraph(nodes, edges)

    # 2. Initialize fields
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

    demand = {
        'A_core': 0.4,
        'B_api': 0.5,
        'C_db': 0.3,
        'D_featureX': 0.7,  # Popular feature
        'E_featureY': 0.5,
        'F_util': 0.2,
    }

    # 3. Create simulation state
    state = SimulationState(
        graph=graph,
        health=health,
        complexity=complexity,
        demand=demand
    )

    # 4. Create actors
    actors = [
        FeatureEngineer(name='Alice', business_weight=0.8, stability_weight=0.2),
        RefactorEngineer(name='Bob', business_weight=0.2, stability_weight=0.8),
        AIAgent(name='Agent-1', feature_bias=0.6),
    ]

    return {
        'state': state,
        'actors': actors,
    }


def run_baseline_experiment(n_steps: int = 100, random_seed: int = 42):
    """
    Run baseline validation experiment (Exp01).

    Args:
        n_steps: Number of simulation steps
        random_seed: Random seed for reproducibility

    Returns:
        SimulationHistory with results
    """
    # Create scenario
    scenario = create_baseline_scenario()

    # Configure simulation
    config = SimulationConfig(
        n_steps=n_steps,
        random_seed=random_seed,
        health_decay_rate=0.01,
        enable_health_decay=True,
        enable_incidents=True,
        incident_threshold=0.6,
        incident_steepness=10.0,
        incident_max_prob=0.05,
        log_interval=1,
    )

    # Run simulation
    print(f"Running baseline experiment for {n_steps} steps...")
    print(f"Actors: {[str(a) for a in scenario['actors']]}")
    print(f"Nodes: {list(scenario['state'].graph.G.nodes)}")
    print(f"Edges: {scenario['state'].graph.edge_count()}")
    print()

    history = run_simulation(
        state=scenario['state'],
        actors=scenario['actors'],
        config=config
    )

    print(f"Simulation complete!")
    print(f"Final H: {history.H[-1]:.3f}")
    print(f"Total incidents: {len(history.incidents)}")
    print(f"Total events: {len(history.events)}")
    print()

    return history


if __name__ == '__main__':
    """Run baseline experiment from command line."""

    import argparse

    parser = argparse.ArgumentParser(description='Run baseline validation experiment')
    parser.add_argument('--steps', type=int, default=100, help='Number of steps')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()

    history = run_baseline_experiment(n_steps=args.steps, random_seed=args.seed)

    # Print summary statistics
    print("Summary Statistics:")
    print(f"  Mean H: {sum(history.H) / len(history.H):.3f}")
    print(f"  Mean T: {sum(history.T) / len(history.T):.3f}")
    print(f"  Mean V: {sum(history.V) / len(history.V):.3f}")
    print(f"  Min H: {min(history.H):.3f}")
    print(f"  Max H: {max(history.H):.3f}")
