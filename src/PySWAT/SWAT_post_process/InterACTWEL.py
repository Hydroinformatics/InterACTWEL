import os, re, zipfile, argparse, subprocess, shutil
import numpy as np
import Formulation

#%%
def UnzipModel(path,pathuzip):
    folderpath = pathuzip+'/Default'
    if os.path.isdir(folderpath):
        shutil.rmtree(folderpath)
        
    with zipfile.ZipFile(path, "r") as z:
        z.extractall(pathuzip)
        os.chdir(pathuzip+'/Default/TxtInOut/')
    exitflag = subprocess.check_call(['swatmodel_64rel.exe'])
    print exitflag
    
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
                    hru_index =self.sub_basins[subs]['HRU'][self.sub_basins[subs]['HRU_ID'] == hrus][0]
                    temp_dict = dict()
                    with open(path + 'TxtInOut/' + self.hrus_file_id[str(hru_index)]['HRU_FILE'] + '.' + uftype) as search:
                        for line in search:
                            findvar = [varname_id for varname_id in range(0,len(temp_list_varnames)) if temp_list_varnames[varname_id] in line]
                            if findvar:
                                linesplit = re.split('\s',line)
                                linesplit = [e for e in linesplit if e != '']
                                temp_dict[temp_list_varnames[findvar][0]] = float(linesplit[0])
                            
                    search.close()
                    baseline_inputs_hru[hrus] = temp_dict
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
        
        self.path = path['SWAT']
        self.sub_basins =[]
        self.hrus_file_id = []
        GetSummary_Data(self,path['SWAT'])
        self.baseline_output = Getbaseline(path['SWAT'],Problem.baseline_vars)
        self.baseline_keys = self.baseline_output.keys()
        self.HRUs = Get_HRUs_ids(path['SWAT'] + 'TxtInOut/output.hru','HRU')
        self.baseline_inputs_sub = []
        self.baseline_inputs_hru = []
        Get_DecisionVars_baseline(self,path['SWAT'],Problem.decisions_vars,Problem.decisions_subbasin)
        
if __name__ == '__main__':
    
#%% Parse Path to Zip file, Uzip and run SWAT Baseline model
    #parser = argparse.ArgumentParser(description='InterACTWEL Model')
    #parser.add_argument('path', metavar='-p', type=str, nargs='+',
    #                help='Path to zip file of SWAT baseline model')
    #args = parser.parse_args()

    #print args.path[0]
#    #path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/flow8gw/TxtInOut/'
#    path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/Default.zip'
#    pathuzip = 'C:/Users/babbarsm/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model'
#    UnzipModel(path,pathuzip)

#%% Setup problem and save baseline data
    path['SWAT'] = 'C:/Users/babbarsm/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default/'
    path['PROB'] = 'C:/Users/babbarsm/Documents/GitHub/InterACTWEL/src/SWAT_DevProb/Formulation2.txt'
    
#    baseline_files = dict()
#    baseline_files['output.rch'] = ['FLOW_OUTcms','EVAPcms']
#    baseline_files['output.wtr'] = ['PNDSEPmm','rose']
#    
#    decision_files = dict()
#    decision_files['mgt'] = ['IRRSC','IRRNO','DIVMAX']
#    decision_files['pnd'] = ['PND_FR','PND_PSA','PND_PVOL','PND_ESA','PND_EVOL','PND_VOL','PND_K']
#    
#    sub_basin_decisions = [6]
#    
    Problem = Formulation.OptFormulation(path)
    #Problem.Objfuction = 
    SWATmodel = SWATmodel(path,Problem)
    
    
    
    