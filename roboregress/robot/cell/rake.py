from typing import List, Tuple

from roboregress.wood.fasteners import Fastener

from .base_rake import BaseRakeMixin
from .base_robot_cell import BaseRobotCell


class Rake(BaseRakeMixin, BaseRobotCell["Rake.Parameters"]):
    color = (1, 0, 0)

    class Parameters(BaseRobotCell.Parameters):
        rake_cycle_seconds: float
        """The seconds it takes to run the rake once"""

    def _run_pick(self) -> Tuple[List[Fastener], float]:
        rake_to = self._get_distance_to_rake_to(
            wood=self._wood,
            workspace_start=self.params.start_pos,
            workspace_end=self.params.end_pos,
        )
        if rake_to == self.params.start_pos:
            return [], 0

        fasteners, _ = self._wood.pick(
            start_pos=self.params.start_pos,
            end_pos=rake_to,
            from_surface=self.params.pickable_surface,
            pick_probabilities=self.params.pick_probabilities,
            # The rake can pick 'unlimited' amounts of fasteners per rake
            n_fasteners_to_sample=None,
        )
        return fasteners, self.params.rake_cycle_seconds
