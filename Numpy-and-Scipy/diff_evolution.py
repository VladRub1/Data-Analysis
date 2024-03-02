
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import random
from scipy.stats import qmc
import math


def differential_evolution(fobj, bounds, mutation_coefficient=0.5,
                           crossover_coefficient=0.5, population_size=50, iterations=50,
                           init_setting='random', mutation_setting='rand1',
                           selection_setting='current', p_min=0.1, p_max=0.2):
    # Initializing the population and obtaining primary results
    SEED = 7
    random.seed(SEED)
    np.random.seed(SEED)
    bounds = np.array(bounds)
    dimensions = len(bounds)
    # Random initialization
    if init_setting == 'LatinHypercube':
        population = qmc.LatinHypercube(dimensions, seed=SEED)
        assert population.__class__ == qmc.LatinHypercube
        population = population.random(n=population_size)
    elif init_setting == 'Halton':
        population = qmc.Halton(dimensions, seed=SEED)
        assert population.__class__ == qmc.Halton
        population = population.random(n=population_size)
    elif init_setting == 'Sobol':
        population = qmc.Sobol(dimensions, seed=SEED)
        assert population.__class__ == qmc.Sobol
        population = population.random(n=population_size)
    else:
        population = np.random.rand(population_size, dimensions)
    min_bound, max_bound = bounds.T
    diff = np.fabs(min_bound - max_bound)
    population_denorm = min_bound + population * diff
    fitness = np.asarray([fobj(ind) for ind in population_denorm])
    # Find the best index
    best_idx = np.argmin(fitness)
    best = population_denorm[best_idx]
    for iteration in range(iterations):
        for population_index in range(population_size):
            idxs = np.setdiff1d(np.arange(population_size), [best_idx, population_index], assume_unique=True)
            # Selection of three random elements
            # Mutation operator
            if mutation_setting == 'rand2':
                a, b, c, d, e = population[np.random.choice(idxs, 5, replace=False)]
                mutant = np.clip(a + mutation_coefficient * (b - c) + mutation_coefficient * (d - e), 0, 1)

                assert 'e' in locals(), "This assert checks that you have written the formula accurately"
                assert 'd' in locals(), "This assert checks that you have written the formula accurately"
            elif mutation_setting == 'best1':
                # sort by target function
                argsort = np.argsort(fitness)
                # remove the best object and the current one
                argsort_no_best_and_cur = argsort[np.isin(argsort, [best_idx, population_index], invert=True)]
                # take the best of the rest
                index_of_best1 = argsort_no_best_and_cur[0]
                # remove the best of the remaining ones from the selection list
                idxs = np.delete(idxs, np.where(idxs == index_of_best1)[0])
                # select two more objects
                b, c = population[np.random.choice(idxs, 2, replace=False)]

                assert index_of_best1 not in idxs,  "This assertion verifies that you will not use the chosen one object to select b and c so that you do not repeat yourself"
                assert index_of_best1 != population_index, "This assert verifies that you have not taken the index of the current individual"
                assert index_of_best1 != best_idx, "This assert verifies that you have not taken the index of the best individual"
                if iteration == 0:
                    for idx in idxs: assert np.array_equal(population[index_of_best1], population[idx]) is False, "This assert verifies that the selected index is correct"
                    assert np.array_equal(population[index_of_best1], population[population_index]) is False, "This assert verifies that the selected index is correct"
                    assert np.array_equal(population[index_of_best1], population[best_idx]) is False, "This assert verifies that the selected index is correct"

                mutant = np.clip(population[index_of_best1] + mutation_coefficient * (b - c), 0, 1)
            elif mutation_setting == 'rand_to_p_best1':
                p = np.random.uniform(p_min, p_max)  # don't delete
                # sort by target function
                argsort = np.argsort(fitness)
                # remove the best object and the current one
                argsort_no_best_and_cur = argsort[np.isin(argsort, [best_idx, population_index], invert=True)]
                # take a quantile
                to_choose = argsort_no_best_and_cur[:int(len(argsort_no_best_and_cur) * p)]
                # select one object from those in the quantile
                index_of_rand_to_p_best1 = np.random.choice(to_choose, 1, replace=False)[0]
                # delete the taken object
                idxs = np.delete(idxs, np.where(idxs == index_of_rand_to_p_best1)[0])
                # select two more objects
                b, c = population[np.random.choice(idxs, 2, replace=False)]

                assert 'a' not in locals()
                assert index_of_rand_to_p_best1 not in idxs, "This assertion verifies that you will not use the chosen one object to select b and c so that you do not repeat yourself"
                assert index_of_rand_to_p_best1 != population_index, "This assert verifies that you have not taken the index of the current individual"
                assert index_of_rand_to_p_best1 != best_idx, "This assert verifies that you have not taken the index of the best individual"
                if iteration == 0:
                    for idx in idxs: assert np.array_equal(population[index_of_rand_to_p_best1], population[idx]) is False, "This assert verifies that the selected index is correct"
                    assert np.array_equal(population[index_of_rand_to_p_best1], population[population_index]) is False, "This assert verifies that the selected index is correct"
                    assert np.array_equal(population[index_of_rand_to_p_best1], population[best_idx]) is False, "This assert verifies that the selected index is correct"

                mutant = np.clip(population[index_of_rand_to_p_best1] + mutation_coefficient * (b - c), 0, 1)
            else:
                a, b, c = population[np.random.choice(idxs, 3, replace = False)]
                mutant = np.clip(a + mutation_coefficient * (b - c), 0, 1)
            # Crossover operator
            cross_points = np.random.rand(dimensions) < crossover_coefficient
            if not np.any(cross_points):
                cross_points[np.random.randint(0, dimensions)] = True
            # Recombination (replacement with mutant values)
            trial = np.where(cross_points, mutant, population[population_index])
            trial_denorm = min_bound + trial * diff
            # Offspring's valuation
            result_of_evolution = fobj(trial_denorm)
            # Breeding
            if selection_setting == 'worst':
                selection_index = np.argmax(fitness)
            elif selection_setting == 'random_among_worst':
                # make a mask of objects worse than the current one
                bad_mask = fitness > result_of_evolution
                if np.sum(bad_mask) > 0:
                    # take the ones that are worse and pick one out of them 
                    bad_guys = np.nonzero(bad_mask)[0]
                    selection_index = np.random.choice(bad_guys, 1, replace=False)
                else:
                    # If there aren't any, we take this object 
                    selection_index = population_index
            elif selection_setting == 'random_selection':
                selection_index = np.random.choice(idxs, 1)
            else:
                selection_index = population_index
            if result_of_evolution < fitness[selection_index]:
                fitness[selection_index] = result_of_evolution
                population[selection_index] = trial
                if result_of_evolution < fitness[best_idx]:
                    best_idx = selection_index
                    best = trial_denorm
        yield best, fitness[best_idx]
