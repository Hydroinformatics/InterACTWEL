# -*- coding: utf-8 -*-

import os, re, zipfile, argparse, subprocess, shutil, random
import numpy as np

#%% Unzip user SWAT model and run baseline scenario
def UnzipModel(path,pathuzip,iterc):
    folderpath = pathuzip + '/ITER_' + str(iterc) + '/'
    if os.path.isdir(folderpath):
        shutil.rmtree(folderpath)
        
    with zipfile.ZipFile(path, "r") as z:
        z.extractall(folderpath)
        #os.chdir(folderpath+'Scenarios/Default/TxtInOut')
    #exitflag = subprocess.check_call(['rev57_64rel.exe'])
    #print exitflag
    
    return folderpath +'Scenarios/Default/TxtInOut'
    

#%%

def AdjustNameLen(temp_line,old_str,new_str):
    strid = temp_line.find(old_str)
    str_lendiff = abs(len(old_str) - len(new_str) )
    
    if len(new_str) > len(old_str):
        temp_line = new_str + temp_line[((strid+len(old_str))+str_lendiff):]
    
    elif len(new_str) < len(old_str):
        temp_line = new_str + ' ' * str_lendiff + temp_line[(strid+len(old_str)):]
    
    elif len(new_str) == len(old_str):
        temp_line = temp_line.replace(old_str,new_str)
    
    return temp_line

def AdjustOpsLen(temp_line,old_str,new_str):
    strid = temp_line.find(old_str)
    str_lendiff = abs(len(old_str) - len(new_str) )
    
    if len(new_str) > len(old_str):
        temp_line = temp_line[0:(strid-str_lendiff)] + new_str + temp_line[(strid+len(old_str)):]
    
    elif len(new_str) < len(old_str):
        temp_line = temp_line[0:strid] + ' ' * str_lendiff + new_str + temp_line[(strid+len(old_str)):]
    
    elif len(new_str) == len(old_str):
        temp_line = temp_line.replace(old_str,new_str)
    
    return temp_line

#%%

