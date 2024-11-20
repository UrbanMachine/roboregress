from roboregress.wood import Fastener

from .base_robot_cell import BaseRobotCell


class ScrewManipulator(BaseRobotCell["ScrewManipulator.Parameters"]):
    color = (0, 0, 1)

    class Parameters(BaseRobotCell.Parameters):
        screw_pick_seconds: float
        """The seconds it takes to pick a screw, for the screw manipulator"""

    def _run_pick(self) -> tuple[list[Fastener], float]:
        fasteners, attempted_pick = self._wood.pick(
            start_pos=self.params.start_pos,
            end_pos=self.params.end_pos,
            from_surface=self.params.pickable_surface,
            pick_probabilities=self.params.pick_probabilities,
            # ScrewManipulator can only pick one fastener at a time
            n_fasteners_to_sample=1,
        )
        return fasteners, self.params.screw_pick_seconds if attempted_pick else 0
