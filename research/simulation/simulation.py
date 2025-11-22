"""
Main simulation loop.

Coordinates actors, events, state updates, and logging.
"""

import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from .core import SimulationState
from .actors.base import Actor
from .events.base import Event
from .events.field_events import HealthDecay
from .core.energy import incident_probability


@dataclass
class SimulationConfig:
    """Configuration for simulation run."""

    n_steps: int = 100
    """Number of time steps to simulate"""

    random_seed: Optional[int] = 42
    """Random seed for reproducibility"""

    health_decay_rate: float = 0.01
    """Per-step health decay rate (entropy)"""

    enable_health_decay: bool = True
    """Whether to apply health decay each step"""

    enable_incidents: bool = True
    """Whether to trigger incidents based on badness"""

    incident_threshold: float = 0.6
    """Badness threshold for incident probability"""

    incident_steepness: float = 10.0
    """Steepness of incident probability sigmoid"""

    incident_max_prob: float = 0.05
    """Maximum incident probability per step"""

    log_interval: int = 1
    """How often to log state (every N steps)"""


@dataclass
class SimulationHistory:
    """
    Complete history of simulation run.

    Contains time series of all metrics.
    """

    # Time series of global metrics
    steps: List[int] = field(default_factory=list)
    H: List[float] = field(default_factory=list)
    T: List[float] = field(default_factory=list)
    V: List[float] = field(default_factory=list)
    V_struct: List[float] = field(default_factory=list)
    V_bus: List[float] = field(default_factory=list)
    L: List[float] = field(default_factory=list)

    # Event and incident logs
    events: List[Dict] = field(default_factory=list)
    incidents: List[Dict] = field(default_factory=list)

    # Per-node time series (dict[node_id, list])
    health: Dict[str, List[float]] = field(default_factory=dict)
    complexity: Dict[str, List[float]] = field(default_factory=dict)
    bad: Dict[str, List[float]] = field(default_factory=dict)
    E_local: Dict[str, List[float]] = field(default_factory=dict)

    def record_step(self, state: SimulationState):
        """
        Record current state to history.

        Args:
            state: Current simulation state
        """
        self.steps.append(state.time_step)
        self.H.append(state.H)
        self.T.append(state.T)
        self.V.append(state.V)
        self.V_struct.append(state.V_struct)
        self.V_bus.append(state.V_bus)
        self.L.append(state.L)

        # Per-node fields
        for node in state.graph.G.nodes:
            if node not in self.health:
                self.health[node] = []
                self.complexity[node] = []
                self.bad[node] = []
                self.E_local[node] = []

            self.health[node].append(state.health[node])
            self.complexity[node].append(state.complexity[node])
            self.bad[node].append(state.bad[node])
            self.E_local[node].append(state.E_local.get(node, 0.0))

    def record_event(self, step: int, actor: str, event: Event):
        """
        Record an event.

        Args:
            step: Time step
            actor: Actor name
            event: Event object
        """
        self.events.append({
            'step': step,
            'actor': actor,
            'event_type': event.__class__.__name__,
            'event_str': str(event),
        })

    def record_incident(self, incident_data: Dict):
        """
        Record an incident.

        Args:
            incident_data: Incident details dict
        """
        self.incidents.append(incident_data)


class Simulator:
    """
    Main simulation engine.

    Coordinates:
    - Actor decision-making
    - Event application
    - State updates
    - Incident triggering
    - History logging
    """

    def __init__(
        self,
        state: SimulationState,
        actors: List[Actor],
        config: Optional[SimulationConfig] = None
    ):
        """
        Initialize simulator.

        Args:
            state: Initial simulation state
            actors: List of actors to simulate
            config: Simulation configuration (uses defaults if None)
        """
        self.state = state
        self.actors = actors
        self.config = config or SimulationConfig()
        self.history = SimulationHistory()

        # Set random seed
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)

    def run(self) -> SimulationHistory:
        """
        Run simulation for configured number of steps.

        Returns:
            SimulationHistory with complete time series
        """
        # Initialize state
        self.state.update_derived_fields()
        self.state.update_energies()

        # Record initial state
        self.history.record_step(self.state)

        # Main simulation loop
        for step in range(self.config.n_steps):
            self._step()

            # Log state periodically
            if (step + 1) % self.config.log_interval == 0:
                self.history.record_step(self.state)

        return self.history

    def _step(self):
        """Execute one simulation step."""

        # Step 1: Actors choose actions
        for actor in self.actors:
            event = actor.act(self.state)
            if event is not None:
                # Apply event
                event.apply(self.state)

                # Log event
                self.history.record_event(
                    self.state.time_step,
                    actor.name,
                    event
                )

        # Step 2: Apply health decay (entropy)
        if self.config.enable_health_decay:
            decay_event = HealthDecay(node=None, rate=self.config.health_decay_rate)
            decay_event.apply(self.state)

        # Step 3: Update derived fields and energies
        self.state.update_derived_fields()
        self.state.update_energies()

        # Step 4: Check for incidents
        if self.config.enable_incidents:
            self._trigger_incidents()

        # Step 5: Advance time
        self.state.step_forward()

    def _trigger_incidents(self):
        """
        Check each node for potential incidents.

        Uses incident_probability() function from energy.py.
        """
        for node in self.state.graph.G.nodes:
            bad_val = self.state.bad[node]

            # Compute incident probability
            prob = incident_probability(
                bad_val,
                threshold=self.config.incident_threshold,
                steepness=self.config.incident_steepness,
                max_prob=self.config.incident_max_prob
            )

            # Trigger incident with probability
            if np.random.random() < prob:
                # Record incident
                self.state.record_incident(
                    node=node,
                    incident_type='badness_critical',
                    severity=bad_val
                )

                # Log to history
                self.history.record_incident(self.state.incidents[-1])


def run_simulation(
    state: SimulationState,
    actors: List[Actor],
    n_steps: int = 100,
    config: Optional[SimulationConfig] = None
) -> SimulationHistory:
    """
    Convenience function to run a simulation.

    Args:
        state: Initial simulation state
        actors: List of actors
        n_steps: Number of steps to simulate
        config: Optional config (creates default if None)

    Returns:
        SimulationHistory with results
    """
    if config is None:
        config = SimulationConfig(n_steps=n_steps)
    else:
        config.n_steps = n_steps

    simulator = Simulator(state, actors, config)
    return simulator.run()
