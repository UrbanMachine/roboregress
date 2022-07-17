from typing import Dict, Set

from roboregress.engine import BaseSimObject


class EngineRuntime:
    """An object that can run the simulation engine"""

    def __init__(self) -> None:
        self._timestamp: float = 0
        self._sim_objects: Set[BaseSimObject] = set()
        self._sleeping_objects: Dict[BaseSimObject, float] = {}
        """Holds a list of objects currently waiting to be reactivated once a certain
        timestamp is reached."""

    @property
    def timestamp(self) -> float:
        """A read-only getter for the timestamp property"""
        return self._timestamp

    def register(self, sim_object: BaseSimObject) -> None:
        """Register a new sim object with the runtime"""
        self._sim_objects.add(sim_object)

    def step(self) -> None:
        """"""
        # Get the next-to-awake timestamp in the _sleeping_objects list
        if len(self._sleeping_objects):
            next_awake_timestamp = sorted(self._sleeping_objects.values())[0]
            assert next_awake_timestamp > self._timestamp
            self._timestamp = next_awake_timestamp

        for sim_object in self._sim_objects:
            # If this object is asleep and it's not yet time to wake them, don't step
            if sim_object in self._sleeping_objects:
                if self._timestamp < self._sleeping_objects[sim_object]:
                    continue
                else:
                    self._sleeping_objects.pop(sim_object)

            sleep_seconds = sim_object.step()
            if sleep_seconds is not None:
                assert isinstance(sleep_seconds, float)
                self._sleeping_objects[sim_object] = self.timestamp + sleep_seconds

    def step_until(self, timestamp: float) -> None:
        """Run the engine until it is at or past the specified timestamp"""
        while self._timestamp < timestamp:
            self._step()
