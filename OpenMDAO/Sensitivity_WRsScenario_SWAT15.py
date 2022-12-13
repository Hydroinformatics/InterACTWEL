# -*- coding: utf-8 -*-

import os, shutil, sys, re, subprocess
import numpy as np
import csv, json
import matplotlib.pyplot as plt
import pyodbc
import shapefile

#%%
def FindHRUID(model_path):
    print(model_path)
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
def GetWaterRigthHRU(input_files):
    
    wr_swat_file = []
    wsrc_sum = dict()
    hrugis_dict = dict()
    wrsrc = dict()
    
    with open(input_files['wrtfile'],'rb') as search:
        for line in search:
            line = str(line.decode('UTF-8'))
            if 'YEAR_ID' not in line:
                linesplit = re.split('\s',line)
                linesplit = [t for t in linesplit if len(t) > 0]
                
                if int(linesplit[2]) not in wsrc_sum and int(linesplit[2]) != 0:
                        wsrc_sum[int(linesplit[2])] = 0
                        #hru_wsrc[int(linesplit[2])] = []
                        
                if len(linesplit) > 0 and int(linesplit[1]) != 9999 and int(linesplit[0])==1:
                    wr_swat_file.append([int(linesplit[1]), int(linesplit[2]), int(linesplit[3]), int(linesplit[4]), int(linesplit[5])])
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
            line = str(line.decode('UTF-8'))
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
            line = str(line.decode('UTF-8'))
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
        print("Successful SWAT run")
    else:
        print(exitflag)
    os.chdir(cwdir)

    
#%%

cdir = os.getcwd()

input_files = dict()
   
input_files['wrtfile'] = cdir +'/SWAT_WR_files/wrdata.dat'
input_files['hruwrt_file'] = cdir +'/SWAT_WR_files/hruwr.dat'
input_files['hru_nowa_file'] = cdir +'/SWAT_WR_files/NOWA_HRU_pumping_limit.csv'
input_files['model_database'] = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\Umatilla_InterACTWEL_QSWATv4.mdb'
input_files['base_irr'] = cdir +'/SWAT_WR_files/BASE_HRU_IRR.csv'
input_files['wrt_out_file'] = cdir +'/SWAT_WR_files/wrs_use.out'


print(input_files['model_database'])

#model_path = cdir +'/BASE'
model_path = r'C:\Users\riversam\Box\Research\SWAT\QSWAT\Backup_v4_Iter15_bestsim\Backup'

#outpath = cdir +'/ITER17'
outpath = r'C:\Users\riversam\Box\Research\SWAT\QSWAT\Backup_v4_Iter15_bestsim\ITER0'

irr_dict = {0: 'No irrigation', 1: 'Surface water', 2: 'Storage/Reservoir', 3: 'Groundwater', 5: 'Columbia River'}

itern = 0
build_model = 1
modeln = 17

hrugis_dict = FindHRUID(input_files['model_database'])

wr_swat_file, wrsrc, wsrc_sum, hruwr, hru_nowa = GetWaterRigthHRU(input_files)

#%%

wruse_base = dict()
with open(input_files['wrt_out_file'],'rb') as search:
    for line in search:
        line = str(line.decode('UTF-8'))
        linesplit = re.split('\s',line)
        linesplit = [t for t in linesplit if len(t) > 0]
        if len(linesplit) > 0 and 'WRID' not in linesplit[0]:
            if int(linesplit[0]) not in wruse_base.keys():
                wruse_base[int(linesplit[0])] = dict()

            wruse_base[int(linesplit[0])][int(linesplit[2])] = float(linesplit[1])

search.close()


#%%

total_per_yr = dict()
wrscr_yr = np.zeros((5,len(range(1997,2019))))
cyr = 0
for yr in range(1997,2019):
    tmp_sum = 0
    for wrid in wruse_base.keys():
        tmp_sum  = tmp_sum + wruse_base[wrid][yr]
        if wrid != 9999:
            temp_wrscr = wr_swat_file[wrid-1][1]
            if temp_wrscr == 5:
                temp_wrscr = 4
        
            wrscr_yr[temp_wrscr, cyr] = wrscr_yr[temp_wrscr, cyr] + wruse_base[wrid][yr]

    total_per_yr[yr] = tmp_sum

    cyr = cyr + 1

per_wrscr_yr = (wrscr_yr/np.sum(wrscr_yr,axis=0))*100

per_hru_yr = np.zeros((len(wruse_base),len(range(1997,2019))))
per_hru = np.zeros((len(wruse_base),len(range(1997,2019))))

