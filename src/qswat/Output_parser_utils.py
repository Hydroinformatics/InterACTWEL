# -*- coding: utf-8 -*-

import os, shutil, sys, re, subprocess, pyodbc
import numpy as np
import csv, json
import random 

#%%
def FindString(startstr, endstr, line):
    
    temp_id_a = line.find(startstr) 
    temp_id_b = line.find(endstr)
    tempstr = line[temp_id_a+1:temp_id_b]
    
    return tempstr

#%%
class SWAT_Parser():
    
    def __init__(self, outputs_path, input_file):
        
        self.outputs_path = outputs_path
        self.input_file = input_file
        
        self.output_vars = self.GetOutputVars()
        
    ##########################################
    def GetOutputVars(self):
        
        output_varsb = dict()
        line_bool = 0
        with open(self.input_file,'rb') as search:
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

    ##########################################
    def GetOutputData(self, iter_array = None):
        
        if iter_array is None:
            output_files = os.listdir(self.outputs_path)
            iter_array = []
            for ifile in output_files:
                if str(ifile.rsplit('_')[-1].split('.')[0].lower()) != 'base':
                    if int(ifile.rsplit('_')[-1].split('.')[0]) not in iter_array:
                        iter_array.append(int(ifile.rsplit('_')[-1].split('.')[0]))
            
        iter_array.append(-1)
        iter_array.sort()

        self.output_vars_data = dict()
        for outfile in self.output_vars:
            for itern in iter_array:
                if itern < 0:
                    fid = 'BASE'
                else:
                    fid = itern
                    
                tfile = self.outputs_path + '/' + os.path.splitext(self.output_vars[outfile]['File'])[0] + '_' + str(fid) + os.path.splitext(self.output_vars[outfile]['File'])[1]
                print 'Reading ' + os.path.basename(tfile)
                
                if tfile[len(tfile)-3:len(tfile)] == 'hru':
                    if 'hru' not in self.output_vars_data.keys():
                        self.output_vars_data['hru'] = dict()
                    if str(fid) not in self.output_vars_data['hru'].keys():
                        self.output_vars_data['hru'][str(fid)] = dict()
                    
                    #self.output_vars_data['hru'][str(fid)] = self.Get_output_hru2(tfile, self.output_vars[outfile]['Vars'])
                        
                    for varkey in self.output_vars[outfile]['Vars'].keys():
                        data_array, hru_sub = self.Get_output_hru(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])
                        self.output_vars_data['hru'][str(fid)][varkey] = data_array
                        
                elif tfile[len(tfile)-3:len(tfile)] == 'sub':
                    if 'sub' not in self.output_vars_data.keys():
                        self.output_vars_data['sub'] = dict()
                    if str(fid) not in self.output_vars_data['sub'].keys():
                        self.output_vars_data['sub'][str(fid)] = dict()
                        
                    for varkey in self.output_vars[outfile]['Vars'].keys():
                        data_array = self.Get_output_sub(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])
                        self.output_vars_data['sub'][str(fid)][varkey] = data_array
                
                elif tfile[len(tfile)-3:len(tfile)] == 'rch':
                    if 'rch' not in self.output_vars_data.keys():
                        self.output_vars_data['rch'] = dict()
                    if str(fid) not in self.output_vars_data['rch'].keys():
                        self.output_vars_data['rch'][str(fid)] = dict()
                        
                    for varkey in self.output_vars[outfile]['Vars'].keys():
                        self.output_vars_data['rch'][str(fid)][varkey] = self.Get_output_rch(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])
        
                elif tfile[len(tfile)-3:len(tfile)] == 'wql':
                    if 'wql' not in self.output_vars_data.keys():
                        self.output_vars_data['wql'] = dict()
                    if str(fid) not in self.output_vars_data['wql'].keys():
                        self.output_vars_data['wql'][str(fid)] = dict()
                        
                    for varkey in self.output_vars[outfile]['Vars'].keys():
                        self.output_vars_data['wql'][str(fid)][varkey] = self.Get_output_wql(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])
                
                elif 'wrdata' in tfile:
                    if 'wrs' not in self.output_vars_data.keys():
                        self.output_vars_data['wrs'] = dict()
                    if str(fid) not in self.output_vars_data['wrs'].keys():
                        self.output_vars_data['wrs'][str(fid)] = dict()
                        
                    for varkey in self.output_vars[outfile]['Vars'].keys():
                        self.output_vars_data['wrs'][str(fid)][varkey] = self.Get_output_wrs(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])

                elif 'hru_wrt' in tfile:
                    if 'hru_wrs' not in self.output_vars_data.keys():
                        self.output_vars_data['hru_wrs'] = dict()
                    if str(fid) not in self.output_vars_data['hru_wrs'].keys():
                        self.output_vars_data['hru_wrs'][str(fid)] = dict()
                        
                    for varkey in self.output_vars[outfile]['Vars'].keys():
                        self.output_vars_data['hru_wrs'][str(fid)][varkey] = self.Get_output_hru_wrs(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])
        
                elif tfile[len(tfile)-3:len(tfile)] == 'std':
                    table = self.output_vars[outfile]['Vars']['Table']
                    if 'std' not in self.output_vars_data.keys():
                        self.output_vars_data['std'] = dict()
                    if str(fid) not in self.output_vars_data['std'].keys():
                        self.output_vars_data['std'][str(fid)] = dict()
                        
                    for varkey in self.output_vars[outfile]['Vars'].keys():
                        if varkey.lower() != 'table':
                            self.output_vars_data['std'][str(fid)][varkey] = self.Get_output_std(tfile, table, varkey, self.output_vars[outfile]['Vars'][varkey])
                        
        return
    
    #####################################     
    def Get_output_rch(self, tfile, var, varcol):
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
                            
                            
        return data_array

    ##############################    
    def Get_output_hru2(self, tfile, varlib):
        
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
    
                    for var in varlib.keys():
                        if len(linesplit[5].split('.')) < 3: # NEEDS to be chceck the HRU file is not displaying a month. ERROR IN SWAT
                            #if int(linesplit[5].split('.')[0]) < 13 and varcol == 6:
                            #if int(linesplit[5].split('.')[0]) > 1900 and varcol == 6:
                            if varlib[var] == 6:
                                if var.lower() == 'mon':
                                    data_array[linesplit[1]].append(int(linesplit[5].split('.')[0]))
                                else:
                                    data_array[linesplit[1]].append(float('0.'+ linesplit[5].split('.')[1]))
                                
                            #elif int(linesplit[5].split('.')[0]) < 13 and varcol != 6: # monthly output
                            #elif int(linesplit[5].split('.')[0]) > 1900 and varcol != 6:
                            elif varlib[var] != 6:
                                if varlib[var] == 1:
                                    data_array[linesplit[1]].append(linesplit[varlib[var]-1])
                                else:
                                    data_array[linesplit[1]].append(float(linesplit[varlib[var]-1]))
                                
                            if int(linesplit[5].split('.')[0]) not in data_array['Years']:
                                data_array['Years'].append(int(linesplit[5].split('.')[0]))

        return data_array, hru_sub
    
    ##############################    
    def Get_output_hru(self, tfile, var, varcol):
        
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
                        #if int(linesplit[5].split('.')[0]) > 1900 and varcol == 6:
                        if varcol == 6:
                            if var.lower() == 'mon':
                                data_array[linesplit[1]].append(int(linesplit[5].split('.')[0]))
                            else:
                                data_array[linesplit[1]].append(float('0.'+ linesplit[5].split('.')[1]))
                            
                        #elif int(linesplit[5].split('.')[0]) < 13 and varcol != 6: # monthly output
                        #elif int(linesplit[5].split('.')[0]) > 1900 and varcol != 6:
                        elif varcol != 6:
                            if varcol == 1:
                                data_array[linesplit[1]].append(linesplit[varcol-1])
                            else:
                                data_array[linesplit[1]].append(float(linesplit[varcol-1]))
                            
                        if int(linesplit[5].split('.')[0]) not in data_array['Years']:
                            data_array['Years'].append(int(linesplit[5].split('.')[0]))

        return data_array, hru_sub

    ###########################        
    def Get_output_sub(self, tfile, var, varcol):
        
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
                        #if int(linesplit[3].split('.')[0]) < 13 and varcol == 4:
                        #if int(linesplit[3].split('.')[0]) > 1900 and varcol == 4:
                        if varcol == 4:
                            if var.lower() == 'mon':
                                data_array[linesplit[1]].append(int(linesplit[3].split('.')[0]))
                            else:    
                                data_array[linesplit[1]].append(float('0.'+ linesplit[3].split('.')[1]))
                            
                        #elif int(linesplit[3].split('.')[0]) < 13 and varcol != 4:
                        #elif int(linesplit[3].split('.')[0]) > 1900 and varcol != 4:
                        elif varcol != 4:
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

    ########################### 
    def Get_output_std(self, tfile, table, var, varcol):
    
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
                        tmon = -1
                    
                    if varbool == 1:
                        linesplit = re.split('\s',line)
                        linesplit = [e for e in linesplit if e != '']
                        
                        if len(linesplit) > 1 and linesplit[0] != 'SWAT':
                            if len(linesplit[0]) == 4:
                                data_array['Years'].append(int(linesplit[0]))
                                data_array['Data'].append(float(linesplit[varcol-1]))
                            #varbool = 0
                        elif len(linesplit) < 1 and tmon == '':
                            varbool = 0
                            
                        if len(linesplit) > 0:
                            tmon = linesplit[0]
                            
                    if 'IRRIGATION - AVE. ANNUAL' in line:
                        break
        
        return data_array
    
    ########################### 
    def Get_output_wrs(self, tfile, var, varcol):
        
        data_array = dict()
        data_array['Years'] = []
        data_array['Type'] = 'WRS'
        varbool = 0
        with open(tfile) as search:
            for line in search:
                if 'WR_ID'.lower() in line.lower():    
                    varbool = 1
                    
                elif varbool == 1:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    
                    if linesplit[2] not in data_array.keys() and int(linesplit[2]) > 0:
                        data_array[linesplit[2]] = dict()
                        
                    if int(linesplit[2]) > 0:
                        if int(linesplit[0]) not in data_array[linesplit[2]].keys():
                            data_array[linesplit[2]][int(linesplit[0])] = []
                            
                    if int(linesplit[2]) > 0:
                        data_array[linesplit[2]][int(linesplit[0])].append(float(linesplit[varcol-1]))
                    
                    #if int(linesplit[0]) not in data_array['Years']:
                    #    data_array['Years'].append(int(linesplit[0]))
                                                        
        return data_array
    
    ########################### 
    def Get_output_hru_wrs(self, tfile, var, varcol):
        
        data_array = dict()
        data_array['Years'] = []
        data_array['Type'] = 'HRU_WRS'
        varbool = 0
        with open(tfile) as search:
            for line in search:
                if 'WRID'.lower() in line.lower():    
                    varbool = 1
                    
                elif varbool == 1:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    
                    if linesplit[2] not in data_array.keys():
                        data_array[linesplit[2]] = dict()
                        
                    if int(linesplit[5]) not in data_array[linesplit[2]].keys():
                        data_array[linesplit[2]][int(linesplit[5])] = []
                            
                    data_array[linesplit[2]][int(linesplit[5])].append(float(linesplit[varcol-1]))
                        
                                                        
        return data_array
        
