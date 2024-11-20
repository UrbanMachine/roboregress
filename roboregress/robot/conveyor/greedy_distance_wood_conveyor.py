from pydantic import BaseModel

from roboregress.engine.base_simulation_object import LoopGenerator

from . import BaseWoodConveyor
from .utils.furthest_move import calculate_furthest_cell


class GreedyDistanceWoodConveyor(
    BaseWoodConveyor["GreedyDistanceWoodConveyor.Parameters"]
):
    """A simple conveyor that moves the wood forward by an increment after each cell
    has operated once"""

    class Parameters(BaseModel):
        move_speed: float
        """How fast the wood moves, in meters/second"""

    def _loop(self) -> LoopGenerator:
        while True:
            # Calculate the maximum amount the wood can be moved
            while calculate_furthest_cell(wood=self.wood, cells=self.cells) == 0:
                yield None

            self.wood.schedule_move()
            while not self.wood.ready_for_move():
                yield None

            move_increment = calculate_furthest_cell(wood=self.wood, cells=self.cells)
            self.wood.move(move_increment)
            with self.stats.time():
                yield move_increment / self.params.move_speed
