# -*- coding: utf-8 -*-
import os, shutil, csv, random, pyodbc, re
from osgeo import gdal
from scipy import stats
import numpy as np

#sys.path.append('C:/Program Files/QGIS 2.18/apps/qgis-ltr/python/plugins')
#sys.path.append('C:/Program Files/QGIS 2.18/apps/qgis-ltr/python')
#sys.path.append('C:/Program Files/QGIS 2.18/apps/Python27/Lib')
#sys.path.append('C:/Program Files/QGIS 2.18/apps/Python27/Lib/site-packages')

import processing 
from qgis.analysis import QgsZonalStatistics
from PyQt4.QtCore import QFileInfo
from qgis.core import *

#sys.path.append('C:/Program Files/QGIS 2.18/apps/qgis-ltr/python/qgis/PyQt')

#os.chdir('../parsers')
#import QSWAT_preprocess

#%%
def StringToRaster(raster):
    # Check if string is provided

    fileInfo = QFileInfo(raster)
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()

    layer = QgsRasterLayer(path, baseName)
    
    return layer

#%%
def copyshp(basefile,copyfile):
    
    shutil.copy2(basefile, copyfile)
    
    exist = os.path.isfile(basefile[:-4] +'.cpg')
    if exist:
        shutil.copy2(basefile[:-4] +'.cpg', copyfile[:-4] + '.cpg')
    
    exist = os.path.isfile(basefile[:-4] +'.dbf')
    if exist:
        shutil.copy2(basefile[:-4] +'.dbf', copyfile[:-4] + '.dbf')
    
    exist = os.path.isfile(basefile[:-4] +'.prj')
    if exist:
        shutil.copy2(basefile[:-4] +'.prj', copyfile[:-4] + '.prj')
    
    exist = os.path.isfile(basefile[:-4] +'.shx')
    if exist:
        shutil.copy2(basefile[:-4] +'.shx', copyfile[:-4] + '.shx')

        
#%%
def Zonal_Statistic_CDL(files, years):
    
    HRU_CDLdict = None
    HRU_NLCDdict = None
    hrusid_cdl = None
    
    if 'hru_file' in files:
        print 'Zonal_Stats of InterACTWEL_Landuse'
        zonal_shape = files['output_path'] + '\zonal_shape_HRUids.shp'
        copyshp(files['hru_file'],zonal_shape)
    
        zonal_lyr = QgsVectorLayer(zonal_shape, 'zonal_shape_HRUids', 'ogr')
        landuse_lyr = files['landuse_file'].replace('\\','/')
        zoneStat = QgsZonalStatistics(zonal_lyr,landuse_lyr,"", 1, QgsZonalStatistics.Majority)
        zoneStat.calculateStatistics(None)
    
        hrusid_cdl = []
        lyr = QgsVectorLayer(zonal_shape, '', 'ogr')
        for feat in lyr.getFeatures():
            attrs = feat.attributes()
            if int(attrs[len(attrs)-1]) > 148:
                hrusid_cdl.append(attrs[6]) 
    
    if 'nlcd_file' in files:
        print 'Zonal_Stats of NLCD'
        zonal_shape = files['output_path'] + '\zonal_shape_NLCD.shp'
        copyshp(files['hru_file'],zonal_shape)
        
        zonal_lyr = QgsVectorLayer(zonal_shape, 'zonal_shape_NLCD', 'ogr')
        landuse_lyr = files['nlcd_file'].replace('\\','/')
        zoneStat = QgsZonalStatistics(zonal_lyr,landuse_lyr,"", 1, QgsZonalStatistics.Majority)
        zoneStat.calculateStatistics(None)
    
        HRU_NLCDdict = dict()
        lyr = QgsVectorLayer(zonal_shape, '', 'ogr')
        for feat in lyr.getFeatures():
            attrs = feat.attributes()
            HRU_NLCDdict[attrs[6]] = int(attrs[len(attrs)-1])
    
    if 'cdl_path' in files:
        # Read and create dictionary of DBF tables. Helps to validate the mapping of raster value to crop type.
        fnames = os.listdir(files['cdl_path'])
        findex = []
        c = 0
        
        for fname in fnames:
            if '.tif.' not in fname and '.tfw' not in fname and '_mf.tif' in fname:
                findex.append((c,int(fname[4:8])))
            c += 1    
    
        findex = np.asarray(findex)
    
        HRU_CDLdict = dict()
    
        for year in years: 
            print 'Zonal_Stats of ' + fnames[findex[findex[:,1]==year,0][0]]
            cdl_raster = files['cdl_path'] + '\\' + fnames[findex[findex[:,1]==year,0][0]]            
            
            zonal_shape = files['output_path'] + '\zonal_shape_' + str(year) + '.shp'
            
            copyshp(files['hru_file'],zonal_shape)
            zonal_lyr = QgsVectorLayer(zonal_shape, 'zonal_shape_' + str(year), 'ogr')
            landuse_lyr = cdl_raster.replace('\\','/')
            zoneStat = QgsZonalStatistics(zonal_lyr,landuse_lyr,"", 1, QgsZonalStatistics.Majority)
            zoneStat.calculateStatistics(None)
            
            temp_dict = dict()
            lyr = QgsVectorLayer(zonal_shape, '', 'ogr')
            for feat in lyr.getFeatures():
                attrs = feat.attributes()
                #print 'Attr' + str(attrs[len(attrs)-1])
                #print attrs[6], attrs[len(attrs)-1]
                temp_dict[attrs[6]] = int(attrs[len(attrs)-1])
            HRU_CDLdict[year] = temp_dict 
        
    return HRU_CDLdict, HRU_NLCDdict, hrusid_cdl
 
