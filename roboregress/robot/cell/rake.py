from typing import List, Tuple

from roboregress.wood.fasteners import Fastener

from .base_robot_cell import BaseRobotCell


class Rake(BaseRobotCell["Rake.Parameters"]):
    class Parameters(BaseRobotCell.Parameters):
        rake_cycle_seconds: float
        """The seconds it takes to run the rake once"""

    def _run_pick(self) -> Tuple[List[Fastener], float]:
        fasteners = self._wood.pick(
            start_pos=self._params.start_pos,
            end_pos=self._params.end_pos,
            from_surface=self._params.pickable_surface,
            pick_probabilities=self._params.pick_probabilities,
            # The rake can pick 'unlimited' amounts of fasteners per rake
            n_fasteners_to_sample=None,
        )
        return fasteners, self._params.rake_cycle_seconds
