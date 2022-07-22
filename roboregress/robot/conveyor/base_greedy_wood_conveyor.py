from typing import List, cast

import numpy as np
from pydantic import BaseModel

from roboregress.wood import Fastener
from roboregress.wood.wood import Wood

from ..cell import BaseRobotCell
from ..statistics import WoodStats
from .base_wood_conveyor import BaseWoodConveyor


class BaseGreedyWoodConveyor(BaseWoodConveyor):
    """A simple conveyor that moves the wood forward by an increment after each cell
    has operated once"""

    class Parameters(BaseModel):
        move_speed: float
        """How fast the wood moves, in meters/second"""

    def __init__(
        self, params: Parameters, cells: List[BaseRobotCell], wood: Wood, wood_stats: WoodStats
    ):
        super().__init__(cells=cells, wood=wood, wood_stats=wood_stats)
        self._params = params
        self._wood = wood

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

            if len(fasteners_of_type) == 0:
                # If no fasteners of this type are present in the wood, at all
                continue

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

            if furthest_move_for >= 0:
                furthest_move_for_fastener.append(furthest_move_for)

        # Move the minimum furthest amount
        if len(furthest_move_for_fastener) == 0:
            return 0
        return cast(float, np.min(furthest_move_for_fastener))
