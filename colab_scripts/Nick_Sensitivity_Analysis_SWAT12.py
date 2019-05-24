# -*- coding: utf-8 -*-

import os
os.chdir('..\src')

from tools.sensitivity.Sensitivity_Analysis_SWAT12 import SensitivityAnalysis


#%%
#input_files = '..\data\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
input_files = 'D:\Nick\Documents\GitHub\InterACTWEL\data\Sensitivity_SWAT12\SWAT12_Input_Files.txt'

for i in range(0,1):
    sensitivity = SensitivityAnalysis(input_files)
    sensitivity.outputcsv = 1
    sensitivity.inputcsv = 1

    sensitivity.swat_exe = 'swat_debug32.exe'
    sensitivity.RunAnalysis(i)
