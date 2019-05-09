# -*- coding: utf-8 -*-

import os
os.chdir('..\src')

from tools.sensitivity.Sensitivity_Analysis_SWAT12 import SensitivityAnalysis


#%%
#input_files = '..\data\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
input_files = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\Sensitivity_SWAT12\SWAT12_Input_Files.txt'

for i in range(6,10):
    sensitivity = SensitivityAnalysis(input_files)
    sensitivity.outputcsv = 1
    sensitivity.inputcsv = 1

    sensitivity.swat_exe = 'swat_debug32.exe'
    sensitivity.RunAnalysis(i)