from typing import Dict, Set

from .base_simulation_object import BaseSimObject
from .visualizer import Visualizer


class NoObjectsToStep(Exception):
    pass


class NoTimestampProgression(Exception):
    pass


class SimulationRuntime:
    """An object that can run the simulation engine"""

    def __init__(self) -> None:
        self._visualization = False
        self._timestamp: float = 0
        self._sim_objects: Set[BaseSimObject] = set()
        self._sleeping_objects: Dict[BaseSimObject, float] = {}
        """Holds a list of objects currently waiting to be reactivated once a certain
        timestamp is reached."""

    @property
    def timestamp(self) -> float:
        """A read-only getter for the timestamp property"""
        return self._timestamp

    def register(self, *sim_objects: BaseSimObject) -> None:
        """Register a new sim object with the runtime"""
        self._sim_objects.update(sim_objects)

    def step(self) -> None:
        """Step the simulation

        :raises NoObjectsToStep: If the runtime has no objects registered
        """
        if len(self._sim_objects) == 0:
            raise NoObjectsToStep("The runtime has no associated objects!")

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
                # Round at 10 decimal places to help prevent floating point drift
                next_awake = round(self.timestamp + sleep_seconds, 10)
                self._sleeping_objects[sim_object] = next_awake

    def step_until(self, timestamp: float, visualization=False) -> None:
        """Run the engine until it is at or past the specified timestamp"""
        consecutive_steps_without_change = 0
        """Track if theres ever more than 1 step in a row where the timestamp didn't
        increment. This can happen if the objects aren't yielding sleeps, which means
        the user of this runtime isn't actually doing anything useful with it...
        """
        visualizer = Visualizer() if visualization else None

        while self._timestamp < timestamp:
            # TODO: Add a check to make sure timestamp changes between consecutive runs
            previous_stamp = self.timestamp
            self.step()

            if previous_stamp == self.timestamp:
                consecutive_steps_without_change += 1
            else:
                consecutive_steps_without_change = 0

            if consecutive_steps_without_change > 1:
                raise NoTimestampProgression(
                    f"There have been {consecutive_steps_without_change} simulation "
                    f"steps in a row without the timestamp changing. This means that "
                    f"the simulation objects in the engine aren't requesting sleeps! "
                    f"Is there a logic error somewhere?"
                )

            if visualizer:
                geometries = sum([o.draw() for o in self._sim_objects], [])
                visualizer.draw(geometries)
