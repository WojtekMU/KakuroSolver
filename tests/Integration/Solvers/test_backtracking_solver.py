import copy
import pytest

from Fixtures.sample_puzzles import SAMPLE_PUZZLE_GRID, SAMPLE_PUZZLE_GRID_NO_SOLUTION
from src.Models.kakuro_model import KakuroModel
from src.Services.kakuro_service import KakuroService
from src.Solvers.backtracking_solver import BacktrackingSolver

def test_backtracking_solver():
    model = KakuroModel(copy.deepcopy(SAMPLE_PUZZLE_GRID))
    service = KakuroService(model)

    expected_grid = [
        ['X', (21, None), (6, None), (5, None), (10, None)],
        [(None, 21), 9, 6, 4, 2],
        [(None, 6), 6, (4, 4), 1, 3],
        [(None, 7), 4, 3, (7, 1), 1],
        [(None, 14), 2, 1, 7, 4]
    ]

    solver = BacktrackingSolver()

    solver.solve(service)

    assert expected_grid == service.model.grid

def test_backtracking_solver_empty():
    model = KakuroModel(copy.deepcopy(SAMPLE_PUZZLE_GRID_NO_SOLUTION))
    service = KakuroService(model)

    solver = BacktrackingSolver()

    assert solver.solve(service) == False