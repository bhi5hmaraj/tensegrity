"""
Refactor engineer actor.

Focuses on improving health/complexity of problematic modules.
"""

from .base import Actor, NodeSelector
from ..events.field_events import Refactor
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..core.state import SimulationState
    from ..events.base import Event


class RefactorEngineer(Actor):
    """
    Refactor engineer improves health and reduces complexity.

    Policy:
    - Selects node with high badness (unhealthy or complex)
    - business_weight controls consideration of demand
    - stability_weight controls focus on high badness
    - Creates Refactor events
    """

    def __init__(
        self,
        name: str,
        business_weight: float = 0.2,
        stability_weight: float = 0.8
    ):
        """
        Initialize refactor engineer.

        Args:
            name: Actor identifier
            business_weight: Weight for demand (0-1)
            stability_weight: Weight for fixing high badness (0-1)

        Note:
            Refactor engineers typically have high stability_weight
            (focus on fixing problems, not just popular modules)
        """
        super().__init__(name)
        self.business_weight = business_weight
        self.stability_weight = stability_weight

    def choose_action(self, state: 'SimulationState') -> Optional['Event']:
        """
        Choose which node to refactor.

        Strategy:
        - Score each node: score = stability_weight * bad + business_weight * demand
        - Select highest scoring node (worst badness, preferably high demand)
        - Create Refactor event

        Returns:
            Refactor event for selected node
        """
        nodes = list(state.graph.G.nodes)

        # Compute score for each node
        scores = {}
        for node in nodes:
            score = (
                self.stability_weight * state.bad[node] +
                self.business_weight * state.demand[node]
            )
            scores[node] = score

        # Select highest scoring node
        best_node = max(scores, key=scores.get)

        # Create refactor event
        return Refactor(node=best_node, magnitude=0.15)

    def __str__(self) -> str:
        return (
            f"RefactorEngineer({self.name}, "
            f"business={self.business_weight:.2f}, "
            f"stability={self.stability_weight:.2f})"
        )
