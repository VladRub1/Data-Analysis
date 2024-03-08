# Logging and Testing

---

This project consists of two parts: 1) **Logging** and 2) **Testing**. Both parts
work with the _differential evolution_ optimization method, which is implemented in the file
[differential_evolution.py](./differential_evolution.py).

## Logging

In this part you can see examples of my custom Python loggers implementation
using the built-in `logging` library. You can see the code with their implementation 
in the [logging_de.py](./logging_de.py) file.

Under [examples/logs](./examples/logs) you can see **examples of logs**
on the results of the program's work and creating files for them:
* [errors.log](./examples/logs/errors.log) — logs of the 4th and 5th levels of
logging (`ERROR` (if the result of the algorithm is greater than 1e-3), `CRITICAL`
(if the result is greater than 1e-1))
* [logging_de.log](./examples/logs/logging_de.log) — logs of levels 1, 2, 3
  (`DEBUG`, `INFO` and `WARNING`)

The loggers log each run and logical step of the algorithm, and are divided 
into two parts, which can be seen in the examples above. 
A different formatter has also been created for each logger.

Also in the logs there is `id` of the runs of the algorithm differential evolution 
(end-to-end between both loggers) to make it easier for potential readers to 
filter the logs they need.

## Testing

In this section the problem of achieving **100% coverage of tests** of the 
differential evolution optimization method using the `pytest` library was solved.

You can read more about test coverage here: https://www.atlassian.com/ru/continuous-delivery/software-testing/code-coverage.

The tests are described in the file `test_de.py`. 
The different steps of logic testing have been divided into different functions.

The tests can be run with the following script:
```bash
pytest -s test_de.py --cov-report=json --cov
```

and the result will be saved to the `coverage.json` file.
Its example can be seen in the file [examples/tests/coverage.json](./examples/tests/coverage.json)

A separate test in [test_coverage.py](./test_coverage.py) file 
checks if the coverage of tests is equal to 100%.
