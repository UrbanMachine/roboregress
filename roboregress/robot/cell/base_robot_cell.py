from abc import ABC

from roboregress.engine import BaseSimObject


class BaseRobotCell(BaseSimObject, ABC):
    """An object in charge of doing _some_ work on some location along the wood axis"""
