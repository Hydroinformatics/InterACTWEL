# -*- coding: utf-8 -*-

import os, shutil, sys, re, subprocess, pyodbc
import numpy as np
import csv, json

qswat_utils_path = r'C:\Users\sammy\Documents\GitHub\InterACTWEL\src'
sys.path.append(qswat_utils_path)

from qswat import QSWAT_output_parser

#%%
def FindHRUID(model_path):
    db_path = model_path
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + db_path + ';'
        )
    cnxn = pyodbc.connect(conn_str)
    crsr = cnxn.cursor()
    
    crsr.execute('select * from hrus')
    hrudict = dict()
    for row in crsr.fetchall():
        hrudict[str(row[12])] = row[0]

    return hrudict

def FindCropName(model_path):
    db_path = model_path + '/QSWATRef2012.mdb'
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + db_path + ';'
        )
    cnxn = pyodbc.connect(conn_str)
    crsr = cnxn.cursor()
    
    crsr.execute('select * from crop')
    cropdict = dict()
    for row in crsr.fetchall():
        cropdict[str(row[2])] = row[4]
    
    cropdict['NOCR'] = 'No Crops'
    return cropdict

def FindString(startstr, endstr, line):
    
    temp_id_a = line.find(startstr) 
    temp_id_b = line.find(endstr)
    tempstr = line[temp_id_a+1:temp_id_b]
    
    return tempstr

#%%
def GetOutputVars(output_vars_file):
    
    output_varsb = dict()
    line_bool = 0
    with open(output_vars_file,'rb') as search:
        for line in search:
            if '#' in line:
                line_bool = 1
                temp_dict = dict()
                outputs_id = "".join(line.split())
                outputs_id = outputs_id.strip('#')
                #opschd_id = re.split(':',linesplit)[1]
                #opschd_counter = 0
            
            elif '#' not in line and line_bool == 1 and len(line.strip()) > 0:
                linesplit = "".join(line.split())
                file_id = re.split('=',linesplit)
                temp_dict = dict()
                temp_dict['File'] = file_id[0]
                output_varsb[outputs_id] = temp_dict
                param_values = FindString('{','}',linesplit)
                param_values = re.split(';',param_values)
                temp_dict = dict()
                for parvals in param_values:
                    temp_var = parvals.split(':')
                    
                    temprange = temp_var[1]
                    temprange = temprange.strip('[')
                    temprange = temprange.strip(']')
                    if temp_var[0].lower() != 'table':
                        temp_dict[temp_var[0]] = int(temprange)
                    else:
                        templine = re.split('=',line)
                        templine = FindString('{','}',templine[1])
                        templine = re.split(';',templine )
                        templine = templine[0].split(':')
                        templine = templine[1].strip('[')
                        templine = templine.strip(']')
                        
                        temp_dict[temp_var[0]] = templine


            elif len(line.strip()) == 0:
                line_bool = 0
                output_varsb[outputs_id]['Vars']  = temp_dict
                
    search.close()
    
    if line_bool == 1:
        line_bool = 0
        output_varsb[outputs_id]['Vars'] = temp_dict
    
    return output_varsb

#%%
def Get_output_wql(tfile, var, varcol):
    #output_data = dict()
    data_array = dict()
    data_array['Years'] = []
    data_array['Type'] = 'RCH'
    varbool = 0
    
    with open(tfile) as search:
        for line in search:
            if varbool == 0:
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                    
                data_array[linesplit[1]].append(float(linesplit[varcol-1])) 
                        
    return data_array

def Get_output_rch(tfile, var, varcol):
    #output_data = dict()
    data_array = dict()
    data_array['Years'] = []
    data_array['Type'] = 'RCH'
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if 'RCH'.lower() in line.lower():    
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                    
                if len(linesplit[3].split('.')) < 2:
                    data_array[linesplit[1]].append(float(linesplit[varcol-1]))
                    if int(linesplit[3]) not in data_array['Years']:
                        data_array['Years'].append(int(linesplit[3]))
                        
#                    if int(linesplit[3]) < 13:# for monthly output
#                        data_array[linesplit[1]].append(float(linesplit[varcol-1]))                   
#                    elif int(linesplit[3]) not in data_array['Years']:
#                        data_array['Years'].append(int(linesplit[3]))
                        
    return data_array

#%%
def Get_output_std(tfile, table, var, varcol):

    #output_data = dict()
    data_array = dict()
    varbool = 0
    if 'Annual Summary for Watershed'.lower() in table.lower():
        data_array['Years'] = []
        data_array['Type'] = 'BSN'
        data_array['Data'] = []
        with open(tfile) as search:
            for line in search:
                if table in line:
                    line = search.next()
                    line = search.next()
                    line = search.next()
                    line = search.next()
                    line = search.next() # only needed when yearly input
                    varbool = 1
                
                elif varbool == 1:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    
                    if len(linesplit) > 1 and linesplit[0] !='SWAT':
                        if len(linesplit[0]) == 4:
                            data_array['Years'].append(int(linesplit[0]))
                            data_array['Data'].append(float(linesplit[varcol-1]))
                        varbool = 0
                    elif len(linesplit) < 1:
                        varbool = 0
    
    return data_array

