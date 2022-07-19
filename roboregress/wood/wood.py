import contextlib
import random
from typing import Dict, Generator, List, Optional

import numpy as np
import numpy.typing as npt
from pydantic import BaseModel

from .fasteners import Fastener
from .surfaces import Surface


class MoveScheduled(Exception):
    """Raised when work is attempted but a move of the wood has been scheduled"""


class MovedWhileWorkActive(Exception):
    """Raised when an attempt is made to move the wood while work is happening on it"""


# Create constants to represent the API for the fastener array
_POSITION_IDX = 0
_SURFACE_IDX = 1
_FASTENER_IDX = 2

_FASTENER_BUFFER_LEN = 10
"""How many meters of fasteners to have generated before the first cell of the robot.
This number will keep fasteners populated in the region from -buffer_len -> 0.0"""


class Wood:
    class Parameters(BaseModel):
        fastener_densities: Dict[Fastener, float]
        """Number of fasteners per meter, adjuster for each fastener type"""

    def __init__(self, parameters: Parameters) -> None:
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

        self._total_translated = 0.0
        """The amount of translation the board has gone through"""

    @property
    def processed_board(self) -> float:
        """How much board has entered the robot"""
        return self._total_translated

    @property
    def board_length(self) -> float:
        """The length of the board including the buffer that hasn't been processed"""
        return self._total_translated + _FASTENER_BUFFER_LEN

    @contextlib.contextmanager
    def work_lock(self) -> Generator[None, None, None]:
        """Lock the workpiece in order to pick"""
        if self._no_new_work:
            raise MoveScheduled()

        self._ongoing_work += 1
        yield
        self._ongoing_work -= 1

    def pick(
        self,
        from_surface: Surface,
        start_pos: float,
        end_pos: float,
        pick_probabilities: Dict[Fastener, float],
        n_fasteners_to_sample: Optional[int] = 1,
    ) -> List[Fastener]:
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
        :return: The types of successfully picked fasteners
        """
        if self._ongoing_work == 0:
            raise ValueError("Hey, you must acquire the work lock in order to operate!")

        if start_pos < 0 or end_pos <= 0 or start_pos >= end_pos:
            raise ValueError(f"Invalid pick range! {start_pos=} {end_pos=}")

        if self._fasteners is None:
            return []

        fasteners_in_range_mask = np.logical_and(
            self._fasteners[:, _POSITION_IDX] > start_pos,
            self._fasteners[:, _POSITION_IDX] <= end_pos,
        )
        fasteners_on_surface_mask = self._fasteners[:, _SURFACE_IDX] == from_surface
        pickable_fasteners_mask = np.logical_and(fasteners_in_range_mask, fasteners_on_surface_mask)

        pickable_fasteners = self._fasteners[pickable_fasteners_mask]

        # Randomly select up to 'n_fasteners_to_sample' from the group
        if n_fasteners_to_sample is None or len(pickable_fasteners) <= n_fasteners_to_sample:
            fasteners_to_attempt = pickable_fasteners
        else:
            choices = np.random.choice(
                len(pickable_fasteners), n_fasteners_to_sample, replace=False
            )
            assert len(choices) == n_fasteners_to_sample
            fasteners_to_attempt = pickable_fasteners[choices]

        picks: List[Fastener] = []
        for fastener in fasteners_to_attempt:
            fastener_type = fastener[_FASTENER_IDX]
            pick_probability = pick_probabilities.get(fastener_type, 0.0)
            if random.random() > pick_probability:
                # The pick failed
                continue

            # Proceed to remove the fastener from the array
            index = np.where(np.all(self._fasteners == fastener, axis=-1))[0][0]
            self._fasteners = np.delete(self._fasteners, index, axis=0)

            # Track the pick
            picks.append(fastener_type)
        return picks

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
            raise MovedWhileWorkActive()

        # "translate" all fasteners by adding the distance
        if self._fasteners is not None:
            self._fasteners[:, _POSITION_IDX] += distance

        # Backfill the new empty space in the buffer
        self._fasteners = self.generate_board(
            start_pos=-_FASTENER_BUFFER_LEN,
            end_pos=-_FASTENER_BUFFER_LEN + distance,
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
        fastener_densities: Dict[Fastener, float],
        append_to: Optional[npt.NDArray[np.float64]] = None,
    ) -> Optional[npt.NDArray[np.float64]]:
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
            raise ValueError("Length cannot be invalid!")

        board = append_to
        length = end_pos - start_pos

        for fastener_type, density in fastener_densities.items():
            n_fasteners = int(round(length * density))

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
                board = new_fasteners if board is None else np.concatenate((board, new_fasteners))

        return board