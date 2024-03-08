# Numpy and Scipy

---

In this project you can see the solution of applied data analysis problems 
using scientific computing with `numpy` and `scipy` libraries.

The description of the problems can be seen in the file 
[Python_numpy_scipy_project.ipynb](./Python_numpy_scipy_project.ipynb).

The solution itself, in addition to the file above, is also contained 
in separate modules:
* [diff_evolution.py](./diff_evolution.py): realization of differential evolution 
  optimization algorithm
* [einsum_task.py](./einsum_task.py): various operations for vectors using `np.einsum`
* [game_of_life.py](./game_of_life.py): [Game of life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
  implementation 
* [gauss_filter.py](./gauss_filter.py): implementation of a two-dimensional 
  Gaussian filter (a powerful tool in image processing, which allows you to 
  get rid of unnecessary noise in the picture, and also gives you the opportunity 
  to blur the picture).
* [greatest_task.py](./greatest_task.py): finding the top-k largest elements in 
  an array using `numpy`

All tests written for each of the tasks, using `pytest`, are in the [tests](./tests) folder.
