#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import pyodbc

import geopandas as gpd
import pandas as pd


#%%
def Get_output_hru(tfile, varcol, varname):
    
    data_array = dict()
    varbool = 0
    rowid = 0
    
    with open(tfile, 'r') as search:
        for line in search:
        
            if 'HRU'.lower() in line.lower():    
                varbool = 1
                
            elif varbool == 1:
                
                linesplit = re.split('\s',line)
                if len(linesplit[0]) > 4:
                    linesplit[2] = linesplit[1]
                    linesplit[1] = linesplit[0][4:]
                    linesplit[0] = linesplit[0][0:4]
                
                linesplit = [e for e in linesplit if e != '']
                
                data_array[rowid] = dict()
                for i in range(0,len(varcol)):
                    if i != 5 and i != 0:
                        data_array[rowid][varname[i]] = float(linesplit[varcol[i]])
                    elif i != 5 and i == 0:
                        data_array[rowid][varname[i]] = linesplit[varcol[i]]
                    else:
                        data_array[rowid]['MON'] = int(linesplit[5].split('.')[0])
                        data_array[rowid][varname[i]] = float('0.'+ linesplit[5].split('.')[1])
                
                rowid = rowid + 1
                
    search.close()

    return pd.DataFrame.from_dict(data_array, orient='index')

#%%
def Get_hruwr_dat(out_path):
    
    df_hru_wr = pd.read_table(out_path, delim_whitespace=True)
    df_hru_wr  = pd.DataFrame.to_dict(df_hru_wr)

    hru_wr_rel = dict()
    for i in range(0,len(df_hru_wr['HRUID,'])):
        
        if df_hru_wr['WR_ID,'][i] != 9999:
            if df_hru_wr['WR_ID,'][i] not in hru_wr_rel.keys():
                hru_wr_rel[df_hru_wr['WR_ID,'][i]] = dict()
                hru_wr_rel[df_hru_wr['WR_ID,'][i]]['HRUID'] = []
                #hru_wr_rel[df_hru_wr['WR_ID,'][i]]['SUBID'] = []
            
            hru_wr_rel[df_hru_wr['WR_ID,'][i]]['HRUID'].append(df_hru_wr['HRUID,'][i])
            #hru_wr_rel[df_hru_wr['WR_ID,'][i]]['SUBID'].append(df_hru_wr['SUB_ID,'][i])
    
    return hru_wr_rel

#%%
def Get_wrdata_dat(out_path):
    
    fnames = os.listdir(out_path)
    
    f_list = ['wrdata_0.dat','wrdata_org.dat', 'wrdata_low.dat']
    
    wrs_dict = {}
    #for ff in fnames:
    for ff in f_list:

        print(ff)
        temp_dict = {}
        cc = 0
        with open(out_path + '/' + ff, 'r') as search:
            for line in search:
                #linesplit = re.split('\s', line.decode('ascii').replace('\x00', ''))
                linesplit = re.split('\s', line)
                linesplit = [t for t in linesplit if len(t) > 0]
                if cc == 0:
                    # print(linesplit)
                    columns = linesplit
                    for inline in linesplit:
                        temp_dict[inline.strip(',')] = []
                else:
                    for ii in range(0, len(columns)):
                        temp_dict[columns[ii].strip(',')].append(
                            float(linesplit[ii]))

                cc += 1

        search.close()
        wrs_dict[ff[:-4]] = temp_dict
        

    numf = len(wrs_dict.keys())
    wrids = np.unique(wrs_dict['wrdata_0']['WR_ID'])
    years = np.unique(wrs_dict['wrdata_0']['YEAR_ID'])

    wrs_data_all = np.zeros((numf, len(wrids)))

    # cwrf = 0
    for wrsf in wrs_dict.keys():
        temp_dict = np.asarray(pd.DataFrame.from_dict(wrs_dict[wrsf]))
        wrsf_id = wrsf[wrsf.find('_')+1:]
        
        if wrsf_id == 'org':
            #wrsf_id = 213
            wrsf_id = 2
        elif wrsf_id == 'low':
            #wrsf_id = 212
            wrsf_id = 1
        else:
            wrsf_id = int(wrsf_id)
        
        print(wrsf)

        cwrid = 0
        for wriid in wrids:
            #cy = 0
            #for yy in years:
            for yy in range(1,2):

                indx = np.where((temp_dict[:, 1] == wriid) & (temp_dict[:, 0] == yy))[0]
                wrs_data_all[wrsf_id, cwrid] = temp_dict[indx,3]
                #cy += 1

            cwrid += 1
            
    return wrs_dict, wrs_data_all

