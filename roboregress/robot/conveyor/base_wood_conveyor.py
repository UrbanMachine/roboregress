from abc import ABC
from copy import deepcopy
from typing import List

import open3d as o3d

from roboregress.engine import BaseSimObject
from roboregress.robot.cell import BaseRobotCell
from roboregress.robot.vis_constants import ROBOT_WIDTH
from roboregress.wood import Wood


class BaseWoodConveyor(BaseSimObject, ABC):
    """An object in charge of organizing how far to move the wood at a time"""

    color = (0.3, 0.3, 1.0)

    def __init__(self, cells: List[BaseRobotCell], wood: Wood):
        super().__init__()
        self.cells = cells
        self.wood = wood

    def draw(self) -> List[o3d.geometry.Geometry]:
        box_1: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_box(
            width=0.1, height=0.1, depth=ROBOT_WIDTH * 2
        )
        box_1.paint_uniform_color(self.color)
        box_2 = deepcopy(box_1)

        box_1_pos = (self.wood.processed_board % 5, 0, -ROBOT_WIDTH)
        box_1.translate(box_1_pos)

        box_2_pos = ((self.wood.processed_board + 2.1) % 5, 0, -ROBOT_WIDTH)
        box_2.translate(box_2_pos)
        return [box_1, box_2]
