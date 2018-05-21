#import numpy as np
#
#from openmdao.api import Problem, ScipyOptimizeDriver, SimpleGADriver
#
#from openmdao.test_suite.test_examples.beam_optimization.beam_group import BeamGroup
#
#E = 1.
#L = 1.
#b = 0.1
#volume = 0.01
#
#num_elements = 50
#
#prob = Problem(model=BeamGroup(E=E, L=L, b=b, volume=volume, num_elements=num_elements))
#
#prob.driver = ScipyOptimizeDriver()
#prob.driver.options['optimizer'] = 'SLSQP'
#prob.driver.options['tol'] = 1e-9
#prob.driver.options['disp'] = True
#
##prob.driver = SimpleGADriver()
#
#
#prob.setup()
#
#prob.run_driver()
#
#print(prob['inputs_comp.h'])

import pyopt

