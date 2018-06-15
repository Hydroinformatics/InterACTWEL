import re


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
                    varcol = [20]
                elif var == 'DA_STmm':
                    varcol = [21]
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
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
def Get_Objectives_Data(self,path):
#    available_obj = Available_Objectives()
    unique_pars = []
    unique_keys = []
    for obj_id in self.objectives.keys():
        if self.objectives[obj_id]['PAR'] not in unique_pars:
            unique_pars.append(self.objectives[obj_id]['PAR'])
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
        for ci in range(0,len(self.objectives[obj_id]['BVAR'])):
            temp_data = Get_output_std(path['SWAT'] + 'TxtInOut/' + self.objectives[obj_id]['FILE'], self.objectives[obj_id]['BVAR'][ci])
            self.objectives_data[temp_data.keys()[0]] = temp_data[temp_data.keys()[0]]
            
    return

#%%

def ParseFormulation(self):
    opt_problem = dict()
    
    with open(self.formulation_path['PROB'],'rb') as search:
        for line in search:
            #if 'variable' in line.lower() and 'conditions' not in line.lower():
            if 'decision variables' in line.lower():       
                line = search.next()
                line = search.next()
                
                while(len(line) > 2):
                    temp_dict = dict()
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    temp_dict['VAR'] = linesplit[1]
                    temp_dict['TYPE'] = linesplit[2]
                    linesplit[3] = linesplit[3][1:len(linesplit[3])-1]
                    temp_linesplit = re.split(',',linesplit[3])
                    var_range = []
                    for temprange in temp_linesplit:
                        if 'range' in temprange: 

                            temprange = temprange.strip('range(')
                            temprange = temprange.strip(')')
                            temprange = re.split('-',temprange)
                            var_range.extend(range(int(temprange[0]),int(temprange[1])+1))
                        else:
                            var_range.extend([float(temprange)])
                    
                    temp_dict['VALUES'] = var_range
                    temp_dict['FILE'] = linesplit[4]
                    
                    opt_problem[linesplit[0]] = temp_dict
                    line = search.next()
                    
            #elif 'variable' in line.lower() and 'conditions' in line.lower():
            elif 'variable conditions' in line.lower():
            
                line = search.next()
                line = search.next()
                condition_dict = dict()
                cc = 1
                while(len(line) > 2):
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    var_range = list()
                    temp_dict = dict()

                    linesplit[3] = linesplit[3][1:len(linesplit[3])-1]
                    temp_linesplit = re.split(',',linesplit[3])
                    var_range = []
                    for temprange in temp_linesplit:
                        if 'range' in temprange: 

                            temprange = temprange.strip('range(')
                            temprange = temprange.strip(')')
                            temprange = re.split('-',temprange)
                            var_range.extend(range(int(temprange[0]),int(temprange[1])+1))
                        else:
                            var_range.extend([int(temprange)])

                    temp_dict['CON_VAR'] = linesplit[0]
                    temp_dict['CON_LOGIC'] = linesplit[1]
                    temp_dict['CON_VALUE'] = linesplit[2]
                    temp_dict['VAR_IDS'] = var_range

                        
                    linesplit[4] = linesplit[4][1:len(linesplit[4])-1]
                    temp_linesplit = re.split(',',linesplit[4])
                    var_range = []
                    for temprange in temp_linesplit:
                        if 'range' in temprange: 

                            temprange = temprange.strip('range(')
                            temprange = temprange.strip(')')
                            temprange = re.split('-',temprange)
                            var_range.extend(range(int(temprange[0]),int(temprange[1])+1))
                        elif 'any' in temprange.lower():
                            var_range.extend([float('nan')])
                        else:
                            var_range.extend([int(temprange)])
                    temp_dict['VAR_VALUES'] = var_range
                    
                    condition_dict[str(cc)] = temp_dict
                    line = search.next()
                    cc = cc + 1
                    
            elif 'sub-basins' in line.lower():
                
                line = search.next()
                line = search.next()
                subbasin_dict = dict()
                while(len(line) > 2):
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    var_range = list()
                    temp_dict = dict()
                    for jj in [1,2]:
                        linesplit[jj] = linesplit[jj][1:len(linesplit[jj])-1]
                        temp_linesplit = re.split(',',linesplit[jj])
                        var_range = []
                        for temprange in temp_linesplit:
                            if 'range' in temprange: 
    
                                temprange = temprange.strip('range(')
                                temprange = temprange.strip(')')
                                temprange = re.split('-',temprange)
                                var_range.extend(range(int(temprange[0]),int(temprange[1])+1))
                            else:
                                var_range.extend([int(temprange)])
                        
                        if jj == 1:
                            temp_dict['HRU'] = var_range
                        elif jj == 2:
                            temp_dict['VAR_IDS'] = var_range
                    
                    subbasin_dict[str(linesplit[0])] = temp_dict
                    line = search.next()
                    
            elif 'constraints' in line.lower():
                line = search.next()
                line = search.next()
                baseline_files = dict()
                while(len(line) > 2):
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    tempbasevars = re.split(',',linesplit[1][1:len(linesplit[1])-1])
                    baseline_files[linesplit[0]] = tempbasevars
                    try:
                        line = search.next()
                    except:
                        break
                    
            elif 'objectives' in line.lower():
                line = search.next()
                line = search.next()
                obj_dict = dict()
                obj_id = 0
                while(len(line) > 2):
                    temp_dict = dict()
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    temp_dict['PAR'] = linesplit[0]
                    temp_dict['DIR'] = linesplit[1]
                    temp_dict['FILE'] = linesplit[3]
                    
                    temp_linesplit = linesplit[2][1:len(linesplit[2])-1]
                    temp_linesplit = re.split(',',temp_linesplit)
                    tdict = dict()
                    for tcount in range(0,len(temp_linesplit)):
                        tdict[tcount] = temp_linesplit[tcount]
                    temp_dict['LEVEL'] = tdict
                    
                    temp_linesplit = linesplit[4][1:len(linesplit[4])-1]
                    temp_linesplit = re.split(',',temp_linesplit)
                    tdict = dict()
                    for tcount in range(0,len(temp_linesplit)):
                        tdict[tcount] = temp_linesplit[tcount]
                    temp_dict['BVAR'] = tdict
                    
                    obj_dict[str(obj_id)] = temp_dict
                    obj_id += 1
                    try:
                        line = search.next()
                    except:
                        break
                    
    self.decisions_vars = opt_problem
    self.decisions_conditions = condition_dict
    self.decisions_subbasin = subbasin_dict
    self.baseline_vars = baseline_files
    self.objectives = obj_dict
    
    return
                   
class OptFormulation():
    def __init__(self,path):
        self.formulation_path = path
        self.decisions_vars = []
        self.decisions_conditions = []
        self.decisions_subbasin = []
        self.baseline_vars =[]
        self.objectives = []
        ParseFormulation(self) 
        
        #import Objectives
        self.objectives_data = dict()
        Get_Objectives_Data(self,self.formulation_path)

#if __name__ == '__main__':
#    
#    path = dict()
#    path['SWAT'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default/'
#    path['PROB'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/SWAT_DevProb/Formulation3.txt'
#
#    problem = OptFormulation(path)