from typing import Set

from roboregress.engine import BaseSimObject


class EngineRuntime:
    """An object that can run the simulation engine"""

    def __init__(self) -> None:
        self._timestamp: float = 0
        self._sim_objects: Set[BaseSimObject]

    @property
    def timestamp(self) -> float:
        """A read-only getter for the timestamp property"""
        return self._timestamp

    def register(self, sim_object: BaseSimObject) -> None:
        """Register a new sim object with the runtime"""
        self._sim_objects.add(sim_object)

    def _step(self) -> None:
        pass

    def run_until(self, timestamp: float) -> None:
        """Run the engine until it is at or past the specified timestamp"""
        while self._timestamp < timestamp:
            self._step()
