from typing import Dict, Tuple, List, Optional, Any, Set
from itertools import permutations
from ortools.sat.python import cp_model

from src.Services.kakuro_service import KakuroService
from src.Types.types import CellPosition


class ConstraintSolver:
    """
    Solver for Kakuro puzzles using constraint programming with OR-Tools CP-SAT solver.

    Models cells as integer variables with domain restrictions,
    applies sum and uniqueness constraints from clues,
    and supports forbidding previously found solutions to explore alternatives.
    """

    ALL_DIFFERENT = [(2, 3), (2, 4), (2, 16), (2, 17), (3, 6), (3, 7), (3, 23), (3, 24), (4, 10), (4, 11), (4, 29),
                     (4, 30), (5, 15), (5, 16), (5, 34), (5, 35), (6, 21), (6, 22), (6, 38), (6, 39), (7, 28), (7, 29),
                     (7, 41), (7, 42), (8, 36), (8, 37), (8, 38), (8, 39), (8, 40), (8, 41), (8, 42), (8, 43), (8, 44),
                     (9, 45)]

    @staticmethod
    def compute_all_different(
        possible_values: Dict[int, Dict[int, Set[Tuple[int, ...]]]]
    ) -> List[CellPosition]:
        """
        Computes all (length, sum) pairs from POSSIBLE_VALUES that have exactly one solution.

        :param possible_values: Nested dictionary: length -> sum -> set of valid digit tuples
        :return: List of (length, sum) pairs with a unique solution
        """
        all_different: List[CellPosition] = []

        for length, sums in possible_values.items():
            if length > 1:
                for s, solutions in sums.items():
                    if len(solutions) == 1:
                        all_different.append((length, s))
        return all_different

    @staticmethod
    def create_variables(
        kakuro_service: KakuroService,
        model: cp_model.CpModel
    ) -> Dict[CellPosition, cp_model.IntVar]:
        """
        Creates integer variables for all cells in the Kakuro grid.

        For empty cells, variables have domains based on possible values.
        For filled cells, variables are fixed to their existing value.
        """
        variables: Dict[CellPosition, cp_model.IntVar] = {}

        for row, column in kakuro_service.empty_cells:
            domain = kakuro_service.domains[(row, column)]

            if domain:
                variables[(row, column)] = model.NewIntVarFromDomain(
                    cp_model.Domain.FromValues(domain),
                    f'cell_{row}_{column}'
                )
            else:
                variables[(row, column)] = model.NewIntVar(kakuro_service.MIN_VALUE, kakuro_service.MAX_VALUE, f'cell_{row}_{column}')

        for row, column in kakuro_service.filled_cells:
            value: int = kakuro_service.model.grid[row][column]
            variables[(row, column)] = model.NewIntVar(value, value, f'cell_{row}_{column}')

        return variables

    @staticmethod
    def create_clue_constraint(
        kakuro_service: KakuroService,
        model: cp_model.CpModel,
        variables: Dict[CellPosition, cp_model.IntVar],
        row: int,
        column: int,
        direction: str,
        target_sum: int
    ) -> None:
        """
        Adds constraints enforcing the clue's sum and uniqueness conditions.
        """
        cells = kakuro_service.clue_cells[(row, column, direction)]
        variables_in_clue = [variables[(r, c)] for r, c in cells]

        if variables_in_clue:
            length = len(variables_in_clue)

            if (length, target_sum) in ConstraintSolver.ALL_DIFFERENT:
                model.AddAllDifferent(variables_in_clue)
            else:
                valid_combinations = kakuro_service.POSSIBLE_VALUES[length][target_sum]
                valid_tuples = []

                for comb in valid_combinations:
                    for perm in permutations(comb):
                        if all(
                                perm[i] in kakuro_service.domains.get(cells[i], [kakuro_service.model.grid[cells[i][0]][cells[i][1]]])
                            for i in range(length)
                        ):
                            valid_tuples.append(list(perm))

                model.AddAllowedAssignments(variables_in_clue, valid_tuples)

    @staticmethod
    def create_constraints(
        kakuro_service: KakuroService,
        model: cp_model.CpModel,
        variables: Dict[CellPosition, cp_model.IntVar]
    ) -> None:
        """
        Adds all clue constraints to the CP model for the puzzle.
        """
        for (row, column), (vertical_sum, horizontal_sum) in kakuro_service.clues.items():
            if vertical_sum:
                ConstraintSolver.create_clue_constraint(kakuro_service, model, variables, row, column, 'V', vertical_sum)
            if horizontal_sum:
                ConstraintSolver.create_clue_constraint(kakuro_service, model, variables, row, column, 'H', horizontal_sum)

    def solve(self, kakuro_service: KakuroService) -> bool:
        """
        Attempts to solve the Kakuro puzzle using constraint programming.
        """
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()

        variables = self.create_variables(kakuro_service, model)
        self.create_constraints(kakuro_service, model, variables)

        status = solver.Solve(model)
        if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
            for (row, column), var in variables.items():
                kakuro_service.model.grid[row][column] = solver.Value(var)
            return True

        return False

    def __str__(self) -> str:
        """Returns the name of the solver."""
        return "Constraint Solver"