from openmdao.api import Problem, IndepVarComp, ParallelGroup, ExecComp, PETScVector, pyOptSparseDriver

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

#prob.setup(vector_class=PETScVector, check=False, mode='fwd')
#prob.set_solver_print(level=0)
#prob.run_model()

prob.driver = pyOptSparseDriver()
prob.driver.options['optimizer'] = 'NSGA2'
prob.driver.options['print_results'] = False
prob.setup(mode='fwd')

print(prob['c3.y'])