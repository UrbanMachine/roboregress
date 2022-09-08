import random
from typing import Dict, List, Optional

import numpy as np
import open3d as o3d
from tqdm.auto import tqdm

from .base_simulation_object import BaseSimObject
from .visualizer import Visualizer

# Make the system deterministic by setting the seed for numpy and python
np.random.seed(1337)
random.seed(1337)


class NoObjectsToStep(Exception):
    pass


class NoTimestampProgression(Exception):
    pass


class SimulationRuntime:
    """An object that can run the simulation engine"""

    def __init__(self) -> None:
        self._timestamp: float = 0
        self._sim_objects: List[BaseSimObject] = []
        self._sleeping_objects: Dict[BaseSimObject, float] = {}
        """Holds a list of objects currently waiting to be reactivated once a certain
        timestamp is reached."""

    @property
    def timestamp(self) -> float:
        """A read-only getter for the timestamp property"""
        return self._timestamp

    def register(self, *sim_objects: BaseSimObject) -> None:
        """Register a new sim object with the runtime"""
        for sim_obj in sim_objects:
            assert sim_obj not in self._sim_objects
            self._sim_objects.append(sim_obj)

    def step(self) -> None:
        """Step the simulation

        :raises NoObjectsToStep: If the runtime has no objects registered
        :raises ValueError: If there's an unexpected inconsistency with timestamps
        """
        if len(self._sim_objects) == 0:
            raise NoObjectsToStep("The runtime has no associated objects!")

        # Get the next-to-awake timestamp in the _sleeping_objects list
        if len(self._sleeping_objects):
            next_awake_timestamp = sorted(self._sleeping_objects.values())[0]
            if next_awake_timestamp < self._timestamp:
                raise ValueError(
                    f"All sleeping objects should be woken on the same timestamp! "
                    f"{next_awake_timestamp=} {self.timestamp=}"
                )
            self._timestamp = next_awake_timestamp

        for sim_object in self._sim_objects:
            # If this object is asleep and it's not yet time to wake them, don't step
            if sim_object in self._sleeping_objects:
                if self._timestamp < self._sleeping_objects[sim_object]:
                    continue
                else:
                    wake_ts = self._sleeping_objects.pop(sim_object)
                    assert wake_ts == self._timestamp

            sleep_seconds = sim_object.step()

            if sleep_seconds is not None:
                assert isinstance(sleep_seconds, float)
                if sleep_seconds <= 0:
                    raise ValueError(f"Sleep must be a positive number! {sleep_seconds}")

                self._sleeping_objects[sim_object] = self.timestamp + sleep_seconds

    def step_until(self, timestamp: float, visualizer: Optional[Visualizer] = None) -> None:
        """Run the engine until it is at or past the specified timestamp"""
        consecutive_steps_without_change = 0
        """Track if theres ever more than 1 step in a row where the timestamp didn't
        increment. This can happen if the objects aren't yielding sleeps, which means
        the user of this runtime isn't actually doing anything useful with it...
        """
        with tqdm(total=timestamp, unit="s") as progress_bar:
            while self._timestamp < timestamp:
                # Update progress bar
                progress_bar.n = round(self._timestamp)
                progress_bar.refresh(progress_bar.lock_args)

                # Update visualization
                if visualizer and consecutive_steps_without_change == 0:
                    geometries: List[o3d.geometry.Geometry] = sum(
                        [o.draw() for o in self._sim_objects], []
                    )
                    geometries.append(o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.3))
                    visualizer.draw(geometries, self.timestamp)

                # Step the system
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
