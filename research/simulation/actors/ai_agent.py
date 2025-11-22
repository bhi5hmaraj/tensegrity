"""
AI agent actor.

Autonomously chooses between features and refactors based on state.
"""

import numpy as np
from .base import Actor, NodeSelector
from ..events.field_events import FeatureChange, Refactor
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..core.state import SimulationState
    from ..events.base import Event


class AIAgent(Actor):
    """
    AI agent chooses actions autonomously.

    Policy:
    - Decides between feature or refactor based on system state
    - feature_bias controls preference for features vs refactors
    - Uses flow field to select target node
    - Higher velocity agent (more aggressive)
    """

    def __init__(
        self,
        name: str,
        feature_bias: float = 0.6,
        use_flow: bool = True
    ):
        """
        Initialize AI agent.

        Args:
            name: Actor identifier
            feature_bias: Probability of choosing feature over refactor (0-1)
            use_flow: If True, use flow field for node selection
        """
        super().__init__(name)
        self.feature_bias = feature_bias
        self.use_flow = use_flow

    def choose_action(self, state: 'SimulationState') -> Optional['Event']:
        """
        Choose action autonomously.

        Strategy:
        1. Decide: feature or refactor? (based on feature_bias)
        2. Select node (flow-based or demand-based)
        3. Create event

        Returns:
            FeatureChange or Refactor event
        """
        # Step 1: Decide action type
        action_type = self._choose_action_type(state)

        # Step 2: Select target node
        if self.use_flow and state.flow:
            # Use flow field to select node
            target_node = self._select_by_flow(state, action_type)
        else:
            # Fallback: select by demand or badness
            if action_type == 'feature':
                target_node = NodeSelector.select_by_demand(state, top_n=1)[0]
            else:
                target_node = NodeSelector.select_by_badness(state, top_n=1)[0]

        # Step 3: Create event
        if action_type == 'feature':
            return FeatureChange(node=target_node, magnitude=0.1)
        else:
            return Refactor(node=target_node, magnitude=0.15)

    def _choose_action_type(self, state: 'SimulationState') -> str:
        """
        Decide between 'feature' or 'refactor'.

        Uses feature_bias as base probability, adjusted by system stress.
        If H is high (crisis), reduce feature_bias (do more refactoring).

        Returns:
            'feature' or 'refactor'
        """
        # Adjust bias based on system stress
        # If H > some threshold, reduce feature bias
        stress_factor = min(1.0, state.H / 2.0)  # Normalize H
        adjusted_bias = self.feature_bias * (1 - 0.5 * stress_factor)

        # Random choice based on adjusted bias
        if np.random.random() < adjusted_bias:
            return 'feature'
        else:
            return 'refactor'

    def _select_by_flow(self, state: 'SimulationState', action_type: str) -> str:
        """
        Select node based on flow field.

        For features: prefer high flow_x (business direction)
        For refactors: prefer high flow_y (stability direction)

        Args:
            state: Simulation state
            action_type: 'feature' or 'refactor'

        Returns:
            Selected node
        """
        nodes = list(state.graph.G.nodes)
        scores = {}

        for node in nodes:
            flow_x, flow_y = state.flow.get(node, (0, 0))

            if action_type == 'feature':
                # Prefer high business flow
                scores[node] = flow_x
            else:
                # Prefer high stability flow (need for refactoring)
                scores[node] = flow_y

        # Select highest scoring node
        if scores:
            best_node = max(scores, key=scores.get)
            return best_node
        else:
            # Fallback to random
            return np.random.choice(nodes)

    def __str__(self) -> str:
        return (
            f"AIAgent({self.name}, "
            f"feature_bias={self.feature_bias:.2f}, "
            f"use_flow={self.use_flow})"
        )
