import os,re,zipfile
import numpy as np

def GetSummary_Data(path):
    sub_basin_bool = 0
    sub_basin_ids = []
    input_std  = open(path + 'input.std', 'rb');
    for line in input_std:
        if 'Subbasin Input Summary:' in line:
            sub_basin_bool = 1
            line = input_std.next()
            line = input_std.next()
            
        if sub_basin_bool == 1:
            line = line.strip()
            if len(line) == 0:
                break
            linesplit = re.split('\s',line)
            sub_id = int(linesplit[0])
            sub_HUC = int(linesplit[len(linesplit)-1])
            sub_basin_ids.append((sub_id,sub_HUC))
            
    return sub_basin_ids
        


def Get_output_data(tfile,var):
    output_data = dict()
    data_array = []
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if var in line:    
                file_list = line.split('\n')
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var]
                varbool = 1
            elif varbool == 1:
                file_list = line.split('\n')
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                data_array.append(linesplit[varcol[0]])
                    
    output_data[var] = data_array
                
    return output_data


def Getbaseline(path,baseline_files):
    baseline_data = dict()
    for tfile in baseline_files.keys():
        for var in baseline_files[tfile]:
            data = Get_output_data(path + tfile, var)
            baseline_data.update(data)
            
    return baseline_data
#        for var in baseline_files[tfile]:
#
#                    
#        fbool = 1
#                    
#        if fbool == 0:
#            print('Error: Mistach between File and variable')
    
    

class SWATmodel():
    def __init__(self,path,baseline_files):
        self.path = path
        self.sub_basin_sum = GetSummary_Data(path)
        self.baseline_data = Getbaseline(path,baseline_files)
        self.baseline_keys = self.baseline_data.keys()


if __name__ == '__main__':
    path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/flow8gw/TxtInOut/'
    
    baseline_files = dict()
    baseline_files['output.rch'] = ['FLOW_OUTcms','EVAPcms']
    baseline_files['output.wtr'] = ['PNDSEPmm']
    
    
    SWATmodel = SWATmodel(path,baseline_files)
    ## Get sub_basin Ids and number of HUCs to iterate over the files
    #sub_basin_sum = GetSummary_Data(path)
    
    #for sub in su_basin_sum:
    #    for i in range(1,sub[1]+1):
            
    
    
    
#    sub_files = [f.rfind('1') for f in os.listdir(path) if f.endswith('.sub')]
#    
#    file_object  = open(“filename”, “mode”
    
#    for i in range(1, subbsnNum+1):
#        
#        csv_file = path2 + '%s.mgt' % str(i)