import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt
from Dummy_SWAT_modelv6_BasicGA import Farmers
import time
start = time.time()

prob = om.Problem()
#prob.model = Farmers()

model = prob.model
model.add_subsystem('Region', Farmers(),promotes =['*'])
model.Region.nactors = 2

# prob.driver = om.ScipyOptimizeDriver()
# prob.driver.options['optimizer'] = "differential_evolution"
# prob.driver.options['maxiter'] = 100
# prob.driver.options['tol'] = 1e-8

prob.driver = om.SimpleGADriver()
prob.driver.options['max_gen'] = 200
prob.driver.options['pop_size'] = 200
prob.driver.options['penalty_parameter'] = 200.
prob.driver.options['penalty_exponent'] = 5.
prob.driver.options['compute_pareto'] = True

model.add_design_var('wr_vols', lower=0, upper=100)
model.add_design_var('hru_irr', lower=0, upper=100)
model.add_design_var('hru_fert', lower=0, upper=2)

model.add_objective('profit', scaler=-1)
#model.add_objective('indv_profit', scaler=-1)

#prob.model.add_constraint('aggregator.gw_wrvols', upper = 20.0)

#prob.model.nonlinear_solver = om.NonlinearBlockGS()
#prob.model.approx_totals()

prob.setup()
prob.run_driver()

end = time.time()
time_consumed=end-start;

print('################# RESULTS ##################')

# print(prob.get_val('wr_vols'))
# print(prob.get_val('profit'))
# print(prob.get_val('hru_irr'))
# print(prob.get_val('hru_fert'))

desvar_nd = prob.driver.desvar_nd
nd_obj = prob.driver.obj_nd

print(desvar_nd )
print(nd_obj)

# sorted_obj = nd_obj[nd_obj[:, 0].argsort()]
# plt.plot(-1*sorted_obj[:,0],np.sort(sorted_obj[:,1]),'-.')