#%%
def Get_output_hru(tfile, var, varcol):
    
    hru_sub = dict()
    
    data_array = dict()
    data_array['Years'] = []
    data_array['Type'] = 'HRU'
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if 'HRU'.lower() in line.lower():    
#                    linesplit = re.split('\s',line)
#                    linesplit = [e for e in linesplit if e != '']
#                    varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var] #Another Error in SWATA DA_STmmSURQ_GENmmSURQ_CNTmm
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                if len(linesplit[0]) > 4:
                    #stp = 0
                    linesplit[2] = linesplit[1]
                    linesplit[1] = linesplit[0][4:]
                    linesplit[0] = linesplit[0][0:4]
                
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                    hru_sub[linesplit[1]] = linesplit[3]

                #try:
                if len(linesplit[5].split('.')) < 3: # NEEDS to be chceck the HRU file is not displaying a month. ERROR IN SWAT
                    #if int(linesplit[5].split('.')[0]) < 13 and varcol == 6:
                    if int(linesplit[5].split('.')[0]) > 1900 and varcol == 6:
                        data_array[linesplit[1]].append(float('0.'+ linesplit[5].split('.')[1]))
                    #elif int(linesplit[5].split('.')[0]) < 13 and varcol != 6: # monthly output
                    elif int(linesplit[5].split('.')[0]) > 1900 and varcol != 6:
                        if varcol == 1:
                            data_array[linesplit[1]].append(linesplit[varcol-1])
                        else:
                            data_array[linesplit[1]].append(float(linesplit[varcol-1]))
                        
                    if int(linesplit[5].split('.')[0]) not in data_array['Years']:
                        data_array['Years'].append(int(linesplit[5].split('.')[0]))
                #except:
                #    pass;
    
    #if varbool == 0:
    #    print('Error: variable ' + var + ' was NOT found in File: ' + tfile)
    #else:               
    #output_data[var] = data_array
    return data_array, hru_sub

#%%
def Get_output_sub(tfile, var, varcol):
    
    data_array = dict()
    data_array['Years'] = []
    data_array['Type'] = 'SUB'
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if 'SUB'.lower() in line.lower() and 'BIGSUB'.lower() not in line.lower():    
#                    linesplit = re.split('\s',line)
#                    linesplit = [e for e in linesplit if e != '']
#                    varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var] #Another Error in SWATA DA_STmmSURQ_GENmmSURQ_CNTmm
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []

                #try:
                if len(linesplit[3].split('.')) < 3: # NEEDS to be chceck the HRU file is not displaying a month. ERROR IN SWAT
                    #if int(linesplit[3].split('.')[0]) < 13 and varcol == 6:
                    if int(linesplit[3].split('.')[0]) > 1900 and varcol == 6:
                        data_array[linesplit[1]].append(float(linesplit[3].split('.')[1]))
                        
                    #elif int(linesplit[3].split('.')[0]) < 13 and varcol != 6:
                    elif int(linesplit[3].split('.')[0]) > 1900 and varcol != 6:
                        data_array[linesplit[1]].append(float(linesplit[varcol-1]))
                        
                    if int(linesplit[3].split('.')[0]) not in data_array['Years']:
                        data_array['Years'].append(int(linesplit[3].split('.')[0]))
                #except:
                #    pass;
    
    #if varbool == 0:
    #    print('Error: variable ' + var + ' was NOT found in File: ' + tfile)
    #else:               
    #output_data[var] = data_array
    return data_array

#%%
def GetOutputData(outpath, output_vars, itern):

    output_vars_data = dict()
    for outfile in output_vars:
        tfile = outpath + '/' + os.path.splitext(output_vars[outfile]['File'])[0] + '_' + str(itern) + os.path.splitext(output_vars[outfile]['File'])[1]
        
        if tfile[len(tfile)-3:len(tfile)] == 'hru':
            print 'Reading output.hru'
            for varkey in output_vars[outfile]['Vars'].keys():
                data_array, hru_sub = Get_output_hru(tfile, varkey, output_vars[outfile]['Vars'][varkey])
                output_vars_data[varkey] = data_array
                
        elif tfile[len(tfile)-3:len(tfile)] == 'sub':
            print 'Reading output.sub'
            for varkey in output_vars[outfile]['Vars'].keys():
                data_array = Get_output_sub(tfile, varkey, output_vars[outfile]['Vars'][varkey])
                output_vars_data[varkey] = data_array
        
        elif tfile[len(tfile)-3:len(tfile)] == 'rch':
            print 'Reading output.rch'
            for varkey in output_vars[outfile]['Vars'].keys():
                output_vars_data[varkey] = Get_output_rch(tfile, varkey, output_vars[outfile]['Vars'][varkey])

        elif tfile[len(tfile)-3:len(tfile)] == 'wql':
            print 'Reading output.wql'
            for varkey in output_vars[outfile]['Vars'].keys():
                output_vars_data[varkey] = Get_output_wql(tfile, varkey, output_vars[outfile]['Vars'][varkey])

        elif tfile[len(tfile)-3:len(tfile)] == 'std':
            print 'Reading output.std'
            table = output_vars[outfile]['Vars']['Table']
            for varkey in output_vars[outfile]['Vars'].keys():
                if varkey.lower() != 'table':
                    output_vars_data[varkey] = Get_output_std(tfile, table, varkey, output_vars[outfile]['Vars'][varkey])
                    
    return output_vars_data

