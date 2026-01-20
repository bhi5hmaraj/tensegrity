"""
Field-modifying events.

Events that change scalar fields (health, complexity, demand) at nodes.
"""

from .base import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.state import SimulationState


class FeatureChange(Event):
    """
    Add a feature to a node.

    Effects:
    - Increases complexity (new code)
    - Decreases health (rushed features introduce bugs)
    - May increase demand (if feature is popular)
    """

    def __init__(self, node: str, magnitude: float = 0.1):
        """
        Initialize feature change event.

        Args:
            node: Target node identifier
            magnitude: Size of change [0, 1]  (default 0.1 = 10% change)
        """
        self.node = node
        self.magnitude = magnitude

    def apply(self, state: 'SimulationState') -> None:
        """
        Apply feature change.

        Increases complexity, decreases health.
        """
        # Increase complexity (new code added)
        state.complexity[self.node] = min(
            1.0,
            state.complexity[self.node] + self.magnitude
        )

        # Decrease health (rushed features → bugs)
        state.health[self.node] = max(
            0.0,
            state.health[self.node] - 0.5 * self.magnitude
        )

    def __str__(self) -> str:
        return f"FeatureChange(node={self.node}, magnitude={self.magnitude:.2f})"


class Refactor(Event):
    """
    Refactor a node.

    Effects:
    - Decreases complexity (code simplified)
    - Increases health (bugs fixed, structure improved)
    - No change to demand (same functionality)
    """

    def __init__(self, node: str, magnitude: float = 0.15):
        """
        Initialize refactor event.

        Args:
            node: Target node identifier
            magnitude: Size of change [0, 1] (default 0.15 = 15% improvement)
        """
        self.node = node
        self.magnitude = magnitude

    def apply(self, state: 'SimulationState') -> None:
        """
        Apply refactor.

        Decreases complexity, increases health.
        """
        # Decrease complexity (code simplified)
        state.complexity[self.node] = max(
            0.0,
            state.complexity[self.node] - self.magnitude
        )

        # Increase health (bugs fixed, structure improved)
        state.health[self.node] = min(
            1.0,
            state.health[self.node] + 0.8 * self.magnitude
        )

    def __str__(self) -> str:
        return f"Refactor(node={self.node}, magnitude={self.magnitude:.2f})"


class Patch(Event):
    """
    Apply a patch (bug fix) to a node.

    Effects:
    - Increases health (bugs fixed)
    - Slight increase in complexity (patch code added)
    """

    def __init__(self, node: str, magnitude: float = 0.2):
        """
        Initialize patch event.

        Args:
            node: Target node identifier
            magnitude: Size of health improvement [0, 1]
        """
        self.node = node
        self.magnitude = magnitude

    def apply(self, state: 'SimulationState') -> None:
        """
        Apply patch.

        Increases health, slight complexity increase.
        """
        # Increase health (bugs fixed)
        state.health[self.node] = min(
            1.0,
            state.health[self.node] + self.magnitude
        )

        # Slight complexity increase (patch code)
        state.complexity[self.node] = min(
            1.0,
            state.complexity[self.node] + 0.05 * self.magnitude
        )

    def __str__(self) -> str:
        return f"Patch(node={self.node}, magnitude={self.magnitude:.2f})"


class HealthDecay(Event):
    """
    Natural health decay (entropy).

    Effects:
    - Decreases health (bit rot, dependency drift)
    - Applied to all nodes or specific node
    """

    def __init__(self, node: str = None, rate: float = 0.01):
        """
        Initialize health decay event.

        Args:
            node: Target node, or None for all nodes
            rate: Decay rate per step [0, 1]
        """
        self.node = node
        self.rate = rate

    def apply(self, state: 'SimulationState') -> None:
        """
        Apply health decay.

        Decreases health at specified rate.
        """
        if self.node is None:
            # Apply to all nodes
            for node in state.graph.G.nodes:
                state.health[node] = max(
                    0.0,
                    state.health[node] - self.rate
                )
        else:
            # Apply to specific node
            state.health[self.node] = max(
                0.0,
                state.health[self.node] - self.rate
            )

    def __str__(self) -> str:
        target = self.node if self.node else "all"
        return f"HealthDecay(target={target}, rate={self.rate:.3f})"
