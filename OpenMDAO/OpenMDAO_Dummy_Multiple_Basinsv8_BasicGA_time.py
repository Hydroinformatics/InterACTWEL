import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt
from Dummy_SWAT_modelv8_BasicGA_time import Farmers
from itertools import product
import time
import json
import os

#%%
print('Starting run')

nyears = 3

hrus_areas = {1:20,
              2:40, 
              3:15,
              4:10,
              5:30, 
              6:25,
              7:15,
              8:30,
              9:35}

hrus_crops = {1:[2,1,2],
              2:[1,3,3], 
              3:[1,2,1],
              4:[1,3,3],
              5:[3,1,1], 
              6:[2,3,3],
              7:[3,3,1],
              8:[1,2,1],
              9:[2,3,3]}

hru_wrs = {1:[1],
           2:[1], 
           3:[1],
           4:[2],
           5:[2], 
           6:[2],
           7:[2,3],
           8:[3],
           9:[3]}

wr_vols = {1:[3,60], 
           2:[1,25], 
           3:[3,80]}


#%%
hrus_areas_model = dict()
hrus_crops_model = dict()

wrs_hrus = dict()

for wrids in wr_vols.keys():
    
    hrus_areas_model[wrids] = []
    hrus_crops_model[wrids] = []
    wrs_hrus[wrids] = []
    
    for hruids in hru_wrs.keys():
        for hruwrid in hru_wrs[hruids]:
            if hruwrid == wrids:
                hrus_areas_model[wrids].append(hrus_areas[hruids])
                wrs_hrus[wrids].append(hruids)
    
    
    for yi in range(0,nyears):
        temp_crops = []
        for hruids in hru_wrs.keys():
            for hruwrid in hru_wrs[hruids]:
                if hruwrid == wrids:
                    temp_crops.append(hrus_crops[hruids][yi])
        
        hrus_crops_model[wrids].append(temp_crops)


#%%

json_actors = 'ga_solutions_farmer_time_v0_'

for wrids in wr_vols.keys():
    if os.path.exists(json_actors + str(wrids) + '_time_sharewr.json'):
        os.remove(json_actors + str(wrids) + '_time_sharewr.json')

#%%

start = time.time()

prob = om.Problem()
#prob.model = Farmers()

model = prob.model
model.add_subsystem('Region', Farmers(), promotes =['*'])
model.Region.nactors = len(wr_vols)

model.Region.hrus_areas = hrus_areas_model
model.Region.hrus_crops = hrus_crops_model
model.Region.wrs_hrus = wrs_hrus
model.Region.org_wr_vols = wr_vols
model.Region.json_file = json_actors

prob.driver = om.SimpleGADriver()
prob.driver.options['max_gen'] = 100
#prob.driver.options['Pm'] = 0.1
prob.driver.options['pop_size'] = 500
prob.driver.options['penalty_parameter'] = 20000.
prob.driver.options['penalty_exponent'] = 5.
prob.driver.options['compute_pareto'] = True

# model.add_design_var('wr_vols', lower=0, upper=100)
# model.add_design_var('hru_irr', lower=0, upper=100)
# model.add_design_var('hru_fert', lower=0, upper=2)

wr_vols_max = []
for wrids in wr_vols.keys():
    wr_vols_max.append(wr_vols[wrids][1])


model.add_design_var('wr_vols', lower=np.zeros(model.Region.nactors,dtype=int), upper = np.ones(model.Region.nactors,dtype=int)*100.)
model.add_design_var('hru_irr', lower=0, upper=100)
model.add_design_var('hru_fert', lower=0, upper=2)

model.add_objective('profit', scaler=-1)
model.add_objective('envir_impact', scaler=1)
model.add_constraint('total_wr', upper=sum(wr_vols_max))
model.add_constraint('const_per', lower=100, upper=100)

prob.setup()
prob.run_driver()

end = time.time()
time_consumed=end-start;
#%%
print('################# RESULTS ##################')

# print(prob.get_val('wr_vols'))
# print(prob.get_val('profit'))
# print(prob.get_val('hru_irr'))
# print(prob.get_val('hru_fert'))

desvar_nd = prob.driver.desvar_nd
nd_obj = prob.driver.obj_nd

json_results = 'opt_ga_resultswr_time_v1.json'
opt_results = dict()
opt_results['desvar_nd'] = desvar_nd.tolist() 
opt_results['nd_obj'] = nd_obj.tolist()

with open(json_results, 'w') as fp:
    json.dump(opt_results, fp)

# print(desvar_nd )
# sorted_obj = nd_obj[nd_obj[:, 0].argsort()]
# print(sorted_obj)

#%%
# plt.plot(sorted_obj[:,0]*-1,sorted_obj[:,1],'-o')
# plt.xlabel("Profit")
# plt.ylabel("Environmental Impact")


#%%
import json
json_results = 'opt_ga_resultswr_time_v1.json'

with open(json_results) as json_file:
    opt_results = json.load(json_file)

# desvar_nd = np.asarray(opt_results['desvar_nd'])
# nd_obj = np.asarray(opt_results['nd_obj'])

# sorted_obj = nd_obj[nd_obj[:, 0].argsort()]
# desvar_nd_sort = desvar_nd[nd_obj[:, 0].argsort()]

# print(desvar_nd_sort)
# print(sorted_obj)

# plt.plot(sorted_obj[:,0]*-1,sorted_obj[:,1],'-o')
# plt.xlabel("Profit")
# plt.ylabel("Environmental Impact")



# total_wrs_vols = np.sum(desvar_nd_sort[:,0:len(wr_vols)],axis=1)