#%%
def Get_wrs_use_dat(out_path):
    
    fnames = os.listdir(out_path)
    
    f_list = ['wrs_use_0.out','wrs_use_org.out', 'wrs_use_low.out']
    
    wrs_use_dict = {}
    
    #for ff in fnames:
    for ff in f_list:

        if 'wrs_use' in ff:
            print(ff)

            temp_dict = {}
            cc = 0
            with open(out_path + '/' + ff, 'r') as search:
                for line in search:

                    #linesplit = re.split('\s', line.decode('ascii').replace('\x00', ''))
                    linesplit = re.split('\s', line.replace('\x00', ''))
                    linesplit = [t for t in linesplit if len(t) > 0]
                    
                    if cc == 0:
                        # print(linesplit)
                        columns = linesplit
                        for inline in linesplit:
                            temp_dict[inline] = []
                    else:
                        for ii in range(0, len(columns)):
                            temp_dict[columns[ii]].append(float(linesplit[ii]))

                    cc += 1

            search.close()
            wrs_use_dict[ff[:-4]] = temp_dict
            
    
    numf = len(wrs_use_dict.keys())
    wrids = np.unique(wrs_use_dict['wrs_use_0']['WRID'])
    years = np.unique(wrs_use_dict['wrs_use_0']['YEAR'])

    wrs_use_all = np.zeros((len(years), numf, len(wrids)))

    #cwrf = 0
    bad_files = []
    bad_filest = ''
    for wrsf in wrs_use_dict.keys():
        
        temp_dict = np.asarray(pd.DataFrame.from_dict(wrs_use_dict[wrsf]))
        wrsf_id = wrsf[[i for i, ltr in enumerate(wrsf) if ltr == '_'][1]+1:]
        
        if wrsf_id == 'org':
            #wrsf_id = 213
            wrsf_id = 2
        elif wrsf_id == 'low':
            #wrsf_id = 212
            wrsf_id = 1
        else:
            wrsf_id = int(wrsf_id)
        
        cwrid = 0
        for wriid in wrids:
            cy = 0
            for yy in years:

                indx = np.where((temp_dict[:, 0] == wriid) & (temp_dict[:, 2] == yy))[0]
                
                if len(indx) > 0:
                    wrs_use_all[cy, wrsf_id, cwrid] = temp_dict[indx,1]
                else:
                    if wrsf not in bad_files:
                        bad_files.append(wrsf)
                        bad_filest = bad_filest + wrsf.split('_')[2] + ','
                        print(wrsf, yy, wrsf_id, wriid)

                cy += 1
            cwrid += 1
    
    return wrs_use_dict, wrs_use_all, bad_files

#%%
def Get_hru_wrt_dat(out_path):
    
    fnames = os.listdir(out_path)
    
    f_list = ['hru_wrt_0.out','hru_wrt_org.out', 'hru_wrt_low.out']
    
    hru_wrt_dict = {}
    #for ff in fnames:
    for ff in f_list:
    
        if 'hru_wrt_' in ff:
            print(ff)
    
            temp_dict = {}
            cc = 0
            with open(out_path + '/' + ff, 'rb') as search:
                for line in search:
    
                    linesplit = re.split('\s', line.decode('ascii').replace('\x00', ''))
                    linesplit = [t for t in linesplit if len(t) > 0]
                    if cc == 0:
                        # print(linesplit)
                        columns = linesplit
                        for inline in linesplit:
                            temp_dict[inline] = []
                    else:
                        for ii in range(0, len(columns)):
                            temp_dict[columns[ii]].append(float(linesplit[ii]))
    
                    cc += 1
    
            search.close()
            hru_wrt_dict[ff[:-4]] = temp_dict
    
    hru_wrt_use = dict()
    for wrsf in hru_wrt_dict.keys():
        
        ttemp = hru_wrt_dict[wrsf]
        
        wrsf_id = wrsf[[i for i, ltr in enumerate(wrsf) if ltr == '_'][1]+1:]
        
        if wrsf_id == 'org':
            #wrsf_id = 213
            wrsf_id = 2
        elif wrsf_id == 'low':
            #wrsf_id = 212
            wrsf_id = 1
        else:
            wrsf_id = int(wrsf_id)
        
        #hru_uid = np.unique(ttemp['HRU'])
        for i in range(0,len(ttemp['HRU'])):
            if ttemp['HRU'][i] not in hru_wrt_use.keys():
                hru_wrt_use[ttemp['HRU'][i]] = dict()
            
            if wrsf_id not in hru_wrt_use[ttemp['HRU'][i]].keys():
                hru_wrt_use[ttemp['HRU'][i]][wrsf_id] = dict()
            
            if ttemp['WRID'][i] not in hru_wrt_use[ttemp['HRU'][i]][wrsf_id].keys():
                hru_wrt_use[ttemp['HRU'][i]][wrsf_id][ttemp['WRID'][i]] = dict()
                hru_wrt_use[ttemp['HRU'][i]][wrsf_id][ttemp['WRID'][i]]['Data'] = [] 
            
            hru_wrt_use[ttemp['HRU'][i]][wrsf_id][ttemp['WRID'][i]]['Data'].append([ttemp['YEAR'][i],ttemp['WATER(acre-ft)'][i]])
    
    return hru_wrt_dict, hru_wrt_use   

