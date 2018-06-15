import re

#def Available_Objectives():
#    available_obj = dict()
#    
#    temp_dict = dict()
#    temp_dict['FILE'] = ['output.hru']
#    temp_dict['VAR'] = ['YLDt/ha']
#    temp_dict['LEVEL'] = ['REGION','SUB','HRU']
#    available_obj['yield'] = temp_dict
#    
#    temp_dict = dict()
#    temp_dict['FILE'] = ['output.hru']
#    temp_dict['VAR'] = ['SA_STmm','DA_STmm']
#    temp_dict['varcol'] = []
#    temp_dict['LEVEL'] = ['REGION','SUB','HRU']
#    available_obj['gw_rch'] = temp_dict
#    
#    
#    return available_obj


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
