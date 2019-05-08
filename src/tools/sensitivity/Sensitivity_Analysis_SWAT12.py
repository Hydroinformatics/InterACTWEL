# -*- coding: utf-8 -*-

import os, re, zipfile, argparse, subprocess, shutil, random, pyodbc, csv, sys
import numpy as np
import SA_SWAT12_LandMngOps as LandMngOps
import SA_SWAT12_utils as sautils
import SA_SWAT12_Outputs as saoutputs

class SensitivityAnalysis():
    
    def __init__(self, input_files):
        
        self.no_change_lum_path = ''
        self.outputcsv = 0
        self.inputcsv = 1
        self.swat_exe = ''
        
        
        self.output_vars = dict()
        self.input_file = input_files.replace('\\','/')
        self.LndMngOps = LandMngOps.LndMngOps()
        self.saoutputs = saoutputs.SA_Outputs()
        
        print "Reading Input Files"
        #self.SAUtils = sautils.SAUtils()
        self.ReadInputs()
        
        if self.LndMngOps:
            self.LndMngOps.Read_MngOps()
            self.LndMngOps.Read_NewMngSchd()
             
            
    #%% Main iterator to run sensitivity analysis
    def RunAnalysis(self,num_sim):
        
        if self.swat_exe == '':
            print 'Please specify a SWAT executable (e.g., .swat_exe)'
            sys.exit(0)
         
        #for i in range(num_sim):
        print "Iteration: " + str(num_sim)
        self.SA(num_sim)
        #self.output_vars_data = dict()
        
        for outfile in self.output_vars:
            tfile = self.output_vars[outfile]['File']
            if tfile[len(tfile)-3:len(tfile)] == 'hru':
                for varkey in self.output_vars[outfile]['Vars'].keys():
                    data_array, hru_sub = self.saoutputs.Get_output_hru(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])
                    self.output_vars_data[varkey] = data_array
            
            elif tfile[len(tfile)-3:len(tfile)] == 'sub':
                for varkey in self.output_vars[outfile]['Vars'].keys():
                    data_array = self.saoutputs.Get_output_sub(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])
                    self.output_vars_data[varkey] = data_array
                   
            elif tfile[len(tfile)-3:len(tfile)] == 'rch':
                for varkey in self.output_vars[outfile]['Vars'].keys():
                    self.output_vars_data[varkey] = self.saoutputs.Get_output_rch(tfile, varkey, self.output_vars[outfile]['Vars'][varkey])
            
            elif tfile[len(tfile)-3:len(tfile)] == 'std':
                table = self.output_vars[outfile]['Vars']['Table']
                for varkey in self.output_vars[outfile]['Vars'].keys():
                    if varkey.lower() != 'table':
                        self.output_vars_data[varkey] = self.saoutputs.Get_output_std(tfile, table, varkey, self.output_vars[outfile]['Vars'][varkey])
        
        if self.outputcsv == 1:
            print "Writing Output Data CSV" 
            csv_file = self.swat_path + '/' + 'SA_Outputs.csv'
            fileout = open(csv_file,'w')
            fileout.write('ITER, OUTVAR, SUBID, UNIT_TYPE, UNIT_ID, TIME (MON) \n')
            for var in self.output_vars_data.keys():
                unit_type = self.output_vars_data[var]['Type']
                for unit_ids in self.output_vars_data[var].keys():
                    #for val in range(0,len(self.output_data[var][unit_ids])):
                    if unit_ids != 'Type' and unit_ids != 'Years': 
                        atxt = ''
                        cc = 0
                        for ast in self.output_vars_data[var][unit_ids]:
                            if cc == 0:
                                atxt = str(ast)
                                cc = cc + 1
                            else:
                                atxt = atxt + ',' + str(ast)
                        if unit_type == 'HRU':
                            subid = hru_sub[unit_ids]
                        elif unit_type == 'RCH':
                            subid = unit_ids
                        elif unit_type == 'BSN':
                            subid = ' '
                        if unit_ids.lower() == 'data':
                            unit_ids = ' '
                            
                        fileout.write(str(num_sim) + ',' + var + ',' + str(subid) + ',' + unit_type + ',' + str(unit_ids) + ',' + atxt + '\n')
                
            fileout.close()
                    