#%%
def Get_hru_output(out_path):
    
    fnames = os.listdir(out_path)
    varnames = ["LULC","HRU","GIS","SUB","MGT","AREAkm2","BIOMt/ha","YLDt/ha","IRRmm","NAUTOkg/ha","PAUTOkg/ha", "ETmm", "SW_INITmm", "SW_ENDmm", "PERCmm", "GW_RCHGmm", "REVAPmm", "W_STRS"]
    varcols = [i for i in range(0,len(varnames))]

    f_list = ['output_0.hru','output_org.hru', 'output_low.hru']
    hru_out_dict = {}
    for ff in fnames:

        #if '.hru' in ff:
        if ff in f_list:
            print(ff)
            
            try:
                df_rch = Get_output_hru(out_path + '/' + ff, varcols, varnames)
                df_rch = df_rch.drop(['MGT', 'GIS'], axis=1)
                df_rch = df_rch.rename(columns={'MON':'YEAR'})
                mon_yr = df_rch['YEAR'].tolist()
                df_rch = df_rch.iloc[np.where(np.asarray(mon_yr) > 13)[0]]
                df_rch['Total_Yield'] = df_rch['AREAkm2']*100*df_rch['YLDt/ha']
                df_rch = df_rch.drop_duplicates()
                
                temp_dict = dict()
                for i, row in df_rch.iterrows():
                    if int(row['HRU']) not in temp_dict.keys():
                        temp_dict[int(row['HRU'])] = dict()
                    for coln in row.keys():
                        if 'hru' not in coln.lower() and coln not in temp_dict[int(row['HRU'])].keys():
                            temp_dict[int(row['HRU'])][coln] = []
                        if 'hru' not in coln.lower():
                            temp_dict[int(row['HRU'])][coln].append(row[coln])    
                            
                hru_out_dict[ff[:-4]] = temp_dict
                
            except:
                print('Problem: ' + str(ff))
    
    return hru_out_dict

#%%
#data_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/'
data_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs'

# hru_nowa = shapefile.Reader(data_path + '/' + 'hru2_NOWA_pumping_limit.shp')
# hru_nowa_records = hru_nowa.records()

# hruid_nowa = []
# for i in range(0,len(hru_nowa_records)):
#     hruid_nowa.append((hrugis_dict[hru_nowa_records[i][6]]))
# hruid_nowa = np.asarray(hruid_nowa)

# hru_portMorrow = shapefile.Reader(data_path + '/' + 'HRUs_Port_Morrow.shp')
# hru_portMorrow_records = hru_portMorrow.records()

# hruid_portMorrow = []
# for i in range(0,len(hru_portMorrow_records)):
#     hruid_portMorrow.append((hru_portMorrow_records[i][6], hrugis_dict[hru_portMorrow_records[i][6]]))
# hruid_portMorrow = np.asarray(hruid_portMorrow)


crs = 'EPSG:26911'
subs = gpd.read_file(data_path + "/subs1.shp")
subs.to_crs(crs, inplace=True)

hrus2 = gpd.read_file(data_path + "/hru2.shp")
hrus2.to_crs(crs, inplace=True)

nowa = gpd.read_file(data_path + "/NOWA_hrus_pumping_limitsv3.shp")
nowa.to_crs(crs, inplace=True)

subs['g1'] = subs.geometry
nowa['g2'] = nowa.geometry
gdf_joined = subs.sjoin(nowa, how="inner")
gdf_joined['area_joined'] = gdf_joined.area
gdf_joined['sub_area'] = (gdf_joined['area_joined'] / gdf_joined['Shape_Area'])

def f(frame):
    """A function to calculate overlap percentage"""
    interpct = 100*frame.g1.intersection(frame.g2).area/frame.g1.area
    return interpct

gdf_joined['pct'] = gdf_joined.apply(f, axis=1)

#%%
db_path = r'C:\Users\riversam\Box\Research\SWAT\QSWAT\Umatilla_InterACTWEL_QSWATv4\Umatilla_InterACTWEL_QSWATv4\Umatilla_InterACTWEL_QSWATv4.mdb'    
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=' + db_path + ';'
    )
cnxn = pyodbc.connect(conn_str)
crsr = cnxn.cursor()

crsr.execute('select * from hrus')
swat_hruid = dict()
for row in crsr.fetchall():
    swat_hruid[int(row[11])] = [row[12],int(row[1])]

#%%
subs_nowa = [int(row['Subbasin']) for i, row in gdf_joined.iterrows() if row['pct'] >= 20]

fig, ax = plt.subplots()
subs.plot(ax=ax, facecolor='none', edgecolor = 'black', lw=0.7)
nowa.plot(ax=ax, facecolor='yellow', edgecolor = 'black', alpha=0.7)
for sid in subs_nowa:
    subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax, facecolor='blue', alpha=0.5)

# %% WATER RIGHTS USED IN ITERS
#out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS'
out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS'
wrs_dict, wrs_data_all = Get_wrdata_dat(out_path)
   
wrids = np.unique(wrs_dict['wrdata_0']['WR_ID'])
wrid_file = dict()
for wrsf in wrs_dict.keys():
    wrsf_id = wrsf[wrsf.find('_')+1:]
    if wrsf_id == 'org':
        #wrsf_id = 213
        wrsf_id = 2
    elif wrsf_id == 'low':
        #wrsf_id = 212
        wrsf_id = 1
    else:
        wrsf_id = int(wrsf_id)
    
    wrid_file[wrsf] = wrids[np.where(wrs_data_all[wrsf_id,:]>999990)[0]] 

# %% WATER RIGHTS ASSIGNED TO HRU
#out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs'
out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs/hruwr.dat'
hru_wr_rel = Get_hruwr_dat(out_path)
 
# %% TOTAL VOL OF WATER RIGHT USED IN ITERATION
#out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'
out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'
wrs_use_dict, wrs_use_all, bad_files = Get_wrs_use_dat(out_path)

#%%
#org_use = wrs_use_all[:,213,:]
#max_use = wrs_use_all[:,0,:]
org_use = wrs_use_all[:,2,:]
max_use = wrs_use_all[:,0,:]

