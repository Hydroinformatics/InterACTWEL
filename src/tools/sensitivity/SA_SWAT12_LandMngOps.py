# -*- coding: utf-8 -*-
import os, re, zipfile, argparse, subprocess, shutil, random, sys, pyodbc
import numpy as np
import SA_SWAT12_utils as sautils

class LndMngOps(object):
    def __init__(self):

        self.file_ext = '.mgt'
        
        self.new_mngops_file = ''
        self.mngops_parmt_file = ''
        self.model_path = ''
        self.water_rights = None
        
        #self.num_parms = []
    
#%%    
    def FindVarIds(self, mngpar):
        datfile = self.MngParams[mngpar]['paramFile']
        
        if datfile == 'plant.dat':
            db_path = self.model_path + 'QSWATRef2012.mdb'
            conn_str = (
                r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                r'DBQ=' + db_path + ';'
                )
            cnxn = pyodbc.connect(conn_str)
            crsr = cnxn.cursor()
            
            crsr.execute('select * from crop')
            param_keys = self.MngParams[mngpar]['options'].keys()
            for row in crsr.fetchall():
                for param_options in param_keys:
                    if param_options.lower() == row[2].lower():
                        self.MngParams[mngpar]['options'][int(row[1])] = self.MngParams[mngpar]['options'][param_options]
                        del self.MngParams[mngpar]['options'][param_options]
            
        else:
            datpath = self.model_path + 'Scenarios/Default/TxtInOut/' + datfile
            if os.path.isfile(datpath):
                param_keys = self.MngParams[mngpar]['options'].keys()
                with open(datpath, 'rb') as search:
                    for line in search:
                        for param_options in param_keys:
                            if param_options.lower() in line.lower():
                                linesplit = re.split('\s',line)
                                linesplit = [l for l in linesplit if len(l) >0]
                                self.MngParams[mngpar]['options'][int(linesplit[0])] = self.MngParams[mngpar]['options'][param_options]
                                del self.MngParams[mngpar]['options'][param_options]
                                
            else:
                sys.exit('File: ' + datfile + ' was not found.')
        
        return

#%%    
    def Read_MngOps(self):
        
        MngParams = dict()
        params_bool = 0
        with open(self.mngops_parmt_file,'rb') as search:
            for line in search:
                if '#' in line:
                    params_bool = 1
                    temp_dict = dict()
                    temp_dict2 = dict()
                    linesplit = "".join(line.split())
                    param_name = sautils.FindString('#',':',linesplit)
                    param_values = sautils.FindString('[',']',linesplit)
                    param_values = re.split(',',param_values)
                    temp_dict['opID'] = int(param_values[0])
                    temp_dict['paramFile'] = param_values[1]
                    temp_dict['param_varname'] = param_values[2]
                    
                    print param_name, param_values[0], param_values[1]
                
                elif '#' not in line and params_bool == 1 and len(line.strip()) > 0:
                    linesplit = "".join(line.split())
                    temp_id = linesplit.find('=')
                    
                    param_values = sautils.FindString('{','}',linesplit)
                    param_values = re.split(';',param_values)
                    temp_dict3 = dict()
                    for parvals in param_values:
                        temp_var = parvals.split(':')
                        temprange = temp_var[1]
                        
                        if 'range' in temprange:
                            temprange = temprange.strip('range(')
                            temprange = temprange.strip(')')
                            temprange = re.split(',',temprange)
                            temp_dict4 = dict()
                            if '.' not in temprange[0] and temprange[0].isdigit():
                                temp_dict4['values'] = range(int(temprange[0]),int(temprange[2]),int(temprange[1]))
                                #temp_dict4['max'] = int(temprange[1])
                                
                            else:
                                temp_dict4['values'] = range(float(temprange[0]),float(temprange[2]),float(temprange[1]))
                                #temp_dict4['min'] = float(temprange[0])
                                #temp_dict4['max'] = float(temprange[1])
                        
                        else:
                            var_range = []
                            temp_dict4 = dict()
                            temprange = temprange.strip('[')
                            temprange = temprange.strip(']')
                            if len(temprange) > 1:
                                temprange = re.split(',',temprange)
                                for tempval in temprange:
                                    if '.' not in tempval and tempval.isdigit():
                                        var_range.extend([int(tempval)])
                                    elif float(tempval):
                                        var_range.extend([float(tempval)])
                                    else:
                                        var_range.extend([tempval])
                                temp_dict4['values'] = var_range
                            else:
                                temp_dict4['values'] = []
                            
                        temp_dict3[temp_var[0]] = temp_dict4
                    
                    temp_dict2[line[0:temp_id]] = temp_dict3
                    #temp_dict['options'][line[0:temp_id]] = temp_dict3
                    
                elif len(line.strip()) == 0:
                    params_bool = 0
                    temp_dict['options'] = temp_dict2
                    MngParams[param_name] = temp_dict
                    
        search.close()
        
        if params_bool == 1:
            temp_dict['options'] = temp_dict2
            MngParams[param_name] = temp_dict
        
        self.MngParams = MngParams
   