cyr = 0
for yr in range(1997,2019):
    tmp_sum = 0
    for wrid in wruse_base.keys():
        if wrid < 9999:
            per_hru_yr[wrid,cyr] = (wruse_base[wrid][yr]/total_per_yr[yr])*100
            per_hru[wrid,cyr] = (wruse_base[wrid][yr]/wr_swat_file[wrid-1][2])*100
    
    cyr = cyr + 1


hruwr_c = []
for hruid in hruwr.keys():
    if hruwr[hruid][1][0] < 9999:
        hruwr_c.append([hruid,len(hruwr[hruid])])
    else:
        hruwr_c.append([hruid,0])
        
hruwr_c = np.asarray(hruwr_c)


#%%

shp_dir = r"C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs"

hru_nowa = shapefile.Reader(shp_dir + '/' + 'hru2_NOWA_pumping_limit.shp')
hru_nowa_records = hru_nowa.records()

hruid_nowa = []
for i in range(0,len(hru_nowa_records)):
    hruid_nowa.append((hrugis_dict[hru_nowa_records[i][6]]))
hruid_nowa = np.asarray(hruid_nowa)


hru_portMorrow = shapefile.Reader(shp_dir + '/' + 'HRUs_Port_Morrow.shp')
hru_portMorrow_records = hru_portMorrow.records()

hruid_portMorrow = []
for i in range(0,len(hru_portMorrow_records)):
    hruid_portMorrow.append((hrugis_dict[hru_portMorrow_records[i][6]]))
hruid_portMorrow = np.asarray(hruid_portMorrow)


mtg_file = r'C:\Users\riversam\Box\Research\SWAT\QSWAT\Backup_v4_Iter15_bestsim\Backup'
fnames = os.listdir(mtg_file)
fnames = [ff for ff in fnames if '.mgt' in ff]
file_prop = list()
for ff in fnames:
    file_size = os.path.getsize(mtg_file + '/' + ff)
    file_prop.append((ff[:-4],file_size))

#%%


# #scenarios  = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55]
# scenarios  = [0.98, 1]

if build_model == 1:
    
#     print "Creating Scenarios"
    
#     hru_irr = [] # This section needs to be automated: using output.std
#     with open(input_files['base_irr'],'rb') as search:
#         for line in search:
#             linesplit = re.split(',',line)
#             linesplit = [t for t in linesplit if len(t) > 0]
#             if len(linesplit) > 0 and int(linesplit[0]) in hru_nowa.keys():
#                 hru_irr.append([int(linesplit[0]),hru_nowa[int(linesplit[0])][0],hru_nowa[int(linesplit[0])][1], float(linesplit[2].strip('\r\n'))])
       
#     hru_irr = np.asarray(sorted(np.asarray(hru_irr), key=lambda x: (x[1], -x[3])))         
    
    CR_wrs = []
    for i in range(len(wr_swat_file)):
        if wr_swat_file[i][1] == 5:
            CR_wrs.append(wr_swat_file[i])
    
#     for itern in range(len(scenarios)): 
          
#         CR_wrs = np.asarray(sorted(np.asarray(CR_wrs), key=lambda x: (-x[2], x[3])))
#         CR_wrs = CR_wrs[CR_wrs[:,2]> 5000]
#         np.random.shuffle(CR_wrs)
    
#         new_CR_vol = wsrc_sum[3]*scenarios[itern]
        
#         scenario_wsrc = np.random.rand(len(CR_wrs))
#         scenario_wsrc = (scenario_wsrc/np.sum(scenario_wsrc))*new_CR_vol
        
    new_hruwr = dict()
    cr_wrdist = dict()
        
#         #check hru 12
    file_path = model_path + '/wrdata.dat'
    shutil.copyfile(input_files['wrtfile'], file_path)
        
#         if scenarios[itern] > 0:
#             cr_wr_counter = 0
#             for i in range(len(hru_irr)):
#                 new_hruwr[int(hru_irr[i,0])] = dict()
#                 if CR_wrs[cr_wr_counter,0] not in cr_wrdist.keys():
#                     cr_wrdist[CR_wrs[cr_wr_counter,0]] = dict()
#                     cr_wrdist[CR_wrs[cr_wr_counter,0]]['per_given'] = scenario_wsrc[cr_wr_counter]
#                     cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'] = []
                
#                 temp = scenario_wsrc[cr_wr_counter] - wr_swat_file[int(hru_irr[i,2])][2]
                
