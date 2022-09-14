import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt
from Dummy_SWAT_modelv8_BasicGA import Farmers
from itertools import product
import time
import json


#%%

hrus_areas = {1:20,
              2:40, 
              3:15,
              4:10,
              5:30, 
              6:25,
              7:15,
              8:30,
              9:35}

hrus_crops = {1:[2],
              2:[1], 
              3:[1],
              4:[1],
              5:[3], 
              6:[2],
              7:[3],
              8:[1],
              9:[2]}

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
                hrus_crops_model[wrids].append(hrus_crops[hruids][0])
                wrs_hrus[wrids].append(hruids)



# items = range(0,100,1)
# hru_irr_per = dict()
# for wrids in wr_vols.keys():
#     temp = []
#     for item in product(items, repeat=len(hrus_areas_model[wrids])):
#         if np.sum(item) == 100:
#             temp.append(item)
        
#     hru_irr_per[wrids] = np.asarray(temp)
#     print(wrids)

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

prob.driver = om.SimpleGADriver()
prob.driver.options['max_gen'] = 2000
#prob.driver.options['Pm'] = 0.1
prob.driver.options['pop_size'] = 2000
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

json_results = 'opt_ga_resultswr_v0.json'
opt_results = dict()
opt_results['desvar_nd'] = desvar_nd.tolist() 
opt_results['nd_obj'] = nd_obj.tolist()

with open(json_results, 'w') as fp:
    json.dump(opt_results, fp)

print(desvar_nd )
sorted_obj = nd_obj[nd_obj[:, 0].argsort()]
print(sorted_obj)

#%%
plt.plot(sorted_obj[:,0]*-1,sorted_obj[:,1],'-o')
plt.xlabel("Profit")
plt.ylabel("Environmental Impact")