def CreateNewSchFile(new_op_path):
    fertilizer = dict()
    fertilizer['elem_n'] = {'op_data2': 'broadcast', 'min': 20, 'max': 90}
    fertilizer['elem_p'] = {'op_data2': 'broadcast', 'min': 20, 'max': 90}
    fertilizer['31_13_00'] = {'op_data2': 'broadcast', 'min': 20, 'max': 90}
    fertilizer['04_08_00'] = {'op_data2': 'broadcast', 'min': 20, 'max': 90}
    
    tillage = ['fldcult','diskplow','beddhipr']
    
    crops = dict()
    crops['corn'] = {'op_data2': 'grain', 'Auto_Irr': 1, 'Till': 2, 'Fert': 2}
    crops['scrn'] = {'op_data2': 'grain', 'Auto_Irr': 1, 'Till': 2, 'Fert': 2}
    crops['onio'] = {'op_data2': 'potatoes', 'Auto_Irr': 1, 'Till': 2, 'Fert': 2}
    crops['swht'] = {'op_data2': 'grain', 'Auto_Irr': 2, 'Till': 2, 'Fert': 2}
    crops['pota'] = {'op_data2': 'potatoes', 'Auto_Irr': 1, 'Till': 2, 'Fert': 2}
    crops['alfa'] = {'op_data2': 'null', 'Auto_Irr': 2, 'Till': 2, 'Fert': 2}
    
    
    add_op_path = 'C:/Users/sammy/Documents/Research/SWAT/QSWATplus'
    add_op_file = 'additional_management.sch'
    
    #new_op_path = 'C:/Users/sammy/Desktop/Nick_Analysis/ITER_1/Scenarios/Default/TxtInOut'
    old_schfile = 'management.sch'
    
    #%%
    Lines_Dict = dict()
    op_counter = 0
    temp_lines = []
    oper_name = None
    with open(add_op_path + '/' + add_op_file,'rb') as search:
            for line in search:
                line = line.strip('\r\n')
                temp_lines.append(line)
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                if linesplit[0].count('_') > 1:
                    op_counter = op_counter + 1
                    
                    if op_counter > 1:
                        Lines_Dict[oper_name] = temp_lines[:-1]
                        new_oper = temp_lines[-1]
                        temp_lines = []
                        temp_lines.append(new_oper)
                        oper_name = linesplit[0]
                    else:
                        oper_name = linesplit[0]
    
    Lines_Dict[oper_name] = temp_lines           
    search.close()
    
    Oper_Ids = dict()
    for ops in Lines_Dict.keys():
        op_ids = re.split('_',ops)
        temp_opds_ids = []
        for oids in op_ids:
            if oids != 'a' and oids.count('y') > 0:
                temp_opds_ids.append(1)
            elif oids != 'a':
                temp_opds_ids.append(0)
        Oper_Ids[ops] = temp_opds_ids
                    
    #%%   
    source_path = new_op_path.replace('/','\\') + '\\' + old_schfile
    id_path = new_op_path.find('TxtInOut')
    destination_path = new_op_path[0:id_path].replace('/','\\') + old_schfile
     
    command = 'copy ' + source_path + ' ' + destination_path
    os.system(command)    
     
    #%%   
    destination_path = new_op_path[0:id_path] + old_schfile
    source_path = new_op_path + '/' + old_schfile
    new_file = open(source_path,'w')
    with open(destination_path,'rb') as search_sch:
            for line in search_sch:
                line = line.strip('\r\n')
                new_file.write(line + '\n')
                
    search_sch.close()
    
    #%%
    bool_str = ['n','y']
    New_OpsNames = []
    OpsNames = []
    for cp in crops.keys():
     
        for ops in Oper_Ids.keys():
            irr_id = [crops[cp]['Auto_Irr']]
            fert_id = [crops[cp]['Fert']]
            till_id = [crops[cp]['Till']]
            
            if crops[cp]['Auto_Irr'] == 2:
                irr_id = [0,1]
            if crops[cp]['Till'] == 2:
                till_id = [0,1]
            if crops[cp]['Fert'] == 2:
                fert_id = [0,1]
                
            temp_op_name = ''
            
            for irr in irr_id:
                for till in till_id:
                    for fert in fert_id:
                        crop_op_bool = 0
                        if [irr,till,fert] == Oper_Ids[ops]:
                            if cp == 'alfa' and ops[0] == 'a':
                                temp_op_name = 'a_' + bool_str[irr] + 'i_' + bool_str[till] + 't_' + bool_str[fert] + 'f'
                                #print cp + '_' + temp_op_name
                                crop_op_bool = 1
                            elif cp != 'alfa' and ops[0] != 'a':
                                temp_op_name = bool_str[irr] + 'i_' + bool_str[till] + 't_' + bool_str[fert] + 'f'
                                #print cp + '_' + temp_op_name
                                crop_op_bool = 1
                                
                            #if crop_op_bool == 1 and cp != 'alfa':
                            if crop_op_bool == 1:
                                for frt in fertilizer.keys():
                                    if Oper_Ids[ops][2] == 1:
                                        frt_opt_id = [i for i, s in enumerate(fertilizer.keys()) if frt in s]
                                        for frtv in range(fertilizer[frt]['min'],fertilizer[frt]['max']+10,10):
                                            for tl in tillage:
                                                if Oper_Ids[ops][1] == 1:
                                                    till_opt_id = [i for i, s in enumerate(tillage) if tl in s]
                                                    name_op = cp + '_' + str(frt_opt_id[0]) + '_' + str(frtv) + '_' + str(till_opt_id[0])
                                                    if name_op not in OpsNames:
                                                        for lis in range(len(Lines_Dict[ops])):
                                                            temp_line = Lines_Dict[ops][lis]
                                                            if lis == 0:
                                                                
                                                                New_OpsNames.append((cp,name_op))
                                                                OpsNames.append(name_op)
                                                                #temp_line = temp_line.replace(ops,name_op)
                                                                temp_line = AdjustNameLen(temp_line,ops,name_op)
                                                            
                                                            if temp_line.find('fert') > 0:
                                                                #temp_line = temp_line.replace('elem-n',frt)
                                                                temp_line = AdjustOpsLen(temp_line,'elem-n',frt)
                                                                new_fert_val = str(frtv) + '.00000'
                                                                temp_line = temp_line.replace('30.00000',new_fert_val)
                                                                
                                                            if temp_line.find('till') > 0:
                                                                #temp_line = temp_line.replace('fldcult',tl)
                                                                temp_line = AdjustOpsLen(temp_line,'fldcult',tl)
                                                                
                                                            if temp_line.find('plnt') > 0:
                                                                temp_line = temp_line.replace('agrc',cp)
                                                                
                                                            if temp_line.find('hvkl') > 0:
                                                                temp_line = temp_line.replace('agrc',cp)
                                                                temp_line = AdjustOpsLen(temp_line,'null',crops[cp]['op_data2'])
                                                                #temp_line = temp_line.replace('null',crops[cp]['op_data2'])
                                                            
                                                            temp_line = temp_line.rstrip()
                                                            new_file.write(temp_line + '  ' + '\n')
                                            
                                                else:
                                                    name_op = cp + '_' + str(frt_opt_id[0]) + '_' + str(frtv) + '_n'
                                                    if name_op not in OpsNames:
                                                        for lis in range(len(Lines_Dict[ops])):
                                                            temp_line = Lines_Dict[ops][lis]
                                                            if lis == 0:
                                                                
                                                                New_OpsNames.append((cp,name_op))
                                                                OpsNames.append(name_op)
                                                                #temp_line = temp_line.replace(ops,name_op)
                                                                temp_line = AdjustNameLen(temp_line,ops,name_op)
                                                            
                                                            if temp_line.find('fert') > 0:
                                                                #temp_line = temp_line.replace('elem-n',frt)
                                                                temp_line = AdjustOpsLen(temp_line,'elem-n',frt)
                                                                new_fert_val = str(frtv) + '.00000'
                                                                temp_line = temp_line.replace('30.00000',new_fert_val)
                                                            
                                                            if temp_line.find('plnt') > 0:
                                                                temp_line = temp_line.replace('agrc',cp)
                                                                
                                                            if temp_line.find('hvkl') > 0:
                                                                temp_line = temp_line.replace('agrc',cp)
                                                                temp_line = AdjustOpsLen(temp_line,'null',crops[cp]['op_data2'])
                                                                #temp_line = temp_line.replace('null',crops[cp]['op_data2'])
                                                            
                                                            temp_line = temp_line.rstrip()
                                                            new_file.write(temp_line + '  ' + '\n')
                                                        
                                    elif Oper_Ids[ops][1] == 1:
                                        till_opt_id = [i for i, s in enumerate(tillage) if tl in s]
                                        name_op = cp + '_n_n' + '_' + str(till_opt_id[0])
                                        if name_op not in OpsNames:
                                            for lis in range(len(Lines_Dict[ops])):
                                                    temp_line = Lines_Dict[ops][lis]
                                                    if lis == 0:
                                                        
                                                        New_OpsNames.append((cp,name_op))
                                                        OpsNames.append(name_op)
                                                        #temp_line = temp_line.replace(ops,name_op)
                                                        temp_line = AdjustNameLen(temp_line,ops,name_op)
                                                                
                                                    if temp_line.find('till') > 0:
                                                        #temp_line = temp_line.replace('fldcult',tl)
                                                        temp_line = AdjustOpsLen(temp_line,'fldcult',tl)
                                                                
                                                    if temp_line.find('plnt') > 0:
                                                        temp_line = temp_line.replace('agrc',cp)
                                                                
                                                    if temp_line.find('hvkl') > 0:
                                                        temp_line = temp_line.replace('agrc',cp)
                                                        temp_line = AdjustOpsLen(temp_line,'null',crops[cp]['op_data2'])
                                                        #temp_line = temp_line.replace('null',crops[cp]['op_data2'])
                                                                
                                                    temp_line = temp_line.rstrip()
                                                    new_file.write(temp_line + '  ' + '\n')   
                                                
    new_file.close()
    
    return New_OpsNames, crops

