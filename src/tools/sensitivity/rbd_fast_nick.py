# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 10:11:29 2019

@author: Nick
"""

import sys
import os
sys.path.append('../..')

from SALib.analyze import rbd_fast
from SALib.sample import latin
from SALib.test_functions import Ishigami
from SALib.util import read_param_file

import numpy as np
import pandas as pd
import random


data_path = os.getcwd() + '\\data_nick\\'
# Read the parameter range file and generate samples
prob_path = data_path + 'rbd_test_pars.txt'

problem = read_param_file(prob_path)

#%% Generate samples
num_iters = 1000
param_values = latin.sample(problem, num_iters)


#np.savetxt(data_path+'param_values_lhc.txt', param_values)

# Normalize Samples
sums = np.sum(param_values, axis=1)
param_values_norm = param_values / sums[:, None]
np.savetxt(data_path+'param_values_lhc_norm.txt', param_values_norm)


#%% Rewrite watrgt.dat files

wr_vars_path = data_path+'wr_vars.csv'
wr_vars = pd.read_csv(wr_vars_path)
norm_coeffs_path = data_path+'param_values_lhc_norm.txt'
norm_coeffs = pd.read_csv(norm_coeffs_path, sep='\s+', header=None)
wrdat_path = data_path+'wrdat.csv'
add_water_af = 20000
r,c = wr_vars.shape
for i in range(0,num_iters):
    watrght_i = pd.read_csv(wrdat_path)
    new_amt = pd.DataFrame(0, index=np.arange(len(wr_vars)), columns=['nAMT','AMT_AF','VAR'])
    new_amt['AMT_AF'] = wr_vars['AMT_AF']
    new_amt['VAR'] = wr_vars['VAR']
    new_amt['nAMT'] = (new_amt['AMT_AF']+((wr_vars['AMT_AF']/wr_vars['SUM_AMT'])*(add_water_af*param_values_norm[i,new_amt['VAR']-1])))
    new_amt.loc[new_amt.VAR == 0, 'nAMT'] = new_amt['AMT_AF']
    new_amt_2write = pd.DataFrame(0, index=np.arange(len(wr_vars)), columns=['WRID', 'SRC', 'AMT_AF', 'D1', 'D2'])
    new_amt_2write['WRID'] = wr_vars['WRID']
    new_amt_2write['SRC'] = wr_vars['SRC']
    new_amt_2write['AMT_AF'] = new_amt['nAMT']
    new_amt_2write['D1'] = wr_vars['D1']
    new_amt_2write['D2'] = wr_vars['D2']
    new_amt_2write = new_amt_2write.round(0)
    new_amt_2write = new_amt_2write.astype(int)
    new_amt_2write = new_amt_2write.astype(str)
    
    new_amt_2write['WRID'] = new_amt_2write['WRID'].str.pad(width=4)
    new_amt_2write['SRC'] = new_amt_2write['SRC'].str.pad(width=6)
    new_amt_2write['AMT_AF'] = new_amt_2write['AMT_AF'].str.pad(width=6)
    new_amt_2write['D1'] = new_amt_2write['D1'].str.pad(width=6)
    new_amt_2write['D2'] = new_amt_2write['D2'].str.pad(width=6)
    #Change to watrgt\
    np.savetxt(data_path+'watrgt_i\watrgt_'+str(i)+'.txt', new_amt_2write, fmt='%s')

#%% Rewrite HRU_Crop_Rotations.csv
for i in range(0,num_iters):
    watrgt_path = data_path+'watrgt_i\watrgt_'+str(i)+".txt"
    wr_area_path = data_path+'WR_area.csv'
    hrudat_path = data_path+'hruwr.csv'
    crp_rots_path = data_path+'crp_rots.csv'
    
    watrgt = pd.read_csv(watrgt_path, sep='\s+', names=['WRID','SRC','AMT_AF','D1','D2'])
    hrudat = pd.read_csv(hrudat_path)
    wr_area = pd.read_csv(wr_area_path)
    
    wr_area['AMT_AF'] = watrgt['AMT_AF']
    wr_area['FT'] = wr_area['AMT_AF']/wr_area['WR_AREA_AC']
    m,n = wr_area.shape
    CRP_CL = np.zeros(m)
    wr_area['CRP_CL'] = CRP_CL
    wr_area.loc[wr_area.FT > 2, 'CRP_CL'] = 1
    
    #Write HRU_Crop_Rotations.csv
    crp_rots = pd.read_csv(crp_rots_path,header=None)
    crp_rots_temp = pd.DataFrame(0, index=np.arange(len(hrudat)), columns=['HRU_ID', '2012', '2013', '2014', '2015', '2016', 'WRID', 'CRP_CL'])
    crp_rots_temp['HRU_ID'] = hrudat['HRU']
    crp_rots_temp['WRID'] = hrudat['WRID']
    
    crp_rots_temp = crp_rots_temp.set_index('WRID')
    wr_area = wr_area.set_index('WRID')
    crp_rots_temp['CRP_CL']=wr_area['CRP_CL']
    crp_rots_temp = crp_rots_temp.reset_index(drop=True)
    
    crp_rots_write = pd.DataFrame(0, index=np.arange(len(hrudat)), columns=['HRU_ID', '2012', '2013', '2014', '2015', '2016'])
    a, b = crp_rots_temp.shape
    zero = crp_rots[0]
    one = crp_rots[1]
    two = crp_rots[2]
    three = crp_rots[3]
    four = crp_rots[4]
       
    for j in range (0,a):
        if crp_rots_temp.loc[j]['CRP_CL'] == 1:
            temp_rand = random.randint(0,4)
            zero_temp = zero[temp_rand]
            one_temp = one[temp_rand]
            two_temp = two[temp_rand]
            three_temp = three[temp_rand]
            four_temp = four[temp_rand]
            crp_rots_write.loc[j] = pd.Series({'2012':zero_temp, '2013':one_temp, '2014':two_temp, '2015':three_temp, '2016':four_temp})
        else:
            temp_rand = random.randint(5,6)
            zero_temp = zero[temp_rand]
            one_temp = one[temp_rand]
            two_temp = two[temp_rand]
            three_temp = three[temp_rand]
            four_temp = four[temp_rand]
            crp_rots_write.loc[j] = pd.Series({'2012':zero_temp, '2013':one_temp, '2014':two_temp, '2015':three_temp, '2016':four_temp})
    crp_rots_write['HRU_ID'] = crp_rots_temp['HRU_ID']
    crp_rots_write = crp_rots_write.astype(int)
    #Write crp_rot_i
    path_crp_rot_i = data_path+'HRU_Crop_Rots_i\crp_rot_'+str(i)+'.csv'
    crp_rots_write.to_csv(path_crp_rot_i,index=False)

#%% Run the "model" and save the output in a text file
# This will happen offline for external models

#Y = Ishigami.evaluate(param_values)
#
#
#
#
#
#copy_path = 'D:/Nick\Documents\INFEWS\Sensitivity/analysis\sens_analysis\watrght_i\watrgt_'+str(iterc)+'.txt'
#paste_path = 'D:/Nick\Documents\INFEWS\Sensitivity/analysis\sens_analysis\watrgt_test.dat'
#shutil.copyfile(copy_path,paste_path)
#
#
#
#
#
#
##%% Perform the sensitivity analysis using the model output
## Specify which column of the output file to analyze (zero-indexed)
#Si = rbd_fast.analyze(problem, param_values, Y, print_to_console=True)
## Returns a dictionary with keys 'S1' and 'ST'
## e.g. Si['S1'] contains the first-order index for each parameter, in the
## same order as the parameter file