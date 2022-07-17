from abc import ABC
from typing import List

from roboregress.engine import BaseSimObject
from roboregress.robot.surfaces import Surface
from roboregress.robot.wood import Wood


class BaseRobotCell(BaseSimObject, ABC):
    """An object in charge of doing _some_ work on some location along the wood axis"""

    def __init__(self, work_envelope):
        pass
