import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt
from Dummy_SWAT_modelv6_trobshoot import FEWNexus

prob = om.Problem()
prob.model = FEWNexus()
prob.model.nactors = 2

prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = "differential_evolution"
prob.driver.options['maxiter'] = 100
prob.driver.options['tol'] = 1e-8

# prob.driver = om.SimpleGADriver()
# prob.driver.options['max_gen'] = 50
# prob.driver.options['pop_size'] = 10
# prob.driver.options['penalty_parameter'] = 200.
# prob.driver.options['penalty_exponent'] = 5.
# prob.driver.options['compute_pareto'] = True

prob.model.add_design_var('wr_vols', lower=0, upper=100)
prob.model.add_objective('profit', scaler=-1)

#prob.model.nonlinear_solver = om.NonlinearBlockGS()
prob.model.approx_totals()

prob.setup()
prob.run_driver()

print('################# RESULTS ##################')

print(prob.get_val('wr_vols'))
print(prob.get_val('profit'))

# for i in range(0,2):
#     print(prob.get_val('farmer_' + str(i+1) + '_plan.indv_profit'))
#     exec("parr = prob.model.farmer_" + str(i+1) + "_plan")
#     print(parr.get_val('indv_profit'))
