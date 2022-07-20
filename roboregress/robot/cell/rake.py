from typing import List, Tuple

from roboregress.wood.fasteners import Fastener

from .base_robot_cell import BaseRobotCell


class Rake(BaseRobotCell["Rake.Parameters"]):
    color = (1, 0, 0)

    class Parameters(BaseRobotCell.Parameters):
        rake_cycle_seconds: float
        """The seconds it takes to run the rake once"""

    def _run_pick(self) -> Tuple[List[Fastener], float]:
        fasteners, _ = self._wood.pick(
            start_pos=self.params.start_pos,
            end_pos=self.params.end_pos,
            from_surface=self.params.pickable_surface,
            pick_probabilities=self.params.pick_probabilities,
            # The rake can pick 'unlimited' amounts of fasteners per rake
            n_fasteners_to_sample=None,
        )
        return fasteners, self.params.rake_cycle_seconds
