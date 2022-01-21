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
        self.wrdict_bool = 0
        self.wrvarname = ''
        
        #self.num_parms = []

#%% 
    def GetWaterRigthHRU(self, wrtfile):
        wrdict = dict()
        temp_dict = dict()
        if os.path.isfile(self.model_path + 'Scenarios/Default/TxtInOut/' + wrtfile):
            with open(self.model_path + 'Scenarios/Default/TxtInOut/' + wrtfile,'rb') as search:
                for line in search:
                    if 'WR_ID' not in line:
                        linesplit = re.split('\s',line)
                        linesplit = [t for t in linesplit if len(t) > 0]
                        if len(linesplit) > 0:
                            wrdict[int(linesplit[1])] = linesplit[2]
            search.close()
        else:
            sys.exit('File: ' + wrtfile + ' was not found.')
        
        if os.path.isfile(self.model_path + 'Scenarios/Default/TxtInOut/hruwr.dat'):
            with open(self.model_path + 'Scenarios/Default/TxtInOut/hruwr.dat','rb') as search:
                for line in search:
                    linesplit = re.split('\s',line)
                    linesplit = [t for t in linesplit if len(t) > 0]
                    if len(linesplit) > 0 and int(linesplit[4]) == 1:
                        temp_dict[int(linesplit[0])] = wrdict[int(linesplit[1])]
            search.close()
        else:
            sys.exit('File: hruwr.dat was not found.')
        
        self.wrdict_bool = 1
        return temp_dict
    
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
                    
#                    if line[0:temp_id] == 'BARR':
#                        print 'BARR'
                    
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
                                temp_dict4['values'] = range(int(temprange[0]),int(temprange[2])+1,int(temprange[1]))
                                temp_dict4['DecSpaces'] = 0
                                #temp_dict4['max'] = int(temprange[1])
                                
                            else:
                                temp_dict4['values'] = range(int(float(temprange[0])),int(float(temprange[2]))+1,int(float(temprange[1])))
                                tempdec = temprange[0].split('.')
                                temp_dict4['DecSpaces'] = len(tempdec[1])
                                #temp_dict4['min'] = float(temprange[0])
                                #temp_dict4['max'] = float(temprange[1])
                        
                        elif 'wrdata.dat' in temprange:  
                            var_range = []
                            temp_dict4 = dict()
                            temprange = temprange.strip('[')
                            temprange = temprange.strip(']')
                            temp_dict4['WRdict'] = temprange
                            self.wrvarname = temp_var[0]
                            
                            
                        else:
                            var_range = []
                            temp_dict4 = dict()
                            temprange = temprange.strip('[')
                            temprange = temprange.strip(']')
                            if len(temprange) >= 1:
                                #if ',' in temprange:
                                temprange = re.split(',',temprange)
                                    
                                #print temprange

                                for tempval in temprange:
                                    if '.' not in tempval and tempval.isdigit():
                                        var_range.extend([int(tempval)])
                                    elif '.' in tempval and tempval.isdigit():
                                        var_range.extend([float(tempval)])
                                    else:
                                        var_range.extend([tempval])
                                temp_dict4['values'] = var_range
                                if '.' in tempval:
                                    tempdec = temprange[0].split('.')
                                    temp_dict4['DecSpaces'] = len(tempdec[1])
                                else:
                                    temp_dict4['DecSpaces'] = 0
                            else:
                                temp_dict4['values'] = []
                                temp_dict4['DecSpaces'] = 0
                            
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
                    oper_order_id = []
                    opschd_counter = 0
                
                elif '#' not in line and sched_bool == 1 and len(line.strip()) > 0:
                    linesplit = line.lstrip()
                    linesplit = linesplit.split(' ')
                    linesplit = [l for l in linesplit if len(l) >0]
                    if len(linesplit) > 1:
                        #temp_dict[int(linesplit[1])] = line.strip('\r\n')
                        oper_order_id.append(int(linesplit[1]))
                        temp_dict[int(opschd_counter)] = line.strip('\r\n')
                        oper_order.append(int(opschd_counter))
                    else:
                        #temp_dict[int(linesplit[0])] = line.strip('\r\n')
                        oper_order_id.append(int(linesplit[0]))
                        temp_dict[int(opschd_counter)] = line.strip('\r\n')
                        oper_order.append(int(opschd_counter))
                        
                    opschd_counter = opschd_counter + 1

                elif len(line.strip()) == 0:
                    temp_dict['OpsOrder'] = oper_order
                    temp_dict['OpsOrderId'] = oper_order_id
                    sched_bool = 0
                    MngSched[int(opschd_id)] = temp_dict
                    
                    
        search.close()
        
        if sched_bool == 1:
            temp_dict['OpsOrder'] = oper_order
            temp_dict['OpsOrderId'] = oper_order_id
            MngSched[int(opschd_id)] = temp_dict

        self.MngSched = MngSched
        


