from itertools import combinations

from src.Models.kakuro_model import KakuroModel
from src.Types.types import CluesDict, ClueToCellsDict, CellToCluesDict, CellsList, CellDomainDict, ClueSums
from typing import Dict, Set, Tuple


class KakuroService:
    """
    Provides logic for extracting clues, generating domains, validating solutions,
    and printing the puzzle grid.

    MIN_VALUE (int): The smallest allowed value in a Kakuro cell (default 1).
    MAX_VALUE (int): The largest allowed value in a Kakuro cell (default 9).
    MAX_SUM (int): The maximum possible sum for a clue, equal to the sum of all digits from MIN_VALUE to MAX_VALUE (i.e., 45 for 1–9).
    POSSIBLE_VALUES (Dict[int, Dict[int, Set[Tuple[int, ...]]]]): A precomputed
        lookup table mapping:
            - length of a run (int) →
            - target sum (int) →
            - set of valid tuples of digits (unique, non-repeating, within range)
              that satisfy the clue.
        This acts as a domain cache for efficient constraint checking.
    """
    MIN_VALUE: int = 1
    MAX_VALUE: int = 9
    MAX_SUM: int = sum(range(MIN_VALUE, MAX_VALUE + 1))
    POSSIBLE_VALUES: Dict[int, Dict[int, Set[Tuple[int, ...]]]] = {}

    def __init__(self, model: KakuroModel):
        """
        Initialize the Kakuro puzzle service with a given model.
        :param  model: Kakuro model representing the puzzle.
        """
        self.model = model
        self.clues, self.clue_cells = self.extract_clues()
        self.empty_cells = self.extract_empty_cells()
        self.filled_cells = self.extract_filled_cells()
        self.cell_clues = self.extract_cell_clues()

        if not self.POSSIBLE_VALUES:
            self.generate_possible_values()

        self.domains = self.extract_domains()

    def generate_possible_values(self) -> None:
        """
        Generate all unique digit combinations for clue lengths and their sums.
        These are stored in POSSIBLE_VALUES for efficient lookup.
        """
        self.POSSIBLE_VALUES = {length: {s: set() for s in range(self.MIN_VALUE, self.MAX_SUM + 1)} for length in range(1, self.MAX_VALUE - self.MIN_VALUE + 2)}

        for length in range(1, self.MAX_VALUE - self.MIN_VALUE + 2):
            for combination in combinations(range(self.MIN_VALUE, self.MAX_VALUE + 1), length):
                if sum(combination) <= self.MAX_SUM:
                    self.POSSIBLE_VALUES[length][sum(combination)].add(combination)

    def get_cells_in_clue(self, row: int, column: int, direction: str) -> CellsList:
        """
        Get all cells influenced by a given clue.
        :param row: Row index of the clue cell
        :param column: Column index of the clue cell
        :param direction: 'V' for vertical, 'H' for horizontal
        :return: List of cell positions affected by the clue
        """
        cells: CellsList = []
        d_row, d_column = (1, 0) if direction == 'V' else (0, 1)
        row, column = row + d_row, column + d_column

        while (0 <= row < self.model.height and
               0 <= column < self.model.width and
               (self.model.grid[row][column] is None or isinstance(self.model.grid[row][column], int))):
            cells.append((row, column))
            row, column = row + d_row, column + d_column

        return cells

    def extract_clues(self) -> Tuple[CluesDict, ClueToCellsDict]:
        """
        Extract all clue cells and map them to the cells they affect.
        :return: (clues, clue_cells) tuple, clues: Dict of clue positions, clue_cells: Dict of clues to list of affected cell positions
        """
        clues: CluesDict = {}
        clue_cells: ClueToCellsDict = {}

        for row in range(self.model.height):
            for column in range(self.model.width):
                if isinstance(self.model.grid[row][column], tuple):
                    vertical_sum, horizontal_sum = self.model.grid[row][column]
                    clues[(row, column)] = (vertical_sum, horizontal_sum)

                    vertical_cells = self.get_cells_in_clue(row, column, 'V')
                    horizontal_cells = self.get_cells_in_clue(row, column, 'H')

                    if vertical_cells:
                        clue_cells[(row, column, 'V')] = vertical_cells
                    if horizontal_cells:
                        clue_cells[(row, column, 'H')] = horizontal_cells

        return clues, clue_cells

    def extract_cell_clues(self) -> CellToCluesDict:
        """
        Create a mapping from each cell to the clues it belongs to.
        :return: Dictionary mapping cell to vertical clue and horizontal clue.
        """
        cell_clues: CellToCluesDict = {}

        for (clue_row, clue_column, direction), cells in self.clue_cells.items():
            for (cell_row, cell_column) in cells:
                if (cell_row, cell_column) not in cell_clues:
                    cell_clues[(cell_row, cell_column)] = (None, None)

                if direction == 'V':
                    cell_clues[(cell_row, cell_column)] = ((clue_row, clue_column, 'V'), cell_clues[(cell_row, cell_column)][1])
                elif direction == 'H':
                    cell_clues[(cell_row, cell_column)] = (cell_clues[(cell_row, cell_column)][0], (clue_row, clue_column, 'H'))

        return cell_clues

    def extract_empty_cells(self) -> CellsList:
        """
        Get all empty cells.
        :return: List of cells.
        """
        return [(row, column) for row in range(self.model.height) for column in range(self.model.width) if self.model.grid[row][column] is None]

    def extract_filled_cells(self) -> CellsList:
        """
        Get all currently filled cells.
        :return: List of cells.
        """
        return [(row, column) for row in range(self.model.height) for column in range(self.model.width) if isinstance(self.model.grid[row][column], int)]


    def extract_domains(self) -> CellDomainDict:
        """
        Calculate the domain (possible values) for each empty cell based on the clues.
        :return: Dictionary mapping each cell to a list of valid values.
        """
        domains: CellDomainDict = {}

        for (row, column) in self.empty_cells:
            possible_values = set(range(self.MIN_VALUE, self.MAX_VALUE + 1))
            vertical_clue, horizontal_clue = self.cell_clues[(row, column)]
            if vertical_clue:
                vertical_sum = self.model.grid[vertical_clue[0]][vertical_clue[1]][0]
                vertical_cells = self.clue_cells[(vertical_clue[0], vertical_clue[1], 'V')]
                vertical_used_numbers = {self.model.grid[row][column] for row, column in vertical_cells if self.model.grid[row][column] is not None}
                length = len(vertical_cells)

                if vertical_sum:
                    valid_combinations = {combination for combination in self.POSSIBLE_VALUES[length][vertical_sum] if vertical_used_numbers.issubset(combination)}
                    possible_values &= {value for combination in valid_combinations for value in combination}

                possible_values -= vertical_used_numbers

            if horizontal_clue:
                horizontal_sum = self.model.grid[horizontal_clue[0]][horizontal_clue[1]][1]
                horizontal_cells = self.clue_cells[(horizontal_clue[0], horizontal_clue[1], 'H')]
                horizontal_used_numbers = {self.model.grid[row][column] for row, column in horizontal_cells if self.model.grid[row][column] is not None}
                length = len(horizontal_cells)

                if horizontal_sum:
                    valid_combinations = {combination for combination in self.POSSIBLE_VALUES[length][horizontal_sum] if horizontal_used_numbers.issubset(combination)}
                    possible_values &= {value for combination in valid_combinations for value in combination}

                possible_values -= horizontal_used_numbers

            domains[(row, column)] = list(possible_values)

        return domains


    def is_solved(self) -> bool:
        """
        Check if the current model satisfies all Kakuro rules.
        :return: True if valid, False otherwise.
        """
        for (clue_row, clue_column), (vertical_sum, horizontal_sum) in self.clues.items():
            if vertical_sum:
                vertical_cells = self.clue_cells[(clue_row, clue_column, 'V')]
                values = [self.model.grid[row][column] for row, column in vertical_cells]

                if not all(isinstance(value, int) and self.MIN_VALUE <= value <= self.MAX_VALUE for value in values):
                    return False

                if sum(values) != vertical_sum or len(set(values)) != len(values):
                    return False

            if horizontal_sum:
                horizontal_cells = self.clue_cells[(clue_row, clue_column, 'H')]
                values = [self.model.grid[row][column] for row, column in horizontal_cells]

                if not all(isinstance(value, int) and self.MIN_VALUE <= value <= self.MAX_VALUE for value in values):
                    return False

                if sum(values) != horizontal_sum or len(set(values)) != len(values):
                    return False

        return True

    @staticmethod
    def format_clue(clue: ClueSums) -> str:
        """
        Formats a clue cell for display in a Kakuro puzzle.

        :param clue: A tuple (down_sum, right_sum) representing the clue values.
                     Each value can be an integer or None if no clue exists in that direction.
        :return: A string in the format "down\\right", "\\right", "down\\", or a space
                 if both values are None.
        """
        down, right = clue
        down_str = str(down) if down is not None else ''
        right_str = str(right) if right is not None else ''

        if down and right:
            return f"{down_str}\\{right_str}"
        elif down:
            return f"{down_str}\\"
        elif right:
            return f"\\{right_str}"
        else:
            return " "

    def print_grid(self) -> None:
        """
        Prints the Kakuro puzzle in a human-readable format.

        The grid is expected to be a 2D list where each cell can be:
          - 'X': a black cell with no clues,
          - a tuple (down_sum, right_sum): a clue cell,
          - an integer: a filled white cell,
          - None: an empty white cell.

        :return: None
        """
        for row in self.model.grid:
            row_str = ""

            for cell in row:
                if cell == 'X':
                    row_str += " ███ "
                elif isinstance(cell, tuple):
                    clue_text = self.format_clue(cell)
                    row_str += f"{clue_text:^5}"
                else:
                    val = str(cell) if cell is not None else '.'
                    row_str += f"  {val}  "

            print(row_str)