# -*- coding: utf-8 -*-

import os, shutil, sys, re, subprocess, pyodbc
import numpy as np
import csv, json

from Output_parser_utils import SWAT_Parser, JSON_SGformatter

#%%
outpath = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Backup_v4_Iter15_bestsim_results'
model_path = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Backup_v4_Iter15_bestsim'

output_vars_file =  'C:\Users\sammy\Documents\GitHub\InterACTWEL\data\Sensitivity_SWAT12\OutputVars_Akilas_CR.txt'

#%%

swat_files  = os.listdir(model_path + '/Scenarios/Default/TxtInOut/')
out_files = [f for f in swat_files if 'output' in f]


for itern in range(-1,2):
    for base in out_files:
        if 'mgt' not in base:
            #file_path = outpath + '/' + base
            if itern < 0:
                file_path = outpath + '/' + os.path.splitext(base)[0] + '_BASE' + os.path.splitext(base)[1]
            else:
                file_path = outpath + '/' + os.path.splitext(base)[0] + '_' + str(itern) + os.path.splitext(base)[1]
            shutil.copyfile(model_path + '/Scenarios/Default/TxtInOut/' + base, file_path)
        
    
    hrwrt_file_out = model_path + '/Scenarios/Default/TxtInOut/hru_wrt.out'
    if itern < 0:
        file_path = outpath + '/' + 'hru_wrt_BASE.out'
    else:
        file_path = outpath + '/' + 'hru_wrt_' + str(itern) + '.out'
    shutil.copyfile(hrwrt_file_out, file_path)
    
    wrsuse_file_out = model_path + '/Scenarios/Default/TxtInOut/wrs_use.out'
    if itern < 0:
        file_path = outpath + '/' + 'wrs_use_BASE.out'
    else:
        file_path = outpath + '/' + 'wrs_use_' + str(itern) + '.out'
    shutil.copyfile(wrsuse_file_out, file_path)
    
    ############################
    wrdata_file_out = model_path + '/Scenarios/Default/TxtInOut/wrdata.dat'
    if itern < 0:
        file_path = outpath + '/' + 'wrdata_BASE.dat'
    else:
        file_path = outpath + '/' + 'wrdata_' + str(itern) + '.dat'
    shutil.copyfile(wrdata_file_out, file_path)
    
    hrwwr_file_out = model_path + '/Scenarios/Default/TxtInOut/hruwr.dat'
    if itern < 0:
        file_path = outpath + '/' + 'hruwr_BASE.dat'
    else:
        file_path = outpath + '/' + 'hruwr_' + str(itern) + '.dat'
    shutil.copyfile(hrwwr_file_out, file_path)

#    file_cio = model_path + '/Scenarios/Default/TxtInOut/file.cio'
#    if itern < 0:
#        file_path = outpath + '/' + 'file_BASE.cio'
#    else:
#        file_path = outpath + '/' + 'file_' + str(itern) + '.cio'
#    shutil.copyfile(file_cio, file_path)

#%%

jsonpath = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\SG_jsonfiles'
parser = SWAT_Parser(outpath, output_vars_file)
parser.GetOutputData()
output = parser.output_vars_data

#wr_swat_file, wrsrc, wsrc_sum, hruwr, hru_nowa = GetWaterRigthHRU(input_files, model_path, outpath, itern)
#cropnames = FindCropName_csv(model_path)

#%%
jsoncreator = JSON_SGformatter()
json_dict = jsoncreator.barGraph(output['std'], 'WATER_YIELD', 'WATER YIELD_reg_year','Water yield from watershed.', 'mm', jsonpath + '/WATER_YIELD.json')
json_dict = jsoncreator.barGraph(output['std'], 'GWQ', 'GWQ_reg_year','Groundwater contribution to stream in watershed.', 'mm', jsonpath + '/GWQ.json')
json_dict = jsoncreator.barGraph(output['std'], 'ET', 'ET_reg_year','Evapotranspiration in watershed.', 'mm', jsonpath + '/ET.json')
json_dict = jsoncreator.barGraph(output['std'], 'SW', 'SW_reg_year','Amount of water stored in soil profile for watershed.', 'mm', jsonpath + '/SW.json')
json_dict = jsoncreator.barGraph(output['std'], 'PERCO_LATE', 'PERCO_LATE_reg_year','Water percolation past bottom of soil profile in watershed.', 'mm', jsonpath + '/PERCO_LATE.json')
json_dict = jsoncreator.barGraph(output['std'], 'SED_YIELD', 'SED_YIELD_reg_year','Sediment yield from watershed.', 'metric tons/ha', jsonpath + '/SED_YIELD.json')

