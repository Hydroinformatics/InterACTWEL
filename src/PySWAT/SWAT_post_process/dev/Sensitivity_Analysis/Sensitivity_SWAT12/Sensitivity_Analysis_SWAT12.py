# -*- coding: utf-8 -*-

import os, re, zipfile, argparse, subprocess, shutil, random, pyodbc
import numpy as np
import LandMngOps
import SA_SWAT12_utils as sautils

class SensitivityAnalysis():
    
    def __init__(self, input_files):
        
        self.input_file = input_files.replace('\\','/')
        self.LndMngOps = LandMngOps.LndMngOps()
        self.SAUtils = sautils.SAUtils()
        self.ReadInputs()
        
        if self.LndMngOps:
            self.LndMngOps.Read_MngOps()
            self.LndMngOps.Read_NewMngSchd()
             
            
    #%% Main iterator to run sensitivity analysis
    def RunAnalysis(self,num_sim):
        for i in range(num_sim):
            #self.swat_path = self.UnzipModel(i)
            self.swat_path = 'C:/Users/sammy/Documents/GitHub/InterACTWEL/src/PySWAT/SWAT_post_process/dev/Sensitivity_Analysis/Test_Nick/ITER_0/'
            self.LndMngOps.model_path = self.swat_path
            
            if self.crop_rots:
                self.HRUCrops = self.GetHRUCropRot()
            
            if not self.CheckActorGroups():
                self.HRU_ACTORS, self.hru_ids, self.total_area, self.no_change_lums = self.GetHRU_ACTORS()
            
            for mngpar in self.LndMngOps.MngParams.keys():
                self.LndMngOps.FindVarIds(mngpar)
             
            self.HRUFiles = self.FindHRUFiles()
            
            for i in self.HRU_ACTORS.keys():
               self.LndMngOps.ChangeHRU_Mgt(self.HRU_ACTORS[i]['HRU_IDS'], self.HRUFiles ,self.HRUCrops)
            

    #%% Unzip user SWAT model and run baseline scenario
    def UnzipModel(self,iterc):
        folderpath = self.pathuzip + '/ITER_' + str(iterc) + '/'
        if os.path.isdir(folderpath):
            shutil.rmtree(folderpath)
            
        with zipfile.ZipFile(self.zipswat_path, "r") as z:
            z.extractall(folderpath)
            #os.chdir(folderpath+'Scenarios/Default/TxtInOut')
        #exitflag = subprocess.check_call(['rev57_64rel.exe'])
        #print exitflag
        
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
        with open(self.no_change_lum_path,'rb') as search:
            for line in search:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                no_change_lums.append(linesplit[0])
        search.close()
        
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
    def FindHRUFiles(self):
        
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
    
    