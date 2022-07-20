from abc import ABC
from typing import List

import numpy as np
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
        box: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_box(
            width=0.1, height=0.1, depth=ROBOT_WIDTH * 2
        )
        box.paint_uniform_color(self.color)

        box.translate(np.array((self.wood.processed_board % 5, 0, -ROBOT_WIDTH)))
        return [box]