#                 if temp < 0:
#                     new_hruwr[hru_irr[i,0]][1] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],1]
#                     cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
#                     cr_wr_counter = cr_wr_counter + 1
                    
#                     if cr_wr_counter < len(CR_wrs):
#                         new_hruwr[int(hru_irr[i,0])][2] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],2]
#                         cr_wrdist[CR_wrs[cr_wr_counter,0]] = dict()
#                         cr_wrdist[CR_wrs[cr_wr_counter,0]]['per_given'] = scenario_wsrc[cr_wr_counter]
#                         cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'] = []
#                         cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
                        
#                     else:
#                         #print int(hru_irr[i,0])
#                         new_hruwr[int(hru_irr[i,0])][2] = [hruwr[int(hru_irr[i,0])][1][0],hruwr[int(hru_irr[i,0])][1][1],hruwr[int(hru_irr[i,0])][1][2],2]
                        
#                         break
#                 else:
#                     new_hruwr[int(hru_irr[i,0])][1] = [CR_wrs[cr_wr_counter,0],5,CR_wrs[cr_wr_counter,5],1]
#                     cr_wrdist[CR_wrs[cr_wr_counter,0]]['hrus'].append(int(hru_irr[i,0]))
#                     scenario_wsrc[cr_wr_counter] = temp
               
#             with open(outpath + '/CR_wr_dist_' + str(itern) + '.json', 'w+') as fp:
#                 json.dump(cr_wrdist, fp)        
           
#         csv_file = outpath + '/hruwr_CR_' + str(itern) + '.dat'
#         filein = open(csv_file,'w+')
        
#         #atxt = 'HRU_ID, WR_ID, PRIOR, HRU_PRIOR'
        
#         for i in range(1,len(hruwr)+1):
#             if i in new_hruwr.keys():
#                 for ii in new_hruwr[i].keys():
#                     atxt = str(i).rjust(6) + ''.rjust(3)
#                     atxt = atxt + str(new_hruwr[i][ii][0]).rjust(6) + ''.rjust(3)
#                     atxt = atxt + str(new_hruwr[i][ii][1]).rjust(4) + ''.rjust(3)
#                     atxt = atxt + str(new_hruwr[i][ii][2]).rjust(4) + ''.rjust(3)
#                     atxt = atxt + str(new_hruwr[i][ii][3]).rjust(4)
#                     filein.write(atxt + '\n') 
#             else:
#                 for ii in hruwr[i].keys():
#                     atxt = str(i).rjust(6) + ''.rjust(3)
#                     atxt = atxt + str(hruwr[i][ii][0]).rjust(6) + ''.rjust(3)
#                     atxt = atxt + str(hruwr[i][ii][1]).rjust(4) + ''.rjust(3)
#                     atxt = atxt + str(hruwr[i][ii][2]).rjust(4) + ''.rjust(3)
#                     atxt = atxt + str(hruwr[i][ii][3]).rjust(4)
        
#                     filein.write(atxt + '\n') 
#         filein.close()
        
        # file_path = model_path + '/Scenarios/Default/TxtInOut/hruwr.dat'
        # shutil.copyfile(csv_file, file_path)
        
        # print 'Iter #: ' + str(itern)
        # run_SWAT(model_path, 'swat_rel64.exe')
        
            
        # swat_files  = os.listdir(model_path + '/Scenarios/Default/TxtInOut/')
        # out_files = [f for f in swat_files if 'output' in f]
            
            
        # for base in out_files:
        #     if 'mgt' not in os.path.splitext(base)[1]:
        #         file_path = outpath + '/' + os.path.splitext(base)[0] + '_' + str(itern) + os.path.splitext(base)[1]
        #         shutil.copyfile(model_path + '/Scenarios/Default/TxtInOut/' + base, file_path)
            
        
        # hrw_file_out = model_path + '/Scenarios/Default/TxtInOut/hru_wrt.out'
        # file_path = outpath + '/' + os.path.splitext('hru_wrt.out')[0] + '_' + str(itern) + os.path.splitext('hru_wrt.out')[1]
        # shutil.copyfile(hrw_file_out, file_path)
        
        # hrw_file_out = model_path + '/Scenarios/Default/TxtInOut/wrs_use.out'
        # file_path = outpath + '/' + os.path.splitext('wrs_use.out')[0] + '_' + str(itern) + os.path.splitext('wrs_use.out')[1]
        # shutil.copyfile(hrw_file_out, file_path)
        
