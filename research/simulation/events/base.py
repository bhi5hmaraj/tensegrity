"""
Base class for all simulation events.

Events modify the simulation state (fields, graph structure, etc.)
in response to actor decisions or scheduled occurrences.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.state import SimulationState


class Event(ABC):
    """
    Base class for all events.

    Subclasses must implement:
    - apply(state): Modifies state in-place
    - __str__(): Human-readable description
    """

    @abstractmethod
    def apply(self, state: 'SimulationState') -> None:
        """
        Apply this event to the simulation state.

        Args:
            state: SimulationState to modify (in-place)

        Note:
            Events modify state directly. After applying an event,
            caller should update derived fields and energies:
                state.update_derived_fields()
                state.update_energies()
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return human-readable description of event."""
        pass

    def __repr__(self) -> str:
        """Return string representation."""
        return self.__str__()
