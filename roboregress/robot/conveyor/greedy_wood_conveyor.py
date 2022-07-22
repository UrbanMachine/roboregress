from roboregress.engine.base_simulation_object import LoopGenerator

from .base_greedy_wood_conveyor import BaseGreedyWoodConveyor


class GreedyWoodConveyor(BaseGreedyWoodConveyor):
    """A simple conveyor that moves the wood forward by an increment after each cell
    has operated once"""

    def _loop(self) -> LoopGenerator:
        while True:
            # Calculate the maximum amount the wood can be moved
            while self._calculate_furthest_cell() == 0:
                yield None

            self.wood.schedule_move()
            while not self.wood.ready_for_move():
                yield None

            move_increment = self._calculate_furthest_cell()
            self.wood.move(move_increment)
            with self.stats.time():
                yield move_increment / self._params.move_speed
