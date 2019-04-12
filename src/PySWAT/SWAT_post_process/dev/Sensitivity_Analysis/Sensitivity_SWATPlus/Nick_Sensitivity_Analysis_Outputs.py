# -*- coding: utf-8 -*-

import os, re
import numpy as np
from peewee import *

#%%
def Get_Rout_Ele_table(db_path):
    db = SqliteDatabase(db_path)
    db.connect()
    cursor = db.execute_sql('SELECT * FROM rout_unit_ele')
    hru_rot =[]
    for row in cursor.fetchall():
        hru_rot.append((row[0],row[2]))
        
    hru_rot = np.asarray(hru_rot)
    cursor = db.execute_sql('SELECT * FROM rout_unit_con_out')
    rot_aqucha=[]
    rot_aqucha_type=[]
    for row in cursor.fetchall(): 
        rot_aqucha.append((int(row[6]),int(row[3])))
        rot_aqucha_type.append((row[3],row[2]))
    
    rot_aqucha = np.asarray(rot_aqucha)
    rot_aqucha_type = np.asarray(rot_aqucha_type)
    hru_aqu = []
    hru_cha = []
    for i in range(len(hru_rot)):    
        temp_id = np.where(rot_aqucha[:,0] == hru_rot[i,1])
        for idt in temp_id[0]:
            
            if rot_aqucha_type[idt,1] == 'aqu':
                hru_aqu.append((hru_rot[i,0],rot_aqucha[idt,1]))
            elif rot_aqucha_type[idt,1] == 'cha':
                hru_cha.append((hru_rot[i,0],rot_aqucha[idt,1]))
            
    return hru_rot, rot_aqucha, np.asarray(hru_aqu), np.asarray(hru_cha)