#%%
    def Read_NewMngSchd(self):
        
        MngSched = dict()
        sched_bool = 0
        
        with open(self.new_mngops_file,'rb') as search:
            for line in search:
                if '#' in line:
                    sched_bool = 1
                    temp_dict = dict()
                    linesplit = "".join(line.split())
                    opschd_id = re.split(':',linesplit)[1]
                    oper_order = []
                    #opschd_counter = 0
                
                elif '#' not in line and sched_bool == 1 and len(line.strip()) > 0:
                    linesplit = line.split(' ')
                    linesplit = [l for l in linesplit if len(l) >0]
                    if len(linesplit) > 1:
                        temp_dict[int(linesplit[1])] = line.strip('\r\n')
                        oper_order.append(int(linesplit[1]))
                    else:
                        temp_dict[int(linesplit[0])] = line.strip('\r\n')
                        oper_order.append(int(linesplit[0]))
                    #opschd_counter = opschd_counter + 1

                elif len(line.strip()) == 0:
                    temp_dict['OpsOrder'] = oper_order
                    sched_bool = 0
                    MngSched[int(opschd_id)] = temp_dict
                    
                    
        search.close()
        
        if sched_bool == 1:
            temp_dict['OpsOrder'] = oper_order
            MngSched[int(opschd_id)] = temp_dict

        self.MngSched = MngSched
        


#%%
    def AddParamsToLine(self, line, mngpardict, sub_basin):
        newline = line
        
        #if self.water_rights is not None and mngpardict['param_varname']:
            
        #else:
        
        ParamDict = dict()
        
        rnd_op = random.choice(mngpardict['options'].keys())
            
        if mngpardict['opID'] == 10:
            mngpardict['options'][rnd_op]['B']['values'] = [sub_basin]
            
        if len(mngpardict['param_varname']) > 0:
            str_lendiff = abs(len(str(mngpardict['param_varname'])) - len(str(rnd_op)))
            newline = line.replace(mngpardict['param_varname'],' ' * str_lendiff + str(rnd_op), 1)
            
        #if decision_vars in line:
        for opvar in mngpardict['options'][rnd_op].keys():
            if opvar != 'OP_SCHD' and len(mngpardict['options'][rnd_op][opvar]['values']) > 0:
                rnd_val = random.choice(mngpardict['options'][rnd_op][opvar]['values'])
                str_lendiff = abs(len(str(rnd_val)) - len(str(opvar)))
                
                newline = newline.replace(opvar,' ' * str_lendiff + str(rnd_val),1)
                #if len(mngpardict['options'][rnd_op][opvar]['values']) > 1:
                ParamDict[opvar] = rnd_val
            else:
                newline = newline.replace(opvar,' ' * len(opvar))
                
        return newline, ParamDict
    
    def Write_MgtSchd(self, file_path, hruid, hru_crops):
    
        cline = 0
        operations_linebool = 0
        InputVars = dict()
        InputVars['CROPS'] = []
        InputVars['SCHOP'] = []

        with open(file_path) as search, open(self.model_path + 'Scenarios/Default/TxtInOut/Tempfile.txt','w') as wrt:
            for line in search:
                if cline == 0:
                    linesplit = re.split('\s',line)
                    for sptline in linesplit:
                        if 'Subbasin' in sptline:
                            sptline = re.split(':',sptline)
                            sub_basin = int(sptline[1])
                            InputVars['SUBID'] = []
                            InputVars['SUBID'].append(sub_basin)
                            
                if operations_linebool == 1:
                    iter_counter = 1
                    for crop_id in hru_crops[hruid]:
                        schd_oper = random.choice(self.MngParams['Crops']['options'][crop_id]['OP_SCHD']['values'])
                        InputVars['CROPS'].append(crop_id)
                        InputVars['SCHOP'].append(schd_oper)
                        temp_operkeys = []
                        for schd_line in self.MngSched[schd_oper]['OpsOrder']:
                        #for schd_line in self.MngSched[schd_oper].keys():
                            #for temp_line in self.MngSched[schd_oper][schd_line]:
                            temp_line = self.MngSched[schd_oper][schd_line]
                            opkey = [mngpar for mngpar in self.MngParams.keys() if self.MngParams[mngpar]['opID'] == schd_line]
                            paramdict = dict()
                            if len(opkey) > 0:
                                temp_line, paramdict = self.AddParamsToLine(temp_line, self.MngParams[opkey[0]], sub_basin)
                                wrt.write(temp_line + '\n')
                            else:
                                wrt.write(temp_line + '\n')
                                
                            for params in paramdict.keys():
                                if params not in temp_operkeys:
                                    temp_operkeys.append(params)
                                if params not in InputVars.keys():
                                    InputVars[params] = []
                                    if iter_counter > 1:
                                        for i in range(iter_counter - 1):
                                            InputVars[params].append(-999)
                                    InputVars[params].append(paramdict[params])
                                            
                                else:
                                    InputVars[params].append(paramdict[params])
                                    
                        if iter_counter > 1:        
                            for tpar in InputVars.keys():
                                if tpar not in temp_operkeys and tpar != 'SUBID' and tpar != 'CROPS' and tpar != 'SCHOP':
                                    InputVars[tpar].append(-999)
                                    
                        iter_counter = iter_counter + 1
                             
                    operations_linebool = 0
                else:
                    wrt.write(line)
                
                if 'Operation Schedule' in line:
                    operations_linebool = 1
            
            cline = cline + 1

                
            search.close()
            wrt.close()
            shutil.copyfile(self.model_path + 'Scenarios/Default/TxtInOut/Tempfile.txt', file_path)
            os.remove(self.model_path + 'Scenarios/Default/TxtInOut/Tempfile.txt')
            
            return InputVars

