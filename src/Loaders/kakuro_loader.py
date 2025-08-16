import json
import os

from src.Types.types import PuzzleGrid


def load_puzzle_from_path(file_path: str) -> PuzzleGrid:
    """
    Loads a Kakuro puzzle grid from a JSON file and converts any lists to tuple objects.

    :param file_path: Path to the puzzle JSON file.
    :return: Loaded 2D puzzle grid.
    :raises FileNotFoundError: If the specified file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")

    with open(file_path, "r") as file:
        puzzle = json.load(file)

    for row in range(len(puzzle)):
        for column in range(len(puzzle[row])):
            if isinstance(puzzle[row][column], list):
                puzzle[row][column] = tuple(puzzle[row][column])

    return puzzle
