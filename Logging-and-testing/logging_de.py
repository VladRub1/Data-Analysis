import logging
import copy
import numpy as np

"""
The task:

1. Using the code from `differential_evolution.py`, write your own logger that logs every run and every logical step of the algorithm's operation
2. Your logger should save logs with 1, 2, 3 logging levels to the file `logging_de.log`
3. If the result of the algorithm is greater than 1e-3, log the result with the ERROR level. If the result is greater than 1e-1, then CRITICAL. 
    Also, the log should reflect the algorithm parameters such as initial population, population size, number of iterations, etc.
4. ERROR and CRITICAL should be saved to the errors.log file.
5. Write your formatter to reflect: 
    a. Logging time in datetime format
    b. The name of the logger
    c. Logging level
    d. The action that was performed

IMPORTANT! 
All code should be written in this file, without touching the original `differential_evolution.py` file
"""


# define two loggers: one for levels 1-3 and one for levels 4-5
logger_low_lev = logging.getLogger("low_level_log")
logger_low_lev.setLevel(logging.DEBUG)  # set logging level to minimum

logger_high_lev = logging.getLogger("high_level_log")  # leave the default level 4+

# define a different handler for each logger
handler_for_logger_low_lev = logging.FileHandler("logging_de.log", mode='w')
handler_for_logger_high_lev = logging.FileHandler("errors.log", mode='w')