#%%    
    def ChangeHRU_Mgt(self, hruids, hru_files, hru_crops):
        
        InputDict = dict()
        
        for hru in hruids:
            #hru = hruids[317]
            #print hru_files[hru], hru_crops[hru]
            file_path = self.model_path + 'Scenarios/Default/TxtInOut/' + hru_files[hru]
            temp_dict = self.Write_MgtSchd(file_path, hru, hru_crops)
            InputDict[hru] = temp_dict
            
        return InputDict
    
        

#        naops_names = np.asarray(ops_names)
#        crop_sch = []
#        for cp in crops.keys():
#            crop_ids = np.where(naops_names[:,0]==cp)
#            crop_sch.append((ops_names[crop_ids[0][random.randint(0,len(crop_ids[0])-1)]]))
#        
#        remaining_ops = len(actors) - len(crop_sch)
#        
#        for i in range(remaining_ops):
#            crop_sch.append((ops_names[random.randint(0,len(ops_names)-1)]))
#        
#        num_crop_sch = range(len(crop_sch))
#        random.shuffle(num_crop_sch)
#        
#        hru_actors = []
#        for actor in actors.keys():
#            for hru_ids in actors[actor]['HRU_IDS']:
#                hru_actors.append((hru_ids,actor,num_crop_sch[actor]))
#                #hru_actors.append((hru_ids,actor,num_crop_sch[0]))
#            
#        hru_file = 'hru-data.hru'
#        source_path = new_op_path.replace('/','\\') + '\\' + hru_file
#        id_path = new_op_path.find('TxtInOut')
#        destination_path = new_op_path[0:id_path].replace('/','\\') + hru_file
#         
#        command = 'copy ' + source_path + ' ' + destination_path
#        os.system(command) 
#        
#        destination_path = new_op_path[0:id_path] + hru_file
#        decision_path = new_op_path[0:id_path] + 'decisions_actors.txt'
#        source_path = new_op_path + '/' + hru_file
#        new_file = open(source_path,'w')
#        decision_file = open(decision_path,'w')
#        hru_actors = np.asarray(hru_actors)
#        with open(destination_path,'rb') as search_hru:
#                for line in search_hru:
#                    line = line.strip('\r\n')
#                    if 'SWAT' not in line and 'name' not in line:
#                        linesplit = re.split('\s',line)
#                        linesplit = [e for e in linesplit if e != '']
#                        hru_actor_id = np.where(hru_actors[:,0] == int(linesplit[0]))
#                        if len(hru_actor_id[0]) > 0:
#                            temp_line = AdjustOpsLen(line, linesplit[5], crop_sch[num_crop_sch[hru_actors[hru_actor_id[0],2][0]]][1]+'_lum')
#                            new_file.write(temp_line + '\n')
#                            decision_file.write(temp_line + '\n')
#                        else:
#                            new_file.write(line + '\n')
#                    else:
#                        new_file.write(line + '\n')  
#            
#        new_file.close() 
#        decision_file.close() 
#        return crop_sch, hru_actors
            

