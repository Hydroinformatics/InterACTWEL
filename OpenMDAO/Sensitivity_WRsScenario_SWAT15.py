# -*- coding: utf-8 -*-

import os, shutil, sys, re, subprocess, pyodbc
import numpy as np
import csv, json

#%%
def FindHRUID(model_path):
    print model_path
    db_path = model_path
# Eric - testing something based on https://docs.microsoft.com/en-us/sql/connect/python/pyodbc/step-3-proof-of-concept-connecting-to-sql-using-pyodbc?view=sql-server-ver15
#        r'DRIVER={ODBC Driver 17 for SQL Server};' # Didn't work; reverted changes
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + db_path + ';'
        )
    cnxn = pyodbc.connect(conn_str)
    crsr = cnxn.cursor()
    
    crsr.execute('select * from hrus')
    hrudict = dict()
    for row in crsr.fetchall():
        hrudict[str(row[12])] = row[0]

    return hrudict

#%%
def GetWaterRigthHRU(input_files, model_path, outpath, itern):
    
    wr_swat_file = []
    wsrc_sum = dict()
    hrugis_dict = dict()
    wrsrc = dict()
    
    with open(input_files['wrtfile'],'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            
            if int(linesplit[2]) not in wsrc_sum and int(linesplit[2]) != 0:
                    wsrc_sum[int(linesplit[2])] = 0
                    #hru_wsrc[int(linesplit[2])] = []
                    
            if len(linesplit) > 0 and int(linesplit[0]) != 9999 and int(linesplit[0])==1:
                wr_swat_file.append([int(linesplit[1]), int(linesplit[2]), int(linesplit[3]), int(linesplit[4]), int(linesplit[5]), int(linesplit[6])])
                wrsrc[int(linesplit[1])] = int(linesplit[2])
                
            if int(linesplit[2]) != 0 and int(linesplit[0])==1:
                wsrc_sum[int(linesplit[2])] = wsrc_sum[int(linesplit[2])] + int(linesplit[3])
                #hru_wsrc[int(linesplit[2])].append(int(linesplit[1]))
                
    search.close()
    
#    num_year_sim = 12
#    csv_file = outpath + '/wrdata_CR_iter_' + str(itern) + '.dat'
#    filein = open(csv_file,'w')
#    
#    for yr in range(0,num_year_sim):
#        for i in range(len(wr_swat_file)):
#            atxt = str(yr+1).rjust(4) + ''.rjust(3)
#            atxt = atxt + str(wr_swat_file[i][0]).rjust(5) + ''.rjust(3)
#            atxt = atxt + str(wr_swat_file[i][1]).rjust(4)  + ''.rjust(3)
#            atxt = atxt + str(int(wr_swat_file[i][2])).rjust(6)  + ''.rjust(3)
#            atxt = atxt + str(wr_swat_file[i][3]).rjust(4)  + ''.rjust(3)
#            atxt = atxt + str(wr_swat_file[i][4]).rjust(4)
#            #if yr == num_year_sim-1 and i == len(wr_swat_file)
#            filein.write(atxt + '\n') 
#    filein.close()

    hruwr = dict()
    with open(input_files['hruwrt_file'],'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if len(linesplit) > 0:
                if int(linesplit[0]) not in hruwr.keys():
                    hruwr[int(linesplit[0])] = dict()
                    #hruwr[int(linesplit[0])][int(linesplit[3])] = [int(linesplit[1]),int(linesplit[2]),int(linesplit[3])]
                #else:
                hruwr[int(linesplit[0])][int(linesplit[4])] = [int(linesplit[1]),int(linesplit[2]),int(linesplit[3]),int(linesplit[4])]
    
    search.close()
    
    hrugis_dict = FindHRUID(input_files['model_database'])
    
    hru_nowa = dict()
    ct = 0
    with open(input_files['hru_nowa_file'],'rb') as search:
        for line in search:
            linesplit = re.split(',',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if '\r\n' in line:
                linesplit[6] = linesplit[6].strip('\r\n')
                
            if len(linesplit) > 0 and ct > 0:
                #print hrugis_dict[linesplit[6]]
                if hrugis_dict[linesplit[6]] not in hru_nowa.keys() and hruwr[hrugis_dict[linesplit[6]]][1][0] != 9999 and len(hruwr[hrugis_dict[linesplit[6]]]) == 1:                    
                    for i in hruwr[hrugis_dict[linesplit[6]]].keys():
                        if hruwr[hrugis_dict[linesplit[6]]][i][1] == 3 and hrugis_dict[linesplit[6]] not in hru_nowa.keys():
                            hru_nowa[hrugis_dict[linesplit[6]]] = [i, hruwr[hrugis_dict[linesplit[6]]][i][0]]
                            
#                if hrugis_dict[linesplit[6].strip('\r\n')] not in hru_nowa.keys() and hruwr[hrugis_dict[linesplit[6].strip('\r\n')]][1][0] != 9999 and len(hruwr[hrugis_dict[linesplit[6].strip('\r\n')]]) == 1:                    
#                    for i in hruwr[hrugis_dict[linesplit[6].strip('\r\n')]].keys():
#                        if hruwr[hrugis_dict[linesplit[6].strip('\r\n')]][i][1] == 3 and hrugis_dict[linesplit[6].strip('\r\n')] not in hru_nowa.keys():
#                            hru_nowa[hrugis_dict[linesplit[6].strip('\r\n')]] = [i, hruwr[hrugis_dict[linesplit[6].strip('\r\n')]][i][0]]

            ct = ct + 1
                    
    search.close()
    
    return wr_swat_file, wrsrc, wsrc_sum, hruwr, hru_nowa

#%%
def run_SWAT(model_path, swat_exe):
    cwdir = os.getcwd()
    os.chdir(model_path + '/Scenarios/Default/TxtInOut')
    exitflag = subprocess.check_call([swat_exe])
    if exitflag == 0:
        print "Successful SWAT run"
    else:
        print exitflag
    os.chdir(cwdir)
    
#%%
# def GetWaterUsed(outpath, itern):
#     hru_wr_use = dict()
#     with open(outpath + '/hru_wrt_' + str(itern) + '.out','rb') as search:
#         first_line = search.readline()
#         for line in search:
#             linesplit = re.split('\s',line)
#             linesplit = [t for t in linesplit if len(t) > 0]
#             if int(linesplit[0]) != 0:
#                 if int(linesplit[0]) not in hru_wr_use.keys():
#                     hru_wr_use[int(linesplit[0])] = dict()
                
#                 if int(linesplit[1]) not in hru_wr_use[int(linesplit[0])].keys():
#                     hru_wr_use[int(linesplit[0])][int(linesplit[1])] = dict()
        
#                 hru_wr_use[int(linesplit[0])][int(linesplit[1])][int(linesplit[5])] = float(linesplit[4])
    
#     search.close()
    
#     wrs_use = dict()
#     with open(outpath + '/wrs_use_' + str(itern) + '.out','rb') as search:
#         first_line = search.readline()
#         for line in search:
#             linesplit = re.split('\s',line)
#             linesplit = [t for t in linesplit if len(t) > 0]
#             if int(linesplit[0]) not in wrs_use.keys():
#                 wrs_use[int(linesplit[0])] = dict()
            
#             wrs_use[int(linesplit[0])][int(linesplit[2])] = float(linesplit[1])
    
#     search.close()
    
#     return hru_wr_use, wrs_use
    
#%%

cdir = os.getcwd()

input_files = dict()
   
input_files['wrtfile'] = cdir+'/wrdata_CR.dat'
input_files['hruwrt_file'] = cdir+'/hruwr_CR.dat'
input_files['hru_nowa_file'] = cdir+'/NOWA_HRU_pumping_limit.csv'
input_files['model_database'] = cdir+'/BASE/Umatilla_InterACTWEL_QSWATv4.mdb'
input_files['base_irr'] = cdir+'/BASE_HRU_IRR.csv'

print input_files['model_database']

model_path = cdir+'/BASE'
outpath = cdir+'/ITER17'

irr_dict = {0: 'No irrigation', 1: 'Surface water', 2: 'Storage/Reservoir', 3: 'Groundwater', 5: 'Columbia River'}

itern = 0
build_model = 0
modeln = 17

wr_swat_file, wrsrc, wsrc_sum, hruwr, hru_nowa = GetWaterRigthHRU(input_files, model_path, outpath, itern)

#scenarios  = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55]
scenarios  = [0.98, 1]

if build_model == 1:
    
    print "Creating Scenarios"
    
    hru_irr = [] # This section needs to be automated: using output.std
    with open(input_files['base_irr'],'rb') as search:
        for line in search:
            linesplit = re.split(',',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            if len(linesplit) > 0 and int(linesplit[0]) in hru_nowa.keys():
                hru_irr.append([int(linesplit[0]),hru_nowa[int(linesplit[0])][0],hru_nowa[int(linesplit[0])][1], float(linesplit[2].strip('\r\n'))])
       
    hru_irr = np.asarray(sorted(np.asarray(hru_irr), key=lambda x: (x[1], -x[3])))         
    
    CR_wrs = []
    for i in range(len(wr_swat_file)):
        if wr_swat_file[i][1] == 5:
            CR_wrs.append(wr_swat_file[i])
    
    for itern in range(len(scenarios)): 
          
        CR_wrs = np.asarray(sorted(np.asarray(CR_wrs), key=lambda x: (-x[2], x[3])))
        CR_wrs = CR_wrs[CR_wrs[:,2]> 5000]
        np.random.shuffle(CR_wrs)
    
        new_CR_vol = wsrc_sum[3]*scenarios[itern]
        
        scenario_wsrc = np.random.rand(len(CR_wrs))
        scenario_wsrc = (scenario_wsrc/np.sum(scenario_wsrc))*new_CR_vol
        
        new_hruwr = dict()
        cr_wrdist = dict()
        
        #check hru 12
        file_path = model_path + '/Scenarios/Default/TxtInOut/wrdata.dat'
        shutil.copyfile(input_files['wrtfile'], file_path)
        
        if scenarios[itern] > 0:
            cr_wr_counter = 0
            for i in range(len(hru_irr)):
                new_hruwr[int(hru_irr[i,0])] = dict()
                if CR_wrs[cr_wr_counter,0] not in cr_wrdist.keys():
                    cr_wrdist[CR_wrs[cr_wr_counter,0]] = dict()
                    cr_wrdist[CR_wrs[cr_wr_counter,0]]['per_given'] = scenario_wsrc[cr_wr_counter]
                    cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'] = []
                
                temp = scenario_wsrc[cr_wr_counter] - wr_swat_file[int(hru_irr[i,2])][2]
                
                if temp < 0:
                    new_hruwr[hru_irr[i,0]][1] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],1]
                    cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
                    cr_wr_counter = cr_wr_counter + 1
                    
                    if cr_wr_counter < len(CR_wrs):
                        new_hruwr[int(hru_irr[i,0])][2] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],2]
                        cr_wrdist[CR_wrs[cr_wr_counter,0]] = dict()
                        cr_wrdist[CR_wrs[cr_wr_counter,0]]['per_given'] = scenario_wsrc[cr_wr_counter]
                        cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'] = []
                        cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
                        
                    else:
                        #print int(hru_irr[i,0])
                        new_hruwr[int(hru_irr[i,0])][2] = [hruwr[int(hru_irr[i,0])][1][0],hruwr[int(hru_irr[i,0])][1][1],hruwr[int(hru_irr[i,0])][1][2],2]
                        
                        break
                else:
                    new_hruwr[int(hru_irr[i,0])][1] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],1]
                    cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
                    scenario_wsrc[cr_wr_counter] = temp
               
            with open(outpath + '/CR_wr_dist_' + str(itern) + '.json', 'w+') as fp:
                json.dump(cr_wrdist, fp)        
           
        csv_file = outpath + '/hruwr_CR_' + str(itern) + '.dat'
        filein = open(csv_file,'w+')
        
        #atxt = 'HRU_ID, WR_ID, PRIOR, HRU_PRIOR'
        
        for i in range(1,len(hruwr)+1):
            if i in new_hruwr.keys():
                for ii in new_hruwr[i].keys():
                    atxt = str(i).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(new_hruwr[i][ii][0]).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(new_hruwr[i][ii][1]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(new_hruwr[i][ii][2]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(new_hruwr[i][ii][3]).rjust(4)
                    filein.write(atxt + '\n') 
            else:
                for ii in hruwr[i].keys():
                    atxt = str(i).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(hruwr[i][ii][0]).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(hruwr[i][ii][1]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(hruwr[i][ii][2]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(hruwr[i][ii][3]).rjust(4)
        
                    filein.write(atxt + '\n') 
        filein.close()
        
        file_path = model_path + '/Scenarios/Default/TxtInOut/hruwr.dat'
        shutil.copyfile(csv_file, file_path)
        
        print 'Iter #: ' + str(itern)
        run_SWAT(model_path, 'swat_rel64.exe')
        
            
        swat_files  = os.listdir(model_path + '/Scenarios/Default/TxtInOut/')
        out_files = [f for f in swat_files if 'output' in f]
            
            
        for base in out_files:
            if 'mgt' not in os.path.splitext(base)[1]:
                file_path = outpath + '/' + os.path.splitext(base)[0] + '_' + str(itern) + os.path.splitext(base)[1]
                shutil.copyfile(model_path + '/Scenarios/Default/TxtInOut/' + base, file_path)
            
        
        hrw_file_out = model_path + '/Scenarios/Default/TxtInOut/hru_wrt.out'
        file_path = outpath + '/' + os.path.splitext('hru_wrt.out')[0] + '_' + str(itern) + os.path.splitext('hru_wrt.out')[1]
        shutil.copyfile(hrw_file_out, file_path)
        
        hrw_file_out = model_path + '/Scenarios/Default/TxtInOut/wrs_use.out'
        file_path = outpath + '/' + os.path.splitext('wrs_use.out')[0] + '_' + str(itern) + os.path.splitext('wrs_use.out')[1]
        shutil.copyfile(hrw_file_out, file_path)
        
# else:
    
#     print "Extracting Scenario Results"
      
#     output_vars_file =  cdir+'/OutputVars_Arjan_CR.txt'
#     output_vars = GetOutputVars(output_vars_file)
    
#     cropnames = FindCropName(model_path)
    
#     csv_file = outpath + '/Arjan_Data_' + str(modeln) + '.csv'
#     filein = open(csv_file,'w+')  
    
#     for itern in range(len(scenarios)): 
            
#         input_files['hruwrt_file'] = outpath + '/hruwr_CR_' + str(itern) + '.dat'
#         wr_swat_file, wrsrc, wsrc_sum, hruwr, hru_nowa = GetWaterRigthHRU(input_files, model_path, outpath, itern)
#         output_vars_data = GetOutputData(outpath, output_vars, itern)
#         hru_wr_use, wrs_use = GetWaterUsed(outpath, itern)
        
#         temp_dict = dict()
#         temp_all, temp_basin = HRU_SUBDict(output_vars_data, cropnames, wrsrc, hruwr, irr_dict, hru_wr_use, wrs_use)
        
        
#     #    for subid in temp_all['hru_sub'].keys():
#     #        wr_amt[subid] = dict()
#     #        for wsrc in temp_all['hru_sub'][subid].keys():
#     #            for hhruid, priort in temp_all['hru_sub'][subid][wsrc]:
                
#         wr_amt = dict()
#         for hrui in output_vars_data['SUB'].keys():
#             if output_vars_data['SUB'][hrui][0] not in wr_amt.keys() and hrui is not 'Type' and hrui is not 'Years':
#                 wr_amt[int(output_vars_data['SUB'][hrui][0])] = dict()
            
#             if hrui is not 'Type' and hrui is not 'Years':
#                 for wrs_hru in hruwr[int(hrui)].keys():
#                     if hruwr[int(hrui)][wrs_hru][0] != 9999 and hruwr[int(hrui)][wrs_hru][1] not in wr_amt[int(output_vars_data['SUB'][hrui][0])].keys():
#                         wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]] = dict()
#                         wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['Sum'] = 0
#                         wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['WR'] = []
                        
#                     if hruwr[int(hrui)][wrs_hru][0] != 9999 and hrui not in wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]] and wr_swat_file[hruwr[int(hrui)][wrs_hru][0]][0] not in wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['WR']:
#                         wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['Sum'] = wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['Sum'] + wr_swat_file[hruwr[int(hrui)][wrs_hru][0]][2]
#                         wr_amt[int(output_vars_data['SUB'][hrui][0])][hruwr[int(hrui)][wrs_hru][1]]['WR'].append(wr_swat_file[hruwr[int(hrui)][wrs_hru][0]][0])
        
#         ucrop = []
#         for hrui in output_vars_data['LULC'].keys():
#             if hrui is not 'Type' and hrui is not 'Years':
#                 for cropn in output_vars_data['LULC'][hrui]:
#                     if cropn.islower():
#                         cropn = 'AGRL'
#                     if cropn not in ucrop:
#                         ucrop.append(cropn)
        
#         actor = dict()
#         actor_c = 1 
#         for subid in temp_all['hru_sub'].keys():
#             for wr in irr_dict.keys():
#                 if subid not in actor.keys():
#                     actor[subid] = dict()
#                 actor[subid][wr] = actor_c 
#                 actor_c = actor_c + 1
                
        
#         if itern == 0:
#             atxt = 'ITER, REDUCTION OF GW WR (PER), ACTOR, SUB ID, WR SRC, WR AMT, YEAR,'
#             for n in range(0,2):
#                 for u in ucrop:
#                     atxt = atxt + str(cropnames[u]) + ','
#             for irrid in irr_dict.keys():
#                 atxt = atxt + str(irr_dict[irrid]) + ','
            
#             atxt = atxt + 'N Fertilizer, P Fertilizer, Groundwater Recharge (acre-ft),	Surface runoff Nitrate (kg N), Lateral flow Nitrate (kg N), Groundwater Nitrate (kg N),'
#             for u in ucrop:
#                     atxt = atxt + 'Profit ' + str(cropnames[u]) + ','
            
#             atxt = atxt + 'Crop Profit ($), Costs ($), Total Profit ($),'
#             filein.write(atxt + '\n')
            
#         yr = 1
#         for iy in output_vars_data['LULC']['Years']:
#             #actor_c = 1                
#             for subid in temp_all['hru_sub'].keys():
#                 #for wr in temp_all['hru_sub'][subid].keys():
#                 for wr in irr_dict.keys():
#                     if wr != 0:
#                         if wr in temp_all['hru_sub'][subid].keys(): 
#                             actor_c = actor[subid][wr]
#                             if itern == 0:
#                                 temptxt = 'BASE,' + str(scenarios[itern]*100) + ',' + str(actor_c) + ',' + str(subid) + ',' + str(irr_dict[wr]) + ',' + str(wr_amt[subid][wr]['Sum']) + ',' + str(iy) + ','
#                             else:
#                                 temptxt = str(itern) + ',' + str(scenarios[itern]*100) + ',' + str(actor_c) + ',' + str(subid) + ',' + str(irr_dict[wr]) + ',' + str(wr_amt[subid][wr]['Sum']) + ',' + str(iy) + ','
                            
#                             for uc in ucrop:
#                                 if uc in temp_all['Planted crops (ha)'][subid][wr].keys():
#                                     temptxt = temptxt + str(temp_all['Planted crops (ha)'][subid][wr][uc]['Data'][yr]) + ','
#                                 else:
#                                     temptxt = temptxt + str(0.0) + ','
                                    
#                             for uc in ucrop:
#                                 if uc in temp_all['Crop yield (kg)'][subid][wr].keys():
#                                     temptxt = temptxt + str(temp_all['Crop yield (kg)'][subid][wr][uc]['Data'][yr]) + ','
#                                 else:
#                                     temptxt = temptxt + str(0.0) + ','
                            
#                             for ir in irr_dict.keys():
#                                 if ir == wr:
#                                     temptxt = temptxt + str(temp_all['Irrigation (acre-ft)'][subid][wr]['Data'][yr]) + ','
#                                 else:
#                                     temptxt = temptxt + str(0.0) + ','
                                
#                             temptxt = temptxt + str(temp_all['N fertilizer (kg N)'][subid][wr][yr]) + ',' + str(temp_all['P fertilizer (kg N)'][subid][wr][yr]) + ','
#                             temptxt = temptxt + str(temp_all['Groundwater Recharge (acre-ft)'][subid][wr][yr]) + ',' + str(temp_all['Surface runoff Nitrate (kg N)'][subid][wr][yr]) + ',' + str(temp_all['Lateral flow Nitrate (kg N)'][subid][wr][yr]) + ',' + str(temp_all['Groundwater Nitrate (kg N)'][subid][wr][yr])
#                             #actor_c = actor_c + 1
#                         else:
#                             actor_c = actor[subid][wr]
#                             if itern == 0:
#                                 temptxt = 'BASE,' + str(scenarios[itern]*100) + ',' + str(actor_c) + ',' + str(subid) + ',' + str(irr_dict[wr]) + ',' + str(0) + ',' + str(iy) + ','
#                             else:
#                                 temptxt = str(itern) + ',' + str(scenarios[itern]*100) + ',' + str(actor_c) + ',' + str(subid) + ',' + str(irr_dict[wr]) + ',' + str(0) + ',' + str(iy) + ','
                                
#                             for uc in ucrop:
#                                 temptxt = temptxt + str(0.0) + ','
#                             for uc in ucrop:
#                                 temptxt = temptxt + str(0.0) + ','
#                             for ir in irr_dict.keys():
#                                 temptxt = temptxt + str(0.0) + ','
                            
#                             temptxt = temptxt + str(0) + ',' + str(0) + ','
#                             temptxt = temptxt + str(0) + ',' + str(0) + ',' + str(0) + ',' + str(0)
                            
#                         filein.write(temptxt + '\n')
                        
#             yr = yr + 1

# filein.close()
    
    
    
# #%%
# #    wrdict = dict()
# #    for wrid in range(len(wr_swat_file)):
# #        if wr_swat_file[wrid][0] not in wrdict.keys():
# #            wrdict[wr_swat_file[wrid][0]] = []
# #            
# #    for hruid in hruwr.keys():
# #        for ii in hruwr[hruid]:
# #            #if hruwr[hruid][ii][0] != 9999:
# #            wrdict[hruwr[hruid][ii][0]].append(hruid)