#%%
def ReplaceIncompleteSeq(HRU_CDLdict):
    
    temp_hrucdl = HRU_CDLdict
    temp_hrus_nans = []
    for hruid in HRU_CDLdict.keys():
        cnans = 0
        for val in HRU_CDLdict[hruid]:
            if val == 'nan':
                cnans = cnans + 1
        
       # if np.isnan(np.asarray(HRU_CDLdict[hruid], dtype=float)).any():
        if cnans > 0 and cnans != len(HRU_CDLdict[hruid]):
            
            temp_ids = HRU_CDLdict.keys()
            for i in range(len(HRU_CDLdict[hruid])):
                if HRU_CDLdict[hruid][i] != 'nan':
                    temp_ids = FindCropSeq(temp_hrucdl, temp_ids, i, hruid)
            
            temp_seq_array = np.empty((len(temp_ids),len(HRU_CDLdict[hruid])))
            for i in range(len(temp_ids)):
                temp_seq_array[i,:] = HRU_CDLdict[temp_ids[i]]
                
            #print temp_seq_array
            #seq, counts = np.unique(temp_seq_array, return_counts=True, axis=1)
            a = temp_seq_array
            b = np.ascontiguousarray(a).view(np.dtype((np.void, a.dtype.itemsize * a.shape[1])))
            _, idx,counts = np.unique(b, return_index=True, return_counts=True)
            seq = a[idx]
            
            #print hruid, seq, counts
            maxid = np.argmax(counts)
            temp_hrucdl[hruid] = seq[maxid,:]
            
        elif cnans == len(HRU_CDLdict[hruid]):
            temp_hrus_nans.append(hruid)
    
    return temp_hrucdl, temp_hrus_nans

def FindCropSeq(HRU_CDLdict, hru_ids, colid, target_hru):
    
    temp_ids = []
    for hruid in hru_ids:
        if hruid != target_hru and np.isnan(np.asarray(HRU_CDLdict[hruid], dtype=float)).any() == False and HRU_CDLdict[hruid][colid] == HRU_CDLdict[target_hru][colid]:
            temp_ids.append(hruid)
    if len(temp_ids) == 0:
        temp_ids = hru_ids
    return temp_ids

#%%
def FindHRUMgtFiles(swat_path):
    
    swat_files  = os.listdir(swat_path + '/Scenarios/Default/TxtInOut/')
    hru_files = [f for f in swat_files if '.mgt' in f and f != 'output.mgt']
    
    HRUFiles = dict()
    #hrufile = []
    for hfile in hru_files:
        cline = 0
        with open(swat_path + '/Scenarios/Default/TxtInOut/' + hfile) as search:
            for line in search:
                if cline == 0:
                    linesplit = re.split('\s',line)
                    for sptline in linesplit:
                        if 'HRU' in sptline and cline == 0:
                            sptline = re.split(':',sptline)
                            HRUFiles[hfile.strip('.mgt')] = int(sptline[1])
                            #hrufile.append((int(sptline[1]),int(hfile.strip('.mgt'))))
                            cline = cline + 1
                     
    return HRUFiles

#%%
def CDL_NLCDtoSWATdict(db_path):
    
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

    crsr.execute('select * from nlcd2001_lu')

    nlcd_cropdict = dict()
    for row in crsr.fetchall():
        nlcd_cropdict[row[1]] = dict()
        nlcd_cropdict[row[1]]['Name'] = str(row[2])
        if str(row[2]) in cropdict.keys():
            nlcd_cropdict[row[1]]['value'] = cropdict[str(row[2])]
            
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

    return nlcd_cropdict, cdl_cropdict

#%%

