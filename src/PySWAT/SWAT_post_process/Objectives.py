
def Available_Objectives():
    available_obj = dict()
    
    temp_dict = dict()
    temp_dict['FILE'] = ['output.std']
    temp_dict['VAR'] = ['Yld']
    temp_dict['LEVEL'] = ['REGION','SUB','HRU']
    available_obj['yield'] = temp_dict
    
    return available_obj


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


def Get_Objectives(self,path):
    available_obj = Available_Objectives()
    
    temp_dict= dict()
    for obj_id in self.objectives.keys():
        if self.objectives[obj_id]['PAR'].lower() == 'yield':
            temp_dict['DATA'] = available_obj['yield']
            baseline_data = Get_output_std(path['SWAT'] + 'TxtInOut/' + available_obj['yield']['FILE'][0],available_obj['yield']['VAR'][0])
                