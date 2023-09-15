# import openmdao.api as om

# class Box(om.ExplicitComponent):

#     def setup(self):
#         self.add_input('length', val=1.)
#         self.add_input('width', val=1.)
#         self.add_input('height', val=1.)

#         self.add_output('front_area', val=1.0)
#         self.add_output('top_area', val=1.0)
#         self.add_output('area', val=1.0)
#         self.add_output('volume', val=1.)

#     def compute(self, inputs, outputs):
#         length = inputs['length']
#         width = inputs['width']
#         height = inputs['height']

#         outputs['top_area'] = length * width
#         outputs['front_area'] = length * height
#         outputs['area'] = 2*length*height + 2*length*width + 2*height*width
#         outputs['volume'] = length*height*width

# prob = om.Problem()

# prob.model.add_subsystem('box', Box(), promotes=['*'])

# # setup the optimization
# prob.driver = om.SimpleGADriver()
# prob.driver.options['max_gen'] = 20
# prob.driver.options['bits'] = {'length': 8, 'width': 8, 'height': 8}
# prob.driver.options['penalty_parameter'] = 10.
# prob.driver.options['compute_pareto'] = True

# prob.model.add_design_var('length', lower=0.1, upper=2.)
# prob.model.add_design_var('width', lower=0.1, upper=2.)
# prob.model.add_design_var('height', lower=0.1, upper=2.)
# prob.model.add_objective('front_area', scaler=-1)  # maximize
# prob.model.add_objective('top_area', scaler=-1)  # maximize
# prob.model.add_constraint('volume', upper=1.)

# prob.setup()

# prob.set_val('length', 1.5)
# prob.set_val('width', 1.5)
# prob.set_val('height', 1.5)

# prob.run_driver()

# desvar_nd = prob.driver.desvar_nd
# nd_obj = prob.driver.obj_nd

# print(desvar_nd)

# sorted_obj = nd_obj[nd_obj[:, 0].argsort()]

# print(sorted_obj)

################################################
#%%
# import openmdao.api as om

# class Cylinder(om.ExplicitComponent):
#     """Main class"""

#     def setup(self):
#         self.add_input('radius', val=1.0)
#         self.add_input('height', val=1.0)

#         self.add_output('Area', val=1.0)
#         self.add_output('Volume', val=1.0)

#     def compute(self, inputs, outputs):
#         radius = inputs['radius']
#         height = inputs['height']

#         area = height * radius * 2 * 3.14 + 3.14 * radius ** 2 * 2
#         volume = 3.14 * radius ** 2 * height
#         outputs['Area'] = area
#         outputs['Volume'] = volume

# prob = om.Problem()
# prob.model.add_subsystem('cylinder', Cylinder(), promotes=['*'])

# # setup the optimization
# prob.driver = om.SimpleGADriver()
# prob.driver.options['penalty_parameter'] = 3.
# prob.driver.options['penalty_exponent'] = 1.
# prob.driver.options['max_gen'] = 50
# prob.driver.options['bits'] = {'radius': 8, 'height': 8}

# prob.model.add_design_var('radius', lower=0.5, upper=5.)
# prob.model.add_design_var('height', lower=0.5, upper=5.)
# prob.model.add_objective('Area')
# prob.model.add_constraint('Volume', lower=10.)

# prob.setup()

# prob.set_val('radius', 2.)
# prob.set_val('height', 3.)

# prob.run_driver()

# # These go to 0.5 for unconstrained problem. With constraint and penalty, they
# # will be above 1.0 (actual values will vary.)
# print(prob.get_val('radius'))
# print(prob.get_val('height'))

#%%

import openmdao.api as om
from openmdao.test_suite.components.branin import Branin

prob = om.Problem()
model = prob.model

model.add_subsystem('comp', Branin(),
                    promotes_inputs=[('x0', 'xI'), ('x1', 'xC')])

model.add_design_var('xI', lower=-5.0, upper=10.0)
model.add_design_var('xC', lower=0.0, upper=15.0)
model.add_objective('comp.f')

prob.driver = om.SimpleGADriver()
prob.driver.options['bits'] = {'xC': 8}
prob.driver.options['pop_size'] = 100
prob.driver.options['max_gen'] = 100

prob.setup()

prob.set_val('xC', 7.5)
prob.set_val('xI', 0.0)

prob.run_driver()

print(prob.get_val('xI'))
print(prob.get_val('xC'))
print(prob.get_val('comp.f'))



from openmdao.api import Problem, Group, IndepVarComp, SimpleGADriver
from openmdao.test_suite.components.branin import Branin

prob = Problem()
model = prob.model = Group()

model.add_subsystem('p1', IndepVarComp('xC', 7.5))
model.add_subsystem('p2', IndepVarComp('xI', 0.0))
model.add_subsystem('comp', Branin())

model.connect('p2.xI', 'comp.x0')
model.connect('p1.xC', 'comp.x1')

model.add_design_var('p2.xI', lower=-5.0, upper=10.0)
model.add_design_var('p1.xC', lower=0.0, upper=15.0)
model.add_objective('comp.f')

prob.driver = SimpleGADriver()
prob.driver.options['bits'] = {'p1.xC': 8}

prob.setup()
prob.run_driver()

# Optimal solution
print('comp.f', prob['comp.f'])