#%%
    def SA(self,num_sim):
        self.swat_path = self.UnzipModel(num_sim)
        self.LndMngOps.model_path = self.swat_path
        self.saoutputs.model_path = self.swat_path + 'Scenarios/Default/TxtInOut/'
        self.saoutputs.output_path = self.pathuzip
        self.saoutputs.output_data = dict()
                    
        
        if self.crop_rots:
            self.HRUCrops = self.GetHRUCropRot()
        
        if not self.CheckActorGroups():
            self.HRU_ACTORS, self.hru_ids, self.total_area, self.no_change_lums = self.GetHRU_ACTORS()
            
        for mngpar in self.LndMngOps.MngParams.keys():
            for opkeys in self.LndMngOps.MngParams[mngpar]['options'].keys():
                for var in self.LndMngOps.MngParams[mngpar]['options'][opkeys]:
                    if 'WRdict' in self.LndMngOps.MngParams[mngpar]['options'][opkeys][var]:
                        self.LndMngOps.MngParams[mngpar]['options'][opkeys][var]['WRdict'] = self.LndMngOps.GetWaterRigthHRU(self.LndMngOps.MngParams[mngpar]['options'][opkeys][var]['WRdict'])
        
        for mngpar in self.LndMngOps.MngParams.keys():
            self.LndMngOps.FindVarIds(mngpar)
         
        self.HRUFiles = self.FindHRUMgtFiles()
        
        print "Writing the Mngt Files"
        
#            for i in self.HRU_ACTORS.keys():
#                self.LndMngOps.ChangeHRU_Mgt(self.HRU_ACTORS[i]['HRU_IDS'], self.HRUFiles ,self.HRUCrops)
        
        HRUids = []
        for i in self.HRU_ACTORS.keys():
            for j in self.HRU_ACTORS[i]['HRU_IDS']:
                HRUids.append(j)
                
        InputDict = dict()
        InputDict = self.LndMngOps.ChangeHRU_Mgt(HRUids, self.HRUFiles ,self.HRUCrops)
        
        if self.inputcsv == 1 and len(InputDict.keys()) > 0:
            print "Writing Input Data CSV"  
            csv_file = self.swat_path + 'SA_Inputs.csv'
            filein = open(csv_file,'w')
            filein.write('ITER, INVAR, SUBID, UNIT_TYPE, UNIT_ID, TIME (YEAR) \n')
            for hruid in InputDict.keys():
                for parms in InputDict[hruid].keys():
                    if parms != 'SUBID': 
                        atxt = ''
                        cc = 0
                        for ast in InputDict[hruid][parms]:
                            if cc == 0:
                                if ast == -999:
                                    ast = '-'
                                atxt = str(ast)
                                cc = cc + 1
                            else:
                                if ast == -999:
                                    ast = '-'
                                atxt = atxt + ',' + str(ast)
                        
                        filein.write(str(num_sim) + ',' + str(parms) + ',' + str(InputDict[hruid]['SUBID'][0]) + ', HRU' + ',' + str(hruid) + ',' + atxt + '\n')
                        
            filein.close()
            
        print "Running SWAT"               
        self.run_SWAT()        
            
