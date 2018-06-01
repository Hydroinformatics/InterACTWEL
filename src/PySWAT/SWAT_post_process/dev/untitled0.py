import numpy as np
from openmdao.api import Problem, Group, IndepVarComp, DeapGADriver
from branin_test import Branin, Branin2, pp1
import itertools

class Var_Dict():
    def __init__(self):
        self.var_names = ['IRR','DIV','PND']
        temp_dict = dict()
        temp_dict['IRR'] = [subset for subset in itertools.product((0,1,3), repeat = 2)]
        temp_dict['DIV'] = [(1,1),(0,0),(1,0),(0,1)]
        temp_dict['PND'] = [(5,8),(5,9),(10,5)]
        self.var_dict = temp_dict
              
prob = Problem()
model = prob.model = Group()

vardict = Var_Dict()

tempvars = IndepVarComp()
tempvars.add_output('IRR', val=1)
tempvars.add_output('DIV', val=1)
tempvars.add_output('PND', val=0)
model.add_subsystem('v',tempvars)


#model.add_subsystem('hur2',Branin2(Var_dict=vardict))
#model.add_subsystem('comp', Branin(Var_dict=vardict))

cycle = model.add_subsystem('cycle',Group())
cycle.add_subsystem('hru1',pp1(Var_dict=vardict))
cycle.add_subsystem('hru2',Branin2())
model.add_subsystem('comp', Branin())

model.connect('v.IRR','cycle.hru1.x0')
model.connect('v.DIV',['cycle.hru1.x1','cycle.hru2.x1'])
model.connect('v.PND','comp.x2')
model.connect('cycle.hru1.x0o','cycle.hru2.x0')
#model.connect('hub.x0o','comp.x0')


model.add_design_var('v.IRR', lower=0.0, upper=10.0)
model.add_design_var('v.DIV', lower=0.0, upper=15.0)
model.add_design_var('v.PND', lower=0.0, upper=10.0)

model.add_objective('comp.f','comp.f2')


prob.driver = DeapGADriver()
prob.driver.options['bits'] = {'p1.xC' : 8}
#prob.driver.options['solve_subsystems'] = True

#prob.hub.driver = SimpleGADriver()
#prob.model.hub.options['bits'] = {'hub.x1' : 8}

prob.setup()
prob.run_driver()
#
## Optimal solution
#print('comp.f', prob['comp.f'], prob['hub.f2'])
#print(prob['p2.xI'],prob['p1.xC'])
