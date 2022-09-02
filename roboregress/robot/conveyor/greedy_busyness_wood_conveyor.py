from pydantic import BaseModel

from roboregress.engine.base_simulation_object import LoopGenerator

from ..cell import Rake
from .base_wood_conveyor import BaseWoodConveyor
from .utils.busyness import calculate_busyness_at_position
from .utils.furthest_move import calculate_furthest_cell


class GreedyBusynessWoodConveyor(BaseWoodConveyor["GreedyBusynessWoodConveyor.Parameters"]):
    """A simple conveyor that moves the wood forward by an increment after each cell
    has operated once"""

    class Parameters(BaseModel):
        move_speed: float
        """How fast the wood moves, in meters/second"""

        optimization_increment: float

    def _loop(self) -> LoopGenerator:
        while True:
            # Calculate the maximum amount the wood can be moved
            move_dist = self._calculate_optimal_busyness_move()

            if move_dist > 0:
                self.wood.schedule_move()
                while not self.wood.ready_for_move():
                    yield None

                self.wood.move(move_dist)
                with self.stats.time():
                    yield move_dist / self.params.move_speed
            else:
                yield None

    def _calculate_optimal_busyness_move(self) -> float:
        furthest_move = calculate_furthest_cell(wood=self.wood, cells=self.cells)

        best_increment = 0.0
        best_busyness = 0
        increment = 0.0

        # Only run without rakes, since rakes may or may not be busy depending on
        # how much the wood moved previously
        cells_without_rakes = [c for c in self.cells if not isinstance(c, Rake)]
        while increment < furthest_move:
            busyness = calculate_busyness_at_position(
                move_distance=increment, wood=self.wood, cells=cells_without_rakes
            )
            if busyness > best_busyness:
                best_busyness = busyness
                best_increment = increment
            increment += self.params.optimization_increment

        # best_increment = best_increment or furthest_move
        assert best_increment < furthest_move
        assert best_increment >= 0
        return best_increment
