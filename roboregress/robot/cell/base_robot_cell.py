from abc import ABC

import open3d as o3d

from roboregress.engine import BaseSimObject


class BaseRobotCell(BaseSimObject, ABC):
    """An object in charge of doing _some_ work on some location along the wood axis"""

    def __init__(self, work_envelope):
        pass
