# -*- coding: utf-8 -*-

import os, shutil, sys, re, subprocess
import numpy as np
import csv, json

#%%
def run_SWAT(model_path, swat_exe):
    cwdir = os.getcwd()
    os.chdir(model_path)
    exitflag = subprocess.check_call([swat_exe])
    if exitflag == 0:
        print("Successful SWAT run")
    else:
        print(exitflag)
    os.chdir(cwdir)
    
#%%

swat_dir = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/SWAT_Model15/TxtInOut'
output_dir = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/SWAT_Model15/ITERS_Results'
#wrdata_file = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS'
wrdata_file = '/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS'
fnames = os.listdir(wrdata_file)

for ff in fnames:
    sub_string = ff[ff.find('_'):-4]
    
    file_path = swat_dir + '/wrdata.dat'
    shutil.copyfile(wrdata_file + '/' + ff, file_path)
    
    #run_SWAT(swat_dir, './swat_rel64')
    
    out_swat_files  = os.listdir(swat_dir)
    out_files = [f for f in out_swat_files if 'output' in f]
    
    for base in out_files:
        if 'mgt' not in os.path.splitext(base)[1]:
            outfile_path = output_dir + '/' + os.path.splitext(base)[0] + sub_string + os.path.splitext(base)[1]
            #print(swat_dir + '/' + base)
            #print(outfile_path)
            shutil.copyfile(swat_dir + '/' + base, outfile_path)
        
    
    hrw_file_out = swat_dir + '/hru_wrt.out'
    file_path = output_dir + '/' + os.path.splitext('hru_wrt.out')[0] + sub_string + os.path.splitext('hru_wrt.out')[1]
    shutil.copyfile(hrw_file_out, file_path)
    
    hrw_file_out = swat_dir + '/wrs_use.out'
    file_path = output_dir + '/' + os.path.splitext('wrs_use.out')[0] + sub_string + os.path.splitext('wrs_use.out')[1]
    shutil.copyfile(hrw_file_out, file_path)

