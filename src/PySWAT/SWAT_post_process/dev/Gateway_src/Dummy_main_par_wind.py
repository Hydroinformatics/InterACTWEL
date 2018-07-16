import os, re, zipfile, argparse, subprocess, shutil
import numpy as np
import Formulation
import time
import datetime

start_time = time.time()
now = datetime.datetime.now()

#%% Unzip user SWAT model and run baseline scenario
def UnzipModel(path,pathuzip):
    folderpath = pathuzip+'/Default'
    if os.path.isdir(folderpath):
        shutil.rmtree(folderpath)
        
    with zipfile.ZipFile(path, "r") as z:
        z.extractall(pathuzip)
        os.chdir(pathuzip+'/Default/TxtInOut/')
    exitflag = subprocess.check_call(['swatmodel_64rel.exe'])
    print exitflag

#%%    
def GetSummary_Data(self,path):
    
    temp_basin_file_id = dict()
    text_files = [f for f in os.listdir(path + 'TxtInOut/') if f.endswith('.sub') and 'output' not in f]
    for tfile in text_files:
        with open(path + 'TxtInOut/' + tfile,'rb') as search:
            line = search.next()
            linesplit = re.split('\s',line)
            linesplit = [e for e in linesplit if e != '']
            temp_basin_file_id[linesplit[3]] = tfile[0:len(tfile)-4]
    search.close()
    
    hrus_file_id = dict()
    text_files = [f for f in os.listdir(path + 'TxtInOut/') if f.endswith('.hru') and 'output' not in f]
    for tfile in text_files:
        temp_dict = dict()
        with open(path + 'TxtInOut/' + tfile,'rb') as search:
            line = search.next()
            linesplit = re.split('\s',line)
            linesplit = [e for e in linesplit if e != '']
            temp_dict['SUB_HRU'] = (int(linesplit[4].strip('Subasin:' )),int(linesplit[5].strip('HRU: ')))
            temp_dict['HRU_FILE']= tfile[0:len(tfile)-4]
        hrus_file_id[linesplit[3].strip('HRU: ')] = temp_dict
    search.close()
    
    self.hrus_file_id = hrus_file_id
    
    temp_array = np.ones((len(hrus_file_id.keys()),3), dtype =int)*-999
    for sub_hru in hrus_file_id.keys():
        temp_array[int(sub_hru)-1, :] = [hrus_file_id[sub_hru]['SUB_HRU'][0],hrus_file_id[sub_hru]['SUB_HRU'][1],int(sub_hru)]
    
    sub_basins = dict()
    for subs in temp_basin_file_id.keys():
       temp_dict = dict()
       temp_dict['FILE'] = temp_basin_file_id[subs]
       temp_dict['HRU_ID'] = temp_array[temp_array[:,0]==int(subs),1]
       temp_dict['HRU'] = temp_array[temp_array[:,0]==int(subs),2]
       sub_basins[subs] = temp_dict

    self.sub_basins = sub_basins
    return


def Get_HRUs_ids(tfile,var):
    output_array = dict()
    templulc = []
    temphru = [] 
    tempsub = []
    tempmgt = []
    tempgis =[]
    varbool = 0

    with open(tfile) as search:
        for line in search:
            if var in line:
                if varbool == 0:
                    line = search.next()
                    varbool = 1
                    
            if varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                templulc.append(linesplit[0])        
                temphru.append(int(linesplit[1]))
                tempgis.append(linesplit[2])
                tempsub.append(int(linesplit[3]))
                tempmgt.append(linesplit[4])
                
    hruids = np.unique(temphru)
     
    for ui in hruids:
        data_array = dict()
        temp = [tempgis[i] for i in range(0,len(templulc)) if temphru[i] == ui]
        data_array['GIS'] = temp[0]
        temp = [tempsub[i] for i in range(0,len(templulc)) if temphru[i] == ui]
        data_array['SUB'] = temp[0]
        data_array['LULC'] = [templulc[i] for i in range(0,len(templulc)) if temphru[i] == ui]
        data_array['MGT'] = [tempmgt[i] for i in range(0,len(templulc)) if temphru[i] == ui]
        output_array[str(ui)] = data_array 
            
    return output_array

