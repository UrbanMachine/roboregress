from unittest.mock import Mock

from roboregress.robot.statistics import WorkTimeTracker


def test_time_tracker() -> None:
    runtime = Mock()
    runtime.timestamp = 0

    time_tracker = WorkTimeTracker(runtime=runtime)
    assert time_tracker.total_time_slacking == 0
    assert time_tracker.total_time_working == 0

    assert not time_tracker.currently_working
    with time_tracker.time():
        assert time_tracker.currently_working
        runtime.timestamp = 5

    assert time_tracker.total_time_working == 5
    assert time_tracker.total_time_slacking == 0

    runtime.timestamp = 7
    assert not time_tracker.currently_working
    with time_tracker.time():
        assert time_tracker.currently_working
        runtime.timestamp = 8
    assert time_tracker.total_time_working == 6
    assert time_tracker.total_time_slacking == 2
    assert time_tracker.total_time == 8
