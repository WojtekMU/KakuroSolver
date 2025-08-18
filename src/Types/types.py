from typing import Dict, List, Optional, Set, Tuple, Union

CellPosition = Tuple[int, int]
ClueSums = Tuple[Optional[int], Optional[int]]
CellValue = Union[CellPosition, str, int]
PuzzleGrid = List[List[CellValue]]
CluesDict = Dict[CellPosition, ClueSums]
ClueToCellsDict = Dict[Tuple[int, int, str], List[CellPosition]]
CellToCluesDict = Dict[CellPosition, Tuple[Optional[Tuple[int, int, str]], Optional[Tuple[int, int, str]]]]
CellsList = List[CellPosition]
CellDomainDict = Dict[CellPosition, List[int]]