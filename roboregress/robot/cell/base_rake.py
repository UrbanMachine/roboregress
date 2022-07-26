from roboregress.wood import Wood


class BaseRakeMixin:
    """This mixin provides a function to 'rake' only swaths of wood that weren't raked
    so far. This is so the rake doesn't perform better when the wood move small amounts.
    """

    color = (1, 0, 0)
    _last_rake_wood_pos = 0.0
    """Keep track of the position of the wood, to know what has and hasn't been raked"""

    def _get_distance_to_rake_to(
        self, wood: Wood, workspace_start: float, workspace_end: float = float("inf")
    ) -> float:
        """Calculate how much distance from the start pos to perform raking on"""

        unraked_wood = wood.processed_board - self._last_rake_wood_pos

        self._last_rake_wood_pos = wood.processed_board
        unraked_end = workspace_start + unraked_wood

        if unraked_end > workspace_end:
            unraked_end = workspace_end
        return unraked_end
