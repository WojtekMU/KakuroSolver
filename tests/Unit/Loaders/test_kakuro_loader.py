import json
import tempfile
import pytest

from Fixtures.sample_puzzles import SAMPLE_PUZZLE_GRID_SMALL
from src.Loaders.kakuro_loader import load_puzzle_from_path


def test_load_puzzle_success():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
        json.dump(SAMPLE_PUZZLE_GRID_SMALL, tmp_file)
        tmp_file_path = tmp_file.name

    loaded_puzzle = load_puzzle_from_path(tmp_file_path)

    assert isinstance(loaded_puzzle, list)
    assert all(isinstance(row, list) for row in loaded_puzzle)
    assert len(loaded_puzzle) == 3
    assert all(len(row) == 3 for row in loaded_puzzle)

    assert loaded_puzzle[0][0] == "X"
    assert isinstance(loaded_puzzle[0][0], str)

    assert loaded_puzzle[0][2] == (12, None)
    assert isinstance(loaded_puzzle[0][2], tuple)

    assert loaded_puzzle[2][0] == (None, 11)
    assert isinstance(loaded_puzzle[2][0], tuple)

    assert loaded_puzzle[1][1] == (3, 4)
    assert isinstance(loaded_puzzle[1][1], tuple)

    assert loaded_puzzle[1][2] == 4
    assert isinstance(loaded_puzzle[1][2], int)

    assert loaded_puzzle[2][2] is None


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_puzzle_from_path("non_existent_file.json")