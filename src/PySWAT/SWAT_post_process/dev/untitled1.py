from openmdao.api import Problem, Group, IndepVarComp, DeapGADriver
#from openmdao.test_suite.components.branin import Branin
from branin_testb import Branin, Branin2

prob = Problem()
model = prob.model = Group()

model.add_subsystem('p1', IndepVarComp('xC', 7.5))
model.add_subsystem('p2', IndepVarComp('xI', 0.0))
model.add_subsystem('comp', Branin())
#model.add_subsystem('comp2', Branin())

model.connect('p2.xI', 'comp.x0')
model.connect('p1.xC', 'comp.x1')
#model.connect('p2.xI', 'comp2.x0')
#model.connect('p1.xC', 'comp2.x1')

model.add_design_var('p2.xI', lower= -5.0, upper= 10.0)
model.add_design_var('p1.xC', lower= 0.0, upper= 15.0)

model.add_objective('comp.f')
model.add_objective('comp.f2')

prob.driver = DeapGADriver()
prob.driver.options['bits'] = {'p1.xC' : 8}
prob.driver.options['pop_size'] = 500
prob.driver.options['weights'] = (1.0,-1.0)
prob.setup()
prob.run_driver()

#%%
# Optimal solution
print('comp.f', prob['comp.f'])
print('X0', prob['p2.xI'], 'X1', prob['p1.xC'])

