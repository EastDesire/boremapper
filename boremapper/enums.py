from enum import IntEnum, auto


class DataVariant(IntEnum):
    RAW = auto()
    DISPLAYED = auto()


class DiagramAlign(IntEnum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()