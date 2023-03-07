#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import re
import matplotlib.pylab as plt

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString


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

data_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/'
crs = 'EPSG:26911'
watershed = gpd.read_file(data_dir+"/subs1.shp")
watershed.to_crs(crs, inplace=True)


# %%

out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS'
#out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS'

fnames = os.listdir(out_path)

wrs_dict = {}
file_counter = 1
for ff in fnames:

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
    

#%%
numf = len(wrs_dict.keys())
wrids = np.unique(wrs_dict['wrdata_0']['WR_ID'])
years = np.unique(wrs_dict['wrdata_0']['YEAR_ID'])

wrs_data_all = np.zeros((numf, len(wrids)))

# cwrf = 0
for wrsf in wrs_dict.keys():
    temp_dict = np.asarray(pd.DataFrame.from_dict(wrs_dict[wrsf]))
    wrsf_id = wrsf[wrsf.find('_')+1:]
    
    if wrsf_id == 'org':
        wrsf_id = 212
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

   
#%%

wrid_file = dict()
for wrsf in wrs_dict.keys():
    wrsf_id = wrsf[wrsf.find('_')+1:]
    if wrsf_id == 'org':
        wrsf_id = 212
    else:
        wrsf_id = int(wrsf_id)
    
    wrid_file[wrsf] = wrids[np.where(wrs_data_all[wrsf_id,:]>999990)[0]]
 

# %%

#out_path = r'/Users/sammy/Documents/Research/SWAT/ITERS_Results/'
out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'
#out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'

fnames = os.listdir(out_path)

wrs_use_dict = {}
file_counter = 1

for ff in fnames:

    if 'wrs_use' in ff:
        print(ff)

        #df = pd.read_table(out_path + '/' + ff, skiprows=1, delim_whitespace=True , index_col = False, low_memory = True)

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


# %%
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
        wrsf_id = 212
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


#%%

org_use = wrs_use_all[:,212,:]
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

diff_wrs_totals = np.zeros((len(org_use.T),3))
diff_wrs_totals[:,0] = np.arange(0,len(org_use.T))
diff_wrs_totals[:,1] = np.round_(sum(org_diff_wrs),3)
diff_wrs_totals[:,2] = np.round_(sum(max_diff_wrs),3)

diff_wrs_totals = diff_wrs_totals[diff_wrs_totals[:,1].argsort()]
max_diff_wrid = diff_wrs_totals[np.where(diff_wrs_totals[:,1]>1),0].T

#plt.matshow(org_diff_wrs[:,[int(k) for k in org_diff_wrid[:0]]])

# %%

out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'
#out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'

fnames = os.listdir(out_path)

hru_wrt_dict = {}
file_counter = 1
for ff in fnames:

    if 'hru_wrt_' in ff:
        print(ff)

        #df = pd.read_table(out_path + '/' + ff, skiprows=1, delim_whitespace=True , index_col = False, low_memory = True)

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

#%%

hru_wrt_use = dict()
for wrsf in hru_wrt_dict.keys():
    
    ttemp = hru_wrt_dict[wrsf]
    
    wrsf_id = wrsf[[i for i, ltr in enumerate(wrsf) if ltr == '_'][1]+1:]
    
    if wrsf_id == 'org':
        wrsf_id = 212
    else:
        wrsf_id = int(wrsf_id)
    
    #hru_uid = np.unique(ttemp['HRU'])
    for i in range(0,len(ttemp['HRU'])):
        if ttemp['HRU'][i] not in hru_wrt_use.keys():
            hru_wrt_use[ttemp['HRU'][i]] = dict()
        
        if wrsf_id not in hru_wrt_use[ttemp['HRU'][i]].keys():
            hru_wrt_use[ttemp['HRU'][i]][wrsf_id] = dict()
        
        if ttemp['WRID'][i] not in hru_wrt_use[ttemp['HRU'][i]][wrsf_id].keys():
            hru_wrt_use[ttemp['HRU'][i]][wrsf_id][ttemp['WRID'][i]] = [] 
        
        hru_wrt_use[ttemp['HRU'][i]][wrsf_id][ttemp['WRID'][i]].append([ttemp['YEAR'][i],ttemp['WATER(acre-ft)'][i]])

#%%

check_wrt_use = dict()
for wrsf in hru_wrt_dict.keys():
    
    ttemp = hru_wrt_dict[wrsf]
    
    wrsf_id = wrsf[[i for i, ltr in enumerate(wrsf) if ltr == '_'][1]+1:]
    
    if wrsf_id == 'org':
        wrsf_id = 212
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

for i in range(0,213):
    ttemp = wrs_use_all[:,i,:]
    for ii in check_wrt_use[i].keys():
        cy = 0
        for iii in check_wrt_use[i][ii].keys():
            tdif = check_wrt_use[i][ii][iii] - ttemp[cy,int(ii-1)]
            if abs(tdif) > 0.001:
                print(i,int(ii),int(iii),tdif)
            
            cy += 1
            

#%%

for hruid in hru_wrt_use.keys():
    for iterid in hru_wrt_use[hruid].keys():
        for wrid in hru_wrt_use[hruid][iterid].keys():
            total_use = 0
            for i in range(0,len(hru_wrt_use[hruid][iterid][wrid])):
                total_use = total_use + hru_wrt_use[hruid][iterid][wrid][i][0]
        hru_wrt_use[hruid][iterid][wrid] = {'TOTAL_USE': total_use}
        

