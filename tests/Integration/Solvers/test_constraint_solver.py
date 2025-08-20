import copy

import pytest
from ortools.sat.python import cp_model

from src.Models.kakuro_model import KakuroModel
from src.Services.kakuro_service import KakuroService
from src.Solvers.constraint_solver import ConstraintSolver
from Fixtures.sample_puzzles import SAMPLE_PUZZLE_GRID, SAMPLE_PUZZLE_GRID_NO_SOLUTION

def test_compute_all_different():
    model = KakuroModel(copy.deepcopy(SAMPLE_PUZZLE_GRID))
    service = KakuroService(model)

    expected_all_different = [(2, 3), (2, 4), (2, 16), (2, 17), (3, 6), (3, 7), (3, 23), (3, 24), (4, 10), (4, 11), (4, 29),
                     (4, 30), (5, 15), (5, 16), (5, 34), (5, 35), (6, 21), (6, 22), (6, 38), (6, 39), (7, 28), (7, 29),
                     (7, 41), (7, 42), (8, 36), (8, 37), (8, 38), (8, 39), (8, 40), (8, 41), (8, 42), (8, 43), (8, 44),
                     (9, 45)]

    all_different = ConstraintSolver.compute_all_different(service.POSSIBLE_VALUES)

    assert sorted(all_different) == sorted(expected_all_different)

def test_create_variables():
    model = KakuroModel(copy.deepcopy(SAMPLE_PUZZLE_GRID))
    service = KakuroService(model)

    solver = ConstraintSolver()
    cp_model_instance = cp_model.CpModel()
    variables = solver.create_variables(service, cp_model_instance)

    assert len(variables) == len(service.empty_cells) + len(service.filled_cells)
    assert variables[(1, 2)].Name() == "cell_1_2"
    assert variables[(4, 1)].Name() == "cell_4_1"

def test_create_clue_constraint_adds_constraints():
    model = KakuroModel(copy.deepcopy(SAMPLE_PUZZLE_GRID))
    service = KakuroService(model)

    solver = ConstraintSolver()
    cp_model_instance = cp_model.CpModel()
    variables = solver.create_variables(service, cp_model_instance)

    solver.create_clue_constraint(service, cp_model_instance, variables, 2, 2, "H", 4)

    assert len(cp_model_instance.Proto().constraints) == 1

def test_create_constraints_applies_all_rules():
    model = KakuroModel(copy.deepcopy(SAMPLE_PUZZLE_GRID))
    service = KakuroService(model)

    solver = ConstraintSolver()
    cp_model_instance = cp_model.CpModel()
    variables = solver.create_variables(service, cp_model_instance)

    solver.create_constraints(service, cp_model_instance, variables)

    assert len(cp_model_instance.Proto().constraints) == 12

def test_constraint_solver():
    model = KakuroModel(copy.deepcopy(SAMPLE_PUZZLE_GRID))
    service = KakuroService(model)

    expected_grid = [
        ['X', (21, None), (6, None), (5, None), (10, None)],
        [(None, 21), 9, 6, 4, 2],
        [(None, 6), 6, (4, 4), 1, 3],
        [(None, 7), 4, 3, (7, 1), 1],
        [(None, 14), 2, 1, 7, 4]
    ]

    solver = ConstraintSolver()

    solver.solve(service)

    assert expected_grid == service.model.grid

def test_constraint_solver_no_solution():
    model = KakuroModel(copy.deepcopy(SAMPLE_PUZZLE_GRID_NO_SOLUTION))
    service = KakuroService(model)

    solver = ConstraintSolver()

    assert solver.solve(service) == False