#%%
def Get_timeseries(tfile,var):
    time_data = dict()
    time_data['MONTH'] =[]
    time_data['YEAR'] = []
    varbool = 0
    cyear = 0
    with open(tfile) as search:
        for line in search:
            if var.lower() in line.lower():    
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                #varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var]
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']

                try:
                    if linesplit[1] is '1' and int(linesplit[3]) < 13:
                        time_data['MONTH'].append(float(linesplit[3]))
                        time_data['YEAR'].append(cyear)
                    elif linesplit[1] is '1' and int(linesplit[3]) > 13:
                        cyear = cyear + 1.0
                except:
                    pass;
    
    return time_data
      
#%%
def Get_output_rch(tfile,var):
    output_data = dict()
    data_array = dict()
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if var.lower() in line.lower():    
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var]
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                try:
                    if int(linesplit[3]) < 13:
                        data_array[linesplit[1]].append(float(linesplit[varcol[0]+1]))
                except:
                    pass;
    
    if varbool == 0:
        print('Error: variable ' + var + ' was found in File: ' + tfile)
    else:               
        output_data[var] = data_array
    
    return output_data


def Get_output_wtr(tfile,var):
    output_data = dict()
    data_array = dict()
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if var.lower() in line.lower():    
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var]
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                try:
                    if int(linesplit[5]) < 13:
                        data_array[linesplit[1]].append(float(linesplit[varcol[0]]))
                except:
                    pass;
    
    if varbool == 0:
        print('Error: variable ' + var + ' was NOT found in File: ' + tfile)
    else:               
        output_data[var] = data_array
    
    return output_data


def Get_output_hru(tfile,var):
    output_data = dict()
    data_array = dict()
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if var.lower() in line.lower():    
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var] #Another Error in SWATA DA_STmmSURQ_GENmmSURQ_CNTmm
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                try:
                    if int(linesplit[5].split('.')[0]) < 13: # NEEDS to be chceck the HRU file is not displaying a month. ERROR IN SWAT
                        data_array[linesplit[1]].append(float(linesplit[varcol[0]-1]))
                except:
                    pass;
    
    if varbool == 0:
        print('Error: variable ' + var + ' was NOT found in File: ' + tfile)
    else:               
        output_data[var] = data_array
    
    return output_data


#%%

def Get_output_data(tfile,var):
    output_data = dict()
    if tfile[len(tfile)-3:len(tfile)] == 'rch':
        output_data = Get_output_rch(tfile,var)
        
    elif tfile[len(tfile)-3:len(tfile)] == 'wtr':
        output_data = Get_output_wtr(tfile,var)
        
    elif tfile[len(tfile)-3:len(tfile)] == 'hru':
        output_data = Get_output_hru(tfile,var)

    return output_data


def Getbaseline(path,baseline_files):
    baseline_data = dict()
    for tfile in baseline_files.keys():
        for var in baseline_files[tfile]:
            data = Get_output_data(path + 'TxtInOut/' + tfile, var)
            baseline_data.update(data)
            
    return baseline_data

#%%
def Get_DecisionVars_baseline(self,path,decision_vars,decision_subbasins):
    
    ftype = []
    varid = []
    for temp_vars in decision_vars.keys():
        ftype.append(decision_vars[temp_vars]['FILE'])
        varid.append(int(temp_vars))
    varid = np.array(varid)
    ftype = np.array(ftype)
    
#    var_file_dict = dict()
#    for u_ftype in np.unique(ftype):
#        var_file_index = [i for i in range(0,len(ftype)) if ftype[i] == u_ftype]
#        var_file_dict[u_ftype.__str__()] = list(varid[var_file_index])

