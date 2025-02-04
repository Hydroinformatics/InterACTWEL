import numpy as np
import os
import openmdao.api as om
import matplotlib.pyplot as plt
import time
import json 
import pandas as pd

#os.chdir(r'M:\GitHub\InterACTWEL\OpenMDAO')
os.chdir(r"C:\Users\kimsiy\Box\MDO_Case Study\New Version_For2025EWRI\InterACTWEL-FEWMDAO_Siyeon\Code")


from FEW_SWAT_modelv8 import FEWNexus
import FEW_SWAT_utils as swat_utils


#%% Paths to the BASE folder with the original (unmodified) SWAT Model and the path
# to the folder that will be used to run the GA iterations (i.e., test_path).
# Additionally, you should add the name of the SWAT executable in case there are different versions of it
# within the SWAT TxtInOut folder.

swat_base_path = r"C:\Users\kimsiy\Box\MDO_Case Study\New Version_For2025EWRI\InterACTWEL-FEWMDAO_Siyeon\Base_backup\TxtInOut"
swat_test_path = r"C:\Users\kimsiy\Box\MDO_Case Study\New Version_For2025EWRI\InterACTWEL-FEWMDAO_Siyeon\Test_Folder\TxtInOut"
#swat_base_path = r'/Users/sammy/Documents/Research/SWAT/swat_model/BASE/Scenarios/Default/TxtInOut'
#swat_test_path = r'/Users/sammy/Documents/Research/SWAT/swat_model/TEST/Scenarios/Default/TxtInOut'
swat_exe_name = 'swat_ShallowAndDeepGWirrig.exe'

#%% Get WRS that are within NOWA limit and will be considered in the problem
# The txt, csv, or which ever format you decide for the input file should have the list of water rights
# to be considered as actors in the scenario.

#Make sure to change this path to you own directory where the file is located.
wrs_file_path = os.getcwd() + '/SWAT_WR_files/MDAO_WRS_NOWA.txt'

wr_mdao = []
wrs_hrus_dict = dict()
wrs_hrus_dict['hrus_map_key'] = dict()

cc = 1
with open(wrs_file_path, 'r') as search:
    for line in search:
        if len(line) > 0:
            wr_mdao.append(int(line))
            wrs_hrus_dict['hrus_map_key'][int(line)] = cc
            cc = cc + 1

search.close()    

#%%
# Read the original water right files (hruwr and wrdata) to get the list of HRUs associated with a given water right
# and get the total volume for each of the considered water rights.

#Make sure to change this path to you own directory where the file is located.
hruwr_file_path = swat_base_path + '/hruwr.dat'

hru_wrs = pd.read_csv(hruwr_file_path, delim_whitespace=True, header=None, index_col=None, na_values='(missing)').to_numpy()

wrs_hrus_dict['hrus'] = dict()
for row in hru_wrs:

    if row[1] in wrs_hrus_dict['hrus_map_key'].keys():
        if wrs_hrus_dict['hrus_map_key'][row[1]] not in wrs_hrus_dict['hrus'].keys():
            wrs_hrus_dict['hrus'][wrs_hrus_dict['hrus_map_key'][row[1]]] = []
    
    if row[1] in wrs_hrus_dict['hrus_map_key'].keys():
        wrs_hrus_dict['hrus'][wrs_hrus_dict['hrus_map_key'][row[1]]].append(row[0])
        
#Make sure to change this path to you own directory where the file is located.
wrdata_file_path = swat_base_path + '/wrdata.dat'

wrdata = pd.read_csv(wrdata_file_path, delim_whitespace=True, header=0, index_col=None, na_values='(missing)').to_numpy()

wrs_hrus_dict['org_vol'] = dict()
for row in wrdata:

    if row[1] in wrs_hrus_dict['hrus_map_key'].keys():
        wrs_hrus_dict['org_vol'][wrs_hrus_dict['hrus_map_key'][row[1]]] = row[3]


#%% Check if there are any water rights that share an HRU ID (i.e., HRU with access to two or more water rights)
# We should not have one as the code does not consider this case at the moment.
# It is possible to modify the code to account for this situation if needed.
wr_share_hru = []

for wr_id in wrs_hrus_dict['hrus'].keys():
    for wr_id2 in wrs_hrus_dict['hrus'].keys():
        if wr_id != wr_id2 and len(np.intersect1d(wrs_hrus_dict['hrus'][wr_id], wrs_hrus_dict['hrus'][wr_id2])) > 0:
            
            wr_share_hru.append([wr_id, wr_id2])
            
#%% Get the business as usal yield for the relevant HRUs.
# Make sure to change the path to the directory where you have the SWAT Model.
# At this point, this function is only reading the output.hru, but you could add more files
# to the Get_hru_output function.

hru_outputs = swat_utils.Get_hru_output(swat_base_path)

