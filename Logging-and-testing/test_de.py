import pytest
import numpy as np

from differential_evolution import DifferentialEvolution


def rastrigin(array, A=10):
    return A * 2 + (array[0] ** 2 - A * np.cos(2 * np.pi * array[0])) + (
                array[1] ** 2 - A * np.cos(2 * np.pi * array[1]))


# CONSTANTS
BOUNDS = np.array([[-20, 20], [-20, 20]])
FOBJ = rastrigin

"""
Your goal is to achieve 100% coverage of DifferentialEvolution tests
Separate the different steps of logic testing into different functions
Start the test command:
pytest -s test_de.py --cov-report=json --cov

or [for windows]

python -m pytest -s test_de.py --cov-report=json --cov
"""


def test_constants():
    """
    This test checks that after at least one iteration
    all class attributes are not None or an empty list
    """
    de = DifferentialEvolution(FOBJ, BOUNDS)
    de._init_population()

    for _ in range(1):
        de.iterate()

    assert de.a is not None
    assert de.b is not None
    assert de.c is not None
    assert de.mutant is not None
    assert de.population is not None
    assert de.idxs is not None
    assert len(de.fitness) > 0
    assert de.min_bound is not None
    assert de.max_bound is not None
    assert de.diff is not None
    assert de.population_denorm is not None
    assert de.best_idx is not None
    assert de.best is not None
    assert de.cross_points is not None


def test_result_more_than_0():
    """
    This test verifies that the result of the algorithm
    is not negative for a small number of iterations
    """
    de = DifferentialEvolution(FOBJ, BOUNDS)
    de._init_population()

    for _ in range(5):
        de.iterate()

    res = de.fitness[de.best_idx]

    assert res > 0


def test_correctness_of_algorithm():
    """
    The test checks if the Differential Evolution algorithm 
    is correctly implemented (going down to the minimum)
    """
    res = []

    for _ in range(100):
        # test 100 times
        de = DifferentialEvolution(FOBJ, BOUNDS)
        de._init_population()

        for _ in range(100):
            # make 200 iterations
            de.iterate()
        # adding result of the run
        res.append(de.fitness[de.best_idx])

    res_np = np.array(res)

    assert res_np.min() < 1e-14
    assert res_np.max() < 2
    assert (res_np < 1e-10).sum() > 50


def test_convergence():
    """
    The test checks the convergence of the algorithm 
    with default parameters for 200 iterations for 95% of runs
    """
    res = []  # results list

    for _ in range(100):
        # test 100 times
        de = DifferentialEvolution(FOBJ, BOUNDS)
        de._init_population()

        for _ in range(200):
            # make 200 iterations
            de.iterate()
        # adding result of the run
        res.append(de.fitness[de.best_idx])

    res_np = np.array(res)

    assert (res_np == 0).sum() >= 95