# Need to add warning when variable is not found (e.g., misspelled words)

    for subs in decision_subbasins.keys():
        tempsub = decision_subbasins[subs]
        temp_list_files = []
        temp_list_files = [ftype[varid==temp_var] for temp_var in tempsub['VAR_IDS']]
        baseline_inputs_sub = dict()
        baseline_inputs_hru = dict()
        
        for uftype in np.unique(temp_list_files):
            if uftype not in ['pnd','rte','sub','swq','wgn','wus']:
                temp_list_varnames = [decision_vars[str(tempsub['VAR_IDS'][temp_var])]['VAR'] 
                        for temp_var in range(0,len(tempsub['VAR_IDS'])) if temp_list_files[temp_var] == uftype]
                temp_list_varnames = np.unique(temp_list_varnames)
                
                for hrus in tempsub['HRU']:
                    hru_index = self.sub_basins[subs]['HRU'][self.sub_basins[subs]['HRU_ID'] == hrus][0]
                    temp_dict = dict()
                    with open(path + 'TxtInOut/' + self.hrus_file_id[str(hru_index)]['HRU_FILE'] + '.' + uftype) as search:
                        for line in search:
                            findvar = [varname_id for varname_id in range(0,len(temp_list_varnames)) if temp_list_varnames[varname_id] in line]
                            if findvar:
                                linesplit = re.split('\s',line)
                                linesplit = [e for e in linesplit if e != '']
                                temp_dict[temp_list_varnames[findvar][0]] = float(linesplit[0])
                            
                    search.close()
                    baseline_inputs_hru[hru_index] = temp_dict
            else:
                temp_list_varnames = [decision_vars[str(tempsub['VAR_IDS'][temp_var])]['VAR'] 
                        for temp_var in range(0,len(tempsub['VAR_IDS'])) if temp_list_files[temp_var] == uftype]
                temp_list_varnames = np.unique(temp_list_varnames)
                temp_dict = dict()
                with open(path + 'TxtInOut/' + self.sub_basins[str(subs)]['FILE'] + '.' + uftype) as search:
                    for line in search:
                        findvar = [varname_id for varname_id in range(0,len(temp_list_varnames)) if temp_list_varnames[varname_id] in line]
                        if findvar:
                            linesplit = re.split('\s',line)
                            linesplit = [e for e in linesplit if e != '']
                            temp_dict[temp_list_varnames[findvar][0]] = float(linesplit[0])
                            
                search.close()
                baseline_inputs_sub[str(subs)] = temp_dict


    self.baseline_inputs_sub = baseline_inputs_sub
    self.baseline_inputs_hru = baseline_inputs_hru
    
    return

#%%
class SWATmodel():
    def __init__(self,path,Problem):
        
        self.path = path
        self.sub_basins =[]
        self.hrus_file_id = []
        GetSummary_Data(self,self.path['SWAT'])
        self.timeseries = []
        self.timeseries = Get_timeseries(self.path['SWAT'] + 'TxtInOut/output.rch','MON')
        self.baseline_output = Getbaseline(self.path['SWAT'],Problem.baseline_vars)
        self.baseline_keys = self.baseline_output.keys()
        self.HRUs = Get_HRUs_ids(self.path['SWAT'] + 'TxtInOut/output.hru','HRU')
        self.baseline_inputs_sub = []
        self.baseline_inputs_hru = []
        Get_DecisionVars_baseline(self,self.path['SWAT'],Problem.decisions_vars,Problem.decisions_subbasin)
        
if __name__ == '__main__':
    
##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
#    parser = argparse.ArgumentParser(description='Optimization File')
#    parser.add_argument('path', metavar='-p', type=str, nargs='+',
#                    help='Path to zip file of SWAT baseline model')
#    args = parser.parse_args()
#
#    print args.path[0]
#    print args.path[1]
#     
##    path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/flow8gw/TxtInOut/'
##    path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/Default.zip'
##    pathuzip = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model'
##    UnzipModel(path,pathuzip)

