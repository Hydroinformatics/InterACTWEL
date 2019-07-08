# -*- coding: utf-8 -*-

import os, argparse
os.chdir('D:\Nick\Documents\GitHub\InterACTWEL\src')



from tools.sensitivity.Sensitivity_Analysis_SWAT12_NG import SensitivityAnalysis


#%%
if __name__ == '__main__':

    ##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
    parser = argparse.ArgumentParser(description='Inputs File')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                        help='Path to text file with list of input Files')
    args = parser.parse_args()
    #%%
    #input_files = '..\data\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
    input_files = args.path[0].replace('\\','/')
    
    for i in range(1,2):
        sensitivity = SensitivityAnalysis(input_files)
        sensitivity.outputcsv = 1
        sensitivity.inputcsv = 1
    
        sensitivity.swat_exe = 'swat_debug32.exe'
        sensitivity.RunAnalysis(i)

