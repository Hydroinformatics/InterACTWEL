import numpy as np
import os
import openmdao.api as om
import matplotlib.pyplot as plt
from Dummy_SWAT_modelv6 import FEWNexus
import time
import json 
from pareto import eps_sort

#%%

start = time.time()

prob = om.Problem()
prob.model = FEWNexus()
prob.model.nactors = 2

# prob.driver = om.ScipyOptimizeDriver()
# prob.driver.options['optimizer'] = "differential_evolution"
# prob.driver.options['maxiter'] = 20
# prob.driver.options['tol'] = 1e-8

if os.path.exists('actors_solutions.json'):
    os.remove('actors_solutions.json')

prob.driver = om.SimpleGADriver()
prob.driver.options['max_gen'] = 50
prob.driver.options['Pm'] =0.1
prob.driver.options['pop_size'] = 50
prob.driver.options['penalty_parameter'] = 200.
prob.driver.options['penalty_exponent'] = 5.
prob.driver.options['compute_pareto'] = True

prob.model.add_design_var('wr_vols', lower=0, upper=100)

prob.model.add_objective('profit', scaler=1)
prob.model.add_objective('envir_impact', scaler=1)

#prob.model.add_constraint('aggregator.gw_wrvols', upper = 20.0)

#prob.model.nonlinear_solver = om.NonlinearBlockGS()
prob.model.approx_totals()

prob.setup()
prob.run_driver()

end = time.time()
time_consumed = end-start;

print('################# RESULTS ##################')

print(time_consumed)
print(prob.driver.obj_nd)
print(prob.driver.desvar_nd)

desvar_nd = prob.driver.desvar_nd
nd_obj = prob.driver.obj_nd
sorted_obj = nd_obj[nd_obj[:, 0].argsort()]

plt.plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')
plt.xlabel("Profit")
plt.ylabel("Environmental Impact")


#%%
fig, ax = plt.subplots(prob.model.nactors, 1)
#plt.subplot(3, 1, 1)
#plt.plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')
#ax[0].plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')


for i in range(0,prob.model.nactors):
    #print(prob.get_val('farmer_' + str(i+1) + '_plan.indv_profit'))
    #exec("parr = prob.model.farmer_" + str(i+1) + "_plan.prob.model")
    #print(parr.get_val('farmer.hru_irr'),parr.get_val('farmer.indv_profit'))
    #print(parr.get_val('farmer.hru_irr'),parr.get_val('farmer.hru_fert'))
    exec("obj_nd = prob.model.farmer_" + str(i+1) + "_plan.prob.driver.obj_nd")
    exec("desvar = prob.model.farmer_" + str(i+1) + "_plan.prob.driver.desvar_nd")
    indobj = obj_nd[:, 0].argsort()
    #plt.subplot(3, 1, i+2)
    #plt.plot(-1*obj_nd[indobj,0],obj_nd[indobj,1],'-o')
    ax[i].plot(-1*obj_nd[indobj,0]/1000000.0,obj_nd[indobj,1],'-o')
    ax[i].set_xlabel("Profit")
    ax[i].set_ylabel("Environmental Impact")
    ax[i].set_title('Farmer_' + str(i+1))
    #print(obj_nd[indobj[0]])
    #print(desvar[indobj][0])
    print(obj_nd[indobj])
    print(desvar[indobj])

fig.tight_layout()
plt.show()


#%%

with open('actors_solutions_v2.json') as json_file:
    actors_solutions = json.load(json_file)

#%%
colors = ['b','r']
cci = 0
plt.subplot(121)
for act_id in actors_solutions.keys():
    for wrid in actors_solutions[act_id].keys():
        temp = actors_solutions[act_id][wrid]['profit']['Value']
        plt.plot(float(wrid), float(temp)*-1,'.', c= colors[cci])
    
    cci = cci + 1
        

cci = 0
plt.subplot(122)
for act_id in actors_solutions.keys():
    for wrid in actors_solutions[act_id].keys():
        temp = actors_solutions[act_id][wrid]['envir']['Value']
        plt.plot(float(wrid), float(temp),'.', c= colors[cci])
    
    cci = cci + 1


#%%

colors = ['b','r']
cci = 0

temp_data = []
pareto_farmer = np.load('Pareto_farmer_1.npy')

#for act_id in actors_solutions.keys():
for act_id in ['farmer_1']:
    for wrid in actors_solutions[act_id].keys():
        tempp = actors_solutions[act_id][wrid]['profit']['Value']
        tempe = actors_solutions[act_id][wrid]['profit']['Envir']
        
        plt.plot(float(tempp)*-1, float(tempe),'.', c=colors[cci])
        
        tempp2 = actors_solutions[act_id][wrid]['envir']['Profit']
        tempe2 = actors_solutions[act_id][wrid]['envir']['Value']
        
        plt.plot(float(tempp2)*-1, float(tempe2),'.', c=colors[cci])
        
        # if tempp != 0:
        #     tempp = tempp*-1
        #if abs(tempp) != 0 and abs(tempe) != 0: 
        temp_data.append([float(wrid),tempp,tempe])
        temp_data.append([float(wrid),tempp2,tempe2])
            

    cci = cci + 1

plt.plot(pareto_farmer[:,1]*-1, pareto_farmer[:,2],'-m.',fillstyle='none')

temp_data = np.asarray(temp_data)
ss = eps_sort(temp_data,[1,2])
ss = np.asarray(ss)
ss = ss[ss[:,1].argsort()]
plt.plot(ss[:,1]*-1, ss[:,2],'-k', marker=(5, 1))

for x in ss: 
    plt.annotate(x[0], (x[1]*-1, x[2]-100),rotation=270)

plt.tight_layout()
plt.show()


#%%


colors = ['b','r']
cci = 0

for act_id in actors_solutions.keys():
    for wrid in actors_solutions[act_id].keys():
        tempp = actors_solutions[act_id][wrid]['profit']['Value']
        tempe = actors_solutions[act_id][wrid]['envir']['Value']
        
        plt.plot(float(tempp)*-1, float(tempe),'.', c=colors[cci])
        

    exec("obj_nd = prob.model." + act_id + "_plan.prob.driver.obj_nd")
    exec("desvar = prob.model." + act_id + "_plan.prob.driver.desvar_nd")
    #indobj = obj_nd[:, 0].argsort()

    #plt.plot(-1*obj_nd[indobj,0],obj_nd[indobj,1],'-o')

    cci = cci + 1


fig.tight_layout()
plt.show()