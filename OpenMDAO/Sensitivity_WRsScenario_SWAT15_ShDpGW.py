# -*- coding: utf-8 -*-

import os, shutil, sys, re, subprocess
import numpy as np
import csv, json
import matplotlib.pyplot as plt
import pyodbc
import shapefile

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

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

def f(frame):
    """A function to calculate overlap percentage"""
    interpct = 100*frame.g1.intersection(frame.g2).area/frame.g1.area
    return interpct

#%%

cdir = os.getcwd()
input_files = dict()

input_files['wrtfile'] = cdir +'/SWAT_WR_files/wrdata_deepGW_CR.dat'
input_files['hruwrt_file'] = cdir +'/SWAT_WR_files/hruwr_deepGW_CR.dat'
input_files['hru_nowa_file'] = cdir +'/SWAT_WR_files/NOWA_HRU_pumping_limit.csv'

input_files['model_database'] = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\Umatilla_InterACTWEL_QSWATv4.mdb'
#input_files['model_database'] = '/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/Umatilla_InterACTWEL_QSWATv4.mdb'
input_files['wrt_out_file'] = cdir +'/SWAT_WR_files/wrs_use.out'

print(input_files['model_database'])

model_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_Models_Umatilla\Backup_v4_Iter15_bestsim_CropsCalib_shallAndDeepGWWR\TxtInOut'
#model_path = '/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_Models_Umatilla/Backup_v4_Iter15_bestsim_CropsCalib_shallAndDeepGWWR/TxtInOut/'

#outpath = r'C:\Users\riversam\Box\Research\SWAT\QSWAT\Backup_v4_Iter15_bestsim\ITER0'
#cluster_path = '/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/'
cluster_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs'

irr_dict = {0: 'No irrigation', 1: 'Surface water', 2: 'Storage/Reservoir', 3: 'Shallow aquifer', 4: 'Deep aquifer', 5: 'Columbia River'}

shp_dir = cluster_path
data_path = cluster_path

#%%
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
years = range(1997,2007)
total_per_yr = dict()
wrscr_yr = np.zeros((6,len(years)))

# Get percent of water use per source per year
cyr = 0
for yr in years:
    tmp_sum = 0
    for wrid in wruse_base.keys():
        tmp_sum  = tmp_sum + wruse_base[wrid][yr]
        if wrid != 9999:
            temp_wrscr = wr_swat_file[wrid-1][1]
        
            wrscr_yr[temp_wrscr, cyr] = wrscr_yr[temp_wrscr, cyr] + wruse_base[wrid][yr]

    total_per_yr[yr] = tmp_sum
    cyr = cyr + 1
    
per_wrscr_yr = (wrscr_yr/np.sum(wrscr_yr,axis=0))*100

per_hru_yr = np.zeros((len(wruse_base),len(years)))
per_hru = np.zeros((len(wruse_base),len(years)))

# Get percent of water right use per year
cyr = 0
for yr in years:
    tmp_sum = 0
    for wrid in wruse_base.keys():
        if wrid < 9999:
            per_hru_yr[wrid,cyr] = (wruse_base[wrid][yr]/total_per_yr[yr])*100
            per_hru[wrid,cyr] = (wruse_base[wrid][yr]/wr_swat_file[wrid-1][2])*100
    
    cyr = cyr + 1

# Num. of WRs available to each HRU
hruwr_c = []
for hruid in hruwr.keys():
    if hruwr[hruid][1][0] < 9999:
        hruwr_c.append([hruid,len(hruwr[hruid])])
    else:
        hruwr_c.append([hruid,0])
        
hruwr_c = np.asarray(hruwr_c)


#%%

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
    hruid_portMorrow.append((hru_portMorrow_records[i][6], hrugis_dict[hru_portMorrow_records[i][6]]))
hruid_portMorrow = np.asarray(hruid_portMorrow)

crs = 'EPSG:26911'
subs = gpd.read_file(data_path + "/subs1.shp")
subs.to_crs(crs, inplace=True)

hrus2 = gpd.read_file(data_path + "/hru2.shp")
hrus2.to_crs(crs, inplace=True)

nowa = gpd.read_file(data_path + "/NOWA_hrus_pumping_limitsv3.shp")
nowa.to_crs(crs, inplace=True)


# #subs['g1'] = subs.geometry
# hrus2['g1'] = hrus2.geometry
# nowa['g2'] = nowa.geometry

# #gdf_joined = subs.sjoin(nowa, how="inner")
# gdf_joined = hrus2.sjoin(nowa, how="inner")
# gdf_joined['area_joined'] = gdf_joined.area
# #gdf_joined['sub_area'] = (gdf_joined['area_joined'] / gdf_joined['Shape_Area'])

# gdf_joined['pct'] = gdf_joined.apply(f, axis=1)

