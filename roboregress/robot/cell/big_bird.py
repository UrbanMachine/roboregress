from typing import List, Tuple

from ..fasteners import Fastener
from .base_robot_cell import BaseRobotCell


class BigBird(BaseRobotCell["BigBird.Parameters"]):
    class Parameters(BaseRobotCell.Parameters):
        big_bird_pick_seconds: float
        """The seconds it takes to pick a fastener, for BigBird"""

    def _run_pick(self) -> Tuple[List[Fastener], float]:
        fasteners = self._wood.pick(
            start_pos=self._params.start_pos,
            end_pos=self._params.end_pos,
            from_surface=self._params.pickable_surface,
            pick_probabilities=self._params.pick_probabilities,
            # Big bird can only pick one fastener at a time
            n_fasteners_to_sample=1,
        )
        return fasteners, self._params.big_bird_pick_seconds
