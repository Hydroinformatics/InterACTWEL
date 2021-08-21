# -*- coding: utf-8 -*-

import os, re, argparse, shutil, zipfile

#os.chdir('..\src')
    
#from tools.sensitivity.Sensitivity_Analysis_SWAT12 import SensitivityAnalysis

##%%
#if __name__ == '__main__':
#
#    ##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
#    parser = argparse.ArgumentParser(description='Inputs File')
#    parser.add_argument('path', metavar='-p', type=str, nargs='+',
#                        help='Path to text file with list of input Files')
#    args = parser.parse_args()
#    #%%
#    #input_files = '..\data\Sensitivity_SWAT12\SWAT12_Input_Files.txt'
#    
#    #input_files = args.path[0].replace('\\','/')


class SensitivityAnalysis():
    
    def __init__(self, swat_path):
        
        self.zipswat_path = None
        self.MGTFiles = None
        self.iter = 0
        
        self.swat_path = swat_path.replace('\\','/')
        self.output_path = output_path.replace('\\','/')
        #self.swat_path = self.UnzipModel() 
        #self.swat_path = swat_path + '/'
        
        #self.swat_path = 'C:/Users/sammy/Documents/Research/SWAT/QSWAT_Input_Data/Umatilla/HRUs_Meghna/Iter11_txtinout_crop_operations/Txtinout_v4_Iter11/ITER_0' + '/'
        #self.LndMngOps.model_path = self.swat_path
        #self.saoutputs.model_path = self.swat_path + 'Scenarios/Default/TxtInOut/'
        #self.saoutputs.output_path = self.pathuzip
        #self.saoutputs.output_data = dict()
        
        print "Reading Input Files"
        #self.SAUtils = sautils.SAUtils()
        self.FindHRUMgtFiles()
        
    #%% Unzip user SWAT model and run baseline scenario
    def UnzipModel(self):
        print "Unzipping SWAT model"  
        folderpath = os.path.split(self.swat_path)[0] + '/ITER_TEST/'
        
        if os.path.isdir(folderpath):
            shutil.rmtree(folderpath)
        
        print self.swat_path
        with zipfile.ZipFile(self.swat_path, "r") as z:
            z.extractall(folderpath)
        
        return folderpath
      
    #%% Find the names for the .mgt files that must be changed in every iteration
    def FindHRUMgtFiles(self):
        
        swat_files  = os.listdir(self.swat_path + '/Scenarios/Default/TxtInOut/')
        mgt_files = [f for f in swat_files if '.mgt' in f and f != 'output.mgt']
        
        MGTFiles = dict()
        for mgtfile in mgt_files:
            cline = 0
            with open(self.swat_path + '/Scenarios/Default/TxtInOut/' + mgtfile) as search:
                for line in search:
                    if cline == 0:
                        linesplit = re.split('\s',line)
                        for sptline in linesplit:
                            if 'HRU' in sptline and cline == 0:
                                sptline = re.split(':',sptline)
                                MGTFiles[int(sptline[1])] = mgtfile
                                cline = cline + 1                         
        
        self.MGTFiles = MGTFiles
    
    #%% Copy the output files from one iteration
    def CopyOutputFiles(self):
        swat_files  = os.listdir(self.swat_path + '/Scenarios/Default/TxtInOut/')
        out_files = [f for f in swat_files if 'output' in f]
        for base in out_files:
            file_path = self.output_path + '/' + os.path.splitext(base)[0] + '_' + str(self.iter) + os.path.splitext(base)[1]
            shutil.copyfile(self.swat_path + '/Scenarios/Default/TxtInOut/' + base, file_path)
   
    #%% Write input summary (.csv)
    
    def OpenInputcsv(self):
        self.csv_file = self.output_path + 'SA_Inputs.csv'
        self.filein = open(self.csv_file,'w')
        self.filein.write('ITER, CROP, SUBID, UNIT_TYPE, UNIT_ID, TIME (YEAR) \n')
    
    def WriteInputs(self):
        
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
#zipswat_path = 'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11\Test_SWAT.zip'
#SA = SensitivityAnalysis(zipswat_path)

swat_path = 'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11\ITER_0'
output_path = 'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\Txtinout_v4_Iter11\ITER_TEST'
SA = SensitivityAnalysis(swat_path)

SA.CopyOutputFiles()



#input_files = 'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Iter11_txtinout_crop_operations\SWAT12_Input_Files.txt'
#
#for i in range(0,1):
#    sensitivity = SensitivityAnalysis(input_files)
#    sensitivity.outputcsv = 0
#    sensitivity.inputcsv = 0
#
#    sensitivity.swat_exe = 'swat_debug32.exe'
#    sensitivity.RunAnalysis(i)

