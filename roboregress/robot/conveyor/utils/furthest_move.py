from typing import List, cast

import numpy as np

from roboregress.robot.cell import BaseRobotCell
from roboregress.wood import Fastener, Wood


def calculate_furthest_cell(wood: Wood, cells: List[BaseRobotCell]) -> float:
    """Calculate the greediest possible furthest move the robot can make"""
    fasteners = wood.fasteners

    if fasteners is None:
        raise ValueError("The wood must have fasteners for this algo to work!")

    # Track the furthest possible move for each fastener type
    furthest_move_for_fastener = []

    # Find the 'furthest cell' of each 'type' of cell
    for fastener_type in Fastener:
        fasteners_of_type = fasteners[fasteners[:, 2] == fastener_type]

        if len(fasteners_of_type) == 0:
            # If no fasteners of this type are present in the wood, at all
            continue

        highest_fastener = fasteners_of_type[np.argmax(fasteners_of_type[:, 0])][0]

        furthest_move_for = -float("inf")
        furthest_cell_for = -float("inf")
        for robot in cells:
            pick_probability = robot.params.pick_probabilities.get(fastener_type, 0)
            if pick_probability <= 0:
                # This robot can't pick this fastener
                continue
            delta = robot.params.end_pos - highest_fastener
            if delta >= furthest_move_for and robot.params.end_pos >= furthest_cell_for:
                furthest_move_for = delta
                furthest_cell_for = robot.params.end_pos

        if furthest_move_for >= 0:
            furthest_move_for_fastener.append(furthest_move_for)

    # Move the minimum furthest amount
    if len(furthest_move_for_fastener) == 0:
        return 0
    return cast(float, np.min(furthest_move_for_fastener))
