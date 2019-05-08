# -*- coding: utf-8 -*-

import os, shutil, sys, re, subprocess, pyodbc
import numpy as np
import csv, json

#os.chdir('..\src')
#
#from tools.sensitivity.Sensitivity_Analysis_SWAT12 import SensitivityAnalysis
#
#
##%%
##input_files = '..\data\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
#input_files = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
#
#for i in range(0,10):
#    sensitivity = SensitivityAnalysis(input_files)
#    sensitivity.outputcsv = 1
#    sensitivity.inputcsv = 1
#
#    sensitivity.swat_exe = 'swat_debug32.exe'
#    sensitivity.RunAnalysis(i)
def FindString(startstr, endstr, line):
    
    temp_id_a = line.find(startstr) 
    temp_id_b = line.find(endstr)
    tempstr = line[temp_id_a+1:temp_id_b]
    
    return tempstr

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
                    if int(linesplit[3]) < 13:
                        data_array[linesplit[1]].append(float(linesplit[varcol-1])) 
                    elif int(linesplit[3]) not in data_array['Years']:
                        data_array['Years'].append(int(linesplit[3]))
                        
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
                    varbool = 1
                
                elif varbool == 1:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    
                    if len(linesplit) < 2 and len(linesplit) > 1:
                        line = search.next()
                        linesplit = re.split('\s',line)
                        linesplit = [e for e in linesplit if e != '']
                        if len(linesplit[0]) == 4:
                            data_array['Years'].append(int(linesplit[0]))
                        varbool = 0
                    elif len(linesplit) < 1:
                        varbool = 0
                    else:
                        if len(linesplit[0]) < 4 and len(linesplit) > 1:
                            data_array['Data'].append(float(linesplit[varcol-1]))
    
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
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                    hru_sub[linesplit[1]] = linesplit[3]

                #try:
                if len(linesplit[5].split('.')) < 3: # NEEDS to be chceck the HRU file is not displaying a month. ERROR IN SWAT
                    if int(linesplit[5].split('.')[0]) < 13 and varcol == 6:
                        data_array[linesplit[1]].append(float('0.'+ linesplit[5].split('.')[1]))
                    elif int(linesplit[5].split('.')[0]) < 13 and varcol != 6:
                        if varcol == 1:
                            data_array[linesplit[1]].append(linesplit[varcol-1])
                        else:
                            data_array[linesplit[1]].append(float(linesplit[varcol-1]))
                        
                    elif int(linesplit[5].split('.')[0]) not in data_array['Years']:
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
            if 'SUB'.lower() in line.lower():    
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
                    if int(linesplit[3].split('.')[0]) < 13 and varcol == 6:
                        data_array[linesplit[1]].append(float(linesplit[3].split('.')[1]))
                        
                    elif int(linesplit[3].split('.')[0]) < 13 and varcol != 6:
                        data_array[linesplit[1]].append(float(linesplit[varcol-1]))
                        
                    elif int(linesplit[3].split('.')[0]) not in data_array['Years']:
                        data_array['Years'].append(int(linesplit[3].split('.')[0]))
                #except:
                #    pass;
    
    #if varbool == 0:
    #    print('Error: variable ' + var + ' was NOT found in File: ' + tfile)
    #else:               
    #output_data[var] = data_array
    return data_array