#%%
def HRU_SUBDict(output_vars_data, cropnames, wrsrc, hruwr, irr_dict, hru_wr_use, wrs_use):
    
    hru_sub = dict()
    temp_all = dict()
    temp_basin = dict()
    
    for hrui in output_vars_data['SUB'].keys():
        if output_vars_data['SUB'][hrui][0] not in hru_sub.keys() and hrui is not 'Type' and hrui is not 'Years':
            hru_sub[int(output_vars_data['SUB'][hrui][0])] = dict()
        
        if hrui is not 'Type' and hrui is not 'Years':
            for wrs_hru in hruwr[int(hrui)].keys():
                if hruwr[int(hrui)][wrs_hru][0] != 9999 and hruwr[int(hrui)][wrs_hru][1] not in hru_sub[int(output_vars_data['SUB'][hrui][0])].keys():
                    hru_sub[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]] = []
                
                if hruwr[int(hrui)][wrs_hru][0] != 9999 and hrui not in hru_sub[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]:
                    hru_sub[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]].append([hrui,wrs_hru])
            
    
    temp_all['hru_sub'] = hru_sub      

    if 'LULC' in output_vars_data.keys() and 'AREAkm2' in output_vars_data.keys():
        
        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()

                
                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    for cropn in output_vars_data['LULC'][hrui]:
                        if cropn.islower():
                            cropn = 'AGRL'
                        if cropn not in temp_dict[subid][wsrc]:
                            temp_dict[subid][wsrc][cropn] = dict()
                            temp_dict[subid][wsrc][cropn]['Name'] = cropnames[cropn]
                            temp_dict[subid][wsrc][cropn]['Data'] = dict()
                        
                            for i in range(len(output_vars_data['LULC']['Years'])):
                                temp_dict[subid][wsrc][cropn]['Data'][i+1] = 0
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            print int(hrui), wr_id
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                        
                        temp_dict[subid][wsrc][cropn]['Data'][cyear] =  temp_dict[subid][wsrc][cropn]['Data'][cyear] + round(per_wrs*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                        cyear = cyear + 1
                        
        temp_all['Planted crops (ha)'] = temp_dict
        temp_all['Planted crops (ha)']['Description'] = 'Total area of planted crops in sub-basin (ha).'            
        
        
    if 'LULC' in output_vars_data.keys() and 'YLDt' in output_vars_data.keys():

        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()

                
                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    yieldc = 0
                    for cropn in output_vars_data['LULC'][hrui]:
                        if cropn.islower():
                            cropn = 'AGRL'
                        if cropn not in temp_dict[subid][wsrc]:
                            temp_dict[subid][wsrc][cropn] = dict()
                            temp_dict[subid][wsrc][cropn]['Name'] = cropnames[cropn]
                            temp_dict[subid][wsrc][cropn]['Data'] = dict()
                        
                            for i in range(len(output_vars_data['LULC']['Years'])):
                                temp_dict[subid][wsrc][cropn]['Data'][i+1] = 0
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                        
                        temp_dict[subid][wsrc][cropn]['Data'][cyear] =  round(temp_dict[subid][wsrc][cropn]['Data'][cyear],2) + round(per_wrs*output_vars_data['YLDt'][str(hrui)][yieldc]*907.185*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                        cyear = cyear + 1
                        yieldc = yieldc + 1
        
        temp_all['Crop yield (kg)'] = temp_dict
        temp_all['Crop yield (kg)']['Description'] = 'Total yield of planted crops in sub-basin (kg).'


    if 'LULC' in output_vars_data.keys() and 'NAUTO' in output_vars_data.keys():
        
        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[subid][wsrc][i+1] = 0

                
                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    yieldc = 0
                    for cropn in output_vars_data['LULC'][hrui]:
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                        
                        temp_dict[subid][wsrc][cyear] =  round(temp_dict[subid][wsrc][cyear],2) + round(per_wrs*output_vars_data['NAUTO'][str(hrui)][yieldc]*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                        cyear = cyear + 1
                        yieldc = yieldc + 1
                        
        temp_all['N fertilizer (kg N)'] = temp_dict
        temp_all['N fertilizer (kg N)']['Description'] = 'Amount of N fertilizer applied automatically in sub-basin (kg N).'
                        
    if 'LULC' in output_vars_data.keys() and 'PAUTO' in output_vars_data.keys():
        
        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[subid][wsrc][i+1] = 0

                
                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    yieldc = 0
                    for cropn in output_vars_data['LULC'][hrui]:
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                        
                        temp_dict[subid][wsrc][cyear] =  round(temp_dict[subid][wsrc][cyear],2) + round(per_wrs*output_vars_data['PAUTO'][str(hrui)][yieldc]*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                        cyear = cyear + 1
                        yieldc = yieldc + 1
                        
        temp_all['P fertilizer (kg N)'] = temp_dict
        temp_all['P fertilizer (kg N)']['Description'] = 'Amount of P fertilizer applied automatically in sub-basin (kg N).'
        
    if 'LULC' in output_vars_data.keys() and 'IRRmm' in output_vars_data.keys():

        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()
                    temp_dict[subid][wsrc]['Name'] = irr_dict[wsrc]
                    temp_dict[subid][wsrc]['Data'] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[subid][wsrc]['Data'][i+1] = 0

                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    counter = 0
                    for irrsrc in output_vars_data['IRRmm'][str(hrui)]:
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                        
                        temp_val = round(per_wrs*output_vars_data['IRRmm'][str(hrui)][counter]*0.001* output_vars_data['AREAkm2'][str(hrui)][0]*1000000.0, 2)
                        temp_val = temp_val * (35.3147 / 43560.)
                        temp_dict[subid][wsrc]['Data'][cyear] =  round(temp_dict[subid][wsrc]['Data'][cyear],2) + round(temp_val,2)
                        cyear = cyear + 1
                        counter = counter + 1

        temp_all['Irrigation (acre-ft)'] = temp_dict
        temp_all['Irrigation (acre-ft)']['Description'] = 'Total irrigation volume applied automatically in sub-basin (acre-ft)'
   
    if 'GW_RCHGmm' in output_vars_data.keys():
                
        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[subid][wsrc][i+1] = 0

                
                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    yieldc = 0
                    for cropn in output_vars_data['LULC'][hrui]:
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                        
                        temp_val = round(per_wrs*output_vars_data['GW_RCHGmm'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0*10.0, 2)
                        temp_val = temp_val * 35.3147 * (1. / 43560.)
                        temp_dict[subid][wsrc][cyear] =  round(temp_dict[subid][wsrc][cyear],2) + round(temp_val,2)
                        cyear = cyear + 1
                        yieldc = yieldc + 1
        
        temp_all['Groundwater Recharge (acre-ft)'] = temp_dict
        temp_all['Groundwater Recharge (acre-ft)']['Description'] = 'Amount of water entering both aquifers (acre-ft).'
        
    if 'NSURQ' in output_vars_data.keys():
        
        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[subid][wsrc][i+1] = 0
            
                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    yieldc = 0
                    for cropn in output_vars_data['LULC'][hrui]:
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                                                
                        temp_val = round(per_wrs*output_vars_data['NSURQ'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                        temp_dict[subid][wsrc][cyear] =  round(temp_dict[subid][wsrc][cyear],2) + round(temp_val,2)
                        
                        cyear = cyear + 1
                        yieldc = yieldc + 1
        
        temp_all['Surface runoff Nitrate (kg N)'] = temp_dict
        temp_all['Surface runoff Nitrate (kg N)']['Description'] = 'NO3 contributed by HRU in surface runoff to reach (kg N).'
    
    if 'NLATQ' in output_vars_data.keys():

        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[subid][wsrc][i+1] = 0
            
                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    yieldc = 0
                    for cropn in output_vars_data['LULC'][hrui]:
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                        
                        temp_val = round(per_wrs*output_vars_data['NLATQ'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                        temp_dict[subid][wsrc][cyear] =  round(temp_dict[subid][wsrc][cyear],2) + round(temp_val,2)
                        
                        cyear = cyear + 1
                        yieldc = yieldc + 1                
        
        temp_all['Lateral flow Nitrate (kg N)'] = temp_dict
        temp_all['Lateral flow Nitrate (kg N)']['Description'] = 'NO3 contributed by HRU in lateral flow to reach (kg N)'
        
    if 'NO3GW' in output_vars_data.keys():
                
        temp_dict = dict()
        for subid in hru_sub.keys():
            if subid not in temp_dict.keys():
                temp_dict[subid] = dict()
            for wsrc in hru_sub[subid].keys():
                if wsrc not in temp_dict[subid].keys():
                    temp_dict[subid][wsrc] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[subid][wsrc][i+1] = 0
            
                for hrui, wrprior in hru_sub[subid][wsrc]:
                    cyear = 1
                    yieldc = 0
                    for cropn in output_vars_data['LULC'][hrui]:
                        
                        per_wrs = 1.0
                        wr_id = hruwr[int(hrui)][wrprior][0]
                        str_year = output_vars_data['LULC']['Years'][cyear-1]

                        if  wrs_use[wr_id][str_year] > 0:
                            per_wrs = (hru_wr_use[int(hrui)][wr_id][str_year]) / (wrs_use[wr_id][str_year])
                        
                        temp_val = round(per_wrs*output_vars_data['NO3GW'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                        temp_dict[subid][wsrc][cyear] =  round(temp_dict[subid][wsrc][cyear],2) + round(temp_val,2)
                        
                        cyear = cyear + 1
                        yieldc = yieldc + 1   
                        
        temp_all['Groundwater Nitrate (kg N)'] = temp_dict
        temp_all['Groundwater Nitrate (kg N)']['Description'] = 'NO3 contributed by HRU in groundwater flow to reach (kg N)'
    
    return temp_all, temp_basin
    


def ReachDict(output_vars_data):
    
    temp = dict()
    temp['Streamflow (cms)'] = output_vars_data['FLOW_OUTcms']
    temp['Streamflow (cms)']['Description'] = 'Average daily streamflow out of reach during time step (m3/s).'
    
    temp['Ammonium (kg N)'] = output_vars_data['NH4_OUT']
    temp['Ammonium (kg N)']['Description'] = 'Ammonium transported with water out of reach during time step (kg N).'
    
    temp['Nitrite (kg N)'] = output_vars_data['NO2_OUT']
    temp['Nitrite (kg N)']['Description'] = 'Nitrite transported with water out of reach during time step (kg N).'
    
    temp['Nitrate (kg N)'] = output_vars_data['NO3_OUT']
    temp['Nitrate (kg N)']['Description'] = 'Nitrate transported with water out of reach during time step (kg N).'
    
    temp['Dissolved oxygen (kg O2)'] = output_vars_data['DISOX_OUT']
    temp['Dissolved oxygen (kg O2)']['Description'] = 'Amount of dissolved oxygen transported out of reach during time step (kg O2).'
    
    temp['Stream Temperature (C)'] = output_vars_data['WTEMP_C']
    temp['Stream Temperature (C)']['Description'] = 'Daily stream temperature of water out of reach during time step (C).'
    
    return temp

#%%
def GetWaterRigthHRU(input_files, model_path, outpath, itern):
    
    wr_swat_file = []
    wsrc_sum = dict()
    hrugis_dict = dict()
    wrsrc = dict()
    
    with open(input_files['wrtfile'],'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            
            if int(linesplit[2]) not in wsrc_sum and int(linesplit[2]) != 0:
                    wsrc_sum[int(linesplit[2])] = 0
                    #hru_wsrc[int(linesplit[2])] = []
                    
            if len(linesplit) > 0 and int(linesplit[0]) != 9999 and int(linesplit[0])==1:
                wr_swat_file.append([int(linesplit[1]), int(linesplit[2]), int(linesplit[3]), int(linesplit[4]), int(linesplit[5]), int(linesplit[6])])
                wrsrc[int(linesplit[1])] = int(linesplit[2])
                
            if int(linesplit[2]) != 0 and int(linesplit[0])==1:
                wsrc_sum[int(linesplit[2])] = wsrc_sum[int(linesplit[2])] + int(linesplit[3])
                #hru_wsrc[int(linesplit[2])].append(int(linesplit[1]))
                
    search.close()
    
#    num_year_sim = 12
#    csv_file = outpath + '/wrdata_CR_iter_' + str(itern) + '.dat'
#    filein = open(csv_file,'w')
#    
#    for yr in range(0,num_year_sim):
#        for i in range(len(wr_swat_file)):
#            atxt = str(yr+1).rjust(4) + ''.rjust(3)
#            atxt = atxt + str(wr_swat_file[i][0]).rjust(5) + ''.rjust(3)
#            atxt = atxt + str(wr_swat_file[i][1]).rjust(4)  + ''.rjust(3)
#            atxt = atxt + str(int(wr_swat_file[i][2])).rjust(6)  + ''.rjust(3)
#            atxt = atxt + str(wr_swat_file[i][3]).rjust(4)  + ''.rjust(3)
#            atxt = atxt + str(wr_swat_file[i][4]).rjust(4)
#            #if yr == num_year_sim-1 and i == len(wr_swat_file)
#            filein.write(atxt + '\n') 
#    filein.close()

    hruwr = dict()
    with open(input_files['hruwrt_file'],'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if len(linesplit) > 0:
                if int(linesplit[0]) not in hruwr.keys():
                    hruwr[int(linesplit[0])] = dict()
                    #hruwr[int(linesplit[0])][int(linesplit[3])] = [int(linesplit[1]),int(linesplit[2]),int(linesplit[3])]
                #else:
                hruwr[int(linesplit[0])][int(linesplit[4])] = [int(linesplit[1]),int(linesplit[2]),int(linesplit[3]),int(linesplit[4])]
    
    search.close()
    
    hrugis_dict = FindHRUID(input_files['model_database'])
    
    hru_nowa = dict()
    ct = 0
    with open(input_files['hru_nowa_file'],'rb') as search:
        for line in search:
            linesplit = re.split(',',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if '\r\n' in line:
                linesplit[6] = linesplit[6].strip('\r\n')
                
            if len(linesplit) > 0 and ct > 0:
                #print hrugis_dict[linesplit[6]]
                if hrugis_dict[linesplit[6]] not in hru_nowa.keys() and hruwr[hrugis_dict[linesplit[6]]][1][0] != 9999 and len(hruwr[hrugis_dict[linesplit[6]]]) == 1:                    
                    for i in hruwr[hrugis_dict[linesplit[6]]].keys():
                        if hruwr[hrugis_dict[linesplit[6]]][i][1] == 3 and hrugis_dict[linesplit[6]] not in hru_nowa.keys():
                            hru_nowa[hrugis_dict[linesplit[6]]] = [i, hruwr[hrugis_dict[linesplit[6]]][i][0]]
                            
#                if hrugis_dict[linesplit[6].strip('\r\n')] not in hru_nowa.keys() and hruwr[hrugis_dict[linesplit[6].strip('\r\n')]][1][0] != 9999 and len(hruwr[hrugis_dict[linesplit[6].strip('\r\n')]]) == 1:                    
#                    for i in hruwr[hrugis_dict[linesplit[6].strip('\r\n')]].keys():
#                        if hruwr[hrugis_dict[linesplit[6].strip('\r\n')]][i][1] == 3 and hrugis_dict[linesplit[6].strip('\r\n')] not in hru_nowa.keys():
#                            hru_nowa[hrugis_dict[linesplit[6].strip('\r\n')]] = [i, hruwr[hrugis_dict[linesplit[6].strip('\r\n')]][i][0]]

            ct = ct + 1
                    
    search.close()
    
    return wr_swat_file, wrsrc, wsrc_sum, hruwr, hru_nowa

#%%
def run_SWAT(model_path, swat_exe):
    cwdir = os.getcwd()
    os.chdir(model_path + '/Scenarios/Default/TxtInOut')
    exitflag = subprocess.check_call([swat_exe])
    if exitflag == 0:
        print "Successful SWAT run"
    else:
        print exitflag
    os.chdir(cwdir)
    
#%%
def GetWaterUsed(outpath, itern):
    hru_wr_use = dict()
    with open(outpath + '/hru_wrt_' + str(itern) + '.out','rb') as search:
        first_line = search.readline()
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if int(linesplit[0]) not in hru_wr_use.keys():
                hru_wr_use[int(linesplit[0])] = dict()
            
            if int(linesplit[1]) not in hru_wr_use[int(linesplit[0])].keys():
                hru_wr_use[int(linesplit[0])][int(linesplit[1])] = dict()
    
            hru_wr_use[int(linesplit[0])][int(linesplit[1])][int(linesplit[5])] = float(linesplit[4])
    
    search.close()
    
    wrs_use = dict()
    with open(outpath + '/wrs_use_' + str(itern) + '.out','rb') as search:
        first_line = search.readline()
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if int(linesplit[0]) not in wrs_use.keys():
                wrs_use[int(linesplit[0])] = dict()
            
            wrs_use[int(linesplit[0])][int(linesplit[2])] = float(linesplit[1])
    
    search.close()
    
    return hru_wr_use, wrs_use
    
#%%
input_files = dict()
   
input_files['wrtfile'] = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11_01212021\Arjan\wrdata_CR.dat'
input_files['hruwrt_file'] = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11_01212021\Arjan\hruwr_CR.dat'
input_files['hru_nowa_file'] = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11_01212021\Arjan\NOWA_HRU_pumping_limit.csv'
input_files['model_database'] = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11_01212021\Meghna\Umatilla_InterACTWEL_QSWATv4.mdb'
input_files['base_irr'] = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11_01212021\Arjan\BASE_HRU_IRR.csv'

model_path = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11_01212021\Arjan\BASE'
outpath = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11_01212021\Arjan\ITERS'

irr_dict = {0: 'No irrigation', 1: 'Surface water', 2: 'Storage/Reservoir', 3: 'Groundwater', 5: 'Columbia River'}

itern = 0
build_model = 0
modeln = 0

wr_swat_file, wrsrc, wsrc_sum, hruwr, hru_nowa = GetWaterRigthHRU(input_files, model_path, outpath, itern)

scenarios  = [0.0, 0.10, 0.20, 0.30]
#scenarios  = [0.0, 0.10]

if build_model == 1:
    
    print "Creating Scenarios"
    
    hru_irr = [] # This section needs to be automated: using output.std
    with open(input_files['base_irr'],'rb') as search:
        for line in search:
            linesplit = re.split(',',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if len(linesplit) > 0 and int(linesplit[0]) in hru_nowa.keys():
                hru_irr.append([int(linesplit[0]),hru_nowa[int(linesplit[0])][0],hru_nowa[int(linesplit[0])][1], float(linesplit[2].strip('\r\n'))])
       
    hru_irr = np.asarray(sorted(np.asarray(hru_irr), key=lambda x: (x[1], -x[3])))         
    
    CR_wrs = []
    for i in range(len(wr_swat_file)):
        if wr_swat_file[i][1] == 5:
            CR_wrs.append(wr_swat_file[i])
    
    for itern in range(len(scenarios)): 
          
        CR_wrs = np.asarray(sorted(np.asarray(CR_wrs), key=lambda x: (-x[2], x[3])))
        CR_wrs = CR_wrs[CR_wrs[:,2]> 5000]
        np.random.shuffle(CR_wrs)
    
        new_CR_vol = wsrc_sum[3]*scenarios[itern]
        
        scenario_wsrc = np.random.rand(len(CR_wrs))
        scenario_wsrc = (scenario_wsrc/np.sum(scenario_wsrc))*new_CR_vol
        
        new_hruwr = dict()
        cr_wrdist = dict()
        
        #check hru 12
        file_path = model_path + '/Scenarios/Default/TxtInOut/wrdata.dat'
        shutil.copyfile(input_files['wrtfile'], file_path)
        
        if scenarios[itern] > 0:
            cr_wr_counter = 0
            for i in range(len(hru_irr)):
                new_hruwr[int(hru_irr[i,0])] = dict()
                if CR_wrs[cr_wr_counter,0] not in cr_wrdist.keys():
                    cr_wrdist[CR_wrs[cr_wr_counter,0]] = dict()
                    cr_wrdist[CR_wrs[cr_wr_counter,0]]['per_given'] = scenario_wsrc[cr_wr_counter]
                    cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'] = []
                
                temp = scenario_wsrc[cr_wr_counter] - wr_swat_file[int(hru_irr[i,2])][2]
                
                if temp < 0:
                    new_hruwr[hru_irr[i,0]][1] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],1]
                    cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
                    cr_wr_counter = cr_wr_counter + 1
                    
                    if cr_wr_counter < len(CR_wrs):
                        new_hruwr[int(hru_irr[i,0])][2] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],2]
                        cr_wrdist[CR_wrs[cr_wr_counter,0]] = dict()
                        cr_wrdist[CR_wrs[cr_wr_counter,0]]['per_given'] = scenario_wsrc[cr_wr_counter]
                        cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'] = []
                        cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
                        
                    else:
                        #print int(hru_irr[i,0])
                        new_hruwr[int(hru_irr[i,0])][2] = [hruwr[int(hru_irr[i,0])][1][0],hruwr[int(hru_irr[i,0])][1][1],hruwr[int(hru_irr[i,0])][1][2],2]
                        
                        break
                else:
                    new_hruwr[int(hru_irr[i,0])][1] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],1]
                    cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
                    scenario_wsrc[cr_wr_counter] = temp
               
            with open(outpath + '/CR_wr_dist_' + str(itern) + '.json', 'w') as fp:
                json.dump(cr_wrdist, fp)        
           
        csv_file = outpath + '/hruwr_CR_' + str(itern) + '.dat'
        filein = open(csv_file,'w')
        
        #atxt = 'HRU_ID, WR_ID, PRIOR, HRU_PRIOR'
        
        for i in range(1,len(hruwr)+1):
            if i in new_hruwr.keys():
                for ii in new_hruwr[i].keys():
                    atxt = str(i).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(new_hruwr[i][ii][0]).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(new_hruwr[i][ii][1]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(new_hruwr[i][ii][2]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(new_hruwr[i][ii][3]).rjust(4)
                    filein.write(atxt + '\n') 
            else:
                for ii in hruwr[i].keys():
                    atxt = str(i).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(hruwr[i][ii][0]).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(hruwr[i][ii][1]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(hruwr[i][ii][2]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(hruwr[i][ii][3]).rjust(4)
        
                    filein.write(atxt + '\n') 
        filein.close()
        
        file_path = model_path + '/Scenarios/Default/TxtInOut/hruwr.dat'
        shutil.copyfile(csv_file, file_path)
        
        print 'Iter #: ' + str(itern)
        run_SWAT(model_path, 'swat_rel64.exe')
        
            
        swat_files  = os.listdir(model_path + '/Scenarios/Default/TxtInOut/')
        out_files = [f for f in swat_files if 'output' in f]
            
            
        for base in out_files:
            file_path = outpath + '/' + os.path.splitext(base)[0] + '_' + str(itern) + os.path.splitext(base)[1]
            shutil.copyfile(model_path + '/Scenarios/Default/TxtInOut/' + base, file_path)
            
        
        hrw_file_out = model_path + '/Scenarios/Default/TxtInOut/hru_wrt.out'
        file_path = outpath + '/' + os.path.splitext('hru_wrt.out')[0] + '_' + str(itern) + os.path.splitext('hru_wrt.out')[1]
        shutil.copyfile(hrw_file_out, file_path)
        
        hrw_file_out = model_path + '/Scenarios/Default/TxtInOut/wrs_use.out'
        file_path = outpath + '/' + os.path.splitext('wrs_use.out')[0] + '_' + str(itern) + os.path.splitext('wrs_use.out')[1]
        shutil.copyfile(hrw_file_out, file_path)
        
else:
    
    print "Extracting Scenario Results"
      
    output_vars_file =  'C:\Users\sammy\Documents\GitHub\InterACTWEL\data\Sensitivity_SWAT12\OutputVars_Arjan_CR.txt'
    output_vars = GetOutputVars(output_vars_file)
    
    cropnames = FindCropName(model_path)
    
    csv_file = outpath + '/Arjan_Data_' + str(modeln) + '.csv'
    filein = open(csv_file,'w')  
    
    for itern in range(len(scenarios)): 
            
        input_files['hruwrt_file'] = outpath + '/hruwr_CR_' + str(itern) + '.dat'
        wr_swat_file, wrsrc, wsrc_sum, hruwr, hru_nowa = GetWaterRigthHRU(input_files, model_path, outpath, itern)
        output_vars_data = GetOutputData(outpath, output_vars, itern)
        hru_wr_use, wrs_use = GetWaterUsed(outpath, itern)
        
        temp_dict = dict()
        temp_all, temp_basin = HRU_SUBDict(output_vars_data, cropnames, wrsrc, hruwr, irr_dict, hru_wr_use, wrs_use)
        
        
    #    for subid in temp_all['hru_sub'].keys():
    #        wr_amt[subid] = dict()
    #        for wsrc in temp_all['hru_sub'][subid].keys():
    #            for hhruid, priort in temp_all['hru_sub'][subid][wsrc]:
                
        wr_amt = dict()
        for hrui in output_vars_data['SUB'].keys():
            if output_vars_data['SUB'][hrui][0] not in wr_amt.keys() and hrui is not 'Type' and hrui is not 'Years':
                wr_amt[int(output_vars_data['SUB'][hrui][0])] = dict()
            
            if hrui is not 'Type' and hrui is not 'Years':
                for wrs_hru in hruwr[int(hrui)].keys():
                    if hruwr[int(hrui)][wrs_hru][0] != 9999 and hruwr[int(hrui)][wrs_hru][1] not in wr_amt[int(output_vars_data['SUB'][hrui][0])].keys():
                        wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]] = dict()
                        wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['Sum'] = 0
                        wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['WR'] = []
                        
                    if hruwr[int(hrui)][wrs_hru][0] != 9999 and hrui not in wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]] and wr_swat_file[hruwr[int(hrui)][wrs_hru][0]][0] not in wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['WR']:
                        wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['Sum'] = wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['Sum'] + wr_swat_file[hruwr[int(hrui)][wrs_hru][0]][2]
                        wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['WR'].append(wr_swat_file[hruwr[int(hrui)][wrs_hru][0]][0])
        
        ucrop = []
        for hrui in output_vars_data['LULC'].keys():
            if hrui is not 'Type' and hrui is not 'Years':
                for cropn in output_vars_data['LULC'][hrui]:
                    if cropn.islower():
                        cropn = 'AGRL'
                    if cropn not in ucrop:
                        ucrop.append(cropn)
        
        actor = dict()
        actor_c = 1 
        for subid in temp_all['hru_sub'].keys():
            for wr in irr_dict.keys():
                if subid not in actor.keys():
                    actor[subid] = dict()
                actor[subid][wr] = actor_c 
                actor_c = actor_c + 1
                
        
        if itern == 0:
            atxt = 'ITER, REDUCTION OF GW WR (PER), ACTOR, SUB ID, WR SRC, WR AMT, YEAR,'
            for n in range(0,2):
                for u in ucrop:
                    atxt = atxt + str(cropnames[u]) + ','
            for irrid in irr_dict.keys():
                atxt = atxt + str(irr_dict[irrid]) + ','
            
            atxt = atxt + 'N Fertilizer, P Fertilizer, Groundwater Recharge (acre-ft),	Surface runoff Nitrate (kg N), Lateral flow Nitrate (kg N), Groundwater Nitrate (kg N),'
            for u in ucrop:
                    atxt = atxt + 'Profit ' + str(cropnames[u]) + ','
            
            atxt = atxt + 'Crop Profit ($), Costs ($), Total Profit ($),'
            filein.write(atxt + '\n')
            
        yr = 1
        for iy in output_vars_data['LULC']['Years']:
            #actor_c = 1                
            for subid in temp_all['hru_sub'].keys():
                #for wr in temp_all['hru_sub'][subid].keys():
                for wr in irr_dict.keys():
                    if wr != 0:
                        if wr in temp_all['hru_sub'][subid].keys(): 
                            actor_c = actor[subid][wr]
                            if itern == 0:
                                temptxt = 'BASE,' + str(scenarios[itern]*100) + ',' + str(actor_c) + ',' + str(subid) + ',' + str(irr_dict[wr]) + ',' + str(wr_amt[subid][wr]['Sum']) + ',' + str(iy) + ','
                            else:
                                temptxt = str(itern) + ',' + str(scenarios[itern]*100) + ',' + str(actor_c) + ',' + str(subid) + ',' + str(irr_dict[wr]) + ',' + str(wr_amt[subid][wr]['Sum']) + ',' + str(iy) + ','
                            
                            for uc in ucrop:
                                if uc in temp_all['Planted crops (ha)'][subid][wr].keys():
                                    temptxt = temptxt + str(temp_all['Planted crops (ha)'][subid][wr][uc]['Data'][yr]) + ','
                                else:
                                    temptxt = temptxt + str(0.0) + ','
                                    
                            for uc in ucrop:
                                if uc in temp_all['Crop yield (kg)'][subid][wr].keys():
                                    temptxt = temptxt + str(temp_all['Crop yield (kg)'][subid][wr][uc]['Data'][yr]) + ','
                                else:
                                    temptxt = temptxt + str(0.0) + ','
                            
                            for ir in irr_dict.keys():
                                if ir == wr:
                                    temptxt = temptxt + str(temp_all['Irrigation (acre-ft)'][subid][wr]['Data'][yr]) + ','
                                else:
                                    temptxt = temptxt + str(0.0) + ','
                                
                            temptxt = temptxt + str(temp_all['N fertilizer (kg N)'][subid][wr][yr]) + ',' + str(temp_all['P fertilizer (kg N)'][subid][wr][yr]) + ','
                            temptxt = temptxt + str(temp_all['Groundwater Recharge (acre-ft)'][subid][wr][yr]) + ',' + str(temp_all['Surface runoff Nitrate (kg N)'][subid][wr][yr]) + ',' + str(temp_all['Lateral flow Nitrate (kg N)'][subid][wr][yr]) + ',' + str(temp_all['Groundwater Nitrate (kg N)'][subid][wr][yr])
                            #actor_c = actor_c + 1
                        else:
                            actor_c = actor[subid][wr]
                            if itern == 0:
                                temptxt = 'BASE,' + str(scenarios[itern]*100) + ',' + str(actor_c) + ',' + str(subid) + ',' + str(irr_dict[wr]) + ',' + str(0) + ',' + str(iy) + ','
                            else:
                                temptxt = str(itern) + ',' + str(scenarios[itern]*100) + ',' + str(actor_c) + ',' + str(subid) + ',' + str(irr_dict[wr]) + ',' + str(0) + ',' + str(iy) + ','
                                
                            for uc in ucrop:
                                temptxt = temptxt + str(0.0) + ','
                            for uc in ucrop:
                                temptxt = temptxt + str(0.0) + ','
                            for ir in irr_dict.keys():
                                temptxt = temptxt + str(0.0) + ','
                            
                            temptxt = temptxt + str(0) + ',' + str(0) + ','
                            temptxt = temptxt + str(0) + ',' + str(0) + ',' + str(0) + ',' + str(0)
                            
                        filein.write(temptxt + '\n')
                        
            yr = yr + 1

filein.close()
    
    
    
#%%
#    wrdict = dict()
#    for wrid in range(len(wr_swat_file)):
#        if wr_swat_file[wrid][0] not in wrdict.keys():
#            wrdict[wr_swat_file[wrid][0]] = []
#            
#    for hruid in hruwr.keys():
#        for ii in hruwr[hruid]:
#            #if hruwr[hruid][ii][0] != 9999:
#            wrdict[hruwr[hruid][ii][0]].append(hruid)