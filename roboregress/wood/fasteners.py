from enum import Enum
from typing import Dict, Tuple


class Fastener(Enum):
    """The 'wood' axis goes along the X."""

    OFFSET_NAIL = "folded_over_nail"

    FLUSH_NAIL = "flush_nail"

    STAPLE = "staple"

    SCREW = "screw"


FASTENER_COLORS: Dict[Fastener, Tuple[float, float, float]] = {
    Fastener.OFFSET_NAIL: (0.0, 0.0, 1.0),
    Fastener.FLUSH_NAIL: (0.8, 0.1, 0.5),
    Fastener.STAPLE: (0.0, 1.0, 0.0),
    Fastener.SCREW: (0.5, 1.0, 0.1),
}
