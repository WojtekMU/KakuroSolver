import pytest

from src.Models.kakuro_model import KakuroModel
from src.Services.kakuro_service import KakuroService

SAMPLE_PUZZLE_GRID = [
    ["X",       (21, None), (6, None),  (5, None),  (10, None)],
    [(None,21), 9,          None,       None,       None],
    [(None, 6), None,       (4, 4),     None,       None],
    [(None, 7), None,       None,       (7, 1),     None],
    [(None,14), None,       None,       None,       None],
]

MODEL = KakuroModel(SAMPLE_PUZZLE_GRID)
KakuroService.MIN_VALUE = 1
KakuroService.MAX_VALUE = 9
KakuroService.MAX_SUM = 45
SERVICE = KakuroService(MODEL)


def test_get_cells_in_clue_vertical():
    cells = SERVICE.get_cells_in_clue(0, 3, 'V')
    expected_cells = [(1, 3), (2, 3)]

    assert sorted(cells) == sorted(expected_cells)

def test_generate_possible_values():
    model = KakuroModel(SAMPLE_PUZZLE_GRID)
    service = KakuroService(model)
    service.MIN_VALUE = 1
    service.MAX_VALUE = 3
    service.MAX_SUM = 6

    expected_possible_values = {
        1: {
            1: {(1,)},
            2: {(2,)},
            3: {(3,)},
            4: set(),
            5: set(),
            6: set()
        },
        2: {
            1: set(),
            2: set(),
            3: {(1, 2)},
            4: {(1, 3)},
            5: {(2, 3)},
            6: set()
        },
        3: {
            1: set(),
            2: set(),
            3: set(),
            4: set(),
            5: set(),
            6: {(1, 2, 3)}
        }
    }

    service.generate_possible_values()

    assert expected_possible_values == service.POSSIBLE_VALUES

def test_get_cells_in_clue_horizontal():
    cells = SERVICE.get_cells_in_clue(3, 0, 'H')
    expected_cells = [(3, 1), (3, 2)]

    assert sorted(cells) == sorted(expected_cells)

def test_extract_clues():
    clues, _ = SERVICE.extract_clues()

    expected_clues = {
        (0, 1): (21, None),
        (0, 2): (6, None),
        (0, 3): (5, None),
        (0, 4): (10, None),
        (1, 0): (None, 21),
        (2, 0): (None, 6),
        (2, 2): (4, 4),
        (3, 0): (None, 7),
        (3, 3): (7, 1),
        (4, 0): (None, 14),
    }

    assert clues == expected_clues

def test_extract_clue_cells():
    _, clue_cells = SERVICE.extract_clues()

    expected_clue_cells = {
        (0, 1, "V"): [(1, 1), (2, 1), (3, 1), (4, 1)],
        (0, 2, "V"): [(1, 2)],
        (0, 3, "V"): [(1, 3), (2, 3)],
        (0, 4, "V"): [(1, 4), (2, 4), (3, 4), (4, 4)],
        (1, 0, "H"): [(1, 1), (1, 2), (1, 3), (1, 4)],
        (2, 0, "H"): [(2, 1)],
        (2, 2, "V"): [(3, 2), (4, 2)],
        (2, 2, "H"): [(2, 3), (2, 4)],
        (3, 0, "H"): [(3, 1), (3, 2)],
        (3, 3, "V"): [(4, 3)],
        (3, 3, "H"): [(3, 4)],
        (4, 0, "H"): [(4, 1), (4, 2), (4, 3), (4, 4)],
    }

    for key in expected_clue_cells:
        assert sorted(clue_cells[key]) == sorted(expected_clue_cells[key])

def test_extract_cell_clues():
    MODEL.clue_cells = {
        (0, 1, "V"): [(1, 1), (2, 1), (3, 1), (4, 1)],
        (0, 2, "V"): [(1, 2)],
        (0, 3, "V"): [(1, 3), (2, 3)],
        (0, 4, "V"): [(1, 4), (2, 4), (3, 4), (4, 4)],
        (1, 0, "H"): [(1, 1), (1, 2), (1, 3), (1, 4)],
        (2, 0, "H"): [(2, 1)],
        (2, 2, "V"): [(3, 2), (4, 2)],
        (2, 2, "H"): [(2, 3), (2, 4)],
        (3, 0, "H"): [(3, 1), (3, 2)],
        (3, 3, "V"): [(4, 3)],
        (3, 3, "H"): [(3, 4)],
        (4, 0, "H"): [(4, 1), (4, 2), (4, 3), (4, 4)],
    }

    cell_clues = SERVICE.extract_cell_clues()

    expected_cell_clues = {
        (1, 1): ((0, 1, 'V'), (1, 0, 'H')),
        (2, 1): ((0, 1, 'V'), (2, 0, 'H')),
        (3, 1): ((0, 1, 'V'), (3, 0, 'H')),
        (4, 1): ((0, 1, 'V'), (4, 0, 'H')),
        (1, 2): ((0, 2, 'V'), (1, 0, 'H')),
        (1, 3): ((0, 3, 'V'), (1, 0, 'H')),
        (2, 3): ((0, 3, 'V'), (2, 2, 'H')),
        (1, 4): ((0, 4, 'V'), (1, 0, 'H')),
        (2, 4): ((0, 4, 'V'), (2, 2, 'H')),
        (3, 4): ((0, 4, 'V'), (3, 3, 'H')),
        (4, 4): ((0, 4, 'V'), (4, 0, 'H')),
        (3, 2): ((2, 2, 'V'), (3, 0, 'H')),
        (4, 2): ((2, 2, 'V'), (4, 0, 'H')),
        (4, 3): ((3, 3, 'V'), (4, 0, 'H')),
    }

    for key in expected_cell_clues:
        assert sorted(cell_clues[key]) == sorted(expected_cell_clues[key])

