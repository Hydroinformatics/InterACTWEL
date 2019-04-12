# -*- coding: utf-8 -*-

import os, re, zipfile, argparse, subprocess, shutil
#import numpy as np
#
##%% Unzip user SWAT model and run baseline scenario
#def UnzipModel(path,pathuzip):
#    folderpath = pathuzip + '/Default'
#    if os.path.isdir(folderpath):
#        shutil.rmtree(folderpath)
#        
#    with zipfile.ZipFile(path, "r") as z:
#        z.extractall(pathuzip)
#        os.chdir(pathuzip+'/Default/TxtInOut/')
#    exitflag = subprocess.check_call(['swatmodel_64rel.exe'])
#    print exitflag
#    
#    
##%%
#if __name__ == '__main__':
#    
###%% Parse Path to Zip file, Uzip and run SWAT Baseline model
##    parser = argparse.ArgumentParser(description='Optimization File')
##    parser.add_argument('path', metavar='-p', type=str, nargs='+',
##                    help='Path to zip file of SWAT baseline model')
##    args = parser.parse_args()
##
##    print args.path[0]
##    print args.path[1]
##     
#    #path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/flow8gw/TxtInOut/'
#    #path = 'Z:/Projects/INFEWS/Modeling/TestProblem/Model/Scenarios/Default.zip'
#    pathuzip = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_Model'
#    UnzipModel(path,pathuzip)

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
new_op_file = 'all_additional_management.sch'

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

Lines_Dict[oper_name] = temp_lines[:-1]           
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
new_file = open(add_op_path + '/' + new_op_file,'w')
bool_str = ['n','y']

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
                            print cp + '_' + temp_op_name
                            crop_op_bool = 1
                        elif cp != 'alfa' and ops[0] != 'a':
                            temp_op_name = bool_str[irr] + 'i_' + bool_str[till] + 't_' + bool_str[fert] + 'f'
                            print cp + '_' + temp_op_name
                            crop_op_bool = 1
                            
                        #if crop_op_bool == 1 and cp != 'alfa':
                        if crop_op_bool == 1:
                            for frt in fertilizer.keys():
                                if Oper_Ids[ops][1] == 1:
                                    frt_opt_id = [i for i, s in enumerate(fertilizer.keys()) if frt in s]
                                    for frtv in range(fertilizer[frt]['min'],fertilizer[frt]['max']+10,10):
                                        for tl in tillage:
                                            if Oper_Ids[ops][2] == 1:
                                                till_opt_id = [i for i, s in enumerate(tillage) if tl in s]
                                                for lis in range(len(Lines_Dict[ops])):
                                                    temp_line = Lines_Dict[ops][lis]
                                                    if lis == 0:
                                                        name_op = cp + '_' + str(frt_opt_id[0]) + '_' + str(frtv) + '_' + str(till_opt_id[0])
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
                                                        
                                                    new_file.write(temp_line + '\n')
                                        
                                            else:
                                                for lis in range(len(Lines_Dict[ops])):
                                                    temp_line = Lines_Dict[ops][lis]
                                                    if lis == 0:
                                                        name_op = cp + '_' + str(frt_opt_id[0]) + '_' + str(frtv) + '_null'
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
                                                    
                                                    new_file.write(temp_line + '\n')
                                                    
#                        elif crop_op_bool == 1 and cp == 'alfa':
#                            for frt in fertilizer.keys():
#                                if Oper_Ids[ops][1] == 1:
#                                    frt_opt_id = [i for i, s in enumerate(fertilizer.keys()) if frt in s]
#                                    for frtv in range(fertilizer[frt]['min'],fertilizer[frt]['max']+10,10):
#                                        for tl in tillage:
#                                            if Oper_Ids[ops][2] == 1:
#                                                till_opt_id = [i for i, s in enumerate(tillage) if tl in s]
#                                                for lis in range(len(Lines_Dict[ops])):
#                                                    temp_line = Lines_Dict[ops][lis]
#                                                    if lis == 0:
#                                                        name_op = cp + '_' + str(frt_opt_id[0]) + '_' + str(frtv) + '_' + str(till_opt_id[0])
#                                                        #temp_line = temp_line.replace(ops,name_op)
#                                                        temp_line = AdjustNameLen(temp_line,ops,name_op)
#                                                    
#                                                    if temp_line.find('fert') > 0:
#                                                        #temp_line = temp_line.replace('elem-n',frt)
#                                                        temp_line = AdjustOpsLen(temp_line,'elem-n',frt)
#                                                        new_fert_val = str(frtv) + '.00000'
#                                                        temp_line = temp_line.replace('30.00000',new_fert_val)
#                                                        
#                                                    if temp_line.find('till') > 0:
#                                                        #temp_line = temp_line.replace('fldcult',tl)
#                                                        temp_line = AdjustOpsLen(temp_line,'fldcult',tl)
#                                                        
##                                                            if temp_line.find('plnt') > 0:
##                                                                temp_line = temp_line.replace('agrc',cp)
#                                                        
#                                                    if temp_line.find('hvkl') > 0:
#                                                        temp_line = temp_line.replace('agrc',cp)
#                                                        temp_line = AdjustOpsLen(temp_line,'null',crops[cp]['op_data2'])
#                                                        #temp_line = temp_line.replace('null',crops[cp]['op_data2'])
#                                                        
#                                                    new_file.write(temp_line + '\n')
#                                        
#                                            else:
#                                                for lis in range(len(Lines_Dict[ops])):
#                                                    temp_line = Lines_Dict[ops][lis]
#                                                    if lis == 0:
#                                                        name_op = cp + '_' + str(frt_opt_id[0]) + '_' + str(frtv) + '_null'
#                                                        #temp_line = temp_line.replace(ops,name_op)
#                                                        temp_line = AdjustNameLen(temp_line,ops,name_op)
#                                                    
#                                                    if temp_line.find('fert') > 0:
#                                                        #temp_line = temp_line.replace('elem-n',frt)
#                                                        temp_line = AdjustOpsLen(temp_line,'elem-n',frt)
#                                                        new_fert_val = str(frtv) + '.00000'
#                                                        temp_line = temp_line.replace('30.00000',new_fert_val)
#                                                    
##                                                            if temp_line.find('plnt') > 0:
##                                                                temp_line = temp_line.replace('agrc',cp)
#                                                        
#                                                    if temp_line.find('hvkl') > 0:
#                                                        temp_line = temp_line.replace('agrc',cp)
#                                                        temp_line = AdjustOpsLen(temp_line,'null',crops[cp]['op_data2'])
#                                                        #temp_line = temp_line.replace('null',crops[cp]['op_data2'])
#                                                    
#                                                    new_file.write(temp_line + '\n')
                                    
                                    
                                            
new_file.close()
