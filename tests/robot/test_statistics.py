from roboregress.robot.statistics import RobotStats


def test_robot_stats():
    robo_stats = RobotStats("bingus")

    assert robo_stats.total_time_slacking == 0
    assert robo_stats.total_time_working == 0

    robo_stats.start_working(0)
    robo_stats.stop_working(5)

    assert robo_stats.total_time_working == 5
    assert robo_stats.total_time_slacking == 0

    robo_stats.start_working(7)
    robo_stats.stop_working(8)
    assert robo_stats.total_time_working == 6
    assert robo_stats.total_time_slacking == 2
