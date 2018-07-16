import numpy as np
from openmdao.api import ExplicitComponent
#import os, zipfile, subprocess, shutil
import os, re, zipfile, subprocess, shutil, random

#def UnzipModel(path,pathuzip,tempname):
#    folderpath = pathuzip+'/Default'
#    if os.path.isdir(folderpath):
#        shutil.rmtree(folderpath)
#    
#    path = path + '/' + tempname + '/'
#    with zipfile.ZipFile(path, "r") as z:
#        z.extractall(pathuzip)
#        os.chdir(pathuzip+'/Default/TxtInOut/')
#    exitflag = subprocess.check_call(['swatmodel_64rel.exe'])
#    print exitflag

def UnzipModel(path,pathuzip,iterc):
#    fbool = 0
#    while(fbol == 0):
    #tempname = random.sample(range(0,50),1)
    
    folderpath = pathuzip + '/POPSWAT_' + str(iterc) + '/'
    if os.path.isdir(folderpath):
        shutil.rmtree(folderpath)
    
    with zipfile.ZipFile(path, "r") as z:
        z.extractall(folderpath)

#    os.chdir(pathuzip + '/Default/TxtInOut/')    
#    exitflag = subprocess.check_call(['swatmodel_64rel.exe'])
#    print exitflag    
    return folderpath

def Write_DecisionVars(path,filename,file_ext,decision_vars,decision_vals):
    
    #if file_ext in ['pnd','rte','sub','swq','wgn','wus']:
    with open(path + 'TxtInOut/' + filename + '.' + file_ext) as search, open(path + 'TxtInOut/Tempfile.txt','w') as wrt:
        for line in search:
            findvar = None
            findvar = [v for v in range(0,len(decision_vars)) if decision_vars[v] in line]
            #if decision_vars in line:
            if findvar:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                newline = line.replace(linesplit[0],str(decision_vals[findvar[0]]))
                wrt.write(newline)
            else:
                wrt.write(line)
                
    search.close()
    wrt.close()
    shutil.copyfile(path + 'TxtInOut/Tempfile.txt', path + 'TxtInOut/' + filename + '.' + file_ext)
    os.remove(path + 'TxtInOut/Tempfile.txt')
    
#        else:
#            
##            temp_list_varnames = [decision_vars[str(tempsub['VAR_IDS'][temp_var])]['VAR'] 
##                    for temp_var in range(0,len(tempsub['VAR_IDS'])) if temp_list_files[temp_var] == uftype]
##            temp_list_varnames = np.unique(temp_list_varnames)
##            temp_dict = dict()
##            with open(path + 'TxtInOut/' + self.sub_basins[str(subs)]['FILE'] + '.' + uftype) as search:
##                for line in search:
##                    findvar = [varname_id for varname_id in range(0,len(temp_list_varnames)) if temp_list_varnames[varname_id] in line]
##                    if findvar:
##                        linesplit = re.split('\s',line)
##                        linesplit = [e for e in linesplit if e != '']
##                        temp_dict[temp_list_varnames[findvar][0]] = float(linesplit[0])
#                        
#        search.close()
#        wrt.close()
         
    return
#%%

def Get_output_std(tfile,var):
    
    output_data = dict()
    data_array = dict()
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if var in line:    
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var] #Another Error in SWATA DA_STmmSURQ_GENmmSURQ_CNTmm
                
                if var == 'YLDt/ha':
                    varcol = [71]
                elif var == 'SA_STmm':
                    varcol = [21]
                elif var == 'DA_STmm':
                    varcol = [22]
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                #print linesplit
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                try:
                    if int(linesplit[5].split('.')[0]) < 13: # NEEDS to be chceck the HRU file is not displaying a month. ERROR IN SWAT
                        data_array[linesplit[1]].append(float(linesplit[varcol[0]]))
                except:
                    pass;
    
    if varbool == 0:
        print('Error: variable ' + var + ' was NOT found in File: ' + tfile)
    else:               
        output_data[var] = data_array
    
    return output_data

#%%
def Get_Objectives_Data(problem,path):
#    available_obj = Available_Objectives()
    unique_pars = []
    unique_keys = []
    objectives_data = dict()
    
    for obj_id in problem.objectives.keys():
        if problem.objectives[obj_id]['PAR'] not in unique_pars:
            unique_pars.append(problem.objectives[obj_id]['PAR'])
            unique_keys.append(obj_id)
    
#    temp_dict= dict()
    for obj_id in unique_keys:
#        if self.objectives[obj_id]['PAR'].lower() == 'yield':
#            temp_dict['DATA'] = available_obj['yield']
#            
#        elif self.objectives[obj_id]['PAR'].lower() == 'gw_rch':
#            temp_dict['DATA'] = available_obj['gw_rch']
#            
#        var_lower = self.objectives[obj_id]['PAR'].lower()
        for ci in range(0,len(problem.objectives[obj_id]['BVAR'])):
            temp_data = Get_output_std(path + 'TxtInOut/' + problem.objectives[obj_id]['FILE'], problem.objectives[obj_id]['BVAR'][ci])
            objectives_data[temp_data.keys()[0]] = temp_data[temp_data.keys()[0]]
            
    return objectives_data