#%%
def CreateNewLumFile(new_op_path,ops_names, crops):
    plantini_file = 'plant.ini'
    base_plant = 'agrl_comm'
    
    source_path = new_op_path.replace('/','\\') + '\\' + plantini_file
    id_path = new_op_path.find('TxtInOut')
    destination_path = new_op_path[0:id_path].replace('/','\\') + plantini_file
     
    command = 'copy ' + source_path + ' ' + destination_path
    os.system(command) 
    
    destination_path = new_op_path[0:id_path] + plantini_file
    source_path = new_op_path + '/' + plantini_file
    new_file = open(source_path,'w')
    base_plant_bool = 0
    with open(destination_path,'rb') as search_lum:
            for line in search_lum:
                line = line.strip('\r\n')
                if base_plant in line:
                    base_plant_bool = 1
                    base_plant_line_a = line
                    base_plant_opts_a = re.split('\s',line)
                    base_plant_opts_a = [e for e in base_plant_opts_a if e != '']
                    
                elif base_plant_bool == 1:
                    base_plant_line = line
                    base_plant_opts = re.split('\s',line)
                    base_plant_opts = [e for e in base_plant_opts if e != '']
                    base_plant_bool = 0
                    
                new_file.write(line + '\n')
                
    search_lum.close()
    
    for crop in crops.keys():
        temp_line = AdjustNameLen(base_plant_line_a,base_plant_opts_a[0], crop +'_comm')
        new_file.write(temp_line + '\n')
        temp_line = base_plant_line.replace('agrl',crop)
        new_file.write(temp_line + '\n')
        
    new_file.close()
    
    
    
    lum_schfile = 'landuse.lum'
    #new_op_file = 'management.sch'
    base_lum = 'agrl_lum'
    
    source_path = new_op_path.replace('/','\\') + '\\' + lum_schfile
    id_path = new_op_path.find('TxtInOut')
    destination_path = new_op_path[0:id_path].replace('/','\\') + lum_schfile
     
    command = 'copy ' + source_path + ' ' + destination_path
    os.system(command) 
    
    destination_path = new_op_path[0:id_path] + lum_schfile
    source_path = new_op_path + '/' + lum_schfile
    new_file = open(source_path,'w')
    with open(destination_path,'rb') as search_lum:
            for line in search_lum:
                line = line.strip('\r\n')
                if base_lum in line:
                    base_lum_line = line
                    base_lum_opts = re.split('\s',line)
                    base_lum_opts = [e for e in base_lum_opts if e != '']
                    
                new_file.write(line + '\n')
                
    search_lum.close()
    
    for op in ops_names:
        temp_line = AdjustNameLen(base_lum_line,base_lum_opts[0],op[1]+'_lum')
        temp_line = AdjustOpsLen(temp_line,base_lum_opts[3],op[1])
        temp_line = AdjustOpsLen(temp_line,base_lum_opts[2],op[0] +'_comm')
        new_file.write(temp_line + '\n')
        
    new_file.close()
    
    return

