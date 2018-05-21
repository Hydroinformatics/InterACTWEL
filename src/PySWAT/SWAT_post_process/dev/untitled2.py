from __future__ import print_function, division, absolute_import

import unittest

from openmdao.utils.assert_utils import assert_rel_error

from openmdao.api import Problem, SimpleGADriver, ExecComp, IndepVarComp, DirectSolver, ScipyOptimizeDriver
from openmdao.test_suite.components.sellar_feature import SellarMDA

prob = Problem()
prob.model = SellarMDA()


#prob.driver = SimpleGADriver()
#prob.driver.options['pop_size'] = 1000

prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-8


prob.model.add_design_var('x', lower=0, upper=10)
prob.model.add_design_var('z', lower=0, upper=10)
prob.model.add_objective('obj')
prob.model.add_constraint('con1', upper=0)
prob.model.add_constraint('con2', upper=0)

#prob.driver.options['bits'] = {'indeps.z' : 16}
#prob.driver.options['bits'] = {'indeps.x' : 16}

prob.setup()
#prob.set_solver_print(level=0)

# Ask OpenMDAO to finite-difference across the model to compute the gradients for the optimizer
#prob.model.approx_totals()

prob.run_driver()
print('minimum found at')
print(prob['x'][0])
print(prob['z'])

print('minumum objective')
print(prob['obj'][0])

#        print('minimum found at')
#        assert_rel_error(self, prob['x'][0], 0., 1e-5)
#        assert_rel_error(self, prob['z'], [1.977639, 0.], 1e-5)
#
#        print('minumum objective')
#        assert_rel_error(self, prob['obj'][0], 3.18339395045, 1e-5)
#        