##%% Setup problem and prase SWAT baseline data
    path = dict()
    path['SWAT'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default/'
    path['PROB'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/SWAT_DevProb/Formulation3.txt'
    path['ZIP'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default.zip'
    path['UNZIP'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/GA'
    
#    path['SWAT'] = '/mnt/c/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default/'
#    path['PROB'] = '/mnt/c/Users/sammy/Documents/GitHub/InterACTWEL/src/SWAT_DevProb/Formulation3.txt'
#    path['ZIP'] = '/mnt/c/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default.zip'
#    path['UNZIP'] = '/mnt/c/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/GA'
    
    OptProblem = Formulation.OptFormulation(path)
    SWATmodel = SWATmodel(path,OptProblem)

#%% Setup optimization problem using OpenMDAO
#    
##from Objetive_Functions import Get_fitness_region, Get_fitness_sub, Get_fitness_hru
##fitness = Get_fitness_region(OptProblem,SWATmodel,OptProblem.objectives_data)
##fitness_sub = Get_fitness_sub(OptProblem,SWATmodel,OptProblem.objectives_data,6)
##fitness_hru = Get_fitness_hru(OptProblem,SWATmodel,OptProblem.objectives_data,6)
#
###%%
##from openmdao.api import Problem, Group, IndepVarComp, DeapGADriver, ParallelGroup
##from Objective_Functions import Fitness_Function
##from test_disciplines import HRU77, HRU76
##
##
#chrom = dict()
##for var in OptProblem.decisions_vars:
##    for sub_id in OptProblem.decisions_subbasin:
#for sub_id in OptProblem.decisions_subbasin:
#    for var in OptProblem.decisions_vars:      
#        if OptProblem.decisions_vars[var]['FILE'] not in ['pnd','rte','sub','swq','wgn','wus']:
#            for hru_id in OptProblem.decisions_subbasin[sub_id]['HRU']:
#                hrukey = [i for i in SWATmodel.hrus_file_id if SWATmodel.hrus_file_id[i]['SUB_HRU'][0] == int(sub_id) and 
#                          SWATmodel.hrus_file_id[i]['SUB_HRU'][1] == int(hru_id)]
#                print OptProblem.decisions_vars[var]['VAR'] + hrukey[0]
#                chrom[OptProblem.decisions_vars[var]['VAR'] + hrukey[0]] = OptProblem.decisions_vars[var]['VALUES']
#        else:
#                print OptProblem.decisions_vars[var]['VAR'] + str(sub_id)
#                chrom[OptProblem.decisions_vars[var]['VAR'] + str(sub_id)] = OptProblem.decisions_vars[var]['VALUES']
#                
#%%
chrom = dict()
for sub_id in OptProblem.decisions_subbasin:
    temp_sub = dict()
    temp_vars = OptProblem.decisions_subbasin[sub_id]
    for hru_id in OptProblem.decisions_subbasin[sub_id]['HRU']:
        temp_hru = dict()
        #for var in OptProblem.decisions_vars:
        for var in temp_vars['VAR_IDS']:
            var = str(var)
            #var = OptProblem.decisions_vars[str(varkey)]['VAR']
            if OptProblem.decisions_vars[var]['FILE'] not in ['pnd','rte','sub','swq','wgn','wus']:
                hrukey = [i for i in SWATmodel.hrus_file_id if SWATmodel.hrus_file_id[i]['SUB_HRU'][0] == int(sub_id) and 
                          SWATmodel.hrus_file_id[i]['SUB_HRU'][1] == int(hru_id)]
                #print OptProblem.decisions_vars[var]['VAR'] + hrukey[0]
                temp_vars_name = OptProblem.decisions_vars[var]['VAR']
                temp_vars_value = OptProblem.decisions_vars[var]['VALUES']
                if SWATmodel.baseline_inputs_hru[int(hrukey[0])][temp_vars_name] not in temp_vars_value:
                    temp_vars_value.insert(0,SWATmodel.baseline_inputs_hru[int(hrukey[0])][temp_vars_name])
                
                #temp_hru[OptProblem.decisions_vars[var]['VAR'] + hrukey[0]] = temp_vars_value
                temp_hru[OptProblem.decisions_vars[var]['VAR']] = temp_vars_value
                
            else:
#                print OptProblem.decisions_vars[var]['VAR'] + str(sub_id)
                temp_vars_name = OptProblem.decisions_vars[var]['VAR']
                temp_vars_value = OptProblem.decisions_vars[var]['VALUES']
                if SWATmodel.baseline_inputs_sub[sub_id][temp_vars_name] not in temp_vars_value:
                    temp_vars_value.insert(0,SWATmodel.baseline_inputs_sub[sub_id][temp_vars_name])
                    
                #temp_sub[OptProblem.decisions_vars[var]['VAR'] + str(sub_id)] = temp_vars_value
                temp_sub[OptProblem.decisions_vars[var]['VAR']] = temp_vars_value
        
        chrom['HRU'+ str(hrukey[0])] = temp_hru
    chrom['SUB' + str(sub_id)] = temp_sub

OptProblem.chrom = chrom

#%%
import itertools

total_plans = dict()
action_plans = dict()
for varkeys in chrom.keys():
    #allNames = sorted(chrom[varkeys])
    allNames = chrom[varkeys]
    bb = list(itertools.product(*(chrom[varkeys][Name] for Name in allNames)))
    action_plans[varkeys] = bb
    total_plans[varkeys] = len(bb)
    
#%%
# Eliminate invalid plans
for condkey in OptProblem.decisions_conditions:
    for plankey in chrom.keys():
        cond_bool = 0
        varnames = [OptProblem.decisions_vars[str(i)]['VAR'] for i in OptProblem.decisions_conditions[condkey]['VAR_IDS']]
        dvars_dict = dict()
        var_counter = 0
        temp_varids = []
        temp_varval = []
        #for dvars in sorted(chrom[plankey]):
        for dvars in chrom[plankey]:
            if dvars in OptProblem.decisions_conditions[condkey]['CON_VAR']:
                cond_bool = 1
                dvars_dict['CON_VAR'] = var_counter
                
            elif dvars in varnames:
                cond_bool = 1
                temp_varids.append(var_counter)
                temp_varval.append(OptProblem.decisions_conditions[condkey]['VAR_VALUES'][varnames.index(dvars)])
            var_counter += 1
        
        dvars_dict['VAR_IDS'] = temp_varids
        dvars_dict['VAR_VAL'] = temp_varval
        
        if cond_bool == 1:
            del_plans = []
            for plan in range(0,len(action_plans[plankey])):
                plan_values = action_plans[plankey][plan]
                valid_bool = 0
                if eval(str(plan_values[dvars_dict['CON_VAR']]) + OptProblem.decisions_conditions[condkey]['CON_LOGIC'] + 
                            OptProblem.decisions_conditions[condkey]['CON_VALUE']):
                    valid_bools = 0
                    for i in range(0,len(dvars_dict['VAR_IDS'])):
                        if plan_values[dvars_dict['VAR_IDS'][i]] != dvars_dict['VAR_VAL'][i]:
                            valid_bools = 1
                            
                    if valid_bools == 1:
                        del_plans.append(plan)
            non_del_plans = set(range(0,len(action_plans[plankey]))) - set(del_plans)
            temp_plans = []
            for plan_ids in non_del_plans:
#                del action_plans[plankey][plan_ids]
                temp_plans.append(action_plans[plankey][plan_ids])
            
            action_plans[plankey] = temp_plans

OptProblem.action_plans = action_plans

#%%
#
#temp_plan = [0,1,2,3,0,1,2,3,0,1,2,3,4,4,4,2,1]
#action_plan_keys = OptProblem.action_plans.keys()
#
#for i in range(0,len(temp_plan)):
#    tempvalues = OptProblem.action_plans[action_plan_keys[i]][temp_plan[i]]
#    tempvars = OptProblem.chrom[action_plan_keys[i]].keys()
#    
#    if 'SUB' in action_plan_keys[i][0:3]:
#        filename = SWATmodel.sub_basins[action_plan_keys[i][3:]]['FILE']
#        
#    elif 'HRU' in action_plan_keys[i][0:3]:
#        filename = SWATmodel.hrus_file_id[action_plan_keys[i][3:]]['HRU_FILE']
#    
#    file_ext = []
#    for t in range(0,len(tempvars)):
##        tvars = tempvars[t]
##        tval = tempvalues[t]
#        varid = [i for i in OptProblem.decisions_vars if tempvars[t] == OptProblem.decisions_vars[i]['VAR']][0]
#        file_ext.append(OptProblem.decisions_vars[varid]['FILE'])
#    
#    for f in np.unique(file_ext):
#        tvars = [tempvars[i]for i in range(0,len(file_ext)) if file_ext[i] == f[0]]
#        tval = [tempvalues[i]for i in range(0,len(file_ext)) if file_ext[i] == f[0]]

#%%

from Objective_Functions import Fitness_Function    
from deap_driver_swat_par import DeapGADriver
#import matplotlib.pyplot as plt
from openmdao.api import Problem, Group, IndepVarComp, pyOptSparseDriver

#from test_disciplines import HRU77, HRU76

prob = Problem()
model = prob.model = Group()

tempvars = IndepVarComp()
for act_plans in action_plans.keys():
    tempvars.add_output(act_plans, val=0)
    
model.add_subsystem('act_plans',tempvars)

#model.add_subsystem('subs', Fitness_Function_Sub())
#model.add_subsystem('hrus', Fitness_Function_HRU())

#model.connect('p2.xI', 'comp.x0')
#model.connect('p1.xC', 'comp.x1')
#model.connect('p2.xI', 'comp2.x0')
#model.connect('p1.xC', 'comp2.x1')

#model.add_subsystem('SWAT', Fitness_Function_Sub(SWAT=SWATmodel,Problem=OptProblem))

#plan_keys = action_plans.keys()
#subids = [i for i in range(0,len(plan_keys)) if plan_keys[i][0:3] == 'SUB']
#for sub_plan in subids:
    
model.add_subsystem('SWAT', Fitness_Function(SWAT=SWATmodel,Problem=OptProblem))

for act_plans in action_plans.keys():
    des_vars = 'act_plans.' + act_plans
    model.SWAT.add_input(act_plans, val=0.0)  
    model.connect(des_vars, 'SWAT.' + act_plans)
    #model.add_design_var(des_vars, lower= 0.0, upper = len(action_plans[act_plans])-1)
    if 'SUB' not in act_plans:
        model.add_design_var(des_vars, lower= 0.0, upper = 0.0)
    else:
        model.add_design_var(des_vars, lower= 0.0, upper = len(action_plans[act_plans])-1)
    
for obje in OptProblem.objectives: 
    for sl in OptProblem.objectives[obje]['LEVEL']:
        if OptProblem.objectives[obje]['LEVEL'][sl].lower() == 'region':
            for bvar in OptProblem.objectives[obje]['BVAR']:
                if OptProblem.objectives[obje]['BVAR'][bvar] == 'SA_STmm':
                    output_name = OptProblem.objectives[obje]['BVAR'][bvar] + '_REGION'
                    model.SWAT.add_output(output_name, val=0.0)
                    model.add_objective('SWAT.'+ output_name)
                
                #print 'model.SWAT.add_output(' + "'" + output_name + "'" + ', val=0.0)'
                #print "model.add_objective('SWAT." + output_name + "'" + ')'
            
#        elif OptProblem.objectives[obje]['LEVEL'][sl].lower() == 'sub':
#            for act_plans in action_plans.keys():
#                if act_plans[0:3] == 'SUB':
#                    for bvar in OptProblem.objectives[obje]['BVAR']:
#                        output_name = OptProblem.objectives[obje]['BVAR'][bvar] + '_' + act_plans
#                        model.SWAT.add_output(output_name, val=0.0)
#                        model.add_objective('SWAT.'+ output_name)
#                        print 'model.SWAT.add_output(' + "'" + output_name + "'" + ', val=0.0)'
#                        print "model.add_objective('SWAT." + output_name + "'" + ')'
#                    
#        elif OptProblem.objectives[obje]['LEVEL'][sl].lower() == 'hru':
#            for act_plans in action_plans.keys():
#                if act_plans[0:3] == 'HRU':
#                    for bvar in OptProblem.objectives[obje]['BVAR']:
#                        output_name = OptProblem.objectives[obje]['BVAR'][bvar] + '_' + act_plans
#                        model.SWAT.add_output(output_name, val=0.0)
#                        model.add_objective('SWAT.'+ output_name)
#                        print 'model.SWAT.add_output(' + "'" + output_name + "'" + ', val=0.0)'
#                        print "model.add_objective('SWAT." + output_name + "'" + ')'


#for act_plans in action_plans.keys():
#    des_vars = 'act_plans.' + act_plans
#    if act_plans[0:3] == 'HRU':
#        hrusub = SWATmodel.hrus_file_id[act_plans[3:]]['SUB_HRU'][0]
#        #addhrus = 'model.SUB' + str(hrusub) + '.add_subsystem(' + "'" + act_plans + "'"+', Fitness_Function_HRU(SWAT=SWATmodel,Problem=OptProblem))'
#        #model.add_subsystem(act_plans, Fitness_Function_HRU(SWAT=SWATmodel,Problem=OptProblem))
#        #exec(addhrus)
#        #model.connect(des_vars, 'model.SUB' + str(hrusub) + '.' + act_plans + '.plan')
#        model.SWAT.add_input(act_plans, val=0.0)
#        
#        model.SWAT.add_output(act_plans, val=0.0)
#        
#        model.connect(des_vars, 'SWAT.' + act_plans)
#        
#    elif act_plans[0:3] == 'SUB':
#        #model.add_subsystem(act_plans, Fitness_Function_Sub(SWAT=SWATmodel,Problem=OptProblem))
#        #model.add_subsystem(act_plans, Group())
#        #model.connect(des_vars, act_plans + '.plan')
#        
#        model.SWAT.add_input(act_plans, val=0.0)
#        model.SWAT.add_output(act_plans, val=0.0)
#        model.connect(des_vars, 'SWAT.' + act_plans)
#    
#    model.add_design_var(des_vars, lower= 0.0, upper = len(action_plans[act_plans]))
#    for act_plansb in action_plans.keys():
#        if act_plansb != act_plans:
#            addinputs = 'model.' + act_plans + '.add_input(' + "'" + act_plansb + "'"+', val=0.0)'
#            exec(addinputs)
#            conn_vars = 'act_plans.' + act_plansb
#            model.connect(conn_vars, act_plans + '.' + act_plansb)
#            #print 'model.connect(' + "'" + conn_vars + "'" + ',' + "'" + act_plans + '.' + act_plansb + "'" + ')'
#


#model.connect('p1.xC', 'comp2.x1')
    
#model.add_design_var('p2.xI', lower= -5.0, upper= 10.0)
#model.add_design_var('p1.xC', lower= 0.0, upper= 15.0)

#model.add_objective('comp.f3')
##model.add_objective('comp.f2')
#model.add_objective('SUB6.f')



prob.driver = DeapGADriver()
#prob.driver.options['bits'] = {'p1.xC' : 8}
prob.driver.options['pop_size'] = 10
prob.driver.options['max_gen'] = 5
prob.driver.options['weights'] = (1.0,)
prob.driver.options['print_results']= True
prob.driver.options['run_parallel'] = False

prob.driver.options['Problem'] = OptProblem
prob.driver.options['SWAT'] = SWATmodel

prob.setup()
prob.run_driver()



## driver file to perform the optimization on the above problem and model system
#prob.driver = pyOptSparseDriver()
#prob.driver.options['optimizer'] = 'NSGA2'
##p.driver.opt_settings['PopSize'] = 150
## this setups all the subsystems and model for the driver optimization
#prob.setup(mode='fwd')

# this runs the driver in the OpenMDAO framework and then driver from pyOPT framwework as specified as the file.
#prob.run_driver()


#prob = Problem()
#model = Group()
#
#
#comp = IndepVarComp()
#comp.add_output('IRRSC77', val = SWATmodel.baseline_inputs_hru[77]['IRRSC'])
#comp.add_output('DIVMAX77', val = SWATmodel.baseline_inputs_hru[77]['DIVMAX'])
##model.add_subsystem('HRU77', comp)
##comp = IndepVarComp()
#comp.add_output('IRRSC76', val = SWATmodel.baseline_inputs_hru[76]['IRRSC'])
#comp.add_output('DIVMAX76', val = SWATmodel.baseline_inputs_hru[76]['DIVMAX'])
##model.add_subsystem('HRU76', comp)
#
#model.add_subsystem('des_vars', comp)
#model.add_subsystem('Comp',Fitness_Function(SWAT= SWATmodel, Problem = OptProblem))
#model.add_objective('Comp.f')
#
#model.Comp.add_subsystem('HRU77',HRU77(SWAT= SWATmodel, Problem = OptProblem))
#model.Comp.add_objective('HRU77.y1')
#model.Comp.add_subsystem('HRU76',HRU76(SWAT= SWATmodel, Problem = OptProblem))
#model.Comp.add_objective('HRU76.y2')
#
##model.add_subsystem('comp77',Fitness_Function(SWAT= SWATmodel, Problem = OptProblem))
##model.add_subsystem('comp76',Fitness_Function(SWAT= SWATmodel, Problem = OptProblem))
#
#model.connect('HRU77.y1', 'Comp.x0')
#varname = 'HRU76.y2'
#compname = 'Comp.x1'
#model.connect(varname, compname)
#
##model.add_design_var('HRU77.IRRSC', lower = 0.0, upper = 3)
##model.add_design_var('HRU77.DIVMAX', lower = 0.0, upper = 3)
##model.add_design_var('HRU76.IRRSC', lower = 0.0, upper = 3)
##model.add_design_var('HRU76.DIVMAX', lower = 0.0, upper = 3)
#
#prob = Problem(model)
#prob.driver = DeapGADriver()
#
#prob.setup()
#prob.run_driver()

final_time = time.time() - start_time

#%%
    
hoff = prob.driver._hof
with open('TempResfile.txt','w') as wrt:
    for hof_temp in prob.driver._hof:
         wrt.write(str(hof_temp)+"\n")

wrt.close()

#%%

with open('TempPopfile.txt','w') as wrt:
    for pop_temp in prob.driver._pop:
         wrt.write(str(pop_temp)+"\n")

wrt.close()

#%%
fname = now.isoformat() + '.txt'
with open(fname,'w') as wrt:
    wrt.write('POP_SIZE: '+ str(prob.driver.options['pop_size'])+"\n")
    wrt.write('MAX_GEN: '+ str(prob.driver.options['max_gen'])+"\n")
    wrt.write('TIME(SEC): '+ str(final_time)+"\n")
    
wrt.close()   

#%%
#
#from Objective_Functions import Get_Objectives_Data, Get_output_std
#
#pathd = 'C:\Users\sammy\Documents\GitHub\InterACTWEL\src\PySWAT\SWAT_Model\GA'
#temp_data = dict()
#data_diff = dict()   
#
#for op in os.listdir(pathd):
#    temp_pathd = pathd + '\\' + op + '\\'
#    print temp_pathd
#    temp_data = Get_Objectives_Data(OptProblem,temp_pathd)
#    
##for okey in temp_data.keys():
#    for var_key in temp_data:
#        for hru_key in temp_data[var_key]:
#            temp_data_base = np.asarray(OptProblem.objectives_data[var_key][hru_key])
#            temp_data_out = np.asarray(temp_data[var_key][hru_key])
#            tempdiff = np.sum(np.subtract(temp_data_out,temp_data_out))
#            if tempdiff > 0.0:
#                data_diff[op][var_key][hru_key] = tempdiff
#            
    
#%%
#import matplotlib.pyplot as plt
#import numpy as np
#from mpl_toolkits.mplot3d import axes3d, Axes3D 
#
#ax = fig.add_subplot(122, projection='3d')
#ax.scatter(X0, X1, f3)
#ax.scatter(X0, X1, f2,c='r')
#ax.set_xlabel('X0')
#ax.set_ylabel('X1')
#ax.set_zlabel('Fitness')    