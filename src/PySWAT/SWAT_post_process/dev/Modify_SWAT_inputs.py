import numpy as np
import os, zipfile, subprocess, shutil, random

#def UnzipModel(path,pathuzip):
##    fbool = 0
##    while(fbol == 0):
#    tempname = random.sample(range(0,50),1)
#    
#    folderpath = pathuzip + '/POPSWAT_' + str(tempname[0]) + '/'
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
#def Modify_SWAT(SWAT,Prob,plan):
#    
#    temp_path = UnzipModel(SWAT.path['ZIP'],SWAT.path['UNZIP'])
#
#class SWAT():
#    def __init__(self,path):
#        self.path = path
#if __name__ == '__main__':
#    
#
##%% Setup problem and prase SWAT baseline data
#
#    path = dict()
#    path['SWAT'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default/'
#    path['PROB'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/SWAT_DevProb/Formulation2.txt'
#    path['ZIP'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/Default.zip'
#    path['UNZIP'] = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/GA'
#    swatmodel = SWAT(path)
#    Modify_SWAT(swatmodel,0,0)
#    


def Modify_SWAT(SWAT,Prob,plan):
    
    path = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model/GA/POPSWAT_12/TxtInOut/'
    
    
    
    
    
    
    