# #subs_nowa = [int(row['Subbasin']) for i, row in gdf_joined.iterrows() if row['pct'] >= 10]
# hrus_nowa = [int(row['Subbasin']) for i, row in gdf_joined.iterrows() if row['pct'] >= 10]

# fig, ax = plt.subplots()
# #subs.plot(ax=ax, facecolor='none', edgecolor = 'black', lw=0.7)
# hrus2.plot(ax=ax, facecolor='none', edgecolor = 'black', lw=0.7)
# nowa.plot(ax=ax, facecolor='yellow', edgecolor = 'black', alpha=0.7)

# # for sid in subs_nowa:
# #     subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax, facecolor='blue', alpha=0.5)

# # for sid in hrus_nowa:
# #     hrus2.loc[hrus2['Subbasin']==sid,'geometry'].plot(ax=ax, facecolor='blue', alpha=0.5)

#%% GET HRUS with IRR in their .mgt files and also have WRs (i.e., WR VOL != 9999)

mtg_file = model_path
fnames = os.listdir(mtg_file)
fnames = [ff for ff in fnames if '.mgt' in ff]
file_prop = list()
for ff in fnames:
    file_size = os.path.getsize(mtg_file + '/' + ff)
    file_prop.append((ff[:-4]))
    

hru_with_irr = []
ccounter = 1
for ii in range(0,len(hruid_portMorrow)):
    if str(hruid_portMorrow[ii][0]) in file_prop:
        with open(mtg_file + '/' + str(hruid_portMorrow[ii][0]) + '.mgt','rb') as search:
            strbool = 0    
            for line in search:
                line = line.decode("utf-8")
                
                if strbool == 1:
                    linesplit = line.split()
                    if len(linesplit) > 1:
                        if int(linesplit[1]) == 10:
                            hru_with_irr.append((hruid_portMorrow[ii]))
                            break
                            strbool = 0
                
                if "Operation Schedule:" in line:
                    strbool = 1
    ccounter += 1
    print(ccounter)
                
final_wr_list = []
for i in range(0,len(hru_with_irr)):
    hruid_temp = np.where(hruwr_c[:,0] == int(hru_with_irr[i][1]))
    if len(hruid_temp) > 0:
        if hruwr_c[hruid_temp[0][0],1] != 0:
            for wk in hruwr[int(hru_with_irr[i][1])].keys():
                #hruwr[int(hru_with_irr[i][1])][wk][0]
                final_wr_list.append(hruwr[int(hru_with_irr[i][1])][wk][0])

final_wr_list = np.asarray(np.unique(final_wr_list))
final_wr_list = np.delete(final_wr_list, np.where(final_wr_list == 9999))

#%%
CR_wrs = []
for i in range(len(wr_swat_file)):
    if wr_swat_file[i][1] == 5:
        CR_wrs.append(wr_swat_file[i])

temp_path = cluster_path + '/ITERS'
    isExist = os.path.exists(temp_path)
    if not isExist:
        os.makedirs(temp_path)

for iterrun in range(0,1):
#for iterrun in range(0,len(final_wr_list)+1):
#     print "Creating Scenarios"     
    
    new_hruwr = dict()
    cr_wrdist = dict()
            
    file_path = temp_path + '/wrdata_org.dat'
    shutil.copyfile(input_files['wrtfile'], file_path)
           
    #txt_file = temp_path + '/wrdata_' + str(iterrun) + '.dat'
    txt_file = temp_path + '/wrdata_cr' + '.dat'
    
    file_org = open(file_path, 'r')
    Lines = file_org.readlines()
    
    filein = open(txt_file,'w+')
    
    for line in Lines:
        linesplit = line.split()
        if 'year' not in linesplit[0].lower():
            atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
            atxt = atxt + str(int(linesplit[1])).rjust(5) + ''.rjust(3)
        
            #432082
            #atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
            
            if iterrun == 0:
                if int(linesplit[1]) == 9999:
                    atxt = atxt + str(int(linesplit[2])).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
                else:
                    if int(linesplit[2]) == 3:
                        atxt = atxt + str('5').rjust(4) + ''.rjust(3)
                        atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
                    # atxt = atxt + str(0).rjust(6) + ''.rjust(3)
                    else:
                        atxt = atxt + str(int(linesplit[2])).rjust(4) + ''.rjust(3)
                        atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
            else:
                if int(linesplit[1]) == final_wr_list[iterrun-1]:
                    atxt = atxt + str(999999).rjust(6) + ''.rjust(3)
                    # atxt = atxt + str(0).rjust(6) + ''.rjust(3)
                else:
                    atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
                    
            
            atxt = atxt + str(int(linesplit[4])).rjust(4) + ''.rjust(3)
            atxt = atxt + str(int(linesplit[5])).rjust(4)
            filein.write(atxt + '\n') 
            
        else:
            filein.write(line) 
    
    
    file_org.close()
    filein.close()
    

        