#%%
#    def CreateNewSchFile(self,hruid):
#        Lines_Dict = dict()
#        op_counter = 0
#        temp_lines = []
#        oper_name = None
#        with open(add_op_path + '/' + add_op_file,'rb') as search:
#                for line in search:
#                    line = line.strip('\r\n')
#                    temp_lines.append(line)
#                    linesplit = re.split('\s',line)
#                    linesplit = [e for e in linesplit if e != '']
#                    if linesplit[0].count('_') > 1:
#                        op_counter = op_counter + 1
#                        
#                        if op_counter > 1:
#                            Lines_Dict[oper_name] = temp_lines[:-1]
#                            new_oper = temp_lines[-1]
#                            temp_lines = []
#                            temp_lines.append(new_oper)
#                            oper_name = linesplit[0]
#                        else:
#                            oper_name = linesplit[0]
#        
#        Lines_Dict[oper_name] = temp_lines           
#        search.close()
#        
#        Oper_Ids = dict()
#        for ops in Lines_Dict.keys():
#            op_ids = re.split('_',ops)
#            temp_opds_ids = []
#            for oids in op_ids:
#                if oids != 'a' and oids.count('y') > 0:
#                    temp_opds_ids.append(1)
#                elif oids != 'a':
#                    temp_opds_ids.append(0)
#            Oper_Ids[ops] = temp_opds_ids
#                        
#        #%%   
#        source_path = new_op_path.replace('/','\\') + '\\' + old_schfile
#        id_path = new_op_path.find('TxtInOut')
#        destination_path = new_op_path[0:id_path].replace('/','\\') + old_schfile
#         
#        command = 'copy ' + source_path + ' ' + destination_path
#        os.system(command)    
#         
#        #%%   
#        destination_path = new_op_path[0:id_path] + old_schfile
#        source_path = new_op_path + '/' + old_schfile
#        new_file = open(source_path,'w')
#        with open(destination_path,'rb') as search_sch:
#                for line in search_sch:
#                    line = line.strip('\r\n')
#                    new_file.write(line + '\n')
#                    
#        search_sch.close()
#        
#        #%%
#        bool_str = ['n','y']
#        New_OpsNames = []
#        OpsNames = []
#        for cp in crops.keys():
#         
#            for ops in Oper_Ids.keys():
#                irr_id = [crops[cp]['Auto_Irr']]
#                fert_id = [crops[cp]['Fert']]
#                till_id = [crops[cp]['Till']]
#                
#                if crops[cp]['Auto_Irr'] == 2:
#                    irr_id = [0,1]
#                if crops[cp]['Till'] == 2:
#                    till_id = [0,1]
#                if crops[cp]['Fert'] == 2:
#                    fert_id = [0,1]
#                    
#                temp_op_name = ''
#                
#                for irr in irr_id:
#                    for till in till_id:
#                        for fert in fert_id:
#                            crop_op_bool = 0
#                            if [irr,till,fert] == Oper_Ids[ops]:
#                                if cp == 'alfa' and ops[0] == 'a':
#                                    temp_op_name = 'a_' + bool_str[irr] + 'i_' + bool_str[till] + 't_' + bool_str[fert] + 'f'
#                                    #print cp + '_' + temp_op_name
#                                    crop_op_bool = 1
#                                elif cp != 'alfa' and ops[0] != 'a':
#                                    temp_op_name = bool_str[irr] + 'i_' + bool_str[till] + 't_' + bool_str[fert] + 'f'
#                                    #print cp + '_' + temp_op_name
#                                    crop_op_bool = 1
#                                    
#                                #if crop_op_bool == 1 and cp != 'alfa':
#                                if crop_op_bool == 1:
#                                    for frt in fertilizer.keys():
#                                        if Oper_Ids[ops][2] == 1:
#                                            frt_opt_id = [i for i, s in enumerate(fertilizer.keys()) if frt in s]
#                                            for frtv in range(fertilizer[frt]['min'],fertilizer[frt]['max']+10,10):
#                                                for tl in tillage:
#                                                    if Oper_Ids[ops][1] == 1:
#                                                        till_opt_id = [i for i, s in enumerate(tillage) if tl in s]
#                                                        name_op = cp + '_' + str(frt_opt_id[0]) + '_' + str(frtv) + '_' + str(till_opt_id[0])
#                                                        if name_op not in OpsNames:
#                                                            for lis in range(len(Lines_Dict[ops])):
#                                                                temp_line = Lines_Dict[ops][lis]
#                                                                if lis == 0:
#                                                                    
#                                                                    New_OpsNames.append((cp,name_op))
#                                                                    OpsNames.append(name_op)
#                                                                    #temp_line = temp_line.replace(ops,name_op)
#                                                                    temp_line = AdjustNameLen(temp_line,ops,name_op)
#                                                                
#                                                                if temp_line.find('fert') > 0:
#                                                                    #temp_line = temp_line.replace('elem-n',frt)
#                                                                    temp_line = AdjustOpsLen(temp_line,'elem-n',frt)
#                                                                    new_fert_val = str(frtv) + '.00000'
#                                                                    temp_line = temp_line.replace('30.00000',new_fert_val)
#                                                                    
#                                                                if temp_line.find('till') > 0:
#                                                                    #temp_line = temp_line.replace('fldcult',tl)
#                                                                    temp_line = AdjustOpsLen(temp_line,'fldcult',tl)
#                                                                    
#                                                                if temp_line.find('plnt') > 0:
#                                                                    temp_line = temp_line.replace('agrc',cp)
#                                                                    
#                                                                if temp_line.find('hvkl') > 0:
#                                                                    temp_line = temp_line.replace('agrc',cp)
#                                                                    temp_line = AdjustOpsLen(temp_line,'null',crops[cp]['op_data2'])
#                                                                    #temp_line = temp_line.replace('null',crops[cp]['op_data2'])
#                                                                
#                                                                temp_line = temp_line.rstrip()
#                                                                new_file.write(temp_line + '  ' + '\n')
#                                                
#                                                    else:
#                                                        name_op = cp + '_' + str(frt_opt_id[0]) + '_' + str(frtv) + '_n'
#                                                        if name_op not in OpsNames:
#                                                            for lis in range(len(Lines_Dict[ops])):
#                                                                temp_line = Lines_Dict[ops][lis]
#                                                                if lis == 0:
#                                                                    
#                                                                    New_OpsNames.append((cp,name_op))
#                                                                    OpsNames.append(name_op)
#                                                                    #temp_line = temp_line.replace(ops,name_op)
#                                                                    temp_line = AdjustNameLen(temp_line,ops,name_op)
#                                                                
#                                                                if temp_line.find('fert') > 0:
#                                                                    #temp_line = temp_line.replace('elem-n',frt)
#                                                                    temp_line = AdjustOpsLen(temp_line,'elem-n',frt)
#                                                                    new_fert_val = str(frtv) + '.00000'
#                                                                    temp_line = temp_line.replace('30.00000',new_fert_val)
#                                                                
#                                                                if temp_line.find('plnt') > 0:
#                                                                    temp_line = temp_line.replace('agrc',cp)
#                                                                    
#                                                                if temp_line.find('hvkl') > 0:
#                                                                    temp_line = temp_line.replace('agrc',cp)
#                                                                    temp_line = AdjustOpsLen(temp_line,'null',crops[cp]['op_data2'])
#                                                                    #temp_line = temp_line.replace('null',crops[cp]['op_data2'])
#                                                                
#                                                                temp_line = temp_line.rstrip()
#                                                                new_file.write(temp_line + '  ' + '\n')
#                                                            
#                                        elif Oper_Ids[ops][1] == 1:
#                                            till_opt_id = [i for i, s in enumerate(tillage) if tl in s]
#                                            name_op = cp + '_n_n' + '_' + str(till_opt_id[0])
#                                            if name_op not in OpsNames:
#                                                for lis in range(len(Lines_Dict[ops])):
#                                                        temp_line = Lines_Dict[ops][lis]
#                                                        if lis == 0:
#                                                            
#                                                            New_OpsNames.append((cp,name_op))
#                                                            OpsNames.append(name_op)
#                                                            #temp_line = temp_line.replace(ops,name_op)
#                                                            temp_line = AdjustNameLen(temp_line,ops,name_op)
#                                                                    
#                                                        if temp_line.find('till') > 0:
#                                                            #temp_line = temp_line.replace('fldcult',tl)
#                                                            temp_line = AdjustOpsLen(temp_line,'fldcult',tl)
#                                                                    
#                                                        if temp_line.find('plnt') > 0:
#                                                            temp_line = temp_line.replace('agrc',cp)
#                                                                    
#                                                        if temp_line.find('hvkl') > 0:
#                                                            temp_line = temp_line.replace('agrc',cp)
#                                                            temp_line = AdjustOpsLen(temp_line,'null',crops[cp]['op_data2'])
#                                                            #temp_line = temp_line.replace('null',crops[cp]['op_data2'])
#                                                                    
#                                                        temp_line = temp_line.rstrip()
#                                                        new_file.write(temp_line + '  ' + '\n')   
#                                                    
#        new_file.close()
#        
#        return New_OpsNames, crops
    
    #%%