org_diff_wrs = np.zeros((len(wrs_use_all[0,:,0])-1,len(org_use.T)))
max_diff_wrs = np.zeros((len(wrs_use_all[0,:,0])-1,len(org_use.T)))

for fid in range(0,len(wrs_use_all[0,:,0])-1):
    ttuse = wrs_use_all[:,fid,:]
    
    for wrid in range(0,len(org_use.T)):    
        otdif = ttuse[:,wrid] - org_use[:,wrid]
        mtdif = max_use[:,wrid] - ttuse[:,wrid]
        
        if sum(abs(otdif)) > 0.1:
            print(wrid, sum(abs(otdif)), sum(abs(mtdif)))
        
        org_diff_wrs[fid,wrid] = sum(abs(otdif))
        max_diff_wrs[fid,wrid] = sum(abs(mtdif))

org_diff_wrs = np.asarray(org_diff_wrs)    
max_diff_wrs = np.asarray(max_diff_wrs)


sum_org_use = np.vstack((wrs_data_all[2,:].T, np.sum(wrs_use_all[:,0,:],axis=0).T, np.sum(wrs_use_all[:,2,:],axis=0).T)).T

#max_org_use = np.vstack((np.max(wrs_use_all[:,0,:],axis=0).T,np.max(wrs_use_all[:,2,:],axis=0).T)).T
max_org_use = (np.max(wrs_use_all[:,0,:],axis=0).T/wrs_data_all[2,:].T)*100
max_org_use[np.where(np.isnan(max_org_use))] = 0

diff_wrs_totals = np.zeros((len(org_use.T),3))
diff_wrs_totals[:,0] = np.arange(0,len(org_use.T))
diff_wrs_totals[:,1] = np.round_(sum(org_diff_wrs),3)
diff_wrs_totals[:,2] = np.round_(sum(max_diff_wrs),3)

diff_wrs_totals = diff_wrs_totals[diff_wrs_totals[:,1].argsort()]
max_diff_wrid = diff_wrs_totals[np.where(diff_wrs_totals[:,1]>1),0].T

#plt.matshow(org_diff_wrs[:,[int(k) for k in org_diff_wrid[:0]]])

# %% WATER USED BY HRU FOR THEIR RESPECTIVE WATER RIGHTS
#out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'
out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'
hru_wrt_dict, hru_wrt_use = Get_hru_wrt_dat(out_path)

#%%
for hruid in hru_wrt_use.keys():
    for iterid in hru_wrt_use[hruid].keys():
        for wrid in hru_wrt_use[hruid][iterid].keys():
            total_use = 0
            for i in range(0,len(hru_wrt_use[hruid][iterid][wrid]['Data'])):
                total_use = total_use + hru_wrt_use[hruid][iterid][wrid]['Data'][i][1]
                
            hru_wrt_use[hruid][iterid][wrid]['TOTAL_USE'] = total_use

#%%
check_wrt_use = dict()
for wrsf in hru_wrt_dict.keys():
    
    ttemp = hru_wrt_dict[wrsf]
    
    wrsf_id = wrsf[[i for i, ltr in enumerate(wrsf) if ltr == '_'][1]+1:]
    
    if wrsf_id == 'org':
        #wrsf_id = 212
        wrsf_id = 2
    elif wrsf_id == 'low':
        #wrsf_id = 213
        wrsf_id = 1
    else:
        wrsf_id = int(wrsf_id)
    
    #hru_uid = np.unique(ttemp['HRU'])
    for i in range(0,len(ttemp['HRU'])):
        if wrsf_id not in check_wrt_use.keys():
            check_wrt_use[wrsf_id] = dict()

        if ttemp['WRID'][i] not in check_wrt_use[wrsf_id].keys():
            check_wrt_use[wrsf_id][ttemp['WRID'][i]] = dict() 
            
        if ttemp['YEAR'][i] not in check_wrt_use[wrsf_id][ttemp['WRID'][i]].keys():
            check_wrt_use[wrsf_id][ttemp['WRID'][i]][ttemp['YEAR'][i]] = 0
        
        check_wrt_use[wrsf_id][ttemp['WRID'][i]][ttemp['YEAR'][i]] = check_wrt_use[wrsf_id][ttemp['WRID'][i]][ttemp['YEAR'][i]] + ttemp['WATER(acre-ft)'][i]
        

#%%
for i in range(0,3):
#for i in range(0,214):
    ttemp = wrs_use_all[:,i,:]
    for ii in check_wrt_use[i].keys():
        cy = 0
        for iii in check_wrt_use[i][ii].keys():
            tdif = check_wrt_use[i][ii][iii] - ttemp[cy,int(ii-1)]
            if abs(tdif) > 0.001:
                print(i,int(ii),int(iii),tdif)
            
            cy += 1

#%%
for wrf in wrs_dict.keys():
    rowids = np.where(np.asarray(wrs_dict[wrf]['WR_VOL_ft-acre']) > 999990)[0][0:10]
    wrid = np.unique(np.asarray(wrs_dict[wrf]['WR_ID'])[rowids])
    if len(wrid) > 1:
        print('Problem with: '+ wrf)

#%% HRU OUTPUTS
#out_path = r'/Users/sammy/Documents/Research/SWAT/ITERS_Results/'
#out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'
out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'
hru_out_dict = Get_hru_output(out_path)

#%%