# define a formatter for each logger
# based on docs: https://docs.python.org/3/library/logging.html#logrecord-attributes
handler_for_logger_low_lev.setFormatter(logging.Formatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s"))
handler_for_logger_high_lev.setFormatter(logging.Formatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s"))

# adding handlers to loggers
logger_low_lev.addHandler(handler_for_logger_low_lev)
logger_high_lev.addHandler(handler_for_logger_high_lev)


class DifferentialEvolution:
    def __init__(self, fobj, bounds, mutation_coefficient=0.8, crossover_coefficient=0.7, population_size=20):

        self.fobj = fobj
        self.bounds = bounds
        self.mutation_coefficient = mutation_coefficient
        self.crossover_coefficient = crossover_coefficient
        self.population_size = population_size
        self.dimensions = len(self.bounds)

        self.a = None
        self.b = None
        self.c = None
        self.mutant = None
        self.population = None
        self.idxs = None
        self.fitness = []
        self.min_bound = None
        self.max_bound = None
        self.diff = None
        self.population_denorm = None
        self.best_idx = None
        self.best = None
        self.cross_points = None
        self.init_population = None  # add for error logs

    def _init_population(self):
        self.population = np.random.rand(self.population_size, self.dimensions)
        self.init_population = copy.deepcopy(self.population)  # add for error logs
        self.min_bound, self.max_bound = self.bounds.T

        self.diff = np.fabs(self.min_bound - self.max_bound)
        self.population_denorm = self.min_bound + self.population * self.diff
        self.fitness = np.asarray([self.fobj(ind) for ind in self.population_denorm])

        self.best_idx = np.argmin(self.fitness)
        self.best = self.population_denorm[self.best_idx]
    
    def _mutation(self):
        self.a, self.b, self.c = self.population[np.random.choice(self.idxs, 3, replace = False)]
        self.mutant = np.clip(self.a + self.mutation_coefficient * (self.b - self.c), 0, 1)
        return self.mutant
    
    def _crossover(self):
        cross_points = np.random.rand(self.dimensions) < self.crossover_coefficient
        if not np.any(cross_points):
            cross_points[np.random.randint(0, self.dimensions)] = True
        return cross_points

    def _recombination(self, population_index):

        trial = np.where(self.cross_points, self.mutant, self.population[population_index])
        trial_denorm = self.min_bound + trial * self.diff
        return trial, trial_denorm
    
    def _evaluate(self, result_of_evolution, population_index):
        if result_of_evolution < self.fitness[population_index]:
                self.fitness[population_index] = result_of_evolution
                self.population[population_index] = self.trial
                if result_of_evolution < self.fitness[self.best_idx]:
                    self.best_idx = population_index
                    self.best = self.trial_denorm

    def iterate(self):
    
        for population_index in range(self.population_size):
            self.idxs = [idx for idx in range(self.population_size) if idx != population_index]

            # originally wanted to add debug logs below, but decided to comment them out as they were clogging up the logs
            self.mutant = self._mutation()
            # logger_low_lev.debug(f"The mutation operator is done")
            self.cross_points = self._crossover()
            # logger_low_lev.debug(f"The operator of the crossover is done")

            self.trial, self.trial_denorm = self._recombination(population_index)
            # logger_low_lev.debug(f"The recombination operator is done")
    
            result_of_evolution = self.fobj(self.trial_denorm)

            self._evaluate(result_of_evolution, population_index)
            # logger_low_lev.debug(f"Evaluation of the offspring is done. Selection of an individual for the next generation is done")


def rastrigin(array, A=10):
    return A * 2 + (array[0] ** 2 - A * np.cos(2 * np.pi * array[0])) + (array[1] ** 2 - A * np.cos(2 * np.pi * array[1]))


if __name__ == "__main__":

    function_obj = rastrigin
    bounds_array = np.array([[-20, 20], [-20, 20]]), np.array([[-10, 50], [-10, 60]]), np.array([[-0, 110], [-42, 32]])
    steps_array = [40, 100, 200]
    mutation_coefficient_array = [0.5, 0.6, 0.3]
    crossover_coefficient_array = [0.5, 0.6, 0.3]
    population_size_array = [20, 30, 40, 50, 60]

    # make launch id to make it easier to search for errors in the logs
    application_id = 0

    for bounds in bounds_array:
        for steps in steps_array:
            for mutation_coefficient in mutation_coefficient_array:
                for crossover_coefficient in crossover_coefficient_array:
                    for population_size in population_size_array:

                        logger_low_lev.info(f"[id={application_id}] Starting the Differential Evolution algorithm")

                        de_solver = DifferentialEvolution(function_obj,
                                                          bounds,
                                                          mutation_coefficient=mutation_coefficient,
                                                          crossover_coefficient=crossover_coefficient,
                                                          population_size=population_size)

                        de_solver._init_population()
                        logger_low_lev.debug(f"[id={application_id}] Initialization of the population for the algorithm is done")

                        logger_low_lev.debug(f"[id={application_id}] Beginning of the iterative algorithm")
                        for _ in range(steps):
                            de_solver.iterate()

                        res = de_solver.fitness[de_solver.best_idx]

                        # depending on the result, select the log type
                        if res > 1e-1:
                            # stack the config lines
                            config = f"bounds={bounds}, population_size={population_size}, steps={steps}, " \
                                     f"mutation_coefficient={mutation_coefficient}, " \
                                     f"crossover_coefficient={crossover_coefficient}, " \
                                     f"init_population={de_solver.init_population}"
                            logger_high_lev.critical(f"[id={application_id}] Critical error detected! Global minimum: 0. The received result exceeds 1e-1: {res}." \
                                                     + f" config=[{config}]")
                        elif res > 1e-3:
                            config = f"bounds={bounds}, population_size={population_size}, steps={steps}, " \
                                     f"mutation_coefficient={mutation_coefficient}, " \
                                     f"crossover_coefficient={crossover_coefficient}, " \
                                     f"init_population={de_solver.init_population}"
                            logger_high_lev.error(f"[id={application_id}] Error detected! Global minimum: 0. Result exceeds 1e-3: {res}." \
                                                  + f" config=[{config}]")
                        elif res == 0:
                            logger_low_lev.debug(f"[id={application_id}] The algorithm converged. Global minimum and the obtained result: 0")
                        else:
                            logger_low_lev.warning(f"[id={application_id}] The algorithm did not converge. Global minimum: 0. Obtained result: {res}")

                        logger_low_lev.info(f"[id={application_id}] End of the Differential Evolution algorithm. Result: {res}")

                        application_id += 1  # updating the launch id
