import enum

class Phase(enum.Enum):
    """Three types of phases for each cell"""
    experimental = 0
    breakthrough = 1
    incremental = 2
