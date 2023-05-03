#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import pyodbc

import geopandas as gpd
import pandas as pd


#%%
def Read_output_hru(tfile, varcol, varname):
    
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
    
    #fnames = os.listdir(out_path)
    
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
    
    #fnames = os.listdir(out_path)
    
    f_list = ['wrs_use_0.out','wrs_use_org.out', 'wrs_use_low.out']
    
    wrs_use_dict = {}
    for ff in f_list:

        if 'wrs_use' in ff:
            print(ff)

            temp_dict = {}
            cc = 0
            with open(out_path + '/' + ff, 'r') as search:
                for line in search:
                    
                    linesplit = re.split('\s', line.replace('\x00', ''))
                    linesplit = [t for t in linesplit if len(t) > 0]
                    
                    if cc == 0:
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
    
    #fnames = os.listdir(out_path)
    
    f_list = ['hru_wrt_0.out','hru_wrt_org.out', 'hru_wrt_low.out']
    
    hru_wrt_dict = {}
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
            wrsf_id = 2
        elif wrsf_id == 'low':
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

        if ff in f_list:
            print(ff)
            
            try:
                df_rch = Read_output_hru(out_path + '/' + ff, varcols, varnames)
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

data_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs'

crs = 'EPSG:26911'
subs = gpd.read_file(data_path + "/subs1.shp")
subs.to_crs(crs, inplace=True)

hrus2 = gpd.read_file(data_path + "/hru2.shp")
hrus2.to_crs(crs, inplace=True)

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
    
crsr.execute('select * from sol')
swat_hrus_soils = dict()
for row in crsr.fetchall():
    swat_hrus_soils[int(row[0])] = [row[8],int(row[15])]


# %% WATER RIGHTS USED IN ITERS
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
out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs/hruwr.dat'
hru_wr_rel = Get_hruwr_dat(out_path)
 
# %% TOTAL VOL OF WATER RIGHT USED IN ITERATION
out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'
wrs_use_dict, wrs_use_all, bad_files = Get_wrs_use_dat(out_path)

# %% WATER USED BY HRU FOR THEIR RESPECTIVE WATER RIGHTS
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

#%% HRU OUTPUTS
out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'
hru_out_dict = Get_hru_output(out_path)

#%%
hru_sub = dict()
for hruid in hru_out_dict['output_org'].keys():
    hru_sub[hruid] = int(hru_out_dict['output_org'][hruid]['SUB'][0])

#%%
hru_wr_sub = dict()
for wrid in hru_wr_rel.keys():
    if 'SUBID' not in hru_wr_rel[wrid].keys():
        hru_wr_rel[wrid]['SUBID'] = []
    
    for hruid in hru_wr_rel[wrid]['HRUID']:
        tsub = int(hru_out_dict['output_org'][hruid]['SUB'][0])
        if tsub not in hru_wr_rel[wrid]['SUBID']:
            hru_wr_rel[wrid]['SUBID'].append(tsub)
     

#%%
fig, ax = plt.subplots()

hrus2.plot(ax=ax, facecolor='none', edgecolor = 'lightgray', lw=0.7)

for wrid in hru_wr_rel.keys():
    for hruid in hru_wr_rel[wrid]['HRUID']:
        hrus2.loc[hrus2['HRUINT'] == hruid].plot(ax=ax, facecolor='red', edgecolor = 'lightgray', lw=0.7)

subs.plot(ax=ax,facecolor='none',edgecolor='black')

#%%
usoils = np.asarray(['A', 'B', 'C', 'D'])
hrus2['HYDGRP']=np.zeros((11346,1))

for hruid in swat_hrus_soils.keys():
    cid = np.where(str(swat_hrus_soils[hruid][0])==usoils)[0][0]
    hrus2.loc[hrus2['HRUINT'] == hruid, 'HYDGRP'] = str(swat_hrus_soils[hruid][0])
    
#%%
fig, ax = plt.subplots()
hrus2.plot(column='HYDGRP', ax=ax, categorical=True, edgecolor = 'none', lw=0.7, legend=True)
subs.plot(ax=ax,facecolor='none',edgecolor='black')
#ax.legend([0,1,2,3],usoils)

#%%
roadPalette = {'A': 'green',
               'B': 'yellow',
               'C': 'orange',
               'D': 'red'}

fig, ax = plt.subplots()

for ctype, data in hrus2.groupby('HYDGRP'):
    color = roadPalette[ctype]
    data.plot(facecolor=color,
             ax=ax,
             label=ctype,
             edgecolor = 'none', lw=0.7)

subs.plot(ax=ax,facecolor='none',edgecolor='black')


#%%
 
# fig, ax = plt.subplots(2,2)

# subs.plot(ax=ax[0,0], facecolor='none', edgecolor = 'black', lw=0.7)
# ax[0,0].set_title('WaterRights Diff')
# for sid in sub_with_diff:
#     subs.loc[subs['Subbasin']==sid+1,'geometry'].plot(ax=ax[0,0], facecolor='blue', alpha=0.5)

# subs.plot(ax=ax[0,1], facecolor='none', edgecolor = 'black', lw=0.7)
# ax[0,1].set_title('Yield Diff')
# for sid in sub_yield_diff:
#       subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax[0,1], facecolor='yellow', alpha=0.5)

# subs.plot(ax=ax[1,0], facecolor='none', edgecolor = 'black', lw=0.7)
# ax[1,0].set_title('NOWA Subs')
# for sid in subs_nowa:
#       subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax[1,0], facecolor='red', alpha=0.5)

# subs.plot(ax=ax[1,1], facecolor='none', edgecolor = 'black', lw=0.7)
# ax[1,1].set_title('MDAO')
# for sid in mdao_subs2:
# #for sid in max_wrs_sub:
#       subs.loc[subs['Subbasin']==sid,'geometry'].plot(ax=ax[1,1], facecolor='red', alpha=0.5)


    