#%%
def GetHRU_ACTORS(new_op_path):
    file_path = 'C:/Users/sammy/Documents/Research/SWAT/QSWATplus/no_change_lums.txt'
    no_change_lums = []
    with open(file_path,'rb') as search:
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
def ChangeHRU_Mgt(new_op_path, ops_names, crops, actors):
        
    naops_names = np.asarray(ops_names)
    crop_sch = []
    for cp in crops.keys():
        crop_ids = np.where(naops_names[:,0]==cp)
        crop_sch.append((ops_names[crop_ids[0][random.randint(0,len(crop_ids[0])-1)]]))
    
    remaining_ops = len(actors) - len(crop_sch)
    
    for i in range(remaining_ops):
        crop_sch.append((ops_names[random.randint(0,len(ops_names)-1)]))
    
    num_crop_sch = range(len(crop_sch))
    random.shuffle(num_crop_sch)
    
    hru_actors = []
    for actor in actors.keys():
        for hru_ids in actors[actor]['HRU_IDS']:
            hru_actors.append((hru_ids,actor,num_crop_sch[actor]))
            #hru_actors.append((hru_ids,actor,num_crop_sch[0]))
        
    hru_file = 'hru-data.hru'
    source_path = new_op_path.replace('/','\\') + '\\' + hru_file
    id_path = new_op_path.find('TxtInOut')
    destination_path = new_op_path[0:id_path].replace('/','\\') + hru_file
     
    command = 'copy ' + source_path + ' ' + destination_path
    os.system(command) 
    
    destination_path = new_op_path[0:id_path] + hru_file
    decision_path = new_op_path[0:id_path] + 'decisions_actors.txt'
    source_path = new_op_path + '/' + hru_file
    new_file = open(source_path,'w')
    decision_file = open(decision_path,'w')
    hru_actors = np.asarray(hru_actors)
    with open(destination_path,'rb') as search_hru:
            for line in search_hru:
                line = line.strip('\r\n')
                if 'SWAT' not in line and 'name' not in line:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    hru_actor_id = np.where(hru_actors[:,0] == int(linesplit[0]))
                    if len(hru_actor_id[0]) > 0:
                        temp_line = AdjustOpsLen(line, linesplit[5], crop_sch[num_crop_sch[hru_actors[hru_actor_id[0],2][0]]][1]+'_lum')
                        new_file.write(temp_line + '\n')
                        decision_file.write(temp_line + '\n')
                    else:
                        new_file.write(line + '\n')
                else:
                    new_file.write(line + '\n')  
        
    new_file.close() 
    decision_file.close() 
    return crop_sch, hru_actors
    
    
#%%
#if __name__ == '__main__':
    
##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
#    parser = argparse.ArgumentParser(description='Optimization File')
#    parser.add_argument('path', metavar='-p', type=str, nargs='+',
#                    help='Path to zip file of SWAT baseline model')
#    args = parser.parse_args()
#
#    print args.path[0]
#    print args.path[1]
#     
    #path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/flow8gw/TxtInOut/'
    #path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/Default.zip'

pathunzip = 'C:/Users/sammy/Desktop/Nick_Analysis'
path = 'C:/Users/sammy/Documents/Research/SWAT/QSWATplus/SWATplus.zip'

for sim_iter in range(100):
    new_op_path = UnzipModel(path,pathunzip,sim_iter)
    HRU_ACTORS, hru_ids, total_area, no_change_lums = GetHRU_ACTORS(new_op_path)
    New_OpsNames, crops = CreateNewSchFile(new_op_path)
    CreateNewLumFile(new_op_path,New_OpsNames,crops)
    crop_sch, hru_actors = ChangeHRU_Mgt(new_op_path, New_OpsNames, crops, HRU_ACTORS)
    
    os.chdir(new_op_path)
    exitflag = subprocess.check_call(['rev57_64rel.exe'])
    print sim_iter, exitflag