#%%
def Get_fitness_region(obj_id,var_key,problem,SWAT,output_data):
    
    fitness = 0.0
    temp_years = np.asarray(SWAT.timeseries['YEAR'])
    temp_mon = np.asarray(SWAT.timeseries['MONTH'])
    
#    for obj_id in problem.objectives.keys():
#        for var_key in problem.objectives[obj_id]['BVAR']:
    temp = []
    var = problem.objectives[obj_id]['BVAR'][var_key]
    
    for levels in problem.objectives[obj_id]['LEVEL']:

        if problem.objectives[obj_id]['LEVEL'][levels].lower() == 'region':
            
#            for years in np.unique(temp_years):
            temp_fitness = []
            temp_base = 0.0
            for hru_key in problem.objectives_data[var].keys():
                temp_data_base = np.asarray(problem.objectives_data[var][hru_key])
                temp_data_out = np.asarray(output_data[var][hru_key])
#                    id_year = np.where(temp_years == years)
#                    if 'yld' in var.lower():
#                        temp_fitness = temp_fitness + np.sum(temp_data_out[id_year])
#                        temp_base = temp_base + np.sum(temp_data_base[id_year])
#                            
#                    elif 'st' in var.lower():
#                         temp_fitness = temp_fitness + temp_data_out[id_year[0][-1]]
#                         temp_base = temp_base + temp_data_base[id_year[0][-1]]
                    
#                temp.append(temp_fitness - temp_base)
                temp_fitness.append(np.sum(np.subtract(temp_data_out,temp_data_base)))
#        fitness = np.dot(temp,(max(np.unique(temp_years))+1)/np.arange(max(np.unique(temp_years))+1,0,-1))
    #print temp_fitness            
    fitness = np.sum(temp_fitness)
    return fitness

#%%

def Get_fitness_sub(obj_id,var_key,problem,SWAT,output_data,input_sub):
    fitness = 0.0
    temp_years = np.asarray(SWAT.timeseries['YEAR'])
    temp_mon = np.asarray(SWAT.timeseries['MONTH'])
    
#    for obj_id in problem.objectives.keys():
#        for var_key in problem.objectives[obj_id]['BVAR']:
    temp = []
    var = problem.objectives[obj_id]['BVAR'][var_key]
    
    for levels in problem.objectives[obj_id]['LEVEL']:

        if problem.objectives[obj_id]['LEVEL'][levels].lower() == 'sub':
            
            hru_keys = [sub_hru for sub_hru in SWAT.HRUs if SWAT.HRUs[sub_hru]['SUB'] == input_sub and sub_hru in problem.objectives_data[var].keys()]
            
            for years in np.unique(temp_years):
                temp_fitness = 0.0
                temp_base = 0.0
                
                for hru_key in hru_keys:
                    temp_data_base = np.asarray(problem.objectives_data[var][hru_key])
                    temp_data_out = np.asarray(output_data[var][hru_key])
                    id_year = np.where(temp_years == years)
                    
                    if 'yld' in var.lower():
                        temp_fitness = temp_fitness + np.sum(temp_data_out[id_year])
                        temp_base = temp_base + np.sum(temp_data_base[id_year])
                            
                    elif 'st' in var.lower():
                         temp_fitness = temp_fitness + temp_data_out[id_year[0][-1]]
                         temp_base = temp_base + temp_data_base[id_year[0][-1]]
                        
                temp.append(temp_fitness - temp_base)
                
            fitness = np.dot(temp,(max(np.unique(temp_years))+1)/np.arange(max(np.unique(temp_years))+1,0,-1))
    
    return fitness

#%%

def Get_fitness_hru(obj_id,var_key,problem,SWAT,output_data,input_hru):
    fitness = 0.0
    temp_years = np.asarray(SWAT.timeseries['YEAR'])
    temp_mon = np.asarray(SWAT.timeseries['MONTH'])
    
#    for obj_id in problem.objectives.keys():
#        for var_key in problem.objectives[obj_id]['BVAR']:
    temp = []
    var = problem.objectives[obj_id]['BVAR'][var_key]
    
    for levels in problem.objectives[obj_id]['LEVEL']:

        if problem.objectives[obj_id]['LEVEL'][levels].lower() == 'hru':
            
            #hru_keys = [sub_hru for sub_hru in SWAT.HRUs if SWAT.HRUs[sub_hru]['SUB'] == input_sub and sub_hru in problem.objectives_data[var].keys()]
            
            for years in np.unique(temp_years):
                temp_fitness = 0.0
                temp_base = 0.0

                temp_data_base = np.asarray(problem.objectives_data[var][str(input_hru)])
                temp_data_out = np.asarray(output_data[var][str(input_hru)])
                id_year = np.where(temp_years == years)
                if 'yld' in var.lower():
                    temp_fitness = temp_fitness + np.sum(temp_data_out[id_year])
                    temp_base = temp_base + np.sum(temp_data_base[id_year])
                            
                elif 'st' in var.lower():
                    temp_fitness = temp_fitness + temp_data_out[id_year[0][-1]]
                    temp_base = temp_base + temp_data_base[id_year[0][-1]]
                        
                temp.append(temp_fitness - temp_base)
                
            fitness = np.dot(temp,(max(np.unique(temp_years))+1)/np.arange(max(np.unique(temp_years))+1,0,-1))
    
    return fitness