varsn = ["YLDt/ha","IRRmm", "ETmm", "SW_INITmm", "SW_ENDmm", "PERCmm", "GW_RCHGmm", "REVAPmm", "W_STRS"]

hru_prob = []
for i in hru_out_dict['output_org'].keys():
    for vn in varsn:
        temp_diff = np.asarray((hru_out_dict['output_org'][i][vn], hru_out_dict['output_0'][i][vn])).T
        if len(np.where(temp_diff[:,0] > temp_diff[:,1])[0]) > 0:
            print(i, vn, temp_diff)
            if i not in hru_prob:
                hru_prob.append(i)
                
#%%
varsn = ["YEAR", "YLDt/ha","IRRmm", "ETmm", "SW_INITmm", "SW_ENDmm", "PERCmm", "GW_RCHGmm", "REVAPmm", "W_STRS"]

all_var = []
for vn in varsn:
    if len(all_var) == 0:
        temp_var = [-999,-999,-999]
    else:
        temp_var = [-999,-999]
        
    for i in hru_out_dict['output_org'].keys():
        temp_diff = np.asarray((hru_out_dict['output_org'][i][vn], hru_out_dict['output_0'][i][vn])).T
        if len(all_var) == 0:
            temp_var = np.vstack((temp_var, np.hstack((np.ones((len(temp_diff),1))*i, temp_diff))))
        else:
            temp_var = np.vstack((temp_var, temp_diff))
        
    #temp_var =  temp_var[1:,:]
    if len(all_var) == 0:
        all_var = temp_var    
    else:
        all_var = np.hstack((all_var, temp_var))

all_var =  all_var[1:,:]

# varsn = ["YLDt/ha"]

# yield_rel = [-999,-999]
# for i in hru_out_dict['output_org'].keys():
#     for vn in varsn:
#         temp_diff = np.asarray((hru_out_dict['output_org'][i][vn], hru_out_dict['output_0'][i][vn])).T
#         yield_rel = np.vstack((yield_rel,temp_diff))
        
# yield_rel =  yield_rel[1:,:]

#%%

fig, ax = plt.subplots()
subs.plot(ax=ax, facecolor='none', edgecolor = 'black', lw=0.7)
#nowa.plot(ax=ax, facecolor='yellow', edgecolor = 'black', alpha=0.7)
for hru_probid in hru_prob:
    hrus2.loc[hrus2['HRUINT']==hru_probid,'geometry'].plot(ax=ax, facecolor='blue', alpha=0.5)

#%%

lulc_unique = []

for fid in hru_out_dict['output_org'].keys():
    for lu in hru_out_dict['output_org'][fid]['LULC'][0:8]:
        if lu.islower():
            lu = 'ZOTHER'
        if lu not in lulc_unique:
            lulc_unique.append(lu)

lulc_unique = np.unique(lulc_unique)

lulc_irr = np.asarray(['AGRL','ALFA','BARL','BERM','CANP','CELR','CORN','HAY','MINT','ONIO','ORCD','PEAS','POTA','RADI','SCRN','SOYB','STRW','SWGR','SWHT','WWHT'])

#org_hru_lulc = np.zeros((len(hru_out_dict['output_org'].keys()),len(lulc_unique)))
#max_hru_lulc = np.zeros((len(hru_out_dict['output_org'].keys()),len(lulc_unique)))
org_hru_lulc = np.zeros((len(hru_out_dict['output_org'].keys()),len(lulc_irr)))
max_hru_lulc = np.zeros((len(hru_out_dict['output_org'].keys()),len(lulc_irr)))

for fid in hru_out_dict['output_org'].keys():
    for li in range(0,8):
        lu = hru_out_dict['output_org'][fid]['LULC'][li]
        if lu.islower():
            lu = 'ZOTHER'
        if lu in lulc_irr:
            #luid = np.where(lulc_unique == lu)[0][0]
            luid = np.where(lulc_irr == lu)[0][0]
            org_hru_lulc[int(fid-1), luid] = org_hru_lulc[int(fid-1), luid] + hru_out_dict['output_org'][fid]['Total_Yield'][li]
            max_hru_lulc[int(fid-1), luid] = max_hru_lulc[int(fid-1), luid] + hru_out_dict['output_0'][fid]['Total_Yield'][li]

#diff_hru_lulc = max_hru_lulc - org_hru_lulc
diff_hru_lulc = np.sum(abs(max_hru_lulc - org_hru_lulc),axis=1)


wr_lulc_diff = np.zeros((1807,1))
for hruid in hru_wrt_use.keys():
    for wrid in hru_wrt_use[hruid][iterid].keys():
        wr_lulc_diff[int(wrid-1)]=diff_hru_lulc[int(hruid-1)]

hru_yield_diff = np.where(np.asarray(diff_hru_lulc) > 0)[0]

#%%
org_hru_data = hru_out_dict['output_org']

hru_param_diff = dict()
hru_param = ['BIOMt/ha', 'YLDt/ha', 'IRRmm', 'NAUTOkg/ha']

