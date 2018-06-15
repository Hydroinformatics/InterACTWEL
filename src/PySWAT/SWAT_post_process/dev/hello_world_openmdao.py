import numpy as np

from openmdao.api import Problem, Group, IndepVarComp, NewtonSolver, ScipyKrylov, LinearBlockGS, pyOptSparseDriver
from openmdao.test_suite.components.double_sellar import SubSellar

prob = Problem()
model = prob.model

model.add_subsystem('pz', IndepVarComp('z', np.array([5.0, 2.0])))

sub1 = model.add_subsystem('sub1', Group())
sub2 = sub1.add_subsystem('sub2', Group())
g1 = sub2.add_subsystem('g1', SubSellar())
g2 = model.add_subsystem('g2', SubSellar())

model.connect('pz.z', 'sub1.sub2.g1.z')
model.connect('sub1.sub2.g1.y2', 'g2.x')
model.connect('g2.y2', 'sub1.sub2.g1.x')

model.nonlinear_solver = NewtonSolver()
model.linear_solver = ScipyKrylov()
model.nonlinear_solver.options['solve_subsystems'] = True
model.nonlinear_solver.options['max_sub_solves'] = 0

g1.nonlinear_solver = NewtonSolver()
g1.linear_solver = LinearBlockGS()

g2.nonlinear_solver = NewtonSolver()
g2.linear_solver = ScipyKrylov()

#g1.nonlinear_solver = pyOptSparseDriver()
#g2.nonlinear_solver.options['optimizer'] = 'NSGA2'

g2.linear_solver.precon = LinearBlockGS()
g2.linear_solver.precon.options['maxiter'] = 2

prob.set_solver_print(level=2)

prob.setup()
prob.run_model()