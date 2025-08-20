import pytest
from ortools.linear_solver import pywraplp

from Fixtures.sample_puzzles import SAMPLE_PUZZLE_GRID, SAMPLE_PUZZLE_GRID_NO_SOLUTION
from src.Models.kakuro_model import KakuroModel
from src.Services.kakuro_service import KakuroService
from src.Solvers.binary_integer_solver import BinaryIntegerSolver

def test_create_variables():
    model = KakuroModel(SAMPLE_PUZZLE_GRID)
    service = KakuroService(model)

    solver = pywraplp.Solver.CreateSolver('SCIP')
    variables = BinaryIntegerSolver.create_variables(service, solver)
    print(variables)

    assert len(variables[(1, 2)]) == 1
    assert len(variables[(4, 1)]) == 8

def test_create_clue_constraint_adds_constraints():
    model = KakuroModel(SAMPLE_PUZZLE_GRID)
    service = KakuroService(model)

    solver = pywraplp.Solver.CreateSolver('SCIP')
    variables = BinaryIntegerSolver.create_variables(service, solver)

    BinaryIntegerSolver.create_clue_constraint(
        service, solver, variables, 2, 2, "H", 4
    )

    assert solver.NumConstraints() == 9

def test_create_constraints_applies_all_rules():
    model = KakuroModel(SAMPLE_PUZZLE_GRID)
    service = KakuroService(model)

    solver = pywraplp.Solver.CreateSolver('SCIP')
    variables = BinaryIntegerSolver.create_variables(service, solver)

    BinaryIntegerSolver.create_constraints(service, solver, variables)


    assert solver.NumConstraints() == 121


def test_binary_integer_solver():
    model = KakuroModel(SAMPLE_PUZZLE_GRID)
    service = KakuroService(model)

    expected_grid = [
        ['X', (21, None), (6, None), (5, None), (10, None)],
        [(None, 21), 9, 6, 4, 2],
        [(None, 6), 6, (4, 4), 1, 3],
        [(None, 7), 4, 3, (7, 1), 1],
        [(None, 14), 2, 1, 7, 4]
    ]

    solver = BinaryIntegerSolver()

    solver.solve(service)

    assert expected_grid == service.model.grid

def test_binary_integer_solver_no_solution():
    model = KakuroModel(SAMPLE_PUZZLE_GRID_NO_SOLUTION)
    service = KakuroService(model)

    solver = BinaryIntegerSolver()

    assert solver.solve(service) == False