for hru_var in hru_param:
    print(hru_var)
    #hru_param_diff[hru_var] = np.zeros((11346,214))
    hru_param_diff[hru_var] = np.zeros((11346,3))
    
    for fid in hru_out_dict.keys():
        fid_id = fid[[i for i, ltr in enumerate(fid) if ltr == '_'][0]+1:]
        
        if fid_id == 'org':
            #fid_id = 213
            fid_id = 2
        elif fid_id == 'low':
            #fid_id = 212
            fid_id = 1
        
        for hruid in hru_out_dict[fid].keys():
            #temp_per_chg = ((np.asarray(hru_out_dict[fid][hruid][hru_var]) - np.asarray(org_hru_data[hruid][hru_var]))/np.asarray(org_hru_data[hruid][hru_var]))*100
            temp_per_chg = (np.asarray(hru_out_dict[fid][hruid][hru_var])[0:8] - np.asarray(org_hru_data[hruid][hru_var])[0:8])
            hru_param_diff[hru_var][int(hruid)-1,int(fid_id)] = sum(abs(temp_per_chg))
        
    
#%%
var_per_diff = np.zeros((len(hru_param_diff[hru_var]),5))
cc = 0
for hru_var in hru_param: 
    var_diff = hru_param_diff[hru_var]
    
    var_diff[np.where(np.isnan(var_diff))] = 0
    #var_per_diff[:,cc] = np.sum(var_diff[:,[0,212]],axis=1)
    var_per_diff[:,cc] = np.max(var_diff[:,[0,1]],axis=1)
    #var_per_diff[:,cc] = var_diff[:,212]
    cc = cc + 1

#%%

for hruid in hru_wrt_use.keys():
    temp = 0
    temp_org = 0
    
    for iterid in [0,1]:
    #for iterid in [0,212]:
    #for iterid in hru_wrt_use[hruid].keys():
    #for iterid in range(0,1):

        for wrid in hru_wrt_use[hruid][iterid].keys():
            temp = temp + hru_wrt_use[hruid][iterid][wrid]['TOTAL_USE']
            #temp_org = temp_org + hru_wrt_use[hruid][212][wrid]['TOTAL_USE']
            temp_org = temp_org + hru_wrt_use[hruid][2][wrid]['TOTAL_USE']
    
    # if temp_org == 0 and temp == 0:
    #     temp_diff = 0
    # elif temp_org == 0 and temp !=0:
    #     temp_org = 0.00001
    #     temp_diff = ((temp-temp_org)/temp_org)*100
    # else:
    #     temp_diff = ((temp-temp_org)/temp_org)*100
    
    temp_diff = abs(temp - temp_org)
    
    print(hruid, temp, temp_org, temp_diff)
    var_per_diff[int(hruid-1),4] = round(temp_diff,3)

hru_yield_diff = np.where(np.asarray(var_per_diff[:,1]) > 100)[0]

#%%
hru_sub = dict()
for hruid in hru_out_dict['output_org'].keys():
    hru_sub[hruid] = int(hru_out_dict['output_org'][hruid]['SUB'][0])
    
sub_yield_diff = []
for i in hru_yield_diff:
    if hru_sub[i+1] not in sub_yield_diff:
        sub_yield_diff.append(hru_sub[i+1])
           
        
        
        
#sub_wr_diff = np.zeros((147,214))
sub_wr_diff = np.zeros((147,3))
for hruid in hru_wrt_use.keys():
    for iterid in hru_wrt_use[hruid].keys():
    #for iterid in [0,212]:
        for wrid in hru_wrt_use[hruid][iterid].keys():
            tsubid = hru_sub[hruid]-1
            sub_wr_diff[tsubid,iterid] = sub_wr_diff[tsubid,iterid] + hru_wrt_use[hruid][iterid][wrid]['TOTAL_USE']
            
            
            


for iterid in range(0,2):
#for iterid in range(0,213):
#for iterid in [0,212]:
    #sub_wr_diff[:,iterid] = abs(sub_wr_diff[:,iterid] - sub_wr_diff[:,213])
    sub_wr_diff[:,iterid] = abs(sub_wr_diff[:,iterid] - sub_wr_diff[:,2])
    
#sub_with_diff = np.where(np.sum(sub_wr_diff[:,0:212],axis=1) > 1)[0]
#sub_with_diff = np.where(np.sum(sub_wr_diff[:,[0,212]],axis=1) > 50000)[0]
sub_with_diff = np.where(np.sum(sub_wr_diff[:,[0,1]],axis=1) > 50000)[0]

#%%
hru_wr_sub = dict()
mdao_wrs =[]

for wrid in hru_wr_rel.keys():
    if 'SUBID' not in hru_wr_rel[wrid].keys():
        hru_wr_rel[wrid]['SUBID'] = []
    
    for hruid in hru_wr_rel[wrid]['HRUID']:
        tsub = int(hru_out_dict['output_org'][hruid]['SUB'][0])
        if tsub not in hru_wr_rel[wrid]['SUBID']:
            hru_wr_rel[wrid]['SUBID'].append(tsub)
        
        #if (tsub-1) in sub_with_diff and (tsub-1) not in mdao_wrs:
        if tsub not in mdao_wrs:
            mdao_wrs.append(wrid)
                    
mdao_wrs = np.unique(mdao_wrs)

mdao_wrs_dict = dict()
for wrid in mdao_wrs:
    mdao_wrs_dict[wrid] = hru_wr_rel[wrid]

#mdao_subs = [subs_nowa, list(sub_with_diff+1), sub_yield_diff]
mdao_subs = [subs_nowa, sub_yield_diff]
mdao_subs = set(mdao_subs[0]).intersection(*mdao_subs)

