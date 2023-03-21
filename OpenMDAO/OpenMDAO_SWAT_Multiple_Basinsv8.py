import numpy as np
import os
import openmdao.api as om
import matplotlib.pyplot as plt
from FEW_SWAT_modelv8 import FEWNexus
import time
import json 
from pareto import eps_sort

#%%

out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\MDAO_WRS_NOWA.txt'
wr_mdao = []
with open(out_path, 'r') as search:
    for line in search:
        if len(line) > 0:
            wr_mdao.append(int(line))

search.close()    

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


#%%
json_actors = 'actors_solutions_v2_farmer_'
json_results = 'opt_resultswr_v2.json'

for wrids in wr_vols.keys():
    if os.path.exists(json_actors + str(wrids) + '_sharewr.json'):
        os.remove(json_actors + str(wrids) + '_sharewr.json')

#%%
#start = time.time()

prob = om.Problem()
prob.model = FEWNexus()
prob.model.nactors = len(wr_vols)

prob.model.hrus_areas = hrus_areas_model
prob.model.hrus_crops = hrus_crops_model
prob.model.wrs_hrus = wrs_hrus
prob.model.org_wr_vols = wr_vols
prob.model.json_file = json_actors
# prob.model.share_wr_irrvol = share_wr_irrvol

# prob.driver = om.ScipyOptimizeDriver()
# prob.driver.options['optimizer'] = "differential_evolution"
# prob.driver.options['maxiter'] = 20
# prob.driver.options['tol'] = 1e-8


prob.driver = om.SimpleGADriver()
prob.driver.options['max_gen'] = 50
prob.driver.options['Pm'] = 0.1
prob.driver.options['pop_size'] = 500
prob.driver.options['penalty_parameter'] = 20000.
prob.driver.options['penalty_exponent'] = 5.
prob.driver.options['compute_pareto'] = True


wr_vols_max = []
for wrids in wr_vols.keys():
    wr_vols_max.append(wr_vols[wrids][1])

#prob.model.add_design_var('wr_vols', lower=np.zeros(prob.model.nactors,dtype=int), upper = np.ones(prob.model.nactors,dtype=int)*sum(wr_vols_max))
prob.model.add_design_var('wr_vols', lower=np.zeros(prob.model.nactors,dtype=int), upper = np.ones(prob.model.nactors,dtype=int)*100.)

prob.model.add_objective('profit', scaler=1)
prob.model.add_objective('envir_impact', scaler=1)
prob.model.add_constraint('total_wr', upper=sum(wr_vols_max))

#prob.model.nonlinear_solver = om.NonlinearBlockGS()
prob.model.approx_totals()

prob.setup()
# om.n2(prob)
prob.run_driver()

#end = time.time()
#time_consumed = end-start;

#%%
print('################# RESULTS ##################')

desvar_nd = prob.driver.desvar_nd
nd_obj = prob.driver.obj_nd
sorted_obj = nd_obj[nd_obj[:, 0].argsort()]

print(sorted_obj)
print(desvar_nd[nd_obj[:, 0].argsort()])
print(np.sum(desvar_nd[nd_obj[:, 0].argsort()], axis=1))

#%%
# plt.plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')
# plt.xlabel("Profit")
# plt.ylabel("Environmental Impact")

# for i in range(0,len(nd_obj[:,0])):
#     plt.annotate(str(int(sum(desvar_nd[i]))), (-1*nd_obj[i,0], nd_obj[i,1]-100),rotation=270)

#%%
# x = range(1,len(desvar_nd)+1)
# y1 = desvar_nd[:,0]
# y2 = desvar_nd[:,1]
# y3 = desvar_nd[:,2]

# plt.bar(x, y1, color='r')
# plt.bar(x, y2, bottom=y1, color='b')
# plt.bar(x, y3, bottom=y2+y1, color='g')
# plt.show()

#%%
opt_results = dict()
opt_results['desvar_nd'] = desvar_nd.tolist() 
opt_results['nd_obj'] = nd_obj.tolist()

with open(json_results, 'w') as fp:
    json.dump(opt_results, fp)

#%%
# fig, ax = plt.subplots(prob.model.nactors, 1)
# #plt.subplot(3, 1, 1)
# #plt.plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')
# #ax[0].plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')


