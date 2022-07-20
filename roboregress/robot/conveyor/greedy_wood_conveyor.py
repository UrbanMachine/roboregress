from typing import List, cast

import numpy as np
import open3d as o3d
from pydantic import BaseModel

from roboregress.engine.base_simulation_object import LoopGenerator
from roboregress.wood import Fastener
from roboregress.wood.wood import Wood

from ..cell import BaseRobotCell
from .base_wood_conveyor import BaseWoodConveyor


class GreedyWoodConveyor(BaseWoodConveyor):
    """A simple conveyor that moves the wood forward by an increment after each cell
    has operated once"""

    class Parameters(BaseModel):
        move_speed: float
        """How fast the wood moves, in meters/second"""

    def __init__(self, params: Parameters, cells: List[BaseRobotCell], wood: Wood):
        super().__init__(cells=cells, wood=wood)
        self._params = params
        self._wood = wood

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
            yield self._params.move_speed * move_increment

    def _calculate_furthest_cell(self) -> float:
        """Calculate the greediest possible furthest move the robot can make"""
        fasteners = self._wood.fasteners

        if fasteners is None:
            raise ValueError("The wood must have fasteners for this algo to work!")

        # Track the furthest possible move for each fastener type
        furthest_move_for_fastener = []

        # Find the 'furthest cell' of each 'type' of cell
        for fastener_type in Fastener:
            fasteners_of_type = fasteners[fasteners[:, 2] == fastener_type]
            highest_fastener = fasteners_of_type[np.argmax(fasteners_of_type[:, 0])][0]

            furthest_move_for = -float("inf")
            furthest_cell_for = -float("inf")
            for robot in self.cells:
                pick_probability = robot.params.pick_probabilities.get(fastener_type, 0)
                if pick_probability <= 0:
                    # This robot can't pick this fastener
                    continue
                delta = robot.params.end_pos - highest_fastener
                if delta >= furthest_move_for and robot.params.end_pos >= furthest_cell_for:
                    furthest_move_for = delta
                    furthest_cell_for = robot.params.end_pos

            furthest_move_for_fastener.append(furthest_move_for)

        # Move the minimum furthest amount
        return cast(float, np.min(furthest_move_for_fastener))

    def draw(self) -> List[o3d.geometry.Geometry]:
        return []