#%%
def GetWaterRigthHRU(wrtfile, model_path, output_vars, sim_num):
    
    wrdict = dict()
    wrsrc = dict()
    temp_sum = 0
    with open(wrtfile,'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if len(linesplit) > 0 and int(linesplit[0]) != 999:
                wrdict[int(linesplit[0])] = int(linesplit[2])
                wrsrc[int(linesplit[0])] = int(linesplit[1])
                temp_sum = temp_sum + int(linesplit[2])
    search.close()
    
    hruwr = dict()
    with open(model_path + 'Scenarios/Default/TxtInOut/hruwr.dat','rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if len(linesplit) > 0:
                #temp_dict[int(linesplit[1])] = wrdict[int(linesplit[3])]
                 hruwr[int(linesplit[3])] = int(linesplit[1])
    search.close()

    output_vars_data = dict()
    #for i in range(num_sim):
    scenario = np.random.rand(len(wrdict))
    scenario  = scenario/np.sum(scenario)
    
    twrfile = open(model_path + 'Scenarios/Default/TxtInOut/watrgt.dat','w')
    # (i4,3x,i4,3x,f4.0,3x,i4,3x,i4)
    with open(wrtfile,'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            
            if len(linesplit) > 0 and int(linesplit[0]) != 999:
                
                str_lendiff = abs(4 - len(linesplit[0]))
                newline = ' ' * str_lendiff + linesplit[0]
                
                str_lendiff = abs(4 - len(linesplit[1]))
                newline = newline + '   ' + ' ' * str_lendiff + linesplit[1]
                
                #temp_wr = int(round(wrdict[int(linesplit[0])]*scenario[int(linesplit[0])-1]))
                if sim_num == 0:
                    str_lendiff = abs(4 - len(linesplit[2]))
                    newline = newline + '   ' + ' ' * str_lendiff + linesplit[2]
                    
                else:
                    temp_wr = int(round(temp_sum*scenario[int(linesplit[0])-1]))
                    wrdict[int(linesplit[0])] = temp_wr
                    str_lendiff = abs(4 - len(str(temp_wr)))
                    newline = newline + '   ' + ' ' * str_lendiff + str(temp_wr)
                
                str_lendiff = abs(4 - len(linesplit[3]))
                newline = newline + '   ' + ' ' * str_lendiff + linesplit[3]
                
                str_lendiff = abs(4 - len(linesplit[4]))
                newline = newline + '   ' + ' ' * str_lendiff + linesplit[4]
                
                twrfile.write(newline + '\n')
                
            elif int(linesplit[0]) == 999:
                twrfile.write(line)
                
    search.close()
    twrfile.close()
        
    run_SWAT(model_path,'swat_debug32.exe')
    
    for outfile in output_vars:
        tfile = model_path + 'Scenarios/Default/TxtInOut/' + output_vars[outfile]['File']
        if tfile[len(tfile)-3:len(tfile)] == 'hru':
            for varkey in output_vars[outfile]['Vars'].keys():
                data_array, hru_sub = Get_output_hru(tfile, varkey, output_vars[outfile]['Vars'][varkey])
                output_vars_data[varkey] = data_array
                
        elif tfile[len(tfile)-3:len(tfile)] == 'sub':
            for varkey in output_vars[outfile]['Vars'].keys():
                data_array = Get_output_sub(tfile, varkey, output_vars[outfile]['Vars'][varkey])
                output_vars_data[varkey] = data_array
        
        elif tfile[len(tfile)-3:len(tfile)] == 'rch':
            for varkey in output_vars[outfile]['Vars'].keys():
                output_vars_data[varkey] = Get_output_rch(tfile, varkey, output_vars[outfile]['Vars'][varkey])

        elif tfile[len(tfile)-3:len(tfile)] == 'wql':
            for varkey in output_vars[outfile]['Vars'].keys():
                output_vars_data[varkey] = Get_output_wql(tfile, varkey, output_vars[outfile]['Vars'][varkey])

        elif tfile[len(tfile)-3:len(tfile)] == 'std':
            table = output_vars[outfile]['Vars']['Table']
            for varkey in output_vars[outfile]['Vars'].keys():
                if varkey.lower() != 'table':
                    output_vars_data[varkey] = Get_output_std(tfile, table, varkey, output_vars[outfile]['Vars'][varkey])
        
         
    return wrdict, wrsrc, hruwr, output_vars_data

#%%
def run_SWAT(model_path, swat_exe):
    cwdir = os.getcwd()
    os.chdir(model_path + 'Scenarios/Default/TxtInOut')
    exitflag = subprocess.check_call([swat_exe])
    if exitflag == 0:
        print "Successful SWAT run"
    else:
        print exitflag
    os.chdir(cwdir)
    
#%%


def FindVarIds(model_path):
    datpath = model_path + 'Scenarios/Default/TxtInOut/irr.dat'
    temp_dict = dict()
    with open(datpath, 'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [l for l in linesplit if len(l) >0]
            temp_dict[int(linesplit[0])] = linesplit[1]
    search.close()
    
    return temp_dict

def FindCropName(model_path):
    db_path = model_path + 'QSWATRef2012.mdb'
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
        
    return cropdict
    
def HRU_SUBDict(output_vars_data, cropnames, wrsrc, hruwr, irr_dict):
    
    hru_sub = dict()
    
    for hrui in output_vars_data['SUB'].keys():
        if output_vars_data['SUB'][hrui][0] not in hru_sub.keys() and hrui is not 'Type' and hrui is not 'Years':
            hru_sub[int(output_vars_data['SUB'][hrui][0])] = []
            
        if hrui is not 'Type' and hrui is not 'Years':
            hru_sub[int(output_vars_data['SUB'][hrui][0])].append(hrui)
           
    temp_all = dict()
    temp_basin = dict()
    
    if 'LULC' in output_vars_data.keys() and 'AREAkm2' in output_vars_data.keys():
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()

            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cropn.islower():
                    cropn = 'AGRL'
                if cropn not in temp_dict[hruwr[hrui]]:
                    temp_dict[hruwr[hrui]][cropn] = dict()
                    temp_dict[hruwr[hrui]][cropn]['Name'] = cropnames[cropn]
                    
#                    temp_dict[hruwr[hrui]][cropn]['Data'] = 0
                    temp_dict[hruwr[hrui]][cropn]['Data'] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[hruwr[hrui]][cropn]['Data'][i+1] = 0
                if cmons <= 12:
                    temp_dict[hruwr[hrui]][cropn]['Data'][cyear] =  temp_dict[hruwr[hrui]][cropn]['Data'][cyear] + round(output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                    
        temp_all['Planted crops (ha)'] = temp_dict
        temp_all['Planted crops (ha)']['Description'] = 'Total area of planted crops in sub-basin (ha).'            
        
        
    if 'LULC' in output_vars_data.keys() and 'YLDt' in output_vars_data.keys():
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cropn.islower():
                    cropn = 'AGRL'
                if cropn not in temp_dict[hruwr[hrui]]:
                    temp_dict[hruwr[hrui]][cropn] = dict()
                    temp_dict[hruwr[hrui]][cropn]['Name'] = cropnames[cropn]
                    
                    temp_dict[hruwr[hrui]][cropn]['Data'] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[hruwr[hrui]][cropn]['Data'][i+1] = 0
                
                if cmons <= 12:
                    temp_dict[hruwr[hrui]][cropn]['Data'][cyear] =  round(temp_dict[hruwr[hrui]][cropn]['Data'][cyear],2) + round(output_vars_data['YLDt'][str(hrui)][yieldc]*907.185*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1


        temp_all['Crop yield (kg)'] = temp_dict
        temp_all['Crop yield (kg)']['Description'] = 'Total yield of planted crops in sub-basin (kg).'


    if 'LULC' in output_vars_data.keys() and 'NAUTO' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_dict[hruwr[hrui]][cyear] =  round(temp_dict[hruwr[hrui]][cyear],2) + round(output_vars_data['NAUTO'][str(hrui)][yieldc]*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['N fertilizer (kg N)'] = temp_dict
        temp_all['N fertilizer (kg N)']['Description'] = 'Amount of N fertilizer applied automatically in sub-basin (kg N).'
        

    if 'LULC' in output_vars_data.keys() and 'PAUTO' in output_vars_data.keys():
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_dict[hruwr[hrui]][cyear] =  round(temp_dict[hruwr[hrui]][cyear],2) + round(output_vars_data['PAUTO'][str(hrui)][yieldc]*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['P fertilizer (kg N)'] = temp_dict
        temp_all['P fertilizer (kg N)']['Description'] = 'Amount of P fertilizer applied automatically in sub-basin (kg N).'
        
        
    if 'LULC' in output_vars_data.keys() and 'IRRmm' in output_vars_data.keys():
        
        uwrsrc = []
        for src in wrsrc.keys():
            uwrsrc.append(wrsrc[src])
            
        uwrsrc = np.unique(uwrsrc)
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            for uwr in uwrsrc:
                if uwr not in temp_dict[hruwr[hrui]].keys():
                    temp_dict[hruwr[hrui]][uwr] = dict()
                    temp_dict[hruwr[hrui]][uwr]['Name'] = irr_dict[uwr]
                    temp_dict[hruwr[hrui]][uwr]['Data'] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[hruwr[hrui]][uwr]['Data'][i+1] = 0
            
            cmons = 1
            cyear = 1
            counter = 0
            for irrsrc in output_vars_data['IRRmm'][str(hrui)]:
                if hruwr[hrui] != 999 and cmons <= 12:
                    temp_val = round(output_vars_data['IRRmm'][str(hrui)][counter]*0.001* output_vars_data['AREAkm2'][str(hrui)][0]*1000000.0, 2)
                    temp_val = temp_val * (35.3147 / 43560.)
                    temp_dict[hruwr[hrui]][wrsrc[hruwr[hrui]]]['Data'][cyear] =  round(temp_dict[hruwr[hrui]][wrsrc[hruwr[hrui]]]['Data'][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
    
                counter = counter + 1

        
        temp_all['Irrigation (acre-ft)'] = temp_dict
        temp_all['Irrigation (acre-ft)']['Description'] = 'Total irrigation volume applied automatically in sub-basin (acre-ft)'

   
    if 'GW_RCHGmm' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_val = round(output_vars_data['GW_RCHGmm'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0*10.0, 2)
                    temp_val = temp_val * 35.3147 * (1. / 43560.)
                    temp_dict[hruwr[hrui]][cyear] =  round(temp_dict[hruwr[hrui]][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['Groundwater Recharge (acre-ft)'] = temp_dict
        temp_all['Groundwater Recharge (acre-ft)']['Description'] = 'Amount of water entering both aquifers (acre-ft).'
        
    if 'NSURQ' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_val = round(output_vars_data['NSURQ'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                    temp_dict[hruwr[hrui]][cyear] =  round(temp_dict[hruwr[hrui]][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['Surface runoff Nitrate (kg N)'] = temp_dict
        temp_all['Surface runoff Nitrate (kg N)']['Description'] = 'NO3 contributed by HRU in surface runoff to reach (kg N).'
    
    if 'NLATQ' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_val = round(output_vars_data['NLATQ'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                    temp_dict[hruwr[hrui]][cyear] =  round(temp_dict[hruwr[hrui]][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['Lateral flow Nitrate (kg N)'] = temp_dict
        temp_all['Lateral flow Nitrate (kg N)']['Description'] = 'NO3 contributed by HRU in lateral flow to reach (kg N)'
        
    if 'NO3GW' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_val = round(output_vars_data['NO3GW'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                    temp_dict[hruwr[hrui]][cyear] =  round(temp_dict[hruwr[hrui]][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
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

wr_path = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\Sensitivity_SWAT12\watrgt.dat'
    
output_vars_file =  'C:\Users\sammy\Documents\GitHub\InterACTWEL\data\Sensitivity_SWAT12\OutputVars_Arjan.txt'
output_vars = GetOutputVars(output_vars_file)

iter_dir = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\Test_Nick'

csv_file = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\Arjan_Data_9.csv'
filein = open(csv_file,'w')

num_sim = 1
for i in range(9,10):
    
    model_path = iter_dir.replace('\\','/') + '/ITER_' + str(i) + '/'
    cropnames = FindCropName(model_path)
    irr_dict = {0: 'No irrigation',1: 'Surface water', 3: 'Groundwater', 5: 'Columbia River'}
    
    for ii in range(0,11):
        if ii == 0:
            print 'ITER_' + str(i) + ' - ADD: BASE'
        else:
            print 'ITER_' + str(i) + ' - ADD: ' + str(ii) 
        
        wrdict, wrsrc, hruwr, output_vars_data = GetWaterRigthHRU(wr_path, model_path, output_vars, ii)
        
        
        temp_dict = dict()
        #temp_dict['REACH'] = ReachDict(output_vars_data)
        temp_all, temp_basin = HRU_SUBDict(output_vars_data, cropnames, wrsrc, hruwr, irr_dict)
       
        ucrop = []
        for hrui in output_vars_data['LULC'].keys():
            if hrui is not 'Type' and hrui is not 'Years':
                for cropn in output_vars_data['LULC'][hrui]:
                    if cropn.islower():
                        cropn = 'AGRL'
                    if cropn not in ucrop:
                        ucrop.append(cropn)
        
        if num_sim == 1:
            atxt = ''
            for u in ucrop:
                atxt = atxt + str(cropnames[u]) + ','
            filein.write(atxt + '\n')
        
        yr = 1
        for iy in output_vars_data['LULC']['Years']:                
            for wr in wrdict.keys():
                if ii == 0:
                    temptxt = 'BASE,' + str(i) + ',' + str(wr) + ',' + str(wrdict[wr]) + ',' + str(iy) + ','
                else:
                    temptxt = str(num_sim) + ',' + str(i) + ',' + str(wr) + ',' + str(wrdict[wr]) + ',' + str(iy) + ','
                
                for uc in ucrop:
                    if uc in temp_all['Planted crops (ha)'][wr].keys():
                        temptxt = temptxt + str(temp_all['Planted crops (ha)'][wr][uc]['Data'][yr]) + ','
                    else:
                        temptxt = temptxt + str(0.0) + ','
                        
                for uc in ucrop:
                    if uc in temp_all['Crop yield (kg)'][wr].keys():
                        temptxt = temptxt + str(temp_all['Crop yield (kg)'][wr][uc]['Data'][yr]) + ','
                    else:
                        temptxt = temptxt + str(0.0) + ','
                
                for ir in irr_dict.keys():
                    if ir in temp_all['Irrigation (acre-ft)'][wr].keys():
                        temptxt = temptxt + str(temp_all['Irrigation (acre-ft)'][wr][ir]['Data'][yr]) + ','
                    else:
                        temptxt = temptxt + str(0.0) + ','
                    
                temptxt = temptxt + str(temp_all['N fertilizer (kg N)'][wr][yr]) + ',' + str(temp_all['P fertilizer (kg N)'][wr][yr]) + ','
                temptxt = temptxt + str(temp_all['Groundwater Recharge (acre-ft)'][wr][yr]) + ',' + str(temp_all['Surface runoff Nitrate (kg N)'][wr][yr]) + ',' + str(temp_all['Lateral flow Nitrate (kg N)'][wr][yr]) + ',' + str(temp_all['Groundwater Nitrate (kg N)'][wr][yr])
                
                filein.write(temptxt + '\n')
            yr = yr + 1
        num_sim = num_sim + 1

filein.close()
    

    