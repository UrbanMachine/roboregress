from .base_wood_conveyor import BaseWoodConveyor


class DumbWoodConveyor(BaseWoodConveyor):
    """A simple conveyor that moves the wood forward by an increment after each cell
    has operated once"""
