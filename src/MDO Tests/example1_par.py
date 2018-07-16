from openmdao.api import Problem, IndepVarComp, ExecComp, pyOptSparseDriver, ParallelGroup
import numpy as np

import time

start = time.time()
print("Starting")

# note: size must be an even number
SIZE = 10
p = Problem()

# Independent subsytem is used for the output of the result set we want to achieve.
indeps = p.model.add_subsystem('indeps', IndepVarComp(), promotes_outputs=['*'])

# the following were randomly generated using np.random.random(10)*2-1 to randomly
# disperse them within a unit circle centered at the origin.
indeps.add_output('x', np.array([ 0.55994437, -0.95923447,  0.21798656, -0.02158783,  0.62183717,
                                  0.04007379,  0.46044942, -0.10129622,  0.27720413, -0.37107886]))
indeps.add_output('y', np.array([ 0.52577864,  0.30894559,  0.8420792 ,  0.35039912, -0.67290778,
                                  -0.86236787, -0.97500023,  0.47739414,  0.51174103,  0.10052582]))
indeps.add_output('r', 0.7)


parallel = p.model.add_subsystem('parallel', ParallelGroup())

# this subsytem is for minimizing the area of the circle with given input values above.
parallel.add_subsystem('circle', ExecComp('area=pi*r**2'))

# this subsystem provides the area of circle as the equation of the form with x and y points in space.
parallel.add_subsystem('r_con', ExecComp('g=x**2 + y**2 - r',
                                        g=np.ones(SIZE), x=np.ones(SIZE), y=np.ones(SIZE)))

thetas = np.linspace(0, np.pi/4, SIZE)

parallel.add_subsystem('theta_con', ExecComp('g=arctan(y/x) - theta',
                                            g=np.ones(SIZE), x=np.ones(SIZE), y=np.ones(SIZE),
                                            theta=thetas))
parallel.add_subsystem('delta_theta_con', ExecComp('g = arctan(y/x)[::2]-arctan(y/x)[1::2]',
                                                  g=np.ones(SIZE//2), x=np.ones(SIZE),
                                                  y=np.ones(SIZE)))

parallel.add_subsystem('l_conx', ExecComp('g=x-1', g=np.ones(SIZE), x=np.ones(SIZE)))

p.model.connect('r', ('parallel.circle.r', 'parallel.r_con.r'))
p.model.connect('x', ['parallel.r_con.x', 'parallel.theta_con.x', 'parallel.delta_theta_con.x', 'parallel.l_conx.x'])
p.model.connect('y', ['parallel.r_con.y', 'parallel.theta_con.y', 'parallel.delta_theta_con.y'])

# adding design variables in the model
p.model.add_design_var('x')
p.model.add_design_var('y')
p.model.add_design_var('r', lower=0.1, upper=10)

# nonlinear constraints
p.model.add_constraint('parallel.r_con.g', equals=0)

IND = np.arange(SIZE, dtype=int)
#ODD_IND = IND[0::2]  # all odd indices
p.model.add_constraint('parallel.theta_con.g', lower=-1e-5, upper=1e-5, indices=IND[0::2])
p.model.add_constraint('parallel.delta_theta_con.g', lower=-1e-5, upper=1e-5)

# this constrains x[0] to be 1 (see definition of l_conx)
p.model.add_constraint('parallel.l_conx.g', equals=0, indices=[0,])

# linear constraints
p.model.add_constraint('y', equals=0, indices=[0,], linear=True)

# the objective of the problem we are trying to run.
p.model.add_objective('parallel.circle.area', ref=-1)

# driver file to perform the optimization on the above problem and model system
p.driver = pyOptSparseDriver()
p.driver.options['optimizer'] = 'NSGA2'
p.driver.options['print_results'] = False
p.driver.opt_settings['PopSize'] = 1000

# this setups all the subsystems and model for the driver optimization
p.setup(mode='fwd')

# this runs the driver in the OpenMDAO framework and then driver from pyOPT framwework as specified as the file.
p.run_driver()

end = time.time()
print(end - start)

print("Radius Min = %f" % (p['r']))
print("Minimum Area of Circle = %f" % p['parallel.circle.area'])