"""
Event system for simulation.

Events modify the simulation state in response to actor decisions or
scheduled occurrences.
"""

from .base import Event
from .field_events import FeatureChange, Refactor, Patch, HealthDecay

__all__ = [
    "Event",
    "FeatureChange",
    "Refactor",
    "Patch",
    "HealthDecay",
]
