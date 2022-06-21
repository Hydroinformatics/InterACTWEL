import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt
from Dummy_SWAT_modelv6 import FEWNexus
import time
start = time.time()

prob = om.Problem()
prob.model = FEWNexus()
prob.model.nactors = 2

# prob.driver = om.ScipyOptimizeDriver()
# prob.driver.options['optimizer'] = "differential_evolution"
# prob.driver.options['maxiter'] = 20
# prob.driver.options['tol'] = 1e-8

prob.driver = om.SimpleGADriver()
prob.driver.options['max_gen'] = 20
prob.driver.options['pop_size'] = 20
prob.driver.options['penalty_parameter'] = 200.
prob.driver.options['penalty_exponent'] = 5.
prob.driver.options['compute_pareto'] = True

prob.model.add_design_var('wr_vols', lower=0, upper=100)
prob.model.add_objective('profit', scaler=1)
prob.model.add_objective('envir_impact', scaler=-1)

#prob.model.add_constraint('aggregator.gw_wrvols', upper = 20.0)

#prob.model.nonlinear_solver = om.NonlinearBlockGS()
prob.model.approx_totals()

prob.setup()
prob.run_driver()

end = time.time()
time_consumed=end-start;

print('################# RESULTS ##################')
print(time_consumed)
print(prob.driver.obj_nd)
print(prob.driver.desvar_nd)

desvar_nd = prob.driver.desvar_nd
nd_obj = prob.driver.obj_nd
sorted_obj = nd_obj[nd_obj[:, 0].argsort()]

fig, ax = plt.subplots(3, 1)
#plt.subplot(3, 1, 1)
#lt.plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')
ax[0].plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')

for i in range(0,2):
    #print(prob.get_val('farmer_' + str(i+1) + '_plan.indv_profit'))
    #exec("parr = prob.model.farmer_" + str(i+1) + "_plan.prob.model")
    #print(parr.get_val('farmer.hru_irr'),parr.get_val('farmer.indv_profit'))
    #print(parr.get_val('farmer.hru_irr'),parr.get_val('farmer.hru_fert'))
    exec("obj_nd = prob.model.farmer_" + str(i+1) + "_plan.prob.driver.obj_nd")
    exec("desvar = prob.model.farmer_" + str(i+1) + "_plan.prob.driver.desvar_nd")
    indobj = obj_nd[:, 0].argsort()
    #plt.subplot(3, 1, i+2)
    #plt.plot(-1*obj_nd[indobj,0],obj_nd[indobj,1],'-o')
    ax[i+1].plot(-1*obj_nd[indobj,0],obj_nd[indobj,1],'-o')
    print(obj_nd[indobj[0]])
    print(desvar[indobj][0])


fig.tight_layout()
plt.show()