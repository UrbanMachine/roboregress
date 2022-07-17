from enum import Enum


class Fastener(Enum):
    """The 'wood' axis goes along the X."""

    OFFSET_NAIL = "folded_over_nail"

    FLUSH_NAIL = "flush_nail"

    STAPLE = "staple"

    SCREW = "screw"
