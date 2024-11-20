from abc import ABC
from copy import deepcopy
from typing import Any, Generic, TypeVar

import numpy as np
import open3d as o3d
from pydantic import BaseModel

from roboregress.engine import BaseSimObject
from roboregress.robot.cell import BaseRobotCell
from roboregress.robot.statistics import WoodStats
from roboregress.robot.vis_constants import ROBOT_WIDTH
from roboregress.wood import Wood

BaseParams = TypeVar("BaseParams", bound=BaseModel)


class BaseWoodConveyor(BaseSimObject, ABC, Generic[BaseParams]):
    """An object in charge of organizing how far to move the wood at a time"""

    color = (0.3, 0.3, 1.0)

    def __init__(
        self,
        params: BaseParams,
        cells: list[BaseRobotCell[Any]],
        wood: Wood,
        wood_stats: WoodStats,
    ):
        super().__init__()
        self.params = params
        self.cells = cells
        self.wood = wood
        self.stats = wood_stats

    def draw(self) -> list[o3d.geometry.Geometry]:
        box_1: o3d.geometry.TriangleMesh = o3d.geometry.TriangleMesh.create_box(
            width=0.1, height=0.1, depth=ROBOT_WIDTH * 2
        )

        # Adjust color based on if it just moved
        if self.stats.currently_working:
            color = np.array(self.color)
        else:
            color = np.array(self.color, dtype=np.float64)
            color += (0.5, 0.5, 0.5)
            color = np.clip(color, a_min=0, a_max=1)
        box_1.paint_uniform_color(color)
        box_2 = deepcopy(box_1)

        box_1_pos = (self.wood.processed_board % 5, 0, -ROBOT_WIDTH)
        box_1.translate(box_1_pos)

        box_2_pos = ((self.wood.processed_board + 2.1) % 5, 0, -ROBOT_WIDTH)
        box_2.translate(box_2_pos)

        return [box_1, box_2]
