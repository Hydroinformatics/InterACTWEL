import re

def ParseFormulation(self):
    opt_problem = dict()
    
    with open(self.formulation_path,'rb') as search:
        for line in search:
            if 'variable' in line.lower() and 'conditions' not in line.lower():
                    
                line = search.next()
                line = search.next()
                
                while(len(line) > 2):
                    temp_dict = dict()
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    temp_dict['VAR'] = linesplit[1]
                    temp_dict['TYPE'] = linesplit[2]
                    temp_dict['MIN'] = float(linesplit[3])
                    if linesplit[2] == 'N':
                        temp_dict['MAX'] = float(linesplit[3])
                        temp_dict['FILE'] = linesplit[4]
                    else:
                        temp_dict['MAX'] = float(linesplit[4])
                        temp_dict['FILE'] = linesplit[5]
                    
                    
                    opt_problem[linesplit[0]] = temp_dict
                    line = search.next()
                    
            elif 'variable' in line.lower() and 'conditions' in line.lower():
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
                    temp_dict['CON_LOG'] = linesplit[1]
                    temp_dict['CON_VALUE'] = linesplit[2]
                    temp_dict['VAR_IDS'] = var_range

                    
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
                    
            elif 'baseline' in line.lower():
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
                
    self.decisions_vars = opt_problem
    self.decisions_conditions = condition_dict
    self.decisions_subbasin = subbasin_dict
    self.baseline_vars = baseline_files
    
    return
                   
class OptFormulation():
    def __init__(self,path):
        self.formulation_path = path
        
        self.decisions_vars = []
        self.decisions_conditions = []
        self.decisions_subbasin = []
        self.baseline_vars =[]
        
        ParseFormulation(self) 
        
#if __name__ == '__main__':
#    
#    path = 'C:/Users/babbarsm/Documents/GitHub/InterACTWEL/src/SWAT_DevProb/Formulation.txt'
#    problem = OptFormulation(path)