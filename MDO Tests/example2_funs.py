from openmdao.api import Problem, ExecComp, IndepVarComp, ExplicitComponent, pyOptSparseDriver
import numpy as np
import random

# note: size must be an even number
SIZE = 10
p = Problem()

# this class volslant provides us with explicit component required to compute the example problem set
# it contains various equations of slant height, volume, base area of a cone
# with given radius and height of an cone.
class VolSlant(ExplicitComponent):
    def initialize(self):
        pass

    def setup(self):
        self.add_input('r', val=np.ones(SIZE))
        self.add_input('h', val=np.ones(SIZE))
        self.add_output('b', val=np.ones(SIZE))
        self.add_output('slant', val=np.ones(SIZE))
        self.add_output('v', val=np.ones(SIZE))
        self.declare_partials(of='*', wrt='*', method='fd')
        
    def compute(self, inputs, outputs):
#        this function defines the computing variables for the component.
#        this function contains output variables and equation computation.
        r= inputs['r']
        h =inputs['h']
        outputs['slant'] = np.sqrt(r**2 + h**2)
        outputs['v'] = (np.pi/3)*h*r**2
        outputs['b'] = np.pi*(r ** 2)

# Independent subsytem is used for the output of the result set we want to achieve.
indeps = p.model.add_subsystem('indeps', IndepVarComp(), promotes_outputs=['*'])

# the input params in our problem set.
#indeps.add_output('r', np.array(np.random.uniform(0,10,SIZE)))
indeps.add_output('r', np.array(random.sample(xrange(10), SIZE)))
indeps.add_output('h', np.array(random.sample(xrange(20), SIZE)))

# adding new subsystems to compute volume of a cone in given input.
p.model.add_subsystem('volumes', subsys=VolSlant())

# adding new subsystems to compute surface area of a cone with given input.
p.model.add_subsystem('surface', ExecComp('area=pi*r*slh', 
                                          area=np.ones(SIZE), r=np.ones(SIZE), slh=np.ones(SIZE)))

# adding new subsystems to compute total surface area of a cone given input.
p.model.add_subsystem('total', ExecComp('area=pi*r*(r+slh)',
                                        slh=np.ones(SIZE), area=np.ones(SIZE), r=np.ones(SIZE)))

# It connects the input variables of each system and to one another in the model.
p.model.connect('r', ['volumes.r', 'surface.r', 'total.r'])
p.model.connect('h', ['volumes.h'])
p.model.connect('volumes.slant', ['surface.slh', 'total.slh'])

# Design variables required in the system which adhere to our design constraints.
p.model.add_design_var('r', lower=0, upper=10.0)
p.model.add_design_var('h', lower=0, upper=20.0)

# this model requires only one constraints which is volume of one parameter.
p.model.add_constraint('volumes.v', lower=200, linear=True)

# We are using mulit objective problem. There are two objective trying to achieve in this problem.
# first to minimize the surface area of the cone
p.model.add_objective('surface.area', ref=-1, index=1)
# second to minimize the total surface area of the cone.
p.model.add_objective('total.area', ref=-1, index=1)

# using pyopt driver import from the library set.
p.driver = pyOptSparseDriver()
p.driver.options['optimizer'] = 'NSGA2'

# the driver in OPENMDAO allows us to make changes in the setting of Optimization Algorithms
# We could add more options to the alogrithms as design permits
#p.driver.opt_settings['PopSize'] =

p.setup(mode='fwd')

p.run_driver()

# the result is an array of 10 values since we are providing 10 inputs.
# the driver computes values based on each subsytem and solves the problem model.
print((p['total.area']))
print((p['surface.area']))

#%%
import matplotlib.pyplot as plt


fig = plt.figure(1)
plt.subplot(221)
#plt.plot(p['r'],p['total.area'], 'rs')
plt.plot(p['surface.area'],p['total.area'], 'rs')
plt.xlabel('f2')
plt.ylabel('f3')
plt.grid(True)
plt.show()

plt.subplot(222)
#plt.plot(p['r'],p['total.area'], 'rs')
plt.plot(p['h'],p['total.area'], 'rs')
plt.xlabel('f2')
plt.ylabel('f3')
plt.grid(True)
plt.show()

plt.subplot(223)
#plt.plot(p['r'],p['total.area'], 'rs')
plt.plot(p['r'],p['total.area'], 'rs')
plt.xlabel('f2')
plt.ylabel('f3')
plt.grid(True)
plt.show()

plt.subplot(224)
#plt.plot(p['r'],p['total.area'], 'rs')
plt.plot(p['r'],p['total.area'], 'rs')
plt.xlabel('f2')
plt.ylabel('f3')
plt.grid(True)
plt.show()

