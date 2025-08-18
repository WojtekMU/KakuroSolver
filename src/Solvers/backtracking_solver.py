from src.Services.kakuro_service import KakuroService


class BacktrackingSolver:
    """
    A solver class that applies a backtracking algorithm to solve a Kakuro puzzle.
    """

    def backtracking(self, kakuro_service: KakuroService) -> bool:
        """
        Recursively attempts to fill the Kakuro grid using backtracking.

        :param kakuro_service: Kakuro instance with current puzzle state
        :return: True if a valid solution is found, False otherwise
        """
        if not kakuro_service.empty_cells:
            return True

        row, column = min(kakuro_service.empty_cells, key=lambda cell: len(kakuro_service.domains[cell]))
        kakuro_service.empty_cells.remove((row, column))

        for value in sorted(kakuro_service.domains[(row, column)], reverse=True):
            kakuro_service.model.grid[row][column] = value
            kakuro_service.domains = kakuro_service.extract_domains()

            if self.backtracking(kakuro_service):
                return True

            kakuro_service.model.grid[row][column] = None

        kakuro_service.empty_cells.append((row, column))

        return False

    def solve(self, kakuro_service: KakuroService) -> bool:
        """
        Solves the given Kakuro puzzle using backtracking.

        :param kakuro_service: Kakuro instance to solve
        :return: True if the puzzle was solved successfully, False otherwise
        """
        return self.backtracking(kakuro_service)

    def __str__(self) -> str:
        """
        String representation of the solver.
        :return: A simple string indicating the solver type
        """
        return "Backtracking Solver"
