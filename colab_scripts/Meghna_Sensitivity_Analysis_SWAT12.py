# -*- coding: utf-8 -*-

import os, argparse

os.chdir('..\src')
    
from tools.sensitivity.Sensitivity_Analysis_SWAT12 import SensitivityAnalysis

##%%
#if __name__ == '__main__':
#
#    ##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
#    parser = argparse.ArgumentParser(description='Inputs File')
#    parser.add_argument('path', metavar='-p', type=str, nargs='+',
#                        help='Path to text file with list of input Files')
#    args = parser.parse_args()
#    #%%
#    #input_files = '..\data\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
#    
#    #input_files = args.path[0].replace('\\','/')

input_files = 'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\SWAT12_Input_Files_CR_v2.txt'

for i in range(0,1):
    sensitivity = SensitivityAnalysis(input_files)
    sensitivity.outputcsv = 0
    sensitivity.inputcsv = 0

    sensitivity.swat_exe = 'swat_debug32.exe'
    sensitivity.RunAnalysis(i)

