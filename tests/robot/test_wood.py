import numpy as np
import pytest

from roboregress.wood import Fastener, Surface
from roboregress.wood.wood import (
    _FASTENER_BUFFER_LEN,
    FASTENER_IDX,
    POSITION_IDX,
    SURFACE_IDX,
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


def test_new_work_when_move_scheduled() -> None:
    """Test an exception is raised if work is attempted while a move is scheduled"""
    wood = Wood(parameters=_SOME_PARAMETERS)

    wood.schedule_move()

    with pytest.raises(MoveScheduled), wood.work_lock():
        pass
    assert wood._ongoing_work == 0


def test_generates_board() -> None:
    wood = Wood(parameters=_SOME_PARAMETERS)
    _validate_fasteners_array(wood)


def test_0_fastener_density() -> None:
    """If no fasteners are created, then the fastener array should be None"""
    wood = Wood(parameters=_ZERO_DENSITY_PARAMS)
    assert wood._fasteners is None


def test_moving_wood_when_not_ready() -> None:
    wood = Wood(parameters=_SOME_PARAMETERS)

    with wood.work_lock():
        assert not wood.ready_for_move()

        with pytest.raises(MovedWhileWorkActive):
            wood.move(10)

    assert wood.ready_for_move()
    wood.move(10)


@pytest.mark.parametrize(
    ("n_fasteners_to_sample", "pick_probabilities", "expected_min_picks"),
    (
        (5, {f: 1.0 for f in Fastener}, 5),
        (None, {f: 1.0 for f in Fastener}, 20),
        (None, {}, 0),
        (1000, {}, 0),
        (1000, {f: 1.0 for f in Fastener}, 20),
    ),
)
def test_pick(
    n_fasteners_to_sample: int | None,
    pick_probabilities: dict[Fastener, float],
    expected_min_picks: int,
) -> None:
    wood = Wood(parameters=_SOME_PARAMETERS)

    # Move some wood into 'view'
    wood.move(10)

    # Try picking 5 fasteners
    fasteners_arr_before = np.copy(wood._fasteners)  # type: ignore
    with wood.work_lock():
        picked_fasteners, attempted_pick = wood.pick(
            from_surface=Surface.TOP,
            n_fasteners_to_sample=n_fasteners_to_sample,
            pick_probabilities=pick_probabilities,
            start_pos=0,
            end_pos=10,
        )
    assert attempted_pick is (expected_min_picks > 0)
    assert len(picked_fasteners) >= expected_min_picks

    assert len(fasteners_arr_before) - len(wood._fasteners) == len(picked_fasteners)  # type: ignore


def test_pick_samples_from_only_pickable_fastener_pytest() -> None:
    """Test that when selecting fasteners from the wood array, only the fasteners with a
    pick probability > 0 are selected to be chosen"""
    # Create wood beam where all the fasteners are super common except screws
    wood = Wood(
        parameters=Wood.Parameters(
            fastener_densities={
                Fastener.STAPLE: 10,
                Fastener.FLUSH_NAIL: 11,
                Fastener.OFFSET_NAIL: 12,
                Fastener.SCREW: 1,
            }
        )
    )

    wood.move(100)

    with wood.work_lock():
        picks, attempted_pick = wood.pick(
            from_surface=Surface.TOP,
            start_pos=0,
            end_pos=100,
            pick_probabilities={Fastener.SCREW: 1},
            n_fasteners_to_sample=1,
        )
    assert len(picks) == 1
    assert picks[0] is Fastener.SCREW
    assert attempted_pick


def test_pick_null_fasteners() -> None:
    """Validate that running 'pick' when there are no fasteners doesn't break"""
    wood = Wood(parameters=_ZERO_DENSITY_PARAMS)
    wood.move(100)

    with wood.work_lock():
        picked_fasteners, attempted_pick = wood.pick(
            from_surface=Surface.TOP,
            n_fasteners_to_sample=9999,
            pick_probabilities={f: 1.0 for f in Fastener},
            start_pos=0,
            end_pos=10,
        )
        assert not attempted_pick
        assert len(picked_fasteners) == 0


def test_moving_with_no_fastener_density() -> None:
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


def test_moving_wood() -> None:
    """Test that moving the wood translates the board and generates more board to
    backfill the buffer"""

    wood = Wood(parameters=_SOME_PARAMETERS)
    wood.schedule_move()
    assert wood._no_new_work

    _validate_fasteners_array(wood)
    assert wood.board_length == _FASTENER_BUFFER_LEN
    assert wood.processed_board == 0

    fasteners = wood._fasteners
    assert fasteners is not None
    initial_highest_fastener_pos = np.max(fasteners[:, POSITION_IDX])

    wood.move(9.5)
    assert not wood._no_new_work, "This flag should have been cleared!"
    assert wood.processed_board == 9.5
    assert wood.board_length == _FASTENER_BUFFER_LEN + 9.5
    _validate_fasteners_array(wood)

    wood.move(1000)
    assert wood.processed_board == 1009.5
    _validate_fasteners_array(wood)

    final_highest_fastener_pos = np.max(wood._fasteners[:, POSITION_IDX])
    assert initial_highest_fastener_pos + 1009.5 == final_highest_fastener_pos


def _validate_fasteners_array(wood: Wood) -> None:
    if wood._fasteners is None:
        assert all(d == 0 for d in wood._params.fastener_densities.values())
        return

    fasteners = wood._fasteners
    lowest_point = np.min(fasteners[:, POSITION_IDX])

    # No fasteners should exist below the buffer line
    assert lowest_point > -_FASTENER_BUFFER_LEN

    # No fasteners should (in all likelyhood) have the exact same position
    assert len(set(fasteners[:, POSITION_IDX])) == len(fasteners)

    # Validate fastener counts are close to the expected densities
    fastener_counts = {
        ft: np.count_nonzero(fasteners[:, FASTENER_IDX] == ft) for ft in Fastener
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
        assert isinstance(cell[POSITION_IDX], float)
        assert isinstance(cell[SURFACE_IDX], Surface)
        assert isinstance(cell[FASTENER_IDX], Fastener)
