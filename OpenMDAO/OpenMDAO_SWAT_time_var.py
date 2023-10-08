import numpy as np
import os
import openmdao.api as om
import matplotlib.pyplot as plt
import time
import json 
import pandas as pd

os.chdir(r'M:\GitHub\InterACTWEL\OpenMDAO')

from pareto import eps_sort
from FEW_SWAT_modelv8 import FEWNexus

#%%
out_path = '/SWAT_WR_files/MDAO_WRS_NOWA.txt'
wr_mdao = []
with open(os.getcwd() + out_path, 'r') as search:
    for line in search:
        if len(line) > 0:
            wr_mdao.append(int(line))

search.close()    

hru_wrs_data = pd.read_csv(os.getcwd()+'/SWAT_WR_files/hruwr_deepGW_CR.dat', delim_whitespace=True, header=0, index_col=None, na_values='(missing)').to_numpy()
#hru_wrs = pd.read_csv(r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\hruwr_deepGW_CR.dat', delim_whitespace=True, header=0, index_col=None, na_values='(missing)').set_index('WR_ID').stack().groupby('WR_ID').apply(list).to_dict()

hru_wrs = dict()
for row in hru_wrs_data:
    if row[1] not in hru_wrs.keys() and row[1] in wr_mdao:
        hru_wrs[row[1]] = []
    
    if row[1] in wr_mdao:
        hru_wrs[row[1]].append(row[0])


wrs_data = pd.read_csv(os.getcwd()+'/SWAT_WR_files/wrdata_deepGW_CR.dat', delim_whitespace=True, header=0, index_col=None, na_values='(missing)').to_numpy()

wr_vols = dict()
for row in wrs_data:
    if row[1] not in wr_vols.keys() and row[1] in wr_mdao:
        wr_vols[row[1]] = row[3]



#%%
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


# #%%
# json_actors = 'actors_solutions_farmer_'
# json_results = 'opt_resultswr_vtime.json'

# for wrids in wr_vols.keys():
#     if os.path.exists(json_actors + str(wrids) + '_sharewr_vtime.json'):
#         os.remove(json_actors + str(wrids) + '_sharewr_vtime.json')

# #%%
# #start = time.time()

# # Create a recorder
# # recorder = om.SqliteRecorder('cases.sql')

# prob = om.Problem()
# prob.model = FEWNexus()
# prob.model.nactors = len(wr_vols)
# prob.model.nyears = nyears

# prob.model.hrus_areas = hrus_areas_model
# prob.model.hrus_crops = hrus_crops_model
# prob.model.wrs_hrus = wrs_hrus
# prob.model.org_wr_vols = wr_vols
# prob.model.json_file = json_actors
# # prob.model.share_wr_irrvol = share_wr_irrvol

# # prob.driver = om.ScipyOptimizeDriver()
# # prob.driver.options['optimizer'] = "differential_evolution"
# # prob.driver.options['maxiter'] = 20
# # prob.driver.options['tol'] = 1e-8

# # prob.add_recorder(recorder)

# prob.driver = om.SimpleGADriver()
# prob.driver.options['max_gen'] = 10
# prob.driver.options['Pm'] = 0.1
# prob.driver.options['pop_size'] = 10
# prob.driver.options['penalty_parameter'] = 20000.
# prob.driver.options['penalty_exponent'] = 5.
# prob.driver.options['compute_pareto'] = True

# # Attach recorder to the driver
# # prob.driver.add_recorder(recorder)


# wr_vols_max = []
# for wrids in wr_vols.keys():
#     wr_vols_max.append(wr_vols[wrids][1])

# #prob.model.add_design_var('wr_vols', lower=np.zeros(prob.model.nactors,dtype=int), upper = np.ones(prob.model.nactors,dtype=int)*sum(wr_vols_max))
# prob.model.add_design_var('wr_vols', lower=np.zeros(prob.model.nactors,dtype=int), upper = np.ones(prob.model.nactors,dtype=int)*100.)

# prob.model.add_objective('profit', scaler=1)
# prob.model.add_objective('envir_impact', scaler=1)
# prob.model.add_constraint('total_wr', upper=sum(wr_vols_max))

# #prob.model.nonlinear_solver = om.NonlinearBlockGS()
# prob.model.approx_totals()

# prob.setup()
# prob.run_driver()
# # prob.record("final_state")
# # prob.cleanup()
# #end = time.time()
# #time_consumed = end-start;

# #%%
# print('################# RESULTS ##################')


# desvar_nd = prob.driver.desvar_nd
# nd_obj = prob.driver.obj_nd
# sorted_obj = nd_obj[nd_obj[:, 0].argsort()]

# print(sorted_obj)
# print(desvar_nd[nd_obj[:, 0].argsort()])
# print(np.sum(desvar_nd[nd_obj[:, 0].argsort()], axis=1))

# #%%
# plt.plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')
# plt.xlabel("Profit")
# plt.ylabel("Environmental Impact")

# for i in range(0,len(nd_obj[:,0])):
#     plt.annotate(str(int(sum(desvar_nd[i]))), (-1*nd_obj[i,0], nd_obj[i,1]-100),rotation=270)

# #%%
# x = range(1,len(desvar_nd)+1)
# y1 = desvar_nd[:,0]
# y2 = desvar_nd[:,1]
# y3 = desvar_nd[:,2]

# plt.bar(x, y1, color='r')
# plt.bar(x, y2, bottom=y1, color='b')
# plt.bar(x, y3, bottom=y2+y1, color='g')
# plt.show()

# #%%
# opt_results = dict()
# opt_results['desvar_nd'] = desvar_nd.tolist() 
# opt_results['nd_obj'] = nd_obj.tolist()

# with open(json_results, 'w') as fp:
#     json.dump(opt_results, fp)


