#import numpy as np
#
#from openmdao.api import Problem, Group, IndepVarComp, NewtonSolver, ScipyKrylov, LinearBlockGS, pyOptSparseDriver
#from openmdao.test_suite.components.double_sellar import SubSellar
#
#prob = Problem()
#model = prob.model
#
#model.add_subsystem('pz', IndepVarComp('z', np.array([5.0, 2.0])))
#
#sub1 = model.add_subsystem('sub1', Group())
#sub2 = sub1.add_subsystem('sub2', Group())
#g1 = sub2.add_subsystem('g1', SubSellar())
#g2 = model.add_subsystem('g2', SubSellar())
#
#model.connect('pz.z', 'sub1.sub2.g1.z')
#model.connect('sub1.sub2.g1.y2', 'g2.x')
#model.connect('g2.y2', 'sub1.sub2.g1.x')
#
#model.nonlinear_solver = NewtonSolver()
#model.linear_solver = ScipyKrylov()
#model.nonlinear_solver.options['solve_subsystems'] = True
#model.nonlinear_solver.options['max_sub_solves'] = 0
#
#g1.nonlinear_solver = NewtonSolver()
#g1.linear_solver = LinearBlockGS()
#
#g2.nonlinear_solver = NewtonSolver()
#g2.linear_solver = ScipyKrylov()
#
##g1.nonlinear_solver = pyOptSparseDriver()
##g2.nonlinear_solver.options['optimizer'] = 'NSGA2'
#
#g2.linear_solver.precon = LinearBlockGS()
#g2.linear_solver.precon.options['maxiter'] = 2
#
#prob.set_solver_print(level=2)
#
#prob.setup()
#prob.run_model()


from openmdao.api import Problem, IndepVarComp, ParallelGroup, ExecComp, PETScVector

prob = Problem()
model = prob.model

model.add_subsystem('p1', IndepVarComp('x', 1.0))
model.add_subsystem('p2', IndepVarComp('x', 1.0))

parallel = model.add_subsystem('parallel', ParallelGroup())
parallel.add_subsystem('c1', ExecComp(['y=-2.0*x']))
parallel.add_subsystem('c2', ExecComp(['y=5.0*x']))

model.add_subsystem('c3', ExecComp(['y=3.0*x1+7.0*x2']))

model.connect("parallel.c1.y", "c3.x1")
model.connect("parallel.c2.y", "c3.x2")

model.connect("p1.x", "parallel.c1.x")
model.connect("p2.x", "parallel.c2.x")

prob.setup(vector_class=PETScVector, check=False, mode='fwd')
prob.set_solver_print(level=0)
prob.run_model()
print(prob['c3.y'])