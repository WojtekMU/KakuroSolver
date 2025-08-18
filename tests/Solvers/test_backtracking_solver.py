import pytest

from src.Models.kakuro_model import KakuroModel
from src.Services.kakuro_service import KakuroService
from src.Solvers.backtracking_solver import BacktrackingSolver

SAMPLE_PUZZLE_GRID = [
    ["X",       (21, None), (6, None),  (5, None),  (10, None)],
    [(None,21), 9,          None,       None,       None],
    [(None, 6), None,       (4, 4),     None,       None],
    [(None, 7), None,       None,       (7, 1),     None],
    [(None,14), None,       None,       None,       None],
]

MODEL = KakuroModel(SAMPLE_PUZZLE_GRID)
SERVICE = KakuroService(MODEL)
SERVICE.MIN_VALUE = 1
SERVICE.MAX_VALUE = 9
SERVICE.MAX_SUM = 45

def test_backtracking_solver():
    expected_grid = [
        ['X', (21, None), (6, None), (5, None), (10, None)],
        [(None, 21), 9, 6, 4, 2],
        [(None, 6), 6, (4, 4), 1, 3],
        [(None, 7), 4, 3, (7, 1), 1],
        [(None, 14), 2, 1, 7, 4]
    ]

    solver = BacktrackingSolver()

    solver.solve(SERVICE)

    assert expected_grid == SERVICE.model.grid