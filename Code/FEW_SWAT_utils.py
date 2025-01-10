# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 11:03:51 2023

@author: riversam
"""
import numpy as np
import os
import re
import pandas as pd
import subprocess

#%%

def Write_new_wrdata(org_file_path, new_file_path, actorid, wrvol):
                   
    txt_file = org_file_path + '/wrdata_' + str(actorid) + '.dat'

    
    file_org = open(org_file_path, 'r')
    Lines = file_org.readlines()
    
    filein = open(new_file_path,'w')
    
    for line in Lines:
        linesplit = line.split()
        if 'year' not in linesplit[0].lower():
            atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
            atxt = atxt + str(int(linesplit[1])).rjust(5) + ''.rjust(3)
            atxt = atxt + str(int(linesplit[2])).rjust(4) + ''.rjust(3)
            
            if int(linesplit[1]) == actorid:
                atxt = atxt + str(wrvol).rjust(6) + ''.rjust(3)
            else:
                atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
                    
            atxt = atxt + str(int(linesplit[4])).rjust(4) + ''.rjust(3)
            atxt = atxt + str(int(linesplit[5])).rjust(4)
            filein.write(atxt + '\n') 
            
        else:
            filein.write(line) 
    
    
    file_org.close()
    filein.close()


#%%
def Get_hru_output(out_path):
    
    fnames = os.listdir(out_path)
    varnames = ["LULC","HRU","GIS","SUB","MGT","AREAkm2","BIOMt/ha","YLDt/ha","IRRmm","NAUTOkg/ha","PAUTOkg/ha", "ETmm", "SW_INITmm", "SW_ENDmm", "PERCmm", "GW_RCHGmm", "REVAPmm", "W_STRS"]
    varcols = [i for i in range(0,len(varnames))]

    f_list = ['output.hru']
    hru_out_dict = {}
    for ff in fnames:

        if ff in f_list:
            
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
                            
                # hru_out_dict[ff[:-4]] = temp_dict
                hru_out_dict = temp_dict
                
            except:
                print('Problem with: ' + str(ff))
    
    return hru_out_dict

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
def run_SWAT(model_path, swat_exe):
    cwdir = os.getcwd()
    os.chdir(model_path)
    exitflag = subprocess.check_call([swat_exe])
    if exitflag == 0:
        print("Successful SWAT run")
    else:
        print(exitflag)
    os.chdir(cwdir)
    
    
#%%

# def Get_wrs_use_dat(out_path, wrlist):
    
#     # fnames = os.listdir(out_path)
    
#     # temp_dict = {}
#     # cc = 0
#     # with open(out_path + '/wrs_use.out', 'r') as search:
#     #     for line in search:

#     #         #linesplit = re.split('\s', line.decode('ascii').replace('\x00', ''))
#     #         linesplit = re.split('\s', line.replace('\x00', ''))
#     #         linesplit = [t for t in linesplit if len(t) > 0]
            
#     #         if cc == 0:
#     #             # print(linesplit)
#     #             columns = linesplit
#     #             for inline in linesplit:
#     #                 temp_dict[inline] = []
#     #         else:
#     #             for ii in range(0, len(columns)):
#     #                 temp_dict[columns[ii]].append(float(linesplit[ii]))

#     #         cc += 1

#     # search.close()
    
#     df = pd.read_table(out_path, sep='\s+', header=0)
    
#     temp_dict = {}
    
#     for wr_id in wrlist:
#         temp_dict[wr_id] = list(df.loc[df['WRID']==wr_id]['WATER(acre-ft)'])    
    
    
#     return temp_dict



#%%


# wrdata_df = pd.read_table(os.getcwd() + '/SWAT_WR_files/test_folder/wrdata.dat', sep='\s+', header=0)
# max_wrid = np.unique(list(wrdata_df['WR_ID']))[-2]

# twrid = 1626
# twrid_data = wrdata_df.loc[(wrdata_df['WR_ID'] == twrid) & (wrdata_df['YEAR_ID'] == 1)]


# hrwwr_dat_df = pd.read_table(os.getcwd() + '/SWAT_WR_files/test_folder/hruwr.dat', sep='\s+', header=None)

# iter_wr_vol = [250, 460]

# temp_hrus = wrs_hrus_dict['hrus'][wrs_hrus_dict['hrus_map_key'][twrid]]


# org_file_path = os.getcwd() + '/SWAT_WR_files/test_folder/wrdata.dat'
# new_file_path = os.getcwd() + '/SWAT_WR_files/test_folder/wrdata_2.dat'


# file_org = open(org_file_path, 'r')
# Lines = file_org.readlines()

# filein = open(new_file_path,'w')

# new_temp_wrs_ids = []

# for line in Lines:
#     linesplit = line.split()
#     if 'year' not in linesplit[0].lower():
#         atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
#         atxt = atxt + str(int(linesplit[1])).rjust(5) + ''.rjust(3)
#         atxt = atxt + str(int(linesplit[2])).rjust(4) + ''.rjust(3)
#         atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
                
#         atxt = atxt + str(int(linesplit[4])).rjust(4) + ''.rjust(3)
#         atxt = atxt + str(int(linesplit[5])).rjust(4)
#         filein.write(atxt + '\n') 
        
#         if int(linesplit[1]) == max_wrid:
#             for ii in range(0,len(iter_wr_vol)):
#                 new_temp_wrs_ids.append(int(max_wrid + ii + 1))
#                 atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
#                 atxt = atxt + str(int(max_wrid + ii + 1)).rjust(5) + ''.rjust(3)
#                 atxt = atxt + str(int(twrid_data.iloc[0]['WR_SOURCE_ID'])).rjust(4) + ''.rjust(3)
#                 atxt = atxt + str(int(iter_wr_vol[ii])).rjust(6) + ''.rjust(3)
                        
#                 atxt = atxt + str(int(twrid_data.iloc[0]['WR_START_PUMPING'])).rjust(4) + ''.rjust(3)
#                 atxt = atxt + str(int(twrid_data.iloc[0]['WR_END_PUMPING'])).rjust(4)
#                 filein.write(atxt + '\n') 
                
#     else:
#         filein.write(line) 

# file_org.close()
# filein.close()


# new_temp_wrs_ids = np.asarray(new_temp_wrs_ids)

# new_file = os.getcwd() + '/SWAT_WR_files/test_folder/hruwr_3.dat'
# filein = open(new_file,'w')

# #atxt = 'HRU_ID, WR_ID, PRIOR, HRU_PRIOR'
# hrucounter = 0
# for i in range(len(hrwwr_dat_df)):
    
#     if hrwwr_dat_df.loc[i][0] in temp_hrus and twrid == hrwwr_dat_df.loc[i][1]:
        
#         atxt = str(hrwwr_dat_df.loc[i][0]).rjust(6) + ''.rjust(3)
#         atxt = atxt + str(new_temp_wrs_ids[hrucounter]).rjust(6) + ''.rjust(3)
#         atxt = atxt + str(hrwwr_dat_df.loc[i][2]).rjust(4) + ''.rjust(3)
#         atxt = atxt + str(hrwwr_dat_df.loc[i][4]).rjust(4) + ''.rjust(3)
#         atxt = atxt + str(hrwwr_dat_df.loc[i][3]).rjust(4)
        
#         hrucounter += 1
        
#     else:
#         atxt = str(hrwwr_dat_df.loc[i][0]).rjust(6) + ''.rjust(3)
#         atxt = atxt + str(hrwwr_dat_df.loc[i][1]).rjust(6) + ''.rjust(3)
#         atxt = atxt + str(hrwwr_dat_df.loc[i][2]).rjust(4) + ''.rjust(3)
#         atxt = atxt + str(hrwwr_dat_df.loc[i][4]).rjust(4) + ''.rjust(3)
#         atxt = atxt + str(hrwwr_dat_df.loc[i][3]).rjust(4)

#     filein.write(atxt + '\n') 
# filein.close()
