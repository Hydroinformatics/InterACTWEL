from openmdao.api import Problem, Group, IndepVarComp, ParallelGroup
#from openmdao.test_suite.components.branin import Branin
from branin_testb import Branin, Branin2
from deap_driver_examples import DeapGADriver
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import axes3d, Axes3D 

prob = Problem()
model = prob.model = Group()
#model = prob.model = ParallelGroup()

model.add_subsystem('p1', IndepVarComp('xC', 7.5))
model.add_subsystem('p2', IndepVarComp('xI', 0.0))

dictvars = dict()
for ii in range(-5,11):
    dictvars[ii] = ii

#tempvars = IndepVarComp()
#tempvars.add_output('xI', 0.0)
#tempvars.add_output('yI', 0.0)
#model.add_subsystem('p2', tempvars)

model.add_subsystem('comp', Branin())
model.add_subsystem('comp2', Branin2(vardict=dictvars))

model.connect('p2.xI', 'comp.x0')
model.connect('p1.xC', 'comp.x1')
#model.connect('p2.yI', 'comp2.x0')
model.connect('p2.xI', 'comp2.x0')
model.connect('p1.xC', 'comp2.x1')

model.add_design_var('p2.xI', lower= -5.0, upper= 10.0)
model.add_design_var('p1.xC', lower= 0.0, upper= 15.0)

model.add_objective('comp.f3')
#model.add_objective('comp.f2')
model.add_objective('comp2.f2')

prob.driver = DeapGADriver()
prob.driver.options['bits'] = {'p1.xC' : 8}
prob.driver.options['pop_size'] = 500
prob.driver.options['max_gen'] = 300
prob.driver.options['weights'] = (1.0,-1.0)
#prob.driver.options['run_parallel'] = True

prob.setup()
prob.run_driver()

#%%
# Optimal solution
print('f3', prob['comp.f3'],'f2', prob['comp2.f2'])
print('X0', prob['p2.xI'], 'X1', prob['p1.xC'])
#print('comp.X0', prob['comp.x0'], 'comp2.x0', prob['comp2.x0'])

#%%

a = 1.0
b = 5.1/(4.0*np.pi**2)
c = 5.0/np.pi
d = 6.0
e = 10.0
fi = 1.0/(8.0*np.pi)

f2 = []
f3 = []
X0 = []
X1 = []

for hof_temp in prob.driver._hof:
#for hof_temp in prob.driver._pop:
    x0 = hof_temp[0]
    x1 = hof_temp[1]
    f = a*(x1 - b*x0**2 + c*x0 - d)**2 + e*(1-fi)*np.cos(x0) + e
    f2i = x0**2 + c*x0*x1
    f2.append(f2i)
    f3.append(f2i + f)
    #f3.append(f)
    X0.append(x0)
    X1.append(x1)

data = [f3,f2]
#data = np.sort(data,axis=0)
#data = [data_temp[:,0].argsort()]

fig = plt.figure(1)
plt.subplot(121)
plt.plot(data[1],data[0], 'rs')
plt.xlabel('f2')
plt.ylabel('f3')
plt.grid(True)
plt.show()

RES = np.transpose(np.asmatrix([X0,X1,f3,f2]))
#RES = np.matrix.sort(RES,axis=0)
#RES = np.array(RES,axis=3)

#plt.plot(X0,f3, 'rs')
#plt.xlabel('x0')
#plt.ylabel('f3')
#plt.show()

ax = fig.add_subplot(122, projection='3d')
ax.scatter(X0, X1, f3)
ax.scatter(X0, X1, f2,c='r')
ax.set_xlabel('X0')
ax.set_ylabel('X1')
ax.set_zlabel('Fitness')
