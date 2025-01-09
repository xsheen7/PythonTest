from enum import Enum
from cell import Cell

class PlacementType(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical" 
    SHIFT_LEFT = "shift_left"
    SHIFT_RIGHT = "shift_right"
    DIAGONAL_RIGHT = "diagonal_right"
    DIAGONAL_LEFT = "diagonal_left"

class Placement:
    def __init__(self, cell: Cell, type: PlacementType):
        self.cell = cell
        self.type = type 