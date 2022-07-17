from .base_wood_planner import BaseWoodPlanner


class DumbWoodPlanner(BaseWoodPlanner):
    """A simple planner that moves the wood forward by an increment after each cell
    has operated once"""
