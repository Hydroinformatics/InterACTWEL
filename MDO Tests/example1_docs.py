from openmdao.api import Problem, IndepVarComp, ExecComp, ScipyOptimizeDriver
import numpy as np

# note: size must be an even number
SIZE = 10
p = Problem()

indeps = p.model.add_subsystem('indeps', IndepVarComp(), promotes_outputs=['*'])

# the following were randomly generated using np.random.random(10)*2-1 to randomly
# disperse them within a unit circle centered at the origin.
indeps.add_output('x', np.array([ 0.55994437, -0.95923447,  0.21798656, -0.02158783,  0.62183717,
                                  0.04007379,  0.46044942, -0.10129622,  0.27720413, -0.37107886]))
indeps.add_output('y', np.array([ 0.52577864,  0.30894559,  0.8420792 ,  0.35039912, -0.67290778,
                                  -0.86236787, -0.97500023,  0.47739414,  0.51174103,  0.10052582]))
indeps.add_output('r', .7)

p.model.add_subsystem('circle', ExecComp('area=pi*r**2'))

p.model.add_subsystem('r_con', ExecComp('g=x**2 + y**2 - r',
                                        g=np.ones(SIZE), x=np.ones(SIZE), y=np.ones(SIZE)))

thetas = np.linspace(0, np.pi/4, SIZE)
p.model.add_subsystem('theta_con', ExecComp('g=arctan(y/x) - theta',
                                            g=np.ones(SIZE), x=np.ones(SIZE), y=np.ones(SIZE),
                                            theta=thetas))
p.model.add_subsystem('delta_theta_con', ExecComp('g = arctan(y/x)[::2]-arctan(y/x)[1::2]',
                                                  g=np.ones(SIZE//2), x=np.ones(SIZE),
                                                  y=np.ones(SIZE)))

thetas = np.linspace(0, np.pi/4, SIZE)

p.model.add_subsystem('l_conx', ExecComp('g=x-1', g=np.ones(SIZE), x=np.ones(SIZE)))

p.model.connect('r', ('circle.r', 'r_con.r'))
p.model.connect('x', ['r_con.x', 'theta_con.x', 'delta_theta_con.x'])

p.model.connect('x', 'l_conx.x')

p.model.connect('y', ['r_con.y', 'theta_con.y', 'delta_theta_con.y'])

p.driver = ScipyOptimizeDriver()
p.driver.options['optimizer'] = 'SLSQP'
p.driver.options['disp'] = False

p.model.add_design_var('x')
p.model.add_design_var('y')
p.model.add_design_var('r', lower=.5, upper=10)

# nonlinear constraints
p.model.add_constraint('r_con.g', equals=0)

IND = np.arange(SIZE, dtype=int)
ODD_IND = IND[0::2]  # all odd indices
p.model.add_constraint('theta_con.g', lower=-1e-5, upper=1e-5, indices=ODD_IND)
p.model.add_constraint('delta_theta_con.g', lower=-1e-5, upper=1e-5)

# this constrains x[0] to be 1 (see definition of l_conx)
p.model.add_constraint('l_conx.g', equals=0, linear=False, indices=[0,])

# linear constraint
p.model.add_constraint('y', equals=0, indices=[0,], linear=True)

p.model.add_objective('circle.area', ref=-1)

## setup coloring
#color_info = ([
#   [20],   # uncolored column list
#   [0, 2, 4, 6, 8],   # color 1
#   [1, 3, 5, 7, 9],   # color 2
#   [10, 12, 14, 16, 18],   # color 3
#   [11, 13, 15, 17, 19],   # color 4
#],
#[
#   [1, 11, 16, 21],   # column 0
#   [2, 16],   # column 1
#   [3, 12, 17],   # column 2
#   [4, 17],   # column 3
#   [5, 13, 18],   # column 4
#   [6, 18],   # column 5
#   [7, 14, 19],   # column 6
#   [8, 19],   # column 7
#   [9, 15, 20],   # column 8
#   [10, 20],   # column 9
#   [1, 11, 16],   # column 10
#   [2, 16],   # column 11
#   [3, 12, 17],   # column 12
#   [4, 17],   # column 13
#   [5, 13, 18],   # column 14
#   [6, 18],   # column 15
#   [7, 14, 19],   # column 16
#   [8, 19],   # column 17
#   [9, 15, 20],   # column 18
#   [10, 20],   # column 19
#   None,   # column 20
#], None)
#
#p.driver.set_simul_deriv_color(color_info)

p.setup(mode='fwd')
p.run_driver()

print(p['circle.area'])