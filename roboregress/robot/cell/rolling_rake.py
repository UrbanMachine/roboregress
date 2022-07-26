from math import pi
from typing import List, Tuple

import open3d as o3d

from roboregress.wood.fasteners import Fastener

from ..vis_constants import ROBOT_HEIGHT, ROBOT_WIDTH
from .base_rake import BaseRakeMixin
from .base_robot_cell import BaseRobotCell


class RollingRake(BaseRakeMixin, BaseRobotCell["RollingRake.Parameters"]):
    class Parameters(BaseRobotCell.Parameters):
        rolling_rake_cycle_seconds: float
        """The seconds it takes to run the rake once"""

        working_width: float = 0

    def _run_pick(self) -> Tuple[List[Fastener], float]:
        rake_to = self._get_distance_to_rake_to(
            wood=self._wood, workspace_start=self.params.start_pos
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
        return fasteners, self.params.rolling_rake_cycle_seconds

    def draw(self) -> List[o3d.geometry.Geometry]:
        cylinder: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_cylinder(
            radius=ROBOT_HEIGHT, height=ROBOT_WIDTH
        )
        position = self._calculate_position()
        cylinder.translate(position - cylinder.get_center())
        cylinder.paint_uniform_color(self._calculate_color())

        # Orient the rectangle to 'face' the surface it corresponds to
        if position[1] == 0:
            cylinder.rotate(cylinder.get_rotation_matrix_from_xyz((pi / 2, 0, 0)))

        return [cylinder]
