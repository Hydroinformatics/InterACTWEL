#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 21:01:06 2023

@author: sammy
"""

import os
import pandas as pd
import numpy as np
import re


#%%


out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS'

fnames = os.listdir(out_path)

wrs_dict = {}
file_counter = 1
for ff in fnames:
    
    print(ff)
    temp_dict = {}
    cc = 0
    with open(out_path + '/' + ff,'rb') as search:
        for line in search:
                linesplit = re.split('\s',line.decode('ascii').replace('\x00',''))
                linesplit = [t for t in linesplit if len(t) > 0]
                if cc == 0:
                    #print(linesplit)
                    columns = linesplit
                    for inline in linesplit:
                        temp_dict[inline.strip(',')] = []
                else:
                    for ii in range(0,len(columns)):
                        temp_dict[columns[ii].strip(',')].append(float(linesplit[ii]))
                        
     
                cc += 1
                
    search.close()
    wrs_dict[ff[:-4]]=temp_dict
        

#%%

out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'

fnames = os.listdir(out_path)

wrs_use_dict = {}
file_counter = 1
for ff in fnames:
    
    if 'wrs_use' in ff:
        print(ff)
        
        #df = pd.read_table(out_path + '/' + ff, skiprows=1, delim_whitespace=True , index_col = False, low_memory = True)
        
        temp_dict = {}
        cc = 0
        with open(out_path + '/' + ff,'rb') as search:
            for line in search:
                    
                    linesplit = re.split('\s',line.decode('ascii').replace('\x00',''))
                    linesplit = [t for t in linesplit if len(t) > 0]
                    if cc == 0:
                        #print(linesplit)
                        columns = linesplit
                        for inline in linesplit:
                            temp_dict[inline] = []
                    else:
                        for ii in range(0,len(columns)):
                            temp_dict[columns[ii]].append(float(linesplit[ii]))
                            
         
                    cc += 1
                    
        search.close()
        wrs_use_dict[ff[:-4]]=temp_dict
        
        
#%%


out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'

fnames = os.listdir(out_path)

hru_wrt_dict = {}
file_counter = 1
for ff in fnames:
    
    if 'hru_wrt_' in ff:
        print(ff)
        
        #df = pd.read_table(out_path + '/' + ff, skiprows=1, delim_whitespace=True , index_col = False, low_memory = True)
        
        temp_dict = {}
        cc = 0
        with open(out_path + '/' + ff,'rb') as search:
            for line in search:
                    
                    linesplit = re.split('\s',line.decode('ascii').replace('\x00',''))
                    linesplit = [t for t in linesplit if len(t) > 0]
                    if cc == 0:
                        #print(linesplit)
                        columns = linesplit
                        for inline in linesplit:
                            temp_dict[inline] = []
                    else:
                        for ii in range(0,len(columns)):
                            temp_dict[columns[ii]].append(float(linesplit[ii]))
                            
         
                    cc += 1
                    
        search.close()
        hru_wrt_dict[ff[:-4]] = temp_dict
        

#%%

for wrf in wrs_dict.keys():
    rowids = np.where(np.asarray(wrs_dict[wrf]['WR_VOL_ft-acre'])>999990)[0][0:10]
    wrid = np.unique(np.asarray(wrs_dict[wrf]['WR_ID'])[rowids])
    if len(wrid) > 1:
        print('Problem with: '+wrf)
        
  





        