#    def CreateNewLumFile(new_op_path,ops_names, crops):
#        plantini_file = 'plant.ini'
#        base_plant = 'agrl_comm'
#        
#        source_path = new_op_path.replace('/','\\') + '\\' + plantini_file
#        id_path = new_op_path.find('TxtInOut')
#        destination_path = new_op_path[0:id_path].replace('/','\\') + plantini_file
#         
#        command = 'copy ' + source_path + ' ' + destination_path
#        os.system(command) 
#        
#        destination_path = new_op_path[0:id_path] + plantini_file
#        source_path = new_op_path + '/' + plantini_file
#        new_file = open(source_path,'w')
#        base_plant_bool = 0
#        with open(destination_path,'rb') as search_lum:
#                for line in search_lum:
#                    line = line.strip('\r\n')
#                    if base_plant in line:
#                        base_plant_bool = 1
#                        base_plant_line_a = line
#                        base_plant_opts_a = re.split('\s',line)
#                        base_plant_opts_a = [e for e in base_plant_opts_a if e != '']
#                        
#                    elif base_plant_bool == 1:
#                        base_plant_line = line
#                        base_plant_opts = re.split('\s',line)
#                        base_plant_opts = [e for e in base_plant_opts if e != '']
#                        base_plant_bool = 0
#                        
#                    new_file.write(line + '\n')
#                    
#        search_lum.close()
#        
#        for crop in crops.keys():
#            temp_line = AdjustNameLen(base_plant_line_a,base_plant_opts_a[0], crop +'_comm')
#            new_file.write(temp_line + '\n')
#            temp_line = base_plant_line.replace('agrl',crop)
#            new_file.write(temp_line + '\n')
#            
#        new_file.close()
#        
#        
#        
#        lum_schfile = 'landuse.lum'
#        #new_op_file = 'management.sch'
#        base_lum = 'agrl_lum'
#        
#        source_path = new_op_path.replace('/','\\') + '\\' + lum_schfile
#        id_path = new_op_path.find('TxtInOut')
#        destination_path = new_op_path[0:id_path].replace('/','\\') + lum_schfile
#         
#        command = 'copy ' + source_path + ' ' + destination_path
#        os.system(command) 
#        
#        destination_path = new_op_path[0:id_path] + lum_schfile
#        source_path = new_op_path + '/' + lum_schfile
#        new_file = open(source_path,'w')
#        with open(destination_path,'rb') as search_lum:
#                for line in search_lum:
#                    line = line.strip('\r\n')
#                    if base_lum in line:
#                        base_lum_line = line
#                        base_lum_opts = re.split('\s',line)
#                        base_lum_opts = [e for e in base_lum_opts if e != '']
#                        
#                    new_file.write(line + '\n')
#                    
#        search_lum.close()
#        
#        for op in ops_names:
#            temp_line = AdjustNameLen(base_lum_line,base_lum_opts[0],op[1]+'_lum')
#            temp_line = AdjustOpsLen(temp_line,base_lum_opts[3],op[1])
#            temp_line = AdjustOpsLen(temp_line,base_lum_opts[2],op[0] +'_comm')
#            new_file.write(temp_line + '\n')
#            
#        new_file.close()
#        
#        return
        
                