json_dict = jsoncreator.barGraph(output['std'], 'NO3_SURQ', 'NO3_SURQ_reg_year','Nitrate loading to stream from watershed’s surface runoff.', 'kg N/ha', jsonpath + '/NO3_SURQ.json')
json_dict = jsoncreator.barGraph(output['std'], 'NO3_LATQ', 'NO3_LATQ_reg_year','Nitrate loading to stream from watershed’s lateral flow.', 'kg N/ha', jsonpath + '/NO3_LATQ.json')
json_dict = jsoncreator.barGraph(output['std'], 'NO3_PERC', 'NO3_PERC_reg_year','Nitrate percolation past bottom of soil profile in watershed.', 'kg N/ha', jsonpath + '/NO3_PERC.json')
json_dict = jsoncreator.barGraph(output['std'], 'NO3_CROP', 'NO3_CROP_reg_year','Plant uptake of N in watershed.', 'kg N/ha', jsonpath + '/NO3_CROP.json')


json_dict = jsoncreator.barGraph(output['sub'], 'PRECIP', 'PRECIP_sub_year','Total amount of precipitation during time step.', 'mm', jsonpath + '/PRECIP_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'WYLD', 'WYLD_sub_year','Water yield from sub-basin.', 'mm', jsonpath + '/WYLD_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'GWQ', 'GW_Q_sub_year','Groundwater contribution to stream in sub-basin.', 'mm', jsonpath + '/GWQ_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'ET', 'ET_sub_year','Evapotranspiration in sub-basin.', 'mm', jsonpath + '/ET_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'SW', 'SW_sub_year','Amount of water stored in soil profile for sub-basin.', 'mm', jsonpath + '/SW_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'PERC', 'PERC_sub_year','Water that percolates past the root zone during the time step.', 'mm', jsonpath + '/PERC_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'SYLD', 'SYLD_sub_year','Sediment yield from sub-basin.', 'mm', jsonpath + '/SYLD_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'NSURQ', 'NSURQ_sub_year','Nitrate loading to stream from sub-basin’s surface runoff.', 'kg N/ha', jsonpath + '/NSURQ_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'LATQ', 'LATQ_sub_year','Nitrate loading to stream from sub-basin’s lateral flow.', 'kg N/ha', jsonpath + '/LATQ_Sub.json')
json_dict = jsoncreator.barGraph(output['sub'], 'GWNO3', 'GWNO3_sub_year','Nitrate percolation past bottom of soil profile in sub-basin.', 'kg N/ha', jsonpath + '/GWNO3_Sub.json')



#%%
#with open(outpath + '/test_data.json', 'w') as fp:
#    json.dump(json_dict, fp)

#%%

#ActPlan = dict()
#plancount = 0
#
#for i in range(0,1):
#    #ActPlan['Plan ' + str(i)] = dict()
#    
#    model_path = outpath.replace('\\','/') + '/ITER_' + str(i) + '/'
##    #shutil.copyfile(model_path + 'Scenarios/Default/TxtInOut/watrgt.dat', model_path + 'Scenarios/Default/Tempfile.txt')
##    temp_path = model_path + 'Scenarios/Default/Tempfile.txt'
#    
#    cropnames = FindCropName(model_path)
##    irr_dict = FindVarIds(model_path)
#    irr_dict = {0: 'No irrigation',1: 'Surface water', 3: 'Groundwater', 5: 'Columbia River'}
#    
#    for ii in range(0,1): 
#        print 'ITER_' + str(i) + ' - ADD: ' + str(ii) 
#        wrdict, owrdict, wrsrc, hruwr, output_vars_data = GetWaterRigthHRU(wr_path, model_path, 1, output_vars)
#    
#        temp_dict = dict()
#        temp_dict['REACH'] = ReachDict(output_vars_data)
#        temp_all, temp_basin = HRU_SUBDict(output_vars_data, cropnames, wrsrc, owrdict, hruwr, irr_dict)
#        temp_dict['SUB'] = temp_all
#        temp_dict['BASIN'] = temp_basin
#        
#        Indiv_BASIN_json(temp_basin)
#        
#        
#        ActPlan['Plan ' + str(i) + str(ii)] = temp_dict
#     
#    #ActPlan['Plan ' + str(i)]['SUB'] = ReachDict(output_vars_data)
#    #ActPlan['Plan ' + str(i)]['BASIN'] = ReachDict(output_vars_data)
#   
#with open(os.getcwd() + '/Mockup_data.json', 'w') as fp:
#    json.dump(ActPlan, fp)
#    
#tte = Indiv_BASIN_json(temp_basin)