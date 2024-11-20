from typing import Any

from roboregress.robot.cell import BaseRobotCell
from roboregress.wood import FASTENER_IDX, POSITION_IDX, SURFACE_IDX, Wood


def calculate_busyness_at_position(
    wood: Wood, cells: list[BaseRobotCell[Any]], move_distance: float
) -> int:
    """Returns the number of robots that would be 'busy' if the wood were moved a
    certain amount"""
    # Move a copy of the wood to the estimated position
    moved_fasteners = wood.fasteners

    if moved_fasteners is None:
        # There are no fasteners!
        return 0

    moved_fasteners[:, POSITION_IDX] += move_distance

    cell_busyness: list[bool] = []
    for cell in cells:
        busyness = 0
        for pickable_type in cell.params.pick_probabilities:
            of_type = moved_fasteners[:, FASTENER_IDX] == pickable_type
            of_surface = moved_fasteners[:, SURFACE_IDX] == cell.params.pickable_surface
            after_start = moved_fasteners[:, POSITION_IDX] > cell.params.start_pos
            after_end = moved_fasteners[:, POSITION_IDX] < cell.params.end_pos
            filtered = moved_fasteners[of_type & of_surface & after_end & after_start]
            busyness += len(filtered)

        cell_busyness.append(busyness > 0)
    return sum(cell_busyness)