#%%
    def run_SWAT(self):
        cwdir = os.getcwd()
        os.chdir(self.swat_path + 'Scenarios/Default/TxtInOut')
        exitflag = subprocess.check_call([self.swat_exe])
        if exitflag == 0:
            print "Successful SWAT run"
        else:
            print exitflag
        os.chdir(cwdir)
        
    #%% Unzip user SWAT model and run baseline scenario
    def UnzipModel(self,iterc):
        print "Unzipping SWAT model"  
        folderpath = self.pathuzip + '/ITER_' + str(iterc) + '/'
        if os.path.isdir(folderpath):
            shutil.rmtree(folderpath)
            
        with zipfile.ZipFile(self.zipswat_path, "r") as z:
            z.extractall(folderpath)
        
        return folderpath
    
    #%% Find paths to all files in project folder
    def ReadInputs(self):
        with open(self.input_file,'rb') as search:
            for line in search:
                if 'zipswat_path' in line:
                    linesplit = re.split('\s',line)
                    self.zipswat_path = linesplit[2].replace('\\','/')
                    
                elif 'no_change_lum_path' in line:
                    linesplit = re.split('\s',line)
                    self.no_change_lum_path = linesplit[2].replace('\\','/')
                    
                elif 'new_mng_ops' in line:
                    linesplit = re.split('\s',line)
                    self.LndMngOps.mngops_parmt_file = linesplit[2].replace('\\','/')
                    
                elif 'new_ops_sched' in line:
                    linesplit = re.split('\s',line)
                    self.LndMngOps.new_mngops_file = linesplit[2].replace('\\','/')

                elif 'unzip_path' in line:
                    linesplit = re.split('\s',line)
                    self.pathuzip = linesplit[2].replace('\\','/')
                    
                elif 'crop_hru_seq' in line:
                    linesplit = re.split('\s',line)
                    self.crop_rots = linesplit[2].replace('\\','/')
                
                elif 'output_vars' in line:
                    linesplit = re.split('\s',line)
                    self.output_vars_file = linesplit[2].replace('\\','/')
                    self.output_vars = self.GetOutputVars()
                    self.output_vars_data = dict()
                    self.outputcsv = 1
                    
                elif 'swat_exe' in line:
                    linesplit = re.split('\s',line)
                    self.swat_exe = linesplit[2].replace('\\','/')
                    
                    
    #%% 
#    def Get_HRUs_ids(tfile,var):
#        output_array = dict()
#        templulc = []
#        temphru = [] 
#        tempsub = []
#        tempmgt = []
#        tempgis =[]
#        varbool = 0
#    
#        with open(tfile) as search:
#            for line in search:
#                if var in line:
#                    if varbool == 0:
#                        line = search.next()
#                        varbool = 1
#                        
#                if varbool == 1:
#                    linesplit = re.split('\s',line)
#                    linesplit = [e for e in linesplit if e != '']
#                    templulc.append(linesplit[0])        
#                    temphru.append(int(linesplit[1]))
#                    tempgis.append(linesplit[2])
#                    tempsub.append(int(linesplit[3]))
#                    tempmgt.append(linesplit[4])
#                    
#        hruids = np.unique(temphru)
#         
#        for ui in hruids:
#            data_array = dict()
#            temp = [tempgis[i] for i in range(0,len(templulc)) if temphru[i] == ui]
#            data_array['GIS'] = temp[0]
#            temp = [tempsub[i] for i in range(0,len(templulc)) if temphru[i] == ui]
#            data_array['SUB'] = temp[0]
#            data_array['LULC'] = [templulc[i] for i in range(0,len(templulc)) if temphru[i] == ui]
#            data_array['MGT'] = [tempmgt[i] for i in range(0,len(templulc)) if temphru[i] == ui]
#            output_array[str(ui)] = data_array 
#                
#        return output_array
    

