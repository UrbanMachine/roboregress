import contextlib
import random
from collections import Counter
from collections.abc import Generator

import numpy as np
import numpy.typing as npt
import open3d as o3d
from pydantic import BaseModel

from ..engine import BaseSimObject
from ..engine.base_simulation_object import LoopGenerator
from ..robot.vis_constants import WOOD_DIST_FROM_CELL_CENTER
from .fasteners import FASTENER_COLORS, Fastener
from .surfaces import SURFACE_NORMALS, Surface


class MoveScheduled(Exception):
    """Raised when work is attempted but a move of the wood has been scheduled"""


class MovedWhileWorkActive(Exception):
    """Raised when an attempt is made to move the wood while work is happening on it"""


# Create constants to represent the API for the fastener array
POSITION_IDX = 0
SURFACE_IDX = 1
FASTENER_IDX = 2

_FASTENER_BUFFER_LEN = 10
"""How many meters of fasteners to have generated before the first cell of the robot.
This number will keep fasteners populated in the region from -buffer_len -> 0.0"""


class Wood(BaseSimObject):
    class Parameters(BaseModel):
        fastener_densities: dict[Fastener, float]
        """Number of fasteners per meter, adjuster for each fastener type"""

    def __init__(self, parameters: Parameters) -> None:
        super().__init__()

        assert len(parameters.fastener_densities) == len(
            Fastener
        ), "All fastener types must be specified!"

        self._params = parameters
        self._no_new_work = False
        """When True, attempting to get work_lock will raise an exception"""
        self._ongoing_work = 0
        """Number of holders of a work_lock"""

        self._fasteners = self.generate_board(
            start_pos=-_FASTENER_BUFFER_LEN,
            end_pos=0,
            fastener_densities=self._params.fastener_densities,
        )
        """A numpy array of shape (n_fasteners, 3) where the first index is the
        position, the second index is the surface, and the third index is the type of
        fastener."""

        self._total_picked_fasteners: int = 0
        self._total_translated = 0.0
        """The amount of translation the board has gone through"""

    @property
    def processed_board(self) -> float:
        """How much board has entered the robot"""
        return self._total_translated

    @property
    def total_picked_fasteners(self) -> int:
        """How much board has entered the robot"""
        return self._total_picked_fasteners

    def missed_fasteners(self, after_pos: float = 0) -> dict[Fastener, int]:
        """Count how many fasteners of each type exist past the given position mark"""
        if self._fasteners is None:
            return {}

        missed_fasteners = self._fasteners[self._fasteners[:, POSITION_IDX] > after_pos]
        missed_fastener_types = missed_fasteners[:, FASTENER_IDX].tolist()
        missed = dict(Counter(missed_fastener_types))
        return {f: missed.get(f, 0) for f in Fastener}

    @property
    def board_length(self) -> float:
        """The length of the board including the buffer that hasn't been processed"""
        return self._total_translated + _FASTENER_BUFFER_LEN

    @property
    def fasteners(self) -> npt.NDArray[np.float64] | None:
        if self._fasteners is None:
            return self._fasteners
        return self._fasteners.copy()

    @contextlib.contextmanager
    def work_lock(self) -> Generator[None, None, None]:
        """Lock the workpiece in order to pick"""
        if self._no_new_work:
            raise MoveScheduled

        self._ongoing_work += 1
        yield
        self._ongoing_work -= 1

    def pick(
        self,
        from_surface: Surface,
        start_pos: float,
        end_pos: float,
        pick_probabilities: dict[Fastener, float],
        n_fasteners_to_sample: int | None = 1,
    ) -> tuple[list[Fastener], bool]:
        """
        :param from_surface: What surface to attempt picking from
        :param start_pos: The 'start' of the picking range
        :param end_pos: The 'end' of the picking range
        :param pick_probabilities: The probability of picking any of the types of
            fasteners
        :param n_fasteners_to_sample: The number of fasteners to 'sample' for a pick.
            This is useful for things like a rake that can attempt multiple picks at
            once. If None, all fasteners in the range will be 'attempted' at once.
        :raises ValueError: If invalid parameters
        :return: A tuple of:
            - The types of successfully picked fasteners
            - Whether or not a pick was even attempted
        """
        if self._ongoing_work == 0:
            raise ValueError("Hey, you must acquire the work lock in order to operate!")

        if start_pos < 0 or end_pos <= 0 or start_pos >= end_pos:
            raise ValueError(f"Invalid pick range! {start_pos=} {end_pos=}")

        if self._fasteners is None:
            return [], False

        fasteners_in_range_mask = np.logical_and(
            self._fasteners[:, POSITION_IDX] > start_pos,
            self._fasteners[:, POSITION_IDX] <= end_pos,
        )
        fasteners_on_surface_mask = self._fasteners[:, SURFACE_IDX] == from_surface
        pickable_fasteners_mask = np.logical_and(
            fasteners_in_range_mask, fasteners_on_surface_mask
        )

        # Now filter for fastener types that have nonzero chance of being picked
        pickable_fastener_types = list(pick_probabilities)
        for fastener_type in Fastener:
            if fastener_type not in pickable_fastener_types:
                # Filter out unpickable fasteners
                pickable_fasteners_mask = np.logical_and(
                    pickable_fasteners_mask,
                    self._fasteners[:, FASTENER_IDX] != fastener_type,
                )

        # Finally, apply the mask to select only pickable fasteners
        pickable_fasteners = self._fasteners[pickable_fasteners_mask]

        # Randomly select up to 'n_fasteners_to_sample' from the group
        if (
            n_fasteners_to_sample is None
            or len(pickable_fasteners) <= n_fasteners_to_sample
        ):
            fasteners_to_attempt = pickable_fasteners
        else:
            choices = np.random.choice(
                len(pickable_fasteners), n_fasteners_to_sample, replace=False
            )
            assert len(choices) == n_fasteners_to_sample
            fasteners_to_attempt = pickable_fasteners[choices]

        picks: list[Fastener] = []

        for fastener in fasteners_to_attempt:
            fastener_type = fastener[FASTENER_IDX]

            pick_probability = pick_probabilities[fastener_type]
            assert pick_probability > 0

            if random.random() > pick_probability:
                # The pick failed
                continue

            # Proceed to remove the fastener from the array
            index = np.where(np.all(self._fasteners == fastener, axis=-1))[0][0]
            self._fasteners = np.delete(self._fasteners, index, axis=0)

            # Track the pick
            picks.append(fastener_type)

        # Do some sanity checks here
        attempted_pick = len(fasteners_to_attempt) > 0

        self._total_picked_fasteners += len(picks)
        return picks, attempted_pick

    def schedule_move(self) -> None:
        self._no_new_work = True

    def ready_for_move(self) -> bool:
        return self._ongoing_work == 0

    def move(self, distance: float) -> None:
        """Translate the wood forward

        :param distance: Distance to move wood, in meters
        :raises ValueError: If the distance is negative
        :raises MovedWhileWorkActive: If called while a picker is active on the wood
        """
        if distance <= 0:
            raise ValueError("Hey now, distance must be nonzero and positive!")

        if not self.ready_for_move():
            raise MovedWhileWorkActive

        # "translate" all fasteners by adding the distance
        if self._fasteners is not None:
            self._fasteners[:, POSITION_IDX] += distance

        # Backfill the new empty space in the buffer
        end_pos = -_FASTENER_BUFFER_LEN + distance
        if end_pos != -_FASTENER_BUFFER_LEN:
            # Sometimes, the distance is technically nonzero, but once added with the
            # buffer len, it becomes == buffer len due to floating point math.
            self._fasteners = self.generate_board(
                start_pos=-_FASTENER_BUFFER_LEN,
                end_pos=end_pos,
                fastener_densities=self._params.fastener_densities,
                append_to=self._fasteners,
            )

        # Clear the work-blocking flag
        self._no_new_work = False

        # Update the board length
        self._total_translated += distance

    @staticmethod
    def generate_board(
        start_pos: float,
        end_pos: float,
        fastener_densities: dict[Fastener, float],
        append_to: npt.NDArray[np.float64] | None = None,
    ) -> npt.NDArray[np.float64] | None:
        """Returns a board array
        :param start_pos: Which position to 'start' placing fasteners in
        :param end_pos: Which position to 'stop' placing fasteners in
        :param fastener_densities: The densities of fasteners in 'fasteners / meter'
        :param append_to: The generated board will be appended to the this array and
            returned.

        :raises ValueError: If the board length is negative
        :return: The fastener array
        """
        """Returns more board"""
        if not end_pos > start_pos:
            raise ValueError(f"Length cannot be invalid! {start_pos=} {end_pos=}")

        board = append_to
        length = end_pos - start_pos

        for fastener_type, density in fastener_densities.items():
            # Figure out how many fasteners to generate of this type
            n_fasteners = length * density
            if (n_fasteners % 1) > random.random():
                # Take care of any 'remainder' by using random chance to add 1 fastener
                n_fasteners += 1
            n_fasteners = int(n_fasteners)

            new_fasteners = np.array(
                [
                    (
                        random.random() * length + start_pos,
                        random.choice(list(Surface)),
                        fastener_type,
                    )
                    for _ in range(n_fasteners)
                ]
            )
            if len(new_fasteners):
                board = (
                    new_fasteners
                    if board is None
                    else np.concatenate((board, new_fasteners))
                )

        return board

    # Sim object methods
    def _loop(self) -> LoopGenerator:
        """Wood doesn't do anything in the sim, it only handles visualizations"""
        while True:
            yield None

    def draw(self) -> list[o3d.geometry.Geometry]:
        # Create a point cloud with colored points for each surface
        if self._fasteners is None:
            return []

        point_cloud = o3d.geometry.PointCloud()
        for fastener_type in Fastener:
            # Create the list of points representing the fasteners on this surface
            fasteners = self._fasteners[
                self._fasteners[:, FASTENER_IDX] == fastener_type
            ]
            points_on_surface = np.zeros((len(fasteners), 3))
            points_on_surface[:, 0] = fasteners[:, POSITION_IDX].copy()

            # Translate it so the line of points is 'closer' to the appropriate surface
            for i in range(len(points_on_surface)):
                surface = fasteners[i, SURFACE_IDX]
                translate = (
                    np.array(SURFACE_NORMALS[surface]) * WOOD_DIST_FROM_CELL_CENTER
                )
                points_on_surface[i] += translate

            # Create the point cloud and paint it appropriately
            surface_cloud = o3d.geometry.PointCloud()
            surface_cloud.points = o3d.utility.Vector3dVector(points_on_surface)
            surface_cloud.paint_uniform_color(FASTENER_COLORS[fastener_type])
            point_cloud += surface_cloud

        return [point_cloud]
