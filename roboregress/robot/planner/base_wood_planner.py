from abc import ABC
from typing import List

from roboregress.engine import BaseSimObject
from roboregress.robot.cell import BaseRobotCell


class BaseWoodPlanner(BaseSimObject, ABC):
    """An object in charge of organizing how far to move the wood at a time"""

    def __init__(self, cells: List[BaseRobotCell]):
        self.cells = cells