#%% Generate groups ("actors") of HRUs that will be managed in the same way 
    def CheckActorGroups(self):
        with open(self.crop_rots, 'rb') as search:
            for line in search:
                if 'actor_id' in line:
                    search.close()
                    return True
                else:
                    search.close()
                    return False
                
    def GetHRU_ACTORS(self):
        no_change_lums = []
        if self.no_change_lum_path != '':
            with open(self.no_change_lum_path,'rb') as search:
                for line in search:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    no_change_lums.append(linesplit[0])
            search.close()
        else:
            no_change_lums = []
        
        file_path = self.swat_path + '/Scenarios/Default/TxtInOut/' + 'input.std'
        
        hru_ids = []
        linebool = 0
        total_area = 0
        with open(file_path,'rb') as search:
            for line in search:
                    if 'HRU CN Input Summary Table' in line:
                        if linebool == 0:
                            line = search.next()
                            line = search.next()
                            linebool = 1
                            
                    if linebool == 1:
                        if len(re.split('\s',line)) < 10:
                            break
                        else:
                            linesplit = re.split('\s',line)
                            linesplit = [e for e in linesplit if e != '']
                            if linesplit[3] not in no_change_lums and int(linesplit[1]) in self.HRUCrops.keys():
                                if len(self.HRUCrops[int(linesplit[1])]) > 0:
                                    hru_ids.append((int(linesplit[1]),int(linesplit[0]),float(linesplit[2])))
                                    total_area = total_area + float(linesplit[2])
        search.close()
        
        hru_counter = 0
        HRU_ACTORS = dict()
        temp_array = []
        
        for i in range(len(hru_ids)):
            if hru_counter == 0 :
                temp_sum = float(hru_ids[i][2])
                temp_array.append(int(hru_ids[i][0]))
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
                    temp_sum = float(hru_ids[i][2])
                    temp_array.append(int(hru_ids[i][0]))
                else:
                    temp_sum = temp_sum + float(hru_ids[i][2])
                    temp_array.append(int(hru_ids[i][0]))
                                
        search.close()
            
        return HRU_ACTORS, hru_ids, total_area, no_change_lums

#%%
    def GetOutputVars(self):
        
        output_varsb = dict()
        line_bool = 0
        with open(self.output_vars_file,'rb') as search:
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
                    param_values = sautils.FindString('{','}',linesplit)
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
                            templine = sautils.FindString('{','}',templine[1])
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
    def FindHRUMgtFiles(self):
        
        swat_files  = os.listdir(self.swat_path + 'Scenarios/Default/TxtInOut/')
        hru_files = [f for f in swat_files if '.mgt' in f and f != 'output.mgt']
        
        HRUFiles = dict()
        #hrufile = []
        for hfile in hru_files:
            cline = 0
            with open(self.swat_path + 'Scenarios/Default/TxtInOut/' + hfile) as search:
                for line in search:
                    if cline == 0:
                        linesplit = re.split('\s',line)
                        for sptline in linesplit:
                            if 'HRU' in sptline and cline == 0:
                                sptline = re.split(':',sptline)
                                HRUFiles[int(sptline[1])] = hfile
                                #hrufile.append((int(sptline[1]),int(hfile.strip('.mgt'))))
                                cline = cline + 1
                         
        return HRUFiles

#%%
    def GetHRUCropRot(self):
        cropdict = self.CDLtoSWATdict()
        HRUCrops = dict()
        cline = 0
        with open(self.crop_rots, 'rb') as search:
            for line in search:
                if cline != 0:
                    linesplit = "".join(line.split())
                    linesplit = re.split(',',linesplit)
                    temp_data = []
                    ncld_bool = 0
                    for i in range(1,len(linesplit)):
                        if int(linesplit[i]) > 0 and int(linesplit[i]) in cropdict.keys():
                            temp_data.append(cropdict[int(linesplit[i])])
                        else:
                            temp_data.append(int(linesplit[i]))
                            ncld_bool = 1
                    if ncld_bool == 0:
                        HRUCrops[int(linesplit[0])] = temp_data
                    else:
                        HRUCrops[int(linesplit[0])] = []
                cline += 1
        
        search.close()
        
        return HRUCrops
    
    def CDLtoSWATdict(self):
        db_path = self.swat_path + 'QSWATRef2012.mdb'
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + db_path + ';'
            )
        cnxn = pyodbc.connect(conn_str)
        crsr = cnxn.cursor()
        
        crsr.execute('select * from crop')
        cropdict = dict()
        for row in crsr.fetchall():
            cropdict[str(row[2])] = row[1]
            
            
        conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + db_path + ';'
        )
        cnxn = pyodbc.connect(conn_str)
        crsr = cnxn.cursor()
    
        crsr.execute('select * from CDL_lu')
    
        cdl_cropdict = dict()
        for row in crsr.fetchall():
            if str(row[2]) in cropdict.keys():
                cdl_cropdict[row[1]] = cropdict[str(row[2])]
        return cdl_cropdict
    
    