# for i in range(0,prob.model.nactors):
#     #print(prob.get_val('farmer_' + str(i+1) + '_plan.indv_profit'))
#     #exec("parr = prob.model.farmer_" + str(i+1) + "_plan.prob.model")
#     #print(parr.get_val('farmer.hru_irr'),parr.get_val('farmer.indv_profit'))
#     #print(parr.get_val('farmer.hru_irr'),parr.get_val('farmer.hru_fert'))
#     exec("obj_nd = prob.model.farmer_" + str(i+1) + "_plan.prob.driver.obj_nd")
#     exec("desvar = prob.model.farmer_" + str(i+1) + "_plan.prob.driver.desvar_nd")
#     indobj = obj_nd[:, 0].argsort()
#     #plt.subplot(3, 1, i+2)
#     #plt.plot(-1*obj_nd[indobj,0],obj_nd[indobj,1],'-o')
#     ax[i].plot(-1*obj_nd[indobj,0]/1000000.0,obj_nd[indobj,1],'-o')
#     ax[i].set_xlabel("Profit")
#     ax[i].set_ylabel("Environmental Impact")
#     ax[i].set_title('Farmer_' + str(i+1))
#     #print(obj_nd[indobj[0]])
#     #print(desvar[indobj][0])
#     print(obj_nd[indobj])
#     print(desvar[indobj])

# fig.tight_layout()
# plt.show()


# #%%
    
# with open(json_results) as json_file:
#     opt_results = json.load(json_file)


# farmer_id = 1
# with open(json_actors + str(farmer_id) + '_sharewr.json') as json_file:
#     actors_solutions = json.load(json_file)

# #%%
# nd_obj = np.asarray(opt_results['nd_obj'])
# desvar_nd = np.asarray(opt_results['desvar_nd'])

# sorted_obj = nd_obj[nd_obj[:, 0].argsort()]
# desvar_nd_sort = desvar_nd[nd_obj[:, 0].argsort()]

# total_wrs_vols = np.sum(desvar_nd_sort, axis=1)

# plt.plot(-1*sorted_obj[:,0],sorted_obj[:,1],'-o')
# plt.xlabel("Profit")
# plt.ylabel("Environmental Impact")

# plt.tight_layout()
# plt.show()

# #%%
# farmer_id = 1
# colors = ['b','r','g']
# cci = 0
# plt.subplot(121)
# for act_id in actors_solutions.keys():
#     for wrid in actors_solutions[act_id].keys():
#         temp = actors_solutions[act_id][wrid]['profit']['Value']
#         plt.plot(float(wrid), float(temp)*-1,'.', c= colors[cci])
    
#     cci = cci + 1
    

# cci = 0
# plt.subplot(122)
# for act_id in actors_solutions.keys():
#     for wrid in actors_solutions[act_id].keys():
#         temp = actors_solutions[act_id][wrid]['envir']['Value']
#         plt.plot(float(wrid), float(temp),'.', c= colors[cci])
    
#     cci = cci + 1


# #%%

# # colors = ['b','r','g']
# # cci = 0

# # temp_data = np.zeros((1,3))
# # # pareto_farmer = np.load('Pareto_farmer_1.npy')

# # #for act_id in actors_solutions.keys():
# # for act_id in ['farmer_1']:
# #     for wrid in actors_solutions[act_id].keys():
# #         if float(wrid) < 101:
# #             tempp = actors_solutions[act_id][wrid]['profit']['Value']
# #             tempe = actors_solutions[act_id][wrid]['profit']['Envir']
            
# #             plt.plot(float(tempp)*-1, float(tempe),'.', c=colors[cci])
            
# #             tempp2 = actors_solutions[act_id][wrid]['envir']['Profit']
# #             tempe2 = actors_solutions[act_id][wrid]['envir']['Value']
            
# #             plt.plot(float(tempp2)*-1, float(tempe2),'.', c=colors[cci])
            
# #             # if tempp != 0:
# #             #     tempp = tempp*-1
# #             #if abs(tempp) != 0 and abs(tempe) != 0: 
# #             temp_data = np.vstack((temp_data,[float(wrid),tempp*-1,tempe]))
# #             temp_data = np.vstack((temp_data,[float(wrid),tempp2*-1,tempe2]))       

# #     cci = cci + 1

