from typing import List, Tuple

from roboregress.wood import Fastener

from .base_robot_cell import BaseRobotCell


class BigBird(BaseRobotCell["BigBird.Parameters"]):
    color = (0, 1, 0)

    class Parameters(BaseRobotCell.Parameters):
        big_bird_pick_seconds: float
        """The seconds it takes to pick a fastener, for BigBird"""

    def _run_pick(self) -> Tuple[List[Fastener], float]:
        fasteners, attempted_pick = self._wood.pick(
            start_pos=self.params.start_pos,
            end_pos=self.params.end_pos,
            from_surface=self.params.pickable_surface,
            pick_probabilities=self.params.pick_probabilities,
            # Big bird can only pick one fastener at a time
            n_fasteners_to_sample=1,
        )
        return fasteners, self.params.big_bird_pick_seconds if attempted_pick else 0