#%%

class JSON_SGformatter():
    def __init__(self):
        self.irr_dict = {0: 'No irrigation',1: 'Surface water', 3: 'Groundwater', 5: 'Columbia River'}
        
    def barGraph(self, data_dict, varname = None, title = None, descrp = None, yaxis = None, jsonpath = None):
        
        temp_dict = dict()
        temp_dict['Data Type'] = title
        temp_dict['Description'] = descrp
        temp_dict['y-axis'] = descrp
        temp_dict['Legend'] = []
        #temp_dict['Adaptation_Plans'] = dict()
        
        plans_dict = dict()
        for dkey in data_dict:
            plans_dict['Adaptation Plan ' + dkey] = dict()
            
            if 'Data' in data_dict[dkey][varname].keys():
                plans_dict['Adaptation Plan ' + dkey]['Data'] = dict()
                counter = 1
                for i in data_dict[dkey][varname]['Data']:
                    temp_str = 'Adaptation Plan ' + str(dkey)
                    if dkey.lower() == 'base':
                        plans_dict[temp_str]['Data'][counter] = data_dict[dkey][varname]['Data'][counter-1]
                    else:
                        tempv = round(data_dict[dkey][varname]['Data'][counter-1]*random.uniform(0.6, 1.0),2)
                        plans_dict[temp_str]['Data'][counter] = tempv
                    
                    if str(data_dict[dkey][varname]['Years'][counter-1]) not in temp_dict['Legend']:
                        temp_dict['Legend'].append(str(data_dict[dkey][varname]['Years'][counter-1]))
                    counter = counter + 1
                    
            elif data_dict[dkey][varname]['Type'] == 'SUB':
                
                for subid in data_dict[dkey][varname].keys():
                    if subid is not 'Type' and subid is not 'Years':
                        plans_dict['Adaptation Plan ' + dkey]['Subbasin ' + str(subid)] = dict()
                        plans_dict['Adaptation Plan ' + dkey]['Subbasin ' + str(subid)]['Data'] = dict()
                        counter = 1
                        for i in data_dict[dkey][varname][subid]:
                            temp_str = 'Adaptation Plan ' + str(dkey)
                            if dkey.lower() == 'base':
                                plans_dict[temp_str]['Subbasin ' + str(subid)]['Data'][counter] = i
                            else:
                                tempv = round(i*random.uniform(0.6, 1.0),2)
                                plans_dict[temp_str]['Subbasin ' + str(subid)]['Data'][counter] = tempv
                            counter = counter + 1
                    elif subid is 'Years':
                        for i in data_dict[dkey][varname][subid]:
                            temp_dict['Legend'].append(str(i))
        
        temp_dict['Adaptation_Plans'] = plans_dict
        
        if jsonpath != None:
            with open(jsonpath, 'w') as fp:
                json.dump(temp_dict, fp)
        
        return temp_dict
        

#    def Indiv_BASIN_json(temp_basin):
#        
#        for kvars in temp_basin.keys():
#    #        #if kvars == 'Planted crops (ha)':
#    #        temp_dict = dict()
#    #        temp_dict['Description'] = temp_basin[kvars]['Description']
#    #        if 'Legend' in temp_basin[kvars].keys():
#    #            temp_dict['Legend'] = temp_basin[kvars]['Legend']
#    #        else:
#    #            temp_dict['Legend'] = temp_basin[kvars]['Data Labels']
#    #        
#    #        temp_dict['Data'] = dict()
#    #        for i in temp_basin[kvars]['Data'].keys():
#    #            temp_dict['Data'][temp_basin[kvars]['Data'][i]['Name']] = temp_basin[kvars]['Data'][i]['Data']
#                
#            txt = 'BASIN_' + kvars.replace(' ','_') + '_data.json'
#            with open(os.getcwd() + '/' + txt, 'w') as fp:
#                json.dump(temp_basin[kvars], fp)
#        return temp_dict
        
        