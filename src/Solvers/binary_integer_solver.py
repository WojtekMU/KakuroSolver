from typing import Dict
from ortools.linear_solver import pywraplp

from src.Services.kakuro_service import KakuroService
from src.Types.types import CellPosition


class BinaryIntegerSolver:
    """
    Solver for Kakuro puzzles using binary integer linear programming.

    Uses OR-Tools' SCIP solver to model the puzzle with binary variables
    representing possible digit assignments, enforcing constraints on sums and uniqueness.
    """

    @staticmethod
    def create_variables(
        kakuro_service: KakuroService,
        solver: pywraplp.Solver
    ) -> Dict[CellPosition, Dict[int, pywraplp.Variable]]:
        """
        Creates binary decision variables for each empty and filled cell.

        For each cell, a set of binary variables corresponds to possible values,
        where exactly one must be set to 1 for empty cells; for filled cells,
        only the existing value has a variable set to 1.

        :param kakuro_service: Kakuro puzzle instance
        :param solver: OR-Tools solver instance
        :return: Dictionary mapping cell positions to dictionaries of value-variable pairs
        """
        variables: Dict[CellPosition, Dict[int, pywraplp.Variable]] = {}

        for row, column in kakuro_service.empty_cells:
            variables[(row, column)] = {
                value: solver.BoolVar(f'cell_{row}_{column}_{value}')
                for value in kakuro_service.domains[(row, column)]
            }

        for row, column in kakuro_service.filled_cells:
            value = kakuro_service.model.grid[row][column]
            variables[(row, column)] = {
                value: solver.BoolVar(f'cell_{row}_{column}_{value}')
            }

        return variables

    @staticmethod
    def create_clue_constraint(
        kakuro_service: KakuroService,
        solver: pywraplp.Solver,
        variables: Dict[CellPosition, Dict[int, pywraplp.Variable]],
        row: int,
        column: int,
        direction: str,
        target_sum: int
    ) -> None:
        """
        Adds constraints for a clue in either vertical or horizontal direction.

        Ensures each possible digit appears at most once in the clue's cells,
        and the sum of assigned values equals the clue's target sum.
        """
        cells = kakuro_service.clue_cells[(row, column, direction)]
        cell_variables = [variables[(r, c)] for r, c in cells]
        length = len(cells)

        for val in range(kakuro_service.MIN_VALUE, kakuro_service.MAX_VALUE):
            solver.Add(
                sum(cell_variables[i][val] for i in range(length) if val in cell_variables[i]) <= 1
            )

        sum_constraint = sum(
            val * cell_variables[i][val]
            for i in range(length)
            for val in cell_variables[i]
        )
        solver.Add(sum_constraint == target_sum)

    @staticmethod
    def create_constraints(
        kakuro_service: KakuroService,
        solver: pywraplp.Solver,
        variables: Dict[CellPosition, Dict[int, pywraplp.Variable]]
    ) -> None:
        """
        Adds constraints for the entire Kakuro puzzle to the solver.

        Enforces that each empty cell must be assigned exactly one value,
        and that clues' sum and uniqueness constraints hold.
        """
        for (row, column) in kakuro_service.empty_cells:
            solver.Add(sum(variables[(row, column)].values()) == 1)

        for (row, column), (vertical_sum, horizontal_sum) in kakuro_service.clues.items():
            if vertical_sum:
                BinaryIntegerSolver.create_clue_constraint(
                    kakuro_service, solver, variables, row, column, 'V', vertical_sum
                )
            if horizontal_sum:
                BinaryIntegerSolver.create_clue_constraint(
                    kakuro_service, solver, variables, row, column, 'H', horizontal_sum
                )

    def solve(self, kakuro_service: KakuroService) -> bool:
        """
        Solves the Kakuro puzzle by formulating it as a binary integer linear program.

        Creates variables and constraints, then uses SCIP solver to find an optimal
        assignment satisfying all constraints. Updates the Kakuro grid with the solution.

        :param kakuro_service: Kakuro puzzle instance to solve
        :return: True if a solution was found, False otherwise
        """
        solver: pywraplp.Solver = pywraplp.Solver.CreateSolver('SCIP')
        variables = self.create_variables(kakuro_service, solver)
        self.create_constraints(kakuro_service, solver, variables)
        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            for (row, column), values in variables.items():
                for value, variable in values.items():
                    if variable.solution_value() == 1:
                        kakuro_service.model.grid[row][column] = value
            return True

        return False

    def __str__(self) -> str:
        """
        Returns a string representation identifying the solver.
        """
        return "Binary Integer Solver"
