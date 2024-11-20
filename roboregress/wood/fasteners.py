from enum import Enum


class Fastener(Enum):
    """The 'wood' axis goes along the X."""

    OFFSET_NAIL = "offset_nail"

    FLUSH_NAIL = "flush_nail"

    STAPLE = "staple"

    SCREW = "screw"


FASTENER_COLORS: dict[Fastener, tuple[float, float, float]] = {
    Fastener.OFFSET_NAIL: (0.0, 0.0, 1.0),
    Fastener.FLUSH_NAIL: (1.0, 0.2, 1.0),
    Fastener.STAPLE: (1.0, 0.1, 0.1),
    Fastener.SCREW: (0.1, 1.0, 0.1),
}
