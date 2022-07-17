from abc import ABC, abstractmethod
from typing import Generator, Optional

LoopGenerator = Generator[Optional[float], None, None]


class BaseSimObject(ABC):
    """An object that can be run by the simulation runtime"""

    def __init__(self) -> None:
        self._loop_generator: Optional[LoopGenerator] = None

    def step(self) -> Optional[float]:
        """Checks if this object has an instantiated loop and runs it."""
        if self._loop_generator is None:
            self._loop_generator = self._loop()
        return next(self._loop_generator)

    @abstractmethod
    def _loop(self) -> LoopGenerator:
        """A generator that yields either None or a float.

        :yields: The amount of time to sleep for, or None
        - If None, that means that the function wants to yield back to the runtime,
          until the all other `run` loops have been called.

        - If a number, that means don't continue this function until the timestamp has
          incremented that exact amount.

        """
