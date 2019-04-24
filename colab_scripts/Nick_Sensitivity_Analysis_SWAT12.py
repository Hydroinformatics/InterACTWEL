# -*- coding: utf-8 -*-

import os
os.chdir('..\src')

from tools.sensitivity.Sensitivity_Analysis_SWAT12 import SensitivityAnalysis


#%%
input_files = '..\data\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
sensitivity = SensitivityAnalysis(input_files)
sensitivity.outputcsv = 0
sensitivity.inputcsv = 1

sensitivity.swat_exe = 'swat_debug32.exe'
sensitivity.RunAnalysis(10)