#%%
    def CheckAddDecimal(self, val, decneed, opvar):
        strval = str(val)
        if '.' in strval:
            declen = strval.split('.')
            declen = declen[1]
        else:
            declen = 0
        
        if declen < decneed and '.' in strval:
            strval = strval + '0'*abs(decneed-declen)
        elif declen < decneed and '.' not in strval:
            strval = strval + '.' + '0'*abs(decneed-declen)
        elif declen > decneed:
            declen = strval.split('.')
            decstr = declen[1]
            strval = declen[0] + '.' + decstr[0:decneed+1]
        
        return strval
            
        
    def AddParamsToLine(self, line, mngpardict, sub_basin, hruid, cropid=None):
        newline = line
        
        ParamDict = dict()
        
        if cropid is not None:
            rnd_op = cropid
        else:
            if mngpardict['opID'] == 10 and self.wrdict_bool == 1:
                rnd_op = random.choice(mngpardict['options'].keys())
                #print rnd_op, self.wrvarname, hruid
                rnd_op = int(mngpardict['options'][rnd_op][self.wrvarname]['WRdict'][hruid])
            else:
                rnd_op = random.choice(mngpardict['options'].keys())
            
        if mngpardict['opID'] == 10:
            #print rnd_op, self.wrvarname, hruid, sub_basin
            mngpardict['options'][rnd_op]['B']['values'] = [sub_basin]
            
        if len(mngpardict['param_varname']) > 0:
            str_lendiff = abs(len(str(mngpardict['param_varname'])) - len(str(rnd_op)))
            newline = line.replace(mngpardict['param_varname'],' ' * str_lendiff + str(rnd_op), 1)
            
        #if decision_vars in line:
        for opvar in mngpardict['options'][rnd_op].keys():
            if 'values' in mngpardict['options'][rnd_op][opvar].keys():
                if opvar != 'OP_SCHD' and len(mngpardict['options'][rnd_op][opvar]['values']) > 0:
                    rnd_val = random.choice(mngpardict['options'][rnd_op][opvar]['values'])
                    
                    if mngpardict['options'][rnd_op][opvar]['DecSpaces'] > 0:
                        rnd_val = self.CheckAddDecimal(rnd_val, mngpardict['options'][rnd_op][opvar]['DecSpaces'], opvar)
                    else:
                        rnd_val = str(rnd_val)
                    
                    if len(rnd_val) > len(str(opvar)):
                        str_lendiff = abs(len(rnd_val) - len(str(opvar)))
                        newline = newline.replace(' ' * str_lendiff + opvar,str(rnd_val),1)
                        
                    elif len(rnd_val) <= len(str(opvar)):
                        str_lendiff = abs(len(rnd_val) - len(str(opvar)))
                        newline = newline.replace(opvar,' ' * str_lendiff + str(rnd_val),1)
                    
                    #if len(mngpardict['options'][rnd_op][opvar]['values']) > 1:
                    ParamDict[opvar] = rnd_val
                else:
                    newline = newline.replace(opvar,' ' * len(opvar))
                
        return newline, ParamDict

#%%    
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
                        
                        if hruid == 98:
                            stddp = 0
                            
                        #print hruid
                        schd_oper = random.choice(self.MngParams['Crops']['options'][crop_id]['OP_SCHD']['values'])
                        InputVars['CROPS'].append(crop_id)
                        InputVars['SCHOP'].append(schd_oper)
                        temp_operkeys = []
                        for schd_line in self.MngSched[schd_oper]['OpsOrder']:
                        #for schd_line in self.MngSched[schd_oper].keys():
                            #for temp_line in self.MngSched[schd_oper][schd_line]:
                            temp_line = self.MngSched[schd_oper][schd_line]
                            opkey = [mngpar for mngpar in self.MngParams.keys() if self.MngParams[mngpar]['opID'] == self.MngSched[schd_oper]['OpsOrderId'][schd_line]]
                            paramdict = dict()
                            if len(opkey) > 0:
                                if self.MngParams[opkey[0]]['opID'] == 1 :
                                    temp_line, paramdict = self.AddParamsToLine(temp_line, self.MngParams[opkey[0]], sub_basin, hruid, crop_id)
                                else:
                                    temp_line, paramdict = self.AddParamsToLine(temp_line, self.MngParams[opkey[0]], sub_basin, hruid)
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
                             
                    #operations_linebool = 0
                    operations_linebool = 2
                    
                elif operations_linebool == 0 and operations_linebool != 2:
                #else:
                    wrt.write(line)
                
                if 'Operation Schedule' in line:
                    operations_linebool = 1
            
                cline = cline + 1

                
        search.close()
        wrt.close()
        shutil.copyfile(self.model_path + 'Scenarios/Default/TxtInOut/Tempfile.txt', file_path)
        os.remove(self.model_path + 'Scenarios/Default/TxtInOut/Tempfile.txt')
            
        return InputVars
        

    def Write_MgtSchd_NoCrops(self, file_path, hruid, hru_non_crops):
    
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
                    
                    if unicode(hru_non_crops[hruid], 'utf-8').isnumeric() == False:
                        luse_id = line.find('Luse:')
                        print hruid, line[luse_id+5:luse_id+9], hru_non_crops[hruid]
                        line[luse_id+5:luse_id+9] = hru_non_crops[hruid]
                        
                            
                if operations_linebool == 0:
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
    def ChangeHRU_Mgt(self, hruids, hruids_nocrop, hru_files, hru_crops, hru_non_crops):
        
        InputDict = dict()
        
        for hru in hruids:
            #hru = hruids[317]
            #print hru_files[hru], hru_crops[hru]
            file_path = self.model_path + 'Scenarios/Default/TxtInOut/' + hru_files[hru]
            temp_dict = self.Write_MgtSchd(file_path, hru, hru_crops)
            InputDict[hru] = temp_dict
        
        for hru in hruids_nocrop:
            file_path = self.model_path + 'Scenarios/Default/TxtInOut/' + hru_files[hru]
            temp_dict = self.Write_MgtSchd_NoCrops(file_path, hru, hru_non_crops)
            
            
        return InputDict
    