"""
Feature engineer actor.

Focuses on adding features to high-demand modules.
"""

from .base import Actor, NodeSelector
from ..events.field_events import FeatureChange
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..core.state import SimulationState
    from ..events.base import Event


class FeatureEngineer(Actor):
    """
    Feature engineer adds features to high-demand modules.

    Policy:
    - Selects node based on weighted combination of demand and low badness
    - business_weight controls preference for demand
    - stability_weight controls aversion to high badness
    - Creates FeatureChange events
    """

    def __init__(
        self,
        name: str,
        business_weight: float = 0.8,
        stability_weight: float = 0.2
    ):
        """
        Initialize feature engineer.

        Args:
            name: Actor identifier
            business_weight: Weight for demand (0-1)
            stability_weight: Weight for avoiding high badness (0-1)

        Note:
            business_weight + stability_weight should = 1.0
        """
        super().__init__(name)
        self.business_weight = business_weight
        self.stability_weight = stability_weight

    def choose_action(self, state: 'SimulationState') -> Optional['Event']:
        """
        Choose which node to add a feature to.

        Strategy:
        - Score each node: score = business_weight * demand - stability_weight * bad
        - Select highest scoring node
        - Create FeatureChange event

        Returns:
            FeatureChange event for selected node
        """
        nodes = list(state.graph.G.nodes)

        # Compute score for each node
        scores = {}
        for node in nodes:
            score = (
                self.business_weight * state.demand[node] -
                self.stability_weight * state.bad[node]
            )
            scores[node] = score

        # Select highest scoring node
        best_node = max(scores, key=scores.get)

        # Create feature change event
        return FeatureChange(node=best_node, magnitude=0.1)

    def __str__(self) -> str:
        return (
            f"FeatureEngineer({self.name}, "
            f"business={self.business_weight:.2f}, "
            f"stability={self.stability_weight:.2f})"
        )
