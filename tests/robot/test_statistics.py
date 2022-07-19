from unittest.mock import Mock

from roboregress.robot.statistics import RobotStats


def test_robot_stats():
    runtime = Mock()
    robo_stats = RobotStats("bingus", runtime=runtime)
    assert robo_stats.total_time_slacking == 0
    assert robo_stats.total_time_working == 0

    runtime.timestamp = 0
    assert not robo_stats.currently_working
    with robo_stats.track_work_time():
        assert robo_stats.currently_working
        runtime.timestamp = 5

    assert robo_stats.total_time_working == 5
    assert robo_stats.total_time_slacking == 0

    runtime.timestamp = 7
    assert not robo_stats.currently_working
    with robo_stats.track_work_time():
        assert robo_stats.currently_working
        runtime.timestamp = 8
    assert robo_stats.total_time_working == 6
    assert robo_stats.total_time_slacking == 2
    assert robo_stats.total_time == 8