def test_extract_empty_cells():
    empty_cells = SERVICE.extract_empty_cells()

    expected_empty_cells = [
        (1, 2), (1, 3), (1, 4),
        (2, 1), (2, 3), (2, 4),
        (3, 1), (3, 2), (3, 4),
        (4, 1), (4, 2), (4, 3), (4, 4),
    ]

    assert sorted(empty_cells) == sorted(expected_empty_cells)

def test_extract_filled_cells():
    filled_cells = SERVICE.extract_filled_cells()

    expected_filled_cells = [
        (1, 1),
    ]

    assert sorted(filled_cells) == sorted(expected_filled_cells)

def test_extract_domains():
    MODEL.clue_cells = {
        (0, 1, "V"): [(1, 1), (2, 1), (3, 1), (4, 1)],
        (0, 2, "V"): [(1, 2)],
        (0, 3, "V"): [(1, 3), (2, 3)],
        (0, 4, "V"): [(1, 4), (2, 4), (3, 4), (4, 4)],
        (1, 0, "H"): [(1, 1), (1, 2), (1, 3), (1, 4)],
        (2, 0, "H"): [(2, 1)],
        (2, 2, "V"): [(3, 2), (4, 2)],
        (2, 2, "H"): [(2, 3), (2, 4)],
        (3, 0, "H"): [(3, 1), (3, 2)],
        (3, 3, "V"): [(4, 3)],
        (3, 3, "H"): [(3, 4)],
        (4, 0, "H"): [(4, 1), (4, 2), (4, 3), (4, 4)],
    }

    MODEL.cell_clues = {
        (1, 1): ((0, 1, 'V'), (1, 0, 'H')),
        (2, 1): ((0, 1, 'V'), (2, 0, 'H')),
        (3, 1): ((0, 1, 'V'), (3, 0, 'H')),
        (4, 1): ((0, 1, 'V'), (4, 0, 'H')),
        (1, 2): ((0, 2, 'V'), (1, 0, 'H')),
        (1, 3): ((0, 3, 'V'), (1, 0, 'H')),
        (2, 3): ((0, 3, 'V'), (2, 2, 'H')),
        (1, 4): ((0, 4, 'V'), (1, 0, 'H')),
        (2, 4): ((0, 4, 'V'), (2, 2, 'H')),
        (3, 4): ((0, 4, 'V'), (3, 3, 'H')),
        (4, 4): ((0, 4, 'V'), (4, 0, 'H')),
        (3, 2): ((2, 2, 'V'), (3, 0, 'H')),
        (4, 2): ((2, 2, 'V'), (4, 0, 'H')),
        (4, 3): ((3, 3, 'V'), (4, 0, 'H')),
    }

    MODEL.empty_cells = [
        (1, 2), (1, 3), (1, 4),
        (2, 1), (2, 3), (2, 4),
        (3, 1), (3, 2), (3, 4),
        (4, 1), (4, 2), (4, 3), (4, 4),
    ]

    expected_domains = {
        (1, 2): [6],
        (1, 3): [1, 2, 3, 4],
        (1, 4): [1, 2, 3, 4],
        (2, 1): [6],
        (2, 3): [1, 3],
        (2, 4): [1, 3],
        (3, 1): [1, 2, 3, 4, 5, 6],
        (3, 2): [1, 3],
        (3, 4): [1],
        (4, 1): [1, 2, 3, 4, 5, 6, 7, 8],
        (4, 2): [1, 3],
        (4, 3): [7],
        (4, 4): [1, 2, 3, 4],
    }

    domains = SERVICE.extract_domains()

    for key in expected_domains:
        assert sorted(domains[key]) == sorted(expected_domains[key])

def test_is_solved_correct():
    grid = [
        ["X", (15, None), (8, None)],
        [(None, 15), 9, 6],
        [(None, 8), 6, 2],

    ]

    model = KakuroModel(grid)
    service = KakuroService(model)

    assert service.is_solved() == True

def test_is_solved_repetition():
    #Repetition of numbers in a row
    grid = [
        ["X", (15, None), (11, None)],
        [(None, 18), 9, 9],
        [(None, 8), 6, 2],

    ]

    model = KakuroModel(grid)
    service = KakuroService(model)

    assert service.is_solved() != True

def test_is_solved_not_filled():
    #Not all cells filled
    grid = [
        ["X", (15, None), (2, None)],
        [(None, 9), 9, None],
        [(None, 8), 6, 2],

    ]

    model = KakuroModel(grid)
    service = KakuroService(model)

    assert service.is_solved() != True

def test_is_solved_outside_upper_limit():
    #Value outside upper limit
    grid = [
        ["X", (16, None), (8, None)],
        [(None, 16), 10, 6],
        [(None, 8), 6, 2],

    ]

    model = KakuroModel(grid)
    service = KakuroService(model)

    assert service.is_solved() != True


def test_is_solved_outside_lower_limit():
    #Value outside lower limit
    grid = [
        ["X", (6, None), (8, None)],
        [(None, 6), 0, 6],
        [(None, 8), 6, 2],

    ]

    model = KakuroModel(grid)
    service = KakuroService(model)

    assert service.is_solved() != True

def test_is_solved_unsatisfied_clue():
    #Clue sum unsatisfied
    grid = [
        ["X", (6, None), (8, None)],
        [(None, 6), 2, 4],
        [(None, 8), 6, 2],

    ]

    model = KakuroModel(grid)
    service = KakuroService(model)

    assert service.is_solved() != True