#crops_considered = ['AGRL', 'ALFA', 'CELR', 'CORN', 'HAY', 'MINT', 'ONIO', 'PAST', 'PEAS', 'POTA', 'RNGE', 'SWGR', 'SWHT', 'WWHT']
crops_considered = ['ALFA', 'CORN', 'ONIO','POTA','SWHT', 'WWHT']

# Should consider only crops that we are concerned with.
wrs_hrus_dict['org_yield'] = dict()
for wr_id in wrs_hrus_dict['hrus'].keys():
    temp_total_yield = 0
    for hruid in wrs_hrus_dict['hrus'][wr_id]:
        cc = 0
        for lulc in hru_outputs[hruid]['LULC']:
            if lulc in crops_considered:
                temp_total_yield = temp_total_yield  + np.sum(hru_outputs[hruid]['Total_Yield'][cc])
        cc += 1
    
    wrs_hrus_dict['org_yield'][wr_id] = temp_total_yield
    
#%% This section creates a mapping between the water right ids and a increasing sequencial numbering 
# (e.g., water right 1005 becomes #1 for the OpenMDAO, water right 1176 is #2, etc.).
# This modiication was made to simplify the tracking of variables along the OpenMDAO framework.

wrdata_df = pd.read_table(swat_base_path + '/wrdata.dat', sep='\s+', header=0)
max_wrid = np.unique(list(wrdata_df['WR_ID,']))[-2]

wrs_hrus_dict['org_wr_data'] = dict()
wrs_hrus_dict['wrs_map_key'] = dict()
for twrid in wrs_hrus_dict['hrus_map_key'].keys():
    wrs_hrus_dict['org_wr_data'][wrs_hrus_dict['hrus_map_key'][twrid]] = wrdata_df.loc[(wrdata_df['WR_ID,'] == twrid) & (wrdata_df['YEAR_ID,'] == 1)]
    wrs_hrus_dict['wrs_map_key'][wrs_hrus_dict['hrus_map_key'][twrid]] = twrid

#%% Removing files that might exist with the same name.
# These files are created to save the partial (each iteration) results for
# the region and each individual farmer.

json_actors = 'actors_solutions_farmer_V3_'
json_results = 'opt_resultswr_V3.json'

for wrids in wrs_hrus_dict['hrus'].keys():
    if os.path.exists(json_actors + str(wrids) + '_sharewr.json'):
        os.remove(json_actors + str(wrids) + '_sharewr.json')
        

#%% Setup the OpenMDAO Problem

prob = om.Problem()
prob.model = FEWNexus()
prob.model.nactors = len(wrs_hrus_dict['hrus'].keys())

prob.model.wrs_hrus = wrs_hrus_dict['hrus'] # List of HRUs for every water rigth.
prob.model.org_wr_vols = wrs_hrus_dict['org_vol'] # Orignal WR volumen.
prob.model.json_file = json_actors # Name of the files where intermidiate results will be saved.
prob.model.org_yield = wrs_hrus_dict['org_yield'] # Bussiness as usual yields for each Water Right (actor)
prob.model.wrs_map_key = wrs_hrus_dict['wrs_map_key'] # Mapping between the water right ids and a increasing sequencial numbering
prob.model.org_wr_data = wrs_hrus_dict['org_wr_data'] # Original WR data
prob.model.max_wrid = max_wrid # Largest Water Right ID
prob.model.swat_paths = [swat_base_path, swat_test_path] # Path of the BASE and TEST SWAT folders

prob.driver = om.SimpleGADriver()
prob.driver.options['max_gen'] = 50
prob.driver.options['Pm'] = 0.1
prob.driver.options['pop_size'] = 500
prob.driver.options['penalty_parameter'] = 20000.
prob.driver.options['penalty_exponent'] = 5.
prob.driver.options['compute_pareto'] = True

# Reformat the water right original vol to a list
wr_vols_max = []
for wrids in range(1,len(wrs_hrus_dict['org_vol'].keys())+1):
    wr_vols_max.append(wrs_hrus_dict['org_vol'][wrids])


prob.model.add_design_var('wr_vols', lower=np.zeros(prob.model.nactors,dtype=int), upper = np.ones(prob.model.nactors,dtype=int)*sum(wr_vols_max))
prob.model.add_objective('profit', scaler=1)
prob.model.add_constraint('total_wr', upper=sum(wr_vols_max))

prob.model.approx_totals()

prob.setup()
# om.n2(prob)
prob.run_driver()


#%%
print('################# RESULTS ##################')

desvar_nd = prob.driver.desvar_nd
nd_obj = prob.driver.obj_nd
sorted_obj = nd_obj[nd_obj[:, 0].argsort()]

print(sorted_obj)
print(desvar_nd[nd_obj[:, 0].argsort()])
print(np.sum(desvar_nd[nd_obj[:, 0].argsort()], axis=1))


#%%
opt_results = dict()
opt_results['desvar_nd'] = desvar_nd.tolist() 
opt_results['nd_obj'] = nd_obj.tolist()

with open(json_results, 'w') as fp:
    json.dump(opt_results, fp)
