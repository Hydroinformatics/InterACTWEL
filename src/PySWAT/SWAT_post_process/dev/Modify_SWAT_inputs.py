import numpy as np
import os, re, zipfile, subprocess, shutil, random

#def UnzipModel(path,pathuzip,iterc):
##    fbool = 0
##    while(fbol == 0):
#    #tempname = random.sample(range(0,50),1)
#    
#    folderpath = pathuzip + '/POPSWAT_' + str(iterc) + '/'
#    if os.path.isdir(folderpath):
#        shutil.rmtree(folderpath)
#    
#    with zipfile.ZipFile(path, "r") as z:
#        z.extractall(folderpath)
#
##    os.chdir(pathuzip + '/Default/TxtInOut/')    
##    exitflag = subprocess.check_call(['swatmodel_64rel.exe'])
##    print exitflag    
#    return folderpath
#    
#
#def Modify_SWAT(SWAT,Prob,plan,iterc):
#    
#    temp_path = UnzipModel(SWAT.path['ZIP'],SWAT.path['UNZIP'],iterc)
#    
#
#class SWAT():
#    def __init__(self,path):
#        self.path = path
#        
#if __name__ == '__main__':
#    
##%% Setup problem and prase SWAT baseline data
#
#    path = dict()
#    path['SWAT'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default/'
#    path['PROB'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/SWAT_DevProb/Formulation2.txt'
#    path['ZIP'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default.zip'
#    path['UNZIP'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/GA'
#    swatmodel = SWAT(path)
#    Modify_SWAT(swatmodel,0,0,0)
#    
#
#
##def Modify_SWAT(SWAT,Prob,plan,iterc):
#    
##    path = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/GA/POPSWAT_12/TxtInOut/'
#    


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


filename = '000060000'
file_ext = 'pnd'
tvars = ['PND_ESA', 'PND_EVOL', 'PND_PSA', 'PND_PVOL', 'PND_FR']
tval = (8.0, 40.0, 5.0, 25.0, 0.0)

path = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/GA/POPSWAT_0/'
Write_DecisionVars(path,filename,file_ext,tvars,tval)  
          
  
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
    
    