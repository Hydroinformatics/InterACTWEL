import os, re, zipfile, argparse, subprocess, shutil, csv
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
            temp_basin_file_id[linesplit[3]] = tfile
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
            temp_dict['HRU_FILE']= tfile
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
            if var in line:    
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
            if var in line:    
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var]
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[2]] = []
                try:
                    if int(linesplit[5]) < 13:
                        data_array[linesplit[2]].append(float(linesplit[varcol[0]]))
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
    #elif tfile[len(tfile)-3:len(tfile)] == 'hru':
    #    output_data = Get_output_wtr(tfile,var)
        
    return output_data


def Getbaseline(path,baseline_files):
    baseline_data = dict()
    for tfile in baseline_files.keys():
        for var in baseline_files[tfile]:
            data = Get_output_data(path + 'TxtInOut/' + tfile, var)
            baseline_data.update(data)
            
    return baseline_data

#%%
def Get_DecisionVars_baseline(path,decision_vars,subbasins):
    for var_id in decision_vars.keys():
        var_data = decision_vars[var_id]
        text_files = []
        text_files = [f for f in os.listdir(path + 'TxtInOut/') if f.endswith('.'+ var_data['FILE'])]
        for subs in subbasins.keys():
            tempsub = subbasins[subs]
            if var_id in tempsub['VAR_IDS'] and var_data['FILE'] not in ['pnd','rte','sub','swq','wgn','wus']:
                for hrus in tempsub['HRU']:
                    print(hrus)
            else:
                print(path)
                #with open(path + 'TxtInOut/' + )
    return

#%%
class SWATmodel():
    def __init__(self,path,Problem):
        
        self.path = path
        self.sub_basins =[]
        self.hrus_file_id = []
        GetSummary_Data(self,path)
        self.baseline_output = Getbaseline(path,Problem.baseline_vars)
        self.baseline_keys = self.baseline_output.keys()
        self.HRUs = Get_HRUs_ids(path + 'TxtInOut/output.hru','HRU')
        #self.baseline_inputs = Get_DecisionVars_baseline(path,Problem.decisions_vars,Problem.decisions_subbasin)
        
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
    path = 'C:/Users/babbarsm/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default/'
    pathform = 'C:/Users/babbarsm/Documents/GitHub/InterACTWEL/src/SWAT_DevProb/Formulation.txt'
    
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
    Problem = Formulation.OptFormulation(pathform)
    SWATmodel = SWATmodel(path,Problem)
    
    
    
    