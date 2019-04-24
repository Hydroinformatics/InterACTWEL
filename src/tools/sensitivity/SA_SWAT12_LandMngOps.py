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
    
                