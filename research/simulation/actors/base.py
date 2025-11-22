"""
Base class for all actors.

Actors observe the simulation state and choose actions (events) to perform.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
import numpy as np

if TYPE_CHECKING:
    from ..core.state import SimulationState
    from ..events.base import Event


class Actor(ABC):
    """
    Base class for all actors.

    Actors have:
    - Name/identifier
    - Policy parameters (weights, biases)
    - choose_action(state) → Event

    Subclasses must implement choose_action().
    """

    def __init__(self, name: str):
        """
        Initialize actor.

        Args:
            name: Actor identifier
        """
        self.name = name
        self.action_count = 0  # Track number of actions taken

    @abstractmethod
    def choose_action(self, state: 'SimulationState') -> Optional['Event']:
        """
        Choose an action based on current state.

        Args:
            state: Current simulation state

        Returns:
            Event to apply, or None if no action
        """
        pass

    def act(self, state: 'SimulationState') -> Optional['Event']:
        """
        Wrapper around choose_action that tracks action count.

        Args:
            state: Current simulation state

        Returns:
            Event chosen by actor
        """
        event = self.choose_action(state)
        if event is not None:
            self.action_count += 1
        return event

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self) -> str:
        return self.__str__()


class NodeSelector:
    """
    Helper for selecting nodes based on different criteria.

    Used by actors to decide where to focus effort.
    """

    @staticmethod
    def select_by_demand(state: 'SimulationState', top_n: int = 1) -> list:
        """Select nodes with highest demand."""
        nodes = list(state.graph.G.nodes)
        sorted_nodes = sorted(nodes, key=lambda n: state.demand[n], reverse=True)
        return sorted_nodes[:top_n]

    @staticmethod
    def select_by_badness(state: 'SimulationState', top_n: int = 1) -> list:
        """Select nodes with highest badness."""
        nodes = list(state.graph.G.nodes)
        sorted_nodes = sorted(nodes, key=lambda n: state.bad[n], reverse=True)
        return sorted_nodes[:top_n]

    @staticmethod
    def select_by_flow_magnitude(state: 'SimulationState', top_n: int = 1) -> list:
        """
        Select nodes with highest flow magnitude.

        Flow = (business_direction, stability_direction)
        Magnitude = sqrt(flow_x^2 + flow_y^2)
        """
        nodes = list(state.graph.G.nodes)

        def flow_magnitude(node):
            fx, fy = state.flow.get(node, (0, 0))
            return np.sqrt(fx**2 + fy**2)

        sorted_nodes = sorted(nodes, key=flow_magnitude, reverse=True)
        return sorted_nodes[:top_n]

    @staticmethod
    def select_by_local_energy(state: 'SimulationState', top_n: int = 1) -> list:
        """Select nodes with highest local Dirichlet energy."""
        nodes = list(state.graph.G.nodes)
        sorted_nodes = sorted(nodes, key=lambda n: state.E_local.get(n, 0), reverse=True)
        return sorted_nodes[:top_n]

    @staticmethod
    def select_random(state: 'SimulationState', n: int = 1) -> list:
        """Select random nodes."""
        nodes = list(state.graph.G.nodes)
        return list(np.random.choice(nodes, size=min(n, len(nodes)), replace=False))

    @staticmethod
    def select_weighted_by_field(state: 'SimulationState', field_name: str) -> str:
        """
        Select node with probability proportional to field value.

        Args:
            state: Simulation state
            field_name: Field to use ('demand', 'bad', etc.)

        Returns:
            Selected node
        """
        nodes = list(state.graph.G.nodes)
        field = getattr(state, field_name)
        weights = np.array([field[n] for n in nodes])

        # Normalize to probabilities
        if weights.sum() > 0:
            probs = weights / weights.sum()
        else:
            probs = np.ones(len(nodes)) / len(nodes)

        return np.random.choice(nodes, p=probs)