#%%

class Fitness_Function(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('SWAT')
        self.metadata.declare('Problem')
        
#    def setup(self):
#        # Inputs
#        #self.add_input('plan', 0.0)
#        
#        # Outputs
#        self.add_output('f', val=0.0)
        
    def compute(self, inputs, outputs):
        """
        Define the function f(xI, xC).

        When Branin is used in a mixed integer problem, x0 is integer and x1 is continuous.
        """
        
        temp_plan = [inputs[i][0] for i in inputs.keys()]
    
        optproblem = self.metadata['Problem']
        SWATmodel = self.metadata['SWAT']
        
        temp_path = UnzipModel(SWATmodel.path['ZIP'],SWATmodel.path['UNZIP'],self.iter_count)
        
        action_plan_keys = optproblem.action_plans.keys()
        filename = []
        for i in range(0,len(temp_plan)):
            tempvalues = optproblem.action_plans[action_plan_keys[i]][int(inputs[action_plan_keys[i]][0])]
            tempvars = optproblem.chrom[action_plan_keys[i]].keys()
            
            if 'SUB' in action_plan_keys[i][0:3]:
                filename = SWATmodel.sub_basins[action_plan_keys[i][3:]]['FILE']
                
            elif 'HRU' in action_plan_keys[i][0:3]:
                filename = SWATmodel.hrus_file_id[action_plan_keys[i][3:]]['HRU_FILE']
            
            file_ext = []
            for t in range(0,len(tempvars)):
        #        tvars = tempvars[t]
        #        tval = tempvalues[t]
                varid = [i for i in optproblem.decisions_vars if tempvars[t] == optproblem.decisions_vars[i]['VAR']][0]
                file_ext.append(optproblem.decisions_vars[varid]['FILE'])
            #if len(np.unique(file_ext)) > 1:
            
            for f in np.unique(file_ext):
                tvars = [tempvars[i]for i in range(0,len(file_ext)) if file_ext[i] == f]
                tval = [tempvalues[i]for i in range(0,len(file_ext)) if file_ext[i] == f]
                Write_DecisionVars(temp_path,filename,file_ext[i],tvars,tval)
        #os.chdir(temp_path +'/TxtInOut/')
        
        try:
            #exitflag = subprocess.check_call([temp_path +'/TxtInOut/swatmodel_64rel.exe'])
            tempcwd = os.getcwd()
            os.chdir(temp_path +'/TxtInOut/')
            #exitflag = subprocess.check_call(['swatmodel_64rel.exe'])
            exitflag = subprocess.check_call(['/export/swat-test/bin/swat2012Rev664Rel'])
            os.chdir(tempcwd)
        
            #output_data = optproblem.objectives_data
            output_data = Get_Objectives_Data(optproblem,temp_path)
            
            for obje in optproblem.objectives: 
                for sl in optproblem.objectives[obje]['LEVEL']:
                    if optproblem.objectives[obje]['LEVEL'][sl].lower() == 'region':
                        for bvar in optproblem.objectives[obje]['BVAR']:
                            if optproblem.objectives[obje]['BVAR'][bvar] == 'SA_STmm':
                                output_name = optproblem.objectives[obje]['BVAR'][bvar] + '_REGION'
                                outputs[output_name] = Get_fitness_region(obje,bvar,optproblem, SWATmodel, output_data)
                                print temp_plan, outputs[output_name]
#                    elif optproblem.objectives[obje]['LEVEL'][sl].lower() == 'sub':
#                        for act_plans in optproblem.action_plans.keys():
#                            if act_plans[0:3] == 'SUB':
#                                for bvar in optproblem.objectives[obje]['BVAR']:
#                                    output_name = optproblem.objectives[obje]['BVAR'][bvar] + '_' + act_plans
#                                    outputs[output_name] = Get_fitness_sub(obje,bvar,optproblem, SWATmodel, output_data)
#
#                    elif optproblem.objectives[obje]['LEVEL'][sl].lower() == 'hru':
#                        for act_plans in optproblem.action_plans.keys():
#                            if act_plans[0:3] == 'HRU':
#                                 for bvar in optproblem.objectives[obje]['BVAR']:
#                                     output_name = optproblem.objectives[obje]['BVAR'][bvar] + '_' + act_plans
#                                     outputs[output_name] = Get_fitness_hru(obje,bvar,optproblem, SWATmodel, output_data)
                                
                                    
        except:
            for outkeys in outputs.keys():
                outputs[outkeys] = -100000000
        