def Get_No_Crop_Ids():
    # Land use IDS of non-crops
    # Use to convert these land uses to background
    no_crop_ids = [0,60,63,64,65,81,82,83,87,88,92,111,112,121,
                   122,123,124,131,141,142,143,152,176,190,195]
               
    # Only consider major Crops
    no_crop_ids =[no_crop_ids,range(2,7),10,11,13,22,range(25,31),range(32,36),38,39,
                  41,42,45,46,47,48,50,51,52,54,55,56,58,60,range(67,71),72,74,
                  75,76,77,204,range(206,215),range(216,228),range(229,251),254]
    
    temp = []
    for i in no_crop_ids:
        if np.size(i) > 1:
            for ii in i:
                temp.append(ii)
        else:
            temp.append(i)
    
    no_crop_ids = temp
    
    return no_crop_ids

#%%

files = dict()        

files['output_path'] = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\willow_update_v2\Zonal_Statistics'
files['cdl_path'] = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\CDL_Data'
files['hru_file'] = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\willow_update_v2\Watershed\Shapes\hru1.shp'
files['landuse_file'] = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\willow_update_v2\Source\crop\InterACTWEL_landuse.tif'
files['nlcd_file'] = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\NLCD_proj.tif'

years = range(2012,2017)

hru_name_dict = FindHRUMgtFiles(files['hru_file'][0:files['hru_file'].find('Watershed')-1].replace('\\','/'))

HRU_CDLdict, HRU_NLCDdict, hrusid_cdl = Zonal_Statistic_CDL(files, years)

db_path = files['hru_file'][0:files['hru_file'].find('Watershed')-1].replace('\\','/') + '/QSWATRef2012.mdb'
nlcd_cropdict, cdl_cropdict = CDL_NLCDtoSWATdict(db_path)

#%%
no_crop_ids = Get_No_Crop_Ids()

temp_dict = HRU_CDLdict
hrus = HRU_CDLdict[years[0]].keys()

HRU_CDLdict = dict()
for hruid in hrus:
    temp_array = []
    for year in years:
        if temp_dict[year][hruid] not in no_crop_ids:
            temp_array.append(int(cdl_cropdict[temp_dict[year][hruid]]))
        else:
            temp_array.append('nan')
    
    HRU_CDLdict[str(hruid)] = temp_array

HRU_CDLdict, temp_hrus_nans = ReplaceIncompleteSeq(HRU_CDLdict)

hrus_complete_seq = []
for hru in  HRU_CDLdict.keys():
    if np.isnan(np.asarray(HRU_CDLdict[hru], dtype=float)).any() == False:
        hrus_complete_seq.append(hru)
        

#%%
print 'Writing CSV'
output_file = files['output_path'].replace('\\','/') + '/HRU_CDL_mode.csv'
with open(output_file, mode='wb') as outputcsv:
    outputcsv_writer = csv.writer(outputcsv, delimiter = ',', quotechar = '"', quoting=csv.QUOTE_MINIMAL)        
    outputcsv_writer.writerow(['HRU_ID','2012','2013','2014','2015','2016'])
    
    for hru in HRU_CDLdict.keys():
        #if hru in hrusid_cdl and hru not in temp_hrus_nans:
        if hru not in temp_hrus_nans:
            outputcsv_writer.writerow([hru_name_dict[str(hru)],str(HRU_CDLdict[hru][0]),str(HRU_CDLdict[hru][1]),str(HRU_CDLdict[hru][2]),
                                   str(HRU_CDLdict[hru][3]),str(HRU_CDLdict[hru][4])])
        else:
#            if HRU_NLCDdict[hru] == 81 or HRU_NLCDdict[hru] == 82:
#                temp_hru = str(random.choice(hrus_complete_seq))
#                outputcsv_writer.writerow([str(hru),str(HRU_CDLdict[temp_hru][0]),str(HRU_CDLdict[temp_hru][1]),str(HRU_CDLdict[temp_hru][2]),
#                                   str(HRU_CDLdict[temp_hru][3]),str(HRU_CDLdict[temp_hru][4])])
            if HRU_NLCDdict[hru] == 81:
                outputcsv_writer.writerow([hru_name_dict[str(hru)],'5','5','5','5','5'])
                
            elif HRU_NLCDdict[hru] == 82:
                outputcsv_writer.writerow([hru_name_dict[str(hru)],'2','2','2','2','2'])
            else:
                if 'value' in nlcd_cropdict[HRU_NLCDdict[hru]].keys():
                    outputcsv_writer.writerow([hru_name_dict[str(hru)],str(nlcd_cropdict[HRU_NLCDdict[hru]]['value']),'-999','-999','-999','-999'])
                else:
                    outputcsv_writer.writerow([hru_name_dict[str(hru)],'-999','-999','-999','-999','-999'])
        
        
outputcsv.close()

print 'Finish writing CSV'

      