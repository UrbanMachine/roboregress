from typing import List

from pydantic import BaseModel

from roboregress.engine.base_simulation_object import LoopGenerator
from roboregress.wood.wood import Wood

from ..cell import BaseRobotCell
from ..statistics import WoodStats
from .base_wood_conveyor import BaseWoodConveyor


class DumbWoodConveyor(BaseWoodConveyor["DumbWoodConveyor.Parameters"]):
    """A simple conveyor that moves the wood forward by an increment after each cell
    has operated once"""

    class Parameters(BaseModel):
        move_increment: float
        """How much to move the wood each time"""

        move_speed: float
        """How fast the wood moves, in meters/second"""

    def __init__(
        self, params: Parameters, cells: List[BaseRobotCell], wood: Wood, wood_stats: WoodStats
    ):
        super().__init__(cells=cells, wood=wood, wood_stats=wood_stats, params=params)

    def _loop(self) -> LoopGenerator:
        while True:

            # Schedule work
            self.wood.schedule_move()
            while not self.wood.ready_for_move():
                yield None

            # Move the wood!
            self.wood.move(self.params.move_increment)
            with self.stats.time():
                yield self.params.move_increment / self.params.move_speed
