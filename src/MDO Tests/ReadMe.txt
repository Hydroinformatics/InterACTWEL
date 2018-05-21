Benchmarking and Testing problems in OpenMDAO Framework with NSGA-II
Under guidance of Dr. Meghna Babbar-Sebens and Dr. Arjan Durresi

By - Shreyansh Mohnot and Milan Patil

Dependencies -

OpenMDAO - Framework for our problem set due to the definition and parameters in the problem.
pyOPT Framework - Contains NSGA2 Algorithm developed in python and as an Optimization problem.
mpi4py - For parallel High Performance computing resources library
pyOpt Driver - pyOptSparseDriver wraps the optimizer package pyOptSparse. Not come included with the OpenMDAO installatio. To download it refer to: 
               http://openmdao.org/twodocs/versions/latest/features/building_blocks/drivers/pyoptsparse_driver.html

Steps to Run the code files:

1. 
To get started with the running of the OpenMDAO and pyOPT framework, ensure they are installed with their latest instances.
Run " ./install.sh " for installing all the dependencies.
This would install all the depending resources and libraries needed for the OpenMDAO framework.
pyoptsprase framework is installed as plugin in the OpenMDAO framework.

**Incase of errors please check the install.sh file. It could be opened in vim or any text editor.**

1. First step is to check for performance of Non-Sorting Genetic Algorithm-II. We have a default code example setup in file - example1.py
This would run a optimization problem to satisfy minimum area of circle and output the result.
Run the following example using "python example1.py"

2. 
We have used an example of multi objective problem in our example case. This is done to get the behavior of our problem set where we would be considering various multi disciplines and objective optimization simultaneously. So we constructed an example set to show proof of concept.
Run the following example from file "python example2.py"
It is an optimization problem to minimize the surface area and total surface area of a circle with respect to some constraints and design variables.

3.
There is an pyoptsparse wrapper which we modified to add some limitations and time boundations to delay the process of computations provided in real environment with simulation derivatives and multiple disciplines.

References -

1. OpenMDAO Example (example1.py) -
http://openmdao.org/twodocs/versions/latest/examples/simul_deriv_example/simul_deriv_example.html

2. Cone Surface Area Example (example2.py) - 
http://www.math.unipd.it/~marcuzzi/DIDATTICA/LEZ&ESE_PIAI_Matematica/3_cones.pdf

3. pyOpt Driver - 
http://openmdao.org/twodocs/versions/latest/features/building_blocks/drivers/pyoptsparse_driver.html

4. NSGA2 -
http://www.pyopt.org/reference/optimizers.nsga2.html