# # # plt.plot(pareto_farmer[:,1]*-1, pareto_farmer[:,2],'-m.',fillstyle='none')

# # temp_data = temp_data[1:,:]  

# # ss = eps_sort(temp_data,[1,2])
# # ss = np.asarray(ss)
# # ss = ss[ss[:,1].argsort()]


# # temp_data = np.asarray(temp_data)
# # ss = eps_sort(temp_data,[1,2])
# # ss = np.asarray(ss)
# # ss = ss[ss[:,1].argsort()]
# # plt.plot(ss[:,1]*-1, ss[:,2],'-k', marker=(5, 1))

# # # for x in ss: 
# # #     plt.annotate(x[0], (x[1]*-1, x[2]-100),rotation=270)

# # with open('Pareto_farmer_2_100.json') as json_file:
# #     pareto_farmer = json.load(json_file)

# # temp_data_p = []  
# # for i in pareto_farmer.keys():
# #     for ii in pareto_farmer[i].keys():
# #         for iii in pareto_farmer[i][ii].keys():
# #                 temp_data_p.append([float(pareto_farmer[i][ii]['indv_profit']), float(pareto_farmer[i][ii]['indv_envir'])])

# # temp_data_p = np.asarray(temp_data_p)
# # # ss_p = eps_sort(temp_data_p,[0,1])
# # # ss_p = np.asarray(ss_p)
# # # ss_p = ss_p[ss_p[:,0].argsort()]
# # temp_data_p = temp_data_p[temp_data_p[:,0].argsort()]
# # plt.plot(temp_data_p[:,0], temp_data_p[:,1],'-m.',fillstyle='none')


# #%%

# #path_file = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/InFEWS/OpenMDAO'
# path_file= r'C:/Users/riversam/Box/Research/InFEWS/OpenMDAO/Full_Solutions'

# ss_data = np.zeros((1,4))

# # #for wrvols in range(1,101,1):
# # for wrvols in range(1,101,1):
# #     print(wrvols)
# with open(path_file + '/Farmer_' +str(farmer_id) +'_ALL_Solutions_v2_.json') as json_file:
#     results = json.load(json_file)

# temp_data = []
# for i in results.keys():
#     for ii in results[i].keys():
#         # print(results[i][ii])
#         # for iii in results[i][ii].keys():

#         if abs(float(results[i][ii]['indv_profit'])) != 0: 
#             temp_data.append([int(i), int(ii), float(results[i][ii]['indv_profit']), float(results[i][ii]['indv_envir'])])

# temp_data = np.asarray(temp_data)
# #plt.plot(temp_data[:,2], temp_data[:,3],'.')

# ss = eps_sort(temp_data,[2,3])
# ss = np.asarray(ss)
# ss = ss[ss[:,2].argsort()]
# ss_data = np.vstack((ss_data,ss))

# ss_data = ss_data[1:,:]  

# plt.plot(temp_data[:,2]*-1, temp_data[:,3],'.')
# plt.plot(ss_data[:,2]*-1, ss_data[:,3],'-o')




# #%%

# colors = ['b','r','g']
# cci = 0

# act_id = 'farmer_' + str(farmer_id)
# temp_data = np.zeros((1,3))


# #for act_id in actors_solutions.keys():
# for wrid in actors_solutions[act_id].keys():
#     if float(wrid) < 101:
        
#         tempp = actors_solutions[act_id][wrid]['profit']['Value']
#         tempe = actors_solutions[act_id][wrid]['profit']['Envir']
#         #tempe = actors_solutions[act_id][wrid]['envir']['Value']
        
#         print(wrid,tempp,tempe)
        
#         #plt.plot(float(tempp)*-1, float(tempe),'.', c=colors[cci])
        
#         tempp2 = actors_solutions[act_id][wrid]['envir']['Profit']
#         tempe2 = actors_solutions[act_id][wrid]['envir']['Value']
        
#         #plt.plot(float(tempp2)*-1, float(tempe2),'.', c=colors[cci])
        
#         temp_data = np.vstack((temp_data,[float(wrid),tempp,tempe]))
#         temp_data = np.vstack((temp_data,[float(wrid),tempp2,tempe2]))     
        
        
# # plt.plot(pareto_farmer[:,1]*-1, pareto_farmer[:,2],'-m.',fillstyle='none')

