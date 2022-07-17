import numpy as np
import pytest

from roboregress.robot.fasteners import Fastener
from roboregress.robot.surfaces import Surface
from roboregress.robot.wood import (
    _FASTENER_BUFFER_LEN,
    _FASTENER_IDX,
    _POSITION_IDX,
    _SURFACE_IDX,
    MovedWhileWorkActive,
    MoveScheduled,
    Wood,
)

_SOME_PARAMETERS = Wood.Parameters(
    fastener_densities={
        Fastener.STAPLE: 0.1,
        Fastener.FLUSH_NAIL: 5,
        Fastener.OFFSET_NAIL: 10,
        Fastener.SCREW: 0.01,
    }
)

_ZERO_DENSITY_PARAMS = Wood.Parameters(
    fastener_densities={fastener_type: 0 for fastener_type in Fastener}
)


def test_new_work_when_move_scheduled():
    """Test an exception is raised if work is attempted while a move is scheduled"""
    wood = Wood(parameters=_SOME_PARAMETERS)

    wood.schedule_move()

    with pytest.raises(MoveScheduled):
        with wood.work_lock():
            pass
    assert wood._ongoing_work == 0


def test_generates_board():
    wood = Wood(parameters=_SOME_PARAMETERS)
    _validate_fasteners_array(wood)


def test_0_fastener_density():
    """If no fasteners are created, then the fastener array should be None"""
    wood = Wood(parameters=_ZERO_DENSITY_PARAMS)
    assert wood._fasteners is None


def test_moving_wood_when_not_ready():
    wood = Wood(parameters=_SOME_PARAMETERS)

    with wood.work_lock():
        assert not wood.ready_for_move()

        with pytest.raises(MovedWhileWorkActive):
            wood.move(10)

    assert wood.ready_for_move()
    wood.move(10)


def test_moving_with_no_fastener_density():
    """Test the wood can be translated despite 0 density"""
    wood = Wood(parameters=_ZERO_DENSITY_PARAMS)
    assert wood._fasteners is None

    wood.move(99.5)
    assert wood._fasteners is None
    assert wood.processed_board == 99.5

    wood._params = _SOME_PARAMETERS
    wood.move(1.0)
    assert wood._fasteners is not None
    assert wood.processed_board == 100.5


def test_moving_wood():
    """Test that moving the wood translates the board and generates more board to
    backfill the buffer"""
    wood = Wood(parameters=_SOME_PARAMETERS)
    wood.schedule_move()
    assert wood._no_new_work

    _validate_fasteners_array(wood)
    assert wood.board_length == _FASTENER_BUFFER_LEN
    assert wood.processed_board == 0
    initial_highest_fastener_pos = np.max(wood._fasteners[:, _POSITION_IDX])

    wood.move(9.5)
    assert not wood._no_new_work, "This flag should have been cleared!"
    assert wood.processed_board == 9.5
    assert wood.board_length == _FASTENER_BUFFER_LEN + 9.5
    _validate_fasteners_array(wood)

    wood.move(1000)
    assert wood.processed_board == 1009.5
    _validate_fasteners_array(wood)

    final_highest_fastener_pos = np.max(wood._fasteners[:, _POSITION_IDX])
    assert initial_highest_fastener_pos + 1009.5 == final_highest_fastener_pos


def _validate_fasteners_array(wood: Wood):
    if wood._fasteners is None:
        assert all(d == 0 for d in wood._params.fastener_densities.values())
        return

    fasteners = wood._fasteners
    lowest_point = np.min(fasteners[:, _POSITION_IDX])

    # No fasteners should exist below the buffer line
    assert lowest_point > -_FASTENER_BUFFER_LEN

    # No fasteners should (in all likelyhood) have the exact same position
    assert len(set(fasteners[:, _POSITION_IDX])) == len(fasteners)

    # Validate fastener counts are close to the expected densities
    fastener_counts = {
        ft: np.count_nonzero(fasteners[:, _FASTENER_IDX] == ft) for ft in Fastener
    }
    # Quick logic check to make sure the test functions as expected
    assert sum(c for c in fastener_counts.values()) == len(fasteners)

    for fastener_type, fastener_count in fastener_counts.items():
        expected_count = round(
            wood._params.fastener_densities[fastener_type] * wood.board_length
        )
        assert np.isclose(expected_count, fastener_count)

    # Validate the types in each index of the array
    for cell in fasteners:
        assert isinstance(cell[_POSITION_IDX], float)
        assert isinstance(cell[_SURFACE_IDX], Surface)
        assert isinstance(cell[_FASTENER_IDX], Fastener)