#%%

for wrf in wrs_dict.keys():
    rowids = np.where(np.asarray(wrs_dict[wrf]['WR_VOL_ft-acre']) > 999990)[0][0:10]
    wrid = np.unique(np.asarray(wrs_dict[wrf]['WR_ID'])[rowids])
    if len(wrid) > 1:
        print('Problem with: '+wrf)

#%%

#out_path = r'/Users/sammy/Documents/Research/SWAT/ITERS_Results/'
out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'
#out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'

fnames = os.listdir(out_path)

varnames = ["LULC","HRU","GIS","SUB","MGT","AREAkm2","BIOMt/ha","YLDt/ha","IRRmm","NAUTOkg/ha","PAUTOkg/ha"]
varcols = [i for i in range(0,10)]

hru_out_dict = {}
# file_counter = 1

for ff in fnames:

    if '.hru' in ff:
        print(ff)
        
        try:
            df_rch = Get_output_hru(out_path + '/' + ff, varcols, varnames)
            #df_rch = pd.read_table(out_path + '/' + ff, skiprows=9, 
                #delim_whitespace=True, names = ["LULC","HRU","GIS","SUB","MGT","AREAkm2","BIOMt/ha","YLDt/ha","IRRmm","NAUTOkg/ha","PAUTOkg/ha"], 
                #index_col = False, low_memory = False)
                
            df_rch = df_rch.drop(['MGT', 'GIS'], axis=1)
            df_rch = df_rch.rename(columns={'MON':'YEAR'})
            mon_yr = df_rch['YEAR'].tolist()
            df_rch = df_rch.iloc[np.where(np.asarray(mon_yr) > 13)[0]]
            df_rch['Total_Yield'] = df_rch['AREAkm2']*100*df_rch['YLDt/ha']
            
            
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


#%%

org_hru_data = hru_out_dict['output_org']
# max_use = wrs_use_all[:,0,:]

hru_param_diff = dict()
hru_param = ['BIOMt/ha', 'YLDt/ha', 'IRRmm', 'NAUTOkg/ha']

for hru_var in hru_param:
    hru_param_diff[hru_var] = np.zeros((11346,213))
    
    for fid in hru_out_dict.keys():
        fid_id = fid[[i for i, ltr in enumerate(fid) if ltr == '_'][0]+1:]
        if fid_id == 'org':
            fid_id = 212
        print(fid_id)
        for hruid in hru_out_dict[fid].keys():
            hru_param_diff[hru_var][int(hruid)-1,int(fid_id)] = sum(abs(np.asarray(hru_out_dict[fid][hruid][hru_var]) - np.asarray(org_hru_data[hruid][hru_var])))
        
        
    
var_diff = hru_param_diff['YLDt/ha']
    


#%%
# #out_path = r'/Users/sammy/Documents/Research/SWAT/ITERS_Results/'
out_path = r'/Users/sammy/Library/CloudStorage/Box-Box/Research/SWAT/SWAT_JetStream_runs/ITERS_Results'
#out_path = r'C:\Users\riversam\Box\Research\SWAT\SWAT_JetStream_runs\ITERS_Results'

fnames = os.listdir(out_path)

wrs_use_dict = {}
file_counter = 1

for ff in fnames:

    if '.rch' in ff:
        print(ff)

        df_rch = pd.read_table(out_path + '/' + ff, skiprows=9, delim_whitespace=True , 
                                usecols=[0,1,2,3,4,5,6,16,17,20,21,28,29,47,48,49], 
                                names = ["FILE","RCH","GIS","MON","AREAkm2","FLOW_INcms","FLOW_OUTcms",
                                        "NO3_INkg","NO3_OUTkg","NO2_INkg","NO2_OUTkg","TOT Nkg","DISOX_INkg", " DISOX_OUTkg",
                                        "TOT Pkg","NO3_mg_l"],
                                index_col = False,low_memory = True)

        REACHES = df_rch['RCH'].unique().tolist()
        YEARS = df_rch['MON'].unique().tolist()
        yrs = [int(item) for item in YEARS]
        yrs = list(filter(lambda x: x >= 999, yrs))
        yrs_start = min(yrs)
        yrs_end = max(yrs)
        
        # data = df[["RCH","MON","FLOW_OUTcms"]].copy()
        # data = data[data["MON"] < 13]
        # for REACH in REACHES:
        #     data2 = data[data["RCH"] == REACH]
        #     pd.options.mode.chained_assignment = None
        #     data2['date'] = pd.date_range(start='1/1/'+str(yrs_start), end = '12/31/'+str(yrs_end), freq='M')
        #     data3 = data2[["date","FLOW_OUTcms"]].copy()
        #     data3.set_index("date",inplace=True)
        #     data3 = data3.rename(columns={"FLOW_OUTcms": "val"})
        #     ### Compute SSI ###
        #     norm_spi = spi(data3, nscale, nseas)
        #     df_SSI = df_SSI.reindex(norm_spi.index)
        #     df_SSI = df_SSI.join(norm_spi)
        #     df_SSI = df_SSI.rename(columns={"spi":REACH})
        # df_SSI.index = pd.to_datetime(df_SSI.index)