#%%
mdao_wrs = []
for wrid in hru_wr_rel.keys():
    for subid in hru_wr_rel[wrid]['SUBID']:
        if subid in mdao_subs and wrid not in mdao_wrs:
            mdao_wrs.append(wrid)

mdao_wrs = np.unique(mdao_wrs)

wrids = np.unique(wrs_dict['wrdata_org']['WR_ID'])
temp_dict = np.asarray(pd.DataFrame.from_dict(wrs_dict['wrdata_org']))


mdao_wr_dict = dict()
for wriid in wrids:
    for yy in range(1,2):
        indx = np.where((temp_dict[:, 1] == wriid) & (temp_dict[:, 0] == yy))[0]
        mdao_wr_dict[wriid] = temp_dict[indx,3][0]

mdao_wrs_vol = []
for wrid in mdao_wrs:
    mdao_wrs_vol.append((wrid, mdao_wr_dict[wrid]))
mdao_wrs_vol = np.asarray(mdao_wrs_vol)


total_vol_mdao_wrs = np.sum(mdao_wrs_vol[:,1])
per_vol_mdao_wrs = mdao_wrs_vol[:,1]/total_vol_mdao_wrs

mdao_wrs_vol = np.hstack((mdao_wrs_vol, np.reshape(per_vol_mdao_wrs,(len(per_vol_mdao_wrs),1))))

wrs_bin = np.zeros((1807,3))
for i in mdao_wrs_vol[:,0]:
    wrs_bin[int(i-1),0] = 1

#wrs_bin[:,1] = np.reshape(max_org_use,(len(max_org_use),1))
wrs_bin[:,1] = max_org_use
wrs_bin[:,2] = wr_lulc_diff[:,0]

max_wrs_sub = []
for wrid in hru_wr_rel.keys():
    if wrs_bin[int(wrid-1),1] > 100 and wrs_bin[int(wrid-1),2] > 0:
        for subid in hru_wr_rel[wrid]['SUBID']:
            if subid not in max_wrs_sub:
                max_wrs_sub.append(subid)
                 
mdao_subs2 = [subs_nowa, max_wrs_sub, sub_yield_diff]
mdao_subs2 = set(mdao_subs2[0]).intersection(*mdao_subs2)

mdao_wrs2 = []
for wrid in hru_wr_rel.keys():
    for subid in hru_wr_rel[wrid]['SUBID']:
        if subid in mdao_subs2 and wrid not in mdao_wrs2:
            mdao_wrs2.append(wrid)

#mdao_wrs2 = np.unique(mdao_wrs2)

#%%
iter_subs = []
for wrsf in wrid_file:
    wrid = wrsf[wrsf.find('_')+1:]
    
    if wrid != '0' and wrid != 'org':
        for wwrid in wrid_file[wrsf]:
            
            if int(wwrid) in hru_wr_rel.keys():
                for sid in hru_wr_rel[int(wwrid)]['SUBID']:
                    if sid not in iter_subs:
                        iter_subs.append(sid)
                
# for wrid in hru_wr_rel.keys():
#     for sid in hru_wr_rel[int(wrid)]['SUBID']:
#         if sid not in iter_subs:
#             iter_subs.append(sid)

#%%

out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\MDAO_WRS.txt'
wr_mdao = []
with open(out_path, 'r') as search:
    for line in search:
        if len(line) > 0:
            wr_mdao.append(int(line))

search.close()    

#%%
mdao_subs2 = []
wr_mdao_nowa = []
for i in range(0,len(wr_mdao)):
#for i in range(0,50):
    wrid = wr_mdao[i] 
    for subid in hru_wr_rel[wrid]['SUBID']:
        #if subid not in mdao_subs2 and subid in subs_nowa and wrid not in wr_mdao_nowa:
        if subid in subs_nowa and wrid not in wr_mdao_nowa:
            mdao_subs2.append(subid)
            wr_mdao_nowa.append(wrid)

#wr_mdao_nowa = np.unique(wr_mdao_nowa)
#mdao_subs2 = np.unique(mdao_subs2)

mdao_subs_wrs = dict()
subs_per_wr = np.zeros((len(wr_mdao_nowa),3))
for i in range(0,len(wr_mdao_nowa)):
    wrid = wr_mdao_nowa[i] 
    temp_area = 0
    for hruid in hru_wr_rel[wrid]['HRUID']:
        temp_area = temp_area + hru_out_dict['output_org'][hruid]['AREAkm2'][0]
    
    for subid in hru_wr_rel[wrid]['SUBID']:
        if subid not in mdao_subs_wrs.keys():
            mdao_subs_wrs[subid] = []
        if subid in subs_nowa:
            mdao_subs_wrs[subid].append(wrid)
    
    print(wrid, len(hru_wr_rel[wrid]['SUBID']), len(hru_wr_rel[wrid]['HRUID']))
    subs_per_wr[i,:]= (wrid, len(hru_wr_rel[wrid]['SUBID']), temp_area)

#%%
# mdao_subs = np.zeros((len(sub_wr_diff),3))
# for i in subs_nowa:
#     subs_nowa, list(sub_with_diff), sub_yield_diff]
    
fig, ax = plt.subplots(2,2)

subs.plot(ax=ax[0,0], facecolor='none', edgecolor = 'black', lw=0.7)
ax[0,0].set_title('WaterRights Diff')
for sid in sub_with_diff:
    subs.loc[subs['Subbasin']==sid+1,'geometry'].plot(ax=ax[0,0], facecolor='blue', alpha=0.5)

