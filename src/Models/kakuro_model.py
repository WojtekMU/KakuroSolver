from src.Types.types import PuzzleGrid, CluesDict, ClueToCellsDict, CellToCluesDict, CellsList, CellDomainDict
from typing import Optional


class KakuroModel:
    """
    Represents the Kakuro puzzle.
    :param grid: 2D list representing the Kakuro grid.
    """
    def __init__(self, grid: PuzzleGrid) -> None:
        self.grid: PuzzleGrid = grid
        self.height: int = len(grid)
        self.width: int = len(grid[0])
        self.clues: Optional[CluesDict] = None
        self.clue_cells: Optional[ClueToCellsDict] = None
        self.empty_cells: Optional[CellsList] = None
        self.filled_cells: Optional[CellsList] = None
        self.cell_clues: Optional[CellToCluesDict] = None
        self.domains: Optional[CellDomainDict] = None