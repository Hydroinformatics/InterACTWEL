# -*- coding: utf-8 -*-

import os, re, zipfile, argparse, subprocess, shutil, random
import numpy as np
from Sensitivity_Analysis_SWAT12 import SensitivityAnalysis

#%%
    
#%%
#if __name__ == '__main__':
    
##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
#    parser = argparse.ArgumentParser(description='Optimization File')
#    parser.add_argument('path', metavar='-p', type=str, nargs='+',
#                    help='Path to zip file of SWAT baseline model')
#    args = parser.parse_args()
#
#    print args.path[0]
#    print args.path[1]
#     
    #path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/flow8gw/TxtInOut/'
    #path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/Default.zip'

#pathunzip = 'C:/Users/sammy/Desktop/Nick_Analysis'
#path = 'C:/Users/sammy/Documents/Research/SWAT/QSWATplus/SWATplus.zip'
#
#for sim_iter in range(100):
#    new_op_path = UnzipModel(path,pathunzip,sim_iter)
#    
#    HRU_ACTORS, hru_ids, total_area, no_change_lums = GetHRU_ACTORS(new_op_path)
#    New_OpsNames, crops = CreateNewSchFile(new_op_path)
#    CreateNewLumFile(new_op_path,New_OpsNames,crops)
#    crop_sch, hru_actors = ChangeHRU_Mgt(new_op_path, New_OpsNames, crops, HRU_ACTORS)
#    
#    os.chdir(new_op_path)
#    exitflag = subprocess.check_call(['rev57_64rel.exe'])
#    print sim_iter, exitflag



#no_change_lum_path = 'C:\Users\sammy\Documents\GitHub\InterACTWEL\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis/no_changeLU_SWAT12.txt'
#swat_path = 'C:\Users\sammy\Documents\Research\SWAT\QSWATplus\WillowSWAT12\WillowSWAT12_test'


input_files = 'C:\Users\sammy\Documents\GitHub\InterACTWEL\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
sensitivity = SensitivityAnalysis(input_files)

sensitivity.RunAnalysis(1)