subs.plot(ax=ax[0,1], facecolor='none', edgecolor = 'black', lw=0.7)
ax[0,1].set_title('Yield Diff')
for sid in sub_yield_diff:
      subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax[0,1], facecolor='yellow', alpha=0.5)

subs.plot(ax=ax[1,0], facecolor='none', edgecolor = 'black', lw=0.7)
ax[1,0].set_title('NOWA Subs')
for sid in subs_nowa:
      subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax[1,0], facecolor='red', alpha=0.5)

subs.plot(ax=ax[1,1], facecolor='none', edgecolor = 'black', lw=0.7)
ax[1,1].set_title('MDAO')
for sid in mdao_subs2:
#for sid in max_wrs_sub:
      subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax[1,1], facecolor='red', alpha=0.5)

# subs.plot(ax=ax[1,1], facecolor='none', edgecolor = 'black', lw=0.7)
# ax[1,1].set_title('ITER SUBS')
# for sid in iter_subs:
#       subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax[1,1], facecolor='red', alpha=0.5)

# subs.apply(lambda x: ax.annotate(text=x['Index'], xy=x.geometry.centroid.coords[0], ha='center', color='orange'), axis=1)

#%%
# wrid = 316
# # for i in range(0,len(wr_mdao_nowa)):
# #     wrid = wr_mdao_nowa[i] 
# #     temp_area = 0

fig, ax = plt.subplots()

hrus2.plot(ax=ax, facecolor='none', edgecolor = 'lightgray', lw=0.7)
for i in range(0,len(wr_mdao_nowa)):
    #wrid = wr_mdao_nowa[i] 
    for hruid in hru_wr_rel[wrid]['HRUID']:
        #hrus2.loc[hrus2['HRUINT'] == hruid].plot(ax=ax, facecolor='red', edgecolor = 'lightgray', lw=0.7)
        hrus2.loc[hrus2['HRUINT'] == hruid].plot(ax=ax, facecolor='red', edgecolor = 'lightgray', lw=0.7)

subs.plot(ax=ax,facecolor='none',edgecolor='black')
#nowa.plot(ax=ax, facecolor='yellow', edgecolor = 'black', alpha=0.1)
for sid in subs_nowa:
    subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax, facecolor='blue', alpha=0.1)


#%%
fig, ax = plt.subplots()

hrus2.plot(ax=ax, facecolor='none', edgecolor = 'lightgray', lw=0.7)


for wrid in hru_wr_rel.keys():
    for hruid in hru_wr_rel[wrid]['HRUID']:
        hrus2.loc[hrus2['HRUINT'] == hruid].plot(ax=ax, facecolor='red', edgecolor = 'lightgray', lw=0.7)

subs.plot(ax=ax,facecolor='none',edgecolor='black')


#%%
# hruid_csv = []
# for i in swat_hruid.keys(): 
#     hruid_csv.append((str(swat_hruid[i][0]),i,swat_hruid[i][1]))
# hruid_csv = np.asarray(hruid_csv)

#%%
# # #out_path = r'/Users/sammy/Documents/Research/SWAT/ITERS_Results/'
# out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'
# #out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'

# fnames = os.listdir(out_path)

# wrs_use_dict = {}
# file_counter = 1

# for ff in fnames:

#     if '.rch' in ff:
#         print(ff)

#         df_rch = pd.read_table(out_path + '/' + ff, skiprows=9, delim_whitespace=True , 
#                                 usecols=[0,1,2,3,4,5,6,16,17,20,21,28,29,47,48,49], 
#                                 names = ["FILE","RCH","GIS","MON","AREAkm2","FLOW_INcms","FLOW_OUTcms",
#                                         "NO3_INkg","NO3_OUTkg","NO2_INkg","NO2_OUTkg","TOT Nkg","DISOX_INkg", " DISOX_OUTkg",
#                                         "TOT Pkg","NO3_mg_l"],
#                                 index_col = False,low_memory = True)

#         REACHES = df_rch['RCH'].unique().tolist()
#         YEARS = df_rch['MON'].unique().tolist()
#         yrs = [int(item) for item in YEARS]
#         yrs = list(filter(lambda x: x >= 999, yrs))
#         yrs_start = min(yrs)
#         yrs_end = max(yrs)
        
#         # data = df[["RCH","MON","FLOW_OUTcms"]].copy()
#         # data = data[data["MON"] < 13]
#         # for REACH in REACHES:
#         #     data2 = data[data["RCH"] == REACH]
#         #     pd.options.mode.chained_assignment = None
#         #     data2['date'] = pd.date_range(start='1/1/'+str(yrs_start), end = '12/31/'+str(yrs_end), freq='M')
#         #     data3 = data2[["date","FLOW_OUTcms"]].copy()
#         #     data3.set_index("date",inplace=True)
#         #     data3 = data3.rename(columns={"FLOW_OUTcms": "val"})
#         #     ### Compute SSI ###
#         #     norm_spi = spi(data3, nscale, nseas)
#         #     df_SSI = df_SSI.reindex(norm_spi.index)
#         #     df_SSI = df_SSI.join(norm_spi)
#         #     df_SSI = df_SSI.rename(columns={"spi":REACH})
#         # df_SSI.index = pd.to_datetime(df_SSI.index)