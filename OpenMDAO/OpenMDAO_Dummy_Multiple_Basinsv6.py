import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt
from Dummy_SWAT_modelv6 import FEWNexus
import time
start = time.time()

prob = om.Problem()
prob.model = FEWNexus()
prob.model.nactors = 2

prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = "differential_evolution"
prob.driver.options['maxiter'] = 20
prob.driver.options['tol'] = 1e-8

# prob.driver = om.SimpleGADriver()
# prob.driver.options['max_gen'] = 10
# prob.driver.options['pop_size'] = 20
# prob.driver.options['penalty_parameter'] = 200.
# prob.driver.options['penalty_exponent'] = 5.
# prob.driver.options['compute_pareto'] = True

prob.model.add_design_var('wr_vols', lower=0, upper=100)
prob.model.add_objective('profit', scaler=1)

#prob.model.add_constraint('aggregator.gw_wrvols', upper = 20.0)

#prob.model.nonlinear_solver = om.NonlinearBlockGS()
prob.model.approx_totals()

prob.setup()
prob.run_driver()

end = time.time()
time_consumed=end-start;

print('################# RESULTS ##################')

print(prob.get_val('wr_vols'))

for i in range(0,2):
    print(prob.get_val('farmer_' + str(i+1) + '_plan.indv_profit'))
    exec("parr = prob.model.farmer_" + str(i+1) + "_plan.prob.model")
    #print(parr.get_val('farmer.hru_irr'),parr.get_val('farmer.indv_profit'))
    print(parr.get_val('farmer.hru_irr'),parr.get_val('farmer.hru_fert'))


# desvar_nd = prob.driver.desvar_nd
# nd_obj = prob.driver.obj_nd
# sorted_obj = nd_obj[nd_obj[:, 0].argsort()]
# plt.plot(-1*sorted_obj[:,0],np.sort(sorted_obj[:,1]),'-.')