#%%
def GetHRU_ACTORS(no_change_lum, new_op_path):
    
    no_change_lums = []
    with open(no_change_lum,'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [e for e in linesplit if e != '']
            no_change_lums.append(linesplit[0])
    search.close()
    
    file_path = new_op_path + '/' + 'hru-data.hru'
    hru_ids = []
    with open(file_path,'rb') as search:
        for line in search:
            if 'SWAT' not in line and 'name' not in line:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                if linesplit[5] not in no_change_lums:
                    hru_ids.append(int(linesplit[0]))
    search.close()
    
    total_area = 0
    file_path = new_op_path + '/' + 'hru.con'
    hru_counter = 0
    
    with open(file_path,'rb') as search:
            for line in search:
                if 'SWAT' not in line and 'gis' not in line:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    if int(linesplit[0]) in hru_ids:
                        total_area = total_area + float(linesplit[3])
    search.close()                    
    
    hru_counter = 0
    HRU_ACTORS = dict()
    temp_array = []
    
    with open(file_path,'rb') as search:
            for line in search:
                if 'SWAT' not in line and 'gis' not in line:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    
                    if int(linesplit[0]) in hru_ids:
                        if hru_counter == 0 :
                            temp_sum = float(linesplit[3])
                            temp_array.append(int(linesplit[0]))
                            hru_counter = hru_counter + 1
                        else:
                            if (temp_sum/total_area)*100 > 5:
                                temp_dict = dict()
                                temp_dict['HRU_IDS'] = temp_array
                                temp_dict['Area'] = temp_sum
                                temp_dict['Area_Per'] = (temp_sum/total_area)*100
                                HRU_ACTORS[hru_counter-1] = temp_dict
                                hru_counter = hru_counter + 1
                                temp_array = []
                                temp_sum = float(linesplit[3])
                                temp_array.append(int(linesplit[0]))
                            else:
                                temp_sum = temp_sum + float(linesplit[3])
                                temp_array.append(int(linesplit[0]))
                            
    search.close()
        
    return HRU_ACTORS, hru_ids, total_area, no_change_lums

#%%
def Get_Actors_Decisions(tfile):
    actors_decisions = dict()
    with open(tfile) as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [e for e in linesplit if e != '']
            decisions = re.split('_',linesplit[5])
            
            actors_decisions[linesplit[0]] = decisions[:-1]
    search.close()
    return actors_decisions

#%%
def Get_output_data(tfile,var):
    output_data = dict()
    data_array = dict()
    varbool = 0
    time_array = []
    with open(tfile) as search:
        for line in search:
            if var.lower() in line.lower():    
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                varcol = [i for i in range(0,len(linesplit)) if linesplit[i] == var]
                varbool = 1
                
            elif varbool == 1 and len(line[0:10].rstrip()) > 0:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                if linesplit[4] not in data_array.keys():
                    #data_array[linesplit[4]]['VALUES'] = []
                    data_array[linesplit[4]] = []
                    
                try:
                    data_array[linesplit[4]].append(float(linesplit[varcol[0]]))
                    if int(linesplit[4]) == 1:
                        time_array.append((linesplit[0],linesplit[1],linesplit[2],linesplit[3]))
                except:
                    pass;
    data_array['time'] = time_array
    if varbool == 0:
        print('Error: variable ' + var + ' was found in File: ' + tfile)
    else:               
        output_data[var] = data_array
    
    search.close()
    return output_data

#%%
    


path_out = 'C:/Users/sammy/Desktop/Nick_Analysis'
no_change_lum_path = 'C:/Users/sammy/Documents/Research/SWAT/QSWATplus/no_change_lums.txt'

output_vars = dict()
output_vars['rchrg'] = {'File': 'aquifer_yr.txt', 'var_col': 10}
output_vars['rchrgn'] = {'File': 'aquifer_yr.txt','var_col': 18}
output_vars['flo_out'] = {'File': 'channel_yr.txt','var_col': 9}
output_vars['orgn_in'] = {'File': 'channel_yr.txt','var_col': 15}
output_vars['YIELD'] = {'File': 'crop_yld_aa.out','var_col': 7}
output_vars['wateryld'] = {'File': 'hru_wb_yr.txt','var_col': 13}
#output_vars['frtn_kgha'] ={'File': 'plantwx_yr_hru.txt','var_col': 10}



iter_folders = [f for f in os.listdir(path_out) if 'ITER_' in f]

if len(iter_folders) > 0:
    temp_path = path_out + '/' + iter_folders[0] +'/Scenarios/Default/TxtInOut'
    HRU_ACTORS, hru_ids, total_area, no_change_lums = GetHRU_ACTORS(no_change_lum_path,temp_path)
    hru_actors = []
    for actor in HRU_ACTORS.keys():
        for hru_ids in HRU_ACTORS[actor]['HRU_IDS']:
            hru_actors.append((hru_ids,actor))
                
    hru_rot, rot_aqucha, hru_aqu, hru_cha = Get_Rout_Ele_table(path_out + '/' + iter_folders[0] + '/Willow_Test2_Sam.sqlite')
    
    ALL_outputs = dict()
    for folder in iter_folders:
        text_files = path_out + '/' + folder + '/Scenarios/Default/decisions_actors.txt'
        decision_actors = Get_Actors_Decisions(text_files)
        Outputs = dict()
        for outvar in output_vars.keys():
            text_files = [f for f in os.listdir(path_out + '/' + folder + '/Scenarios/Default/TxtInOut/') if output_vars[outvar]['File'] == f]
            if len(text_files) ==0:
                print('Error: File ' + output_vars[outvar]['File'] + ' was not found in ' + path_out + '/' + folder + '/Scenarios/Default/TxtInOut/')
            else:
                text_files = path_out + '/' + folder + '/Scenarios/Default/TxtInOut/' + text_files[0]
                output_data = Get_output_data(text_files,outvar)
                Outputs[outvar] = output_data
        
        ALL_outputs[folder] = {'Decision': decision_actors, 'Outputs': Outputs}
        
        
    #%%
    hru_actors = np.asarray(hru_actors)
    import csv
    csv_file = 'Arjan_SwatData.csv'
    with open(path_out + '/' + csv_file, mode='wb') as outputcsv:
        outputcsv_writer = csv.writer(outputcsv, delimiter = ',', quotechar = '"', quoting=csv.QUOTE_MINIMAL)
        outputcsv_writer.writerow(['Actor','HRUIDs','Crop','Fert','Fert_Value','Tillage','Yield','Water_Yield','Aqu_Rchrg','Aqu_orgn','Cha_Flout','Cha_orgn_in'])
        outputcsv_writer.writerow(['','','','','kg','','kg','mm','','','',''])
        for folder in ALL_outputs.keys():
            for hru_ids in ALL_outputs[folder]['Decision'].keys():
                crop = ALL_outputs[folder]['Decision'][hru_ids][0]
                fert = ALL_outputs[folder]['Decision'][hru_ids][1]
                fertv = ALL_outputs[folder]['Decision'][hru_ids][2]
                till = ALL_outputs[folder]['Decision'][hru_ids][3]
                actor = hru_actors[np.where(hru_actors[:,0] == int(hru_ids)),1][0]
                
                yld = ALL_outputs[folder]['Outputs']['YIELD']['YIELD'][hru_ids][0]
                wateryld = ALL_outputs[folder]['Outputs']['wateryld']['wateryld'][hru_ids][0]
                
                aqu_id = hru_aqu[np.where(hru_aqu[:,0] == int(hru_ids))[0],1]
                aqu_rchrg = ALL_outputs[folder]['Outputs']['rchrg']['rchrg'][str(aqu_id[0])][0]
                aqu_orgn = ALL_outputs[folder]['Outputs']['orgn']['orgn'][str(aqu_id[0])][0]
                
                cha_id = hru_cha[np.where(hru_cha[:,0]==int(hru_ids))[0],1]
                cha_floout = ALL_outputs[folder]['Outputs']['flo_out']['flo_out'][str(cha_id[0])][0]
                cha_orgnin = ALL_outputs[folder]['Outputs']['orgn_in']['orgn_in'][str(cha_id[0])][0]
                outputcsv_writer.writerow([actor[0],hru_ids,crop,fert,fertv,till,yld,wateryld,aqu_rchrg,aqu_orgn,cha_floout,cha_orgnin])
    
        
    outputcsv.close()    
#        
#        