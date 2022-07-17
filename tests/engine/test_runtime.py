import math
from typing import Generator, Optional

import pytest

from roboregress.engine import (
    BaseSimObject,
    EngineRuntime,
    NoObjectsToStep,
    NoTimestampProgression,
)


class BasicObject(BaseSimObject):
    def __init__(self, delay: Optional[float]):
        super().__init__()
        self.delay = delay
        self.call_count = 0

    def _loop(self) -> Generator[Optional[float], None, None]:
        while True:
            self.call_count += 1
            yield self.delay


def test_step() -> None:
    runtime = EngineRuntime()

    obj_no_delay = BasicObject(delay=None)
    obj_small_delay = BasicObject(delay=1.0)
    obj_large_delay = BasicObject(delay=1.1)

    runtime.register(obj_small_delay)
    runtime.register(obj_large_delay)
    runtime.register(obj_no_delay)

    # FIRST STEP
    runtime.step()

    # Loop generators should have been created for each object
    assert obj_no_delay.call_count == 1
    assert obj_small_delay.call_count == 1
    assert obj_large_delay.call_count == 1

    # Two of three of the objects should be 'asleep', the other should not
    assert runtime._sleeping_objects == {
        obj_small_delay: obj_small_delay.delay,
        obj_large_delay: obj_large_delay.delay,
    }

    # The timestamp should not have changed
    assert runtime.timestamp == 0

    # SECOND STEP
    runtime.step()

    # The timestamp should now be equivalent to the object with the smallest delay
    assert runtime.timestamp == obj_small_delay.delay

    # Validate call counts
    assert obj_no_delay.call_count == 2, "No delay means it must be called every step!"
    assert obj_small_delay.call_count == 2, "Should be called again"
    assert obj_large_delay.call_count == 1, "Should not have been called again"

    # Two of three objects should still be asleep
    assert runtime._sleeping_objects == {
        # This means that the small delay obj should have been triggered, run, and then
        # scheduled again
        obj_small_delay: obj_small_delay.delay * 2,
        obj_large_delay: obj_large_delay.delay,
    }

    # THIRD STEP
    runtime.step()
    assert runtime.timestamp == obj_large_delay.delay

    # Validate call counts
    assert obj_no_delay.call_count == 3, "No delay means it must be called every step!"
    assert obj_small_delay.call_count == 2, "Should not have been called again"
    assert obj_large_delay.call_count == 2, "Should have been called again"

    # Check that the large_delay obj is now put back to sleep
    assert runtime._sleeping_objects == {
        # This means that the small delay obj should have been triggered, run, and then
        # scheduled again
        obj_small_delay: obj_small_delay.delay * 2,
        obj_large_delay: obj_large_delay.delay * 2,
    }


def test_fails_if_step_doesnt_change_timestamp():
    """Test that an exception is raised if the timestamp isn't incremented between
    two steps"""
    engine = EngineRuntime()
    obj_a = BasicObject(delay=None)
    obj_b = BasicObject(delay=None)

    engine.register(obj_a)
    engine.register(obj_b)

    with pytest.raises(NoTimestampProgression):
        engine.step_until(timestamp=100)

    assert obj_a.call_count == 2
    assert obj_a.call_count == 2


def test_stepping_without_objects_fails():
    engine = EngineRuntime()
    with pytest.raises(NoObjectsToStep):
        engine.step()


def test_step_until():
    engine = EngineRuntime()
    obj_a = BasicObject(delay=1.1)
    engine.register(obj_a)

    engine.step_until(100)

    assert obj_a.call_count == 92
    assert math.isclose(engine.timestamp, 100.1)