# temp_data = temp_data[1:,:]  

# actor_ss = eps_sort(temp_data,[1,2])
# actor_ss = np.asarray(actor_ss)
# actor_ss = actor_ss[actor_ss[:,1].argsort()]

# f_pareto = eps_sort(ss_data,[3,4])
# f_pareto  = np.asarray(f_pareto)
# f_pareto = f_pareto[f_pareto[:,3].argsort()]

# plt.plot(f_pareto[:,3]*-1, f_pareto[:,4],'-mo',fillstyle='none')
# plt.plot(actor_ss[:,1]*-1, actor_ss[:,2],'k.',fillstyle='full')
# plt.tight_layout()
# plt.show()



# #%%
# farmer_id = 1
# colors = ['b','r','g']

# temp_data = np.zeros((1,4))
# for iwrvols in opt_results['desvar_nd']:
#     print(iwrvols)
    
#     wrid = str(iwrvols[0])
#     tempp = actors_solutions[act_id][wrid]['profit']['Value']
#     tempe = actors_solutions[act_id][wrid]['profit']['Envir']
#     #tempe = actors_solutions[act_id][wrid]['envir']['Value']
    
#     print(wrid,tempp,tempe)
    
#     #plt.plot(float(tempp)*-1, float(tempe),'.', c=colors[cci])
    
#     tempp2 = actors_solutions[act_id][wrid]['envir']['Profit']
#     tempe2 = actors_solutions[act_id][wrid]['envir']['Value']
    
#     #plt.plot(float(tempp2)*-1, float(tempe2),'.', c=colors[cci])
    
#     temp_data = np.vstack((temp_data,[float(wrid),tempp,tempe,0]))
#     temp_data = np.vstack((temp_data,[float(wrid),tempp2,tempe2,1])) 
    

# temp_data = temp_data[1:,:] 
# temp_data = temp_data[temp_data[:,0].argsort()]



# #path_file = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/InFEWS/OpenMDAO'
# path_file= r'C:/Users/riversam/Box/Research/InFEWS/OpenMDAO/Full_Solutions'
# ss_data = np.zeros((1,4))

# with open(path_file + '/Farmer_' +str(farmer_id) +'_ALL_Solutions_v2_.json') as json_file:
#     results_actfull = json.load(json_file)

# temp_data2 = []
# for i in np.unique(temp_data[:,0]):
#     if int(i) > 0:
#         for ii in results_actfull[str(int(i))].keys():
#             temp_data2.append([int(i), int(ii), float(results_actfull[str(int(i))][ii]['indv_profit']), float(results_actfull[str(int(i))][ii]['indv_envir'])])

# temp_data2 = np.asarray(temp_data2)


# # # ss = eps_sort(temp_data2,[2,3])
# # # ss = np.asarray(ss)
# # # ss = ss[ss[:,2].argsort()]
# # # ss_data = np.vstack((ss_data,ss))

# # # ss_data = ss_data[1:,:]  

# # plt.plot(temp_data[:,1]*-1, temp_data[:,2],'oc')
# # plt.plot(temp_data2[:,2]*-1, temp_data2[:,3],'.k')
# # # plt.plot(ss_data[:,2]*-1, ss_data[:,3],'-o')


# # for ii in results_actfull['19'].keys():
# #     plt.plot(results_actfull['19'][ii]['indv_profit']*-1,results_actfull['19'][ii]['indv_envir'],'o')

# #%%

# temp_data2 = []
# for i in results.keys():
#     for ii in results[i].keys():
#         temp_data2.append([int(i), int(ii), float(results_actfull[str(int(i))][ii]['indv_profit']), float(results_actfull[str(int(i))][ii]['indv_envir'])])

# temp_data2 = np.asarray(temp_data2)

# plt.plot(temp_data2[:,0], temp_data2[:,2]*-1,'or')
    
# cci = 0
# for act_id in actors_solutions.keys():
#     for wrid in actors_solutions[act_id].keys():
#         temp = actors_solutions[act_id][wrid]['profit']['Value']
#         plt.plot(float(wrid), float(temp)*-1,'.', c= colors[cci])
        
#         temp = actors_solutions[act_id][wrid]['envir']['Profit']
#         plt.plot(float(wrid), float(temp)*-1,'.', c= colors[cci])
    
#     cci = cci + 1

