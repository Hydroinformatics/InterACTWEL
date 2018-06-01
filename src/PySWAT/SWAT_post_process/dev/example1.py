# Link to example page: http://openmdao.org/twodocs/versions/latest/examples/simul_deriv_example/simul_deriv_example.html
from openmdao.api import Problem, IndepVarComp, ExecComp, pyOptSparseDriver
import numpy as np
#from deap_driver_examples import DeapGADriver
from deap_driver_examples1 import DeapGADriver

from example1_circle import circle, r_con, theta_con, delta_theta_con, l_conx

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

# this subsytem is for minimizing the area of the circle with given input values above.
#p.model.add_subsystem('circle', ExecComp('area=pi*r**2'))
p.model.add_subsystem('circle', circle())

# this subsystem provides the area of circle as the equation of the form with x and y points in space.
#p.model.add_subsystem('r_con', ExecComp('g=x**2 + y**2 - r', g=np.ones(SIZE), x=np.ones(SIZE), y=np.ones(SIZE)))
p.model.add_subsystem('r_con', r_con())
                      
#thetas = np.linspace(0, np.pi/4, SIZE)

#p.model.add_subsystem('theta_con', ExecComp('g=arctan(y/x) - theta', g=np.ones(SIZE), x=np.ones(SIZE), y=np.ones(SIZE), theta=thetas))
p.model.add_subsystem('theta_con', theta_con())

#p.model.add_subsystem('delta_theta_con', ExecComp('g = arctan(y/x)[::2]-arctan(y/x)[1::2]', g=np.ones(SIZE//2), x=np.ones(SIZE), y=np.ones(SIZE)))
p.model.add_subsystem('delta_theta_con', delta_theta_con())
                      
#p.model.add_subsystem('l_conx', ExecComp('g=x-1', g=np.ones(SIZE), x=np.ones(SIZE)))
p.model.add_subsystem('l_conx', l_conx())

# adding design variables in the model
p.model.add_design_var('indeps.x')
p.model.add_design_var('indeps.y')
p.model.add_design_var('indeps.r', lower=0.1, upper=10)

p.model.connect('indeps.r', ['circle.r', 'r_con.r'])
p.model.connect('indeps.x', ['r_con.x', 'theta_con.x', 'delta_theta_con.x', 'l_conx.x'])
p.model.connect('indeps.y', ['r_con.y', 'theta_con.y', 'delta_theta_con.y'])


## nonlinear constraints
#p.model.add_constraint('r_con.g', equals=0)
#
#IND = np.arange(SIZE, dtype=int)
##ODD_IND = IND[0::2]  # all odd indices
#p.model.add_constraint('theta_con.g', lower=-1e-5, upper=1e-5, indices=IND[0::2])
#p.model.add_constraint('delta_theta_con.g', lower=-1e-5, upper=1e-5)
#
## this constrains x[0] to be 1 (see definition of l_conx)
#p.model.add_constraint('l_conx.g', equals=0, indices=[0,])
#
## linear constraints
#p.model.add_constraint('y', equals=0, indices=[0,], linear=True)

# the objective of the problem we are trying to run.
p.model.add_objective('circle.area')

# driver file to perform the optimization on the above problem and model system
p.driver = DeapGADriver()
#p.driver.options['optimizer'] = 'NSGA2'

p.driver.options['bits'] = {'indeps.x' : 8}
p.driver.options['bits'] = {'indeps.y' : 8}
p.driver.options['bits'] = {'indeps.r' : 8}
p.driver.options['pop_size'] = 500
p.driver.options['max_gen'] = 300
p.driver.options['weights'] = (-1.0,-1.0)

p.setup()
p.run_driver()

#p.driver.opt_settings['PopSize'] = 150

## this setups all the subsystems and model for the driver optimization
#p.setup(mode='fwd')

## this runs the driver in the OpenMDAO framework and then driver from pyOPT framwework as specified as the file.
#p.run_driver()

print("Radius Min = %f" % (p['r']))
print("Minimum Area of Circle = %f" % p['circle.area'])