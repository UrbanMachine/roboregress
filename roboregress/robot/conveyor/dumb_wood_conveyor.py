from typing import List

import open3d as o3d
from pydantic import BaseModel

from roboregress.engine.base_simulation_object import LoopGenerator
from roboregress.wood.wood import Wood

from ..cell import BaseRobotCell
from .base_wood_conveyor import BaseWoodConveyor


class DumbWoodConveyor(BaseWoodConveyor):
    """A simple conveyor that moves the wood forward by an increment after each cell
    has operated once"""

    class Parameters(BaseModel):
        move_increment: float
        """How much to move the wood each time"""

        move_speed: float
        """How fast the wood moves, in meters/second"""

    def __init__(self, params: Parameters, cells: List[BaseRobotCell], wood: Wood):
        super().__init__(cells=cells, wood=wood)
        self._params = params

    def _loop(self) -> LoopGenerator:
        while True:

            # Schedule work
            self.wood.schedule_move()
            while not self.wood.ready_for_move():
                yield None

            # Move the wood!
            self.wood.move(self._params.move_increment)
            yield self._params.move_speed * self._params.move_increment

    def draw(self) -> List[o3d.geometry.Geometry]:
        return []
