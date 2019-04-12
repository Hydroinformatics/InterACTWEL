# -*- coding: utf-8 -*-
import os, shutil, csv
from osgeo import gdal
from scipy import stats
import numpy as np

#sys.path.append('C:/Program Files/QGIS 2.18/apps/qgis-ltr/python/plugins')
#sys.path.append('C:/Program Files/QGIS 2.18/apps/qgis-ltr/python')
#sys.path.append('C:/Program Files/QGIS 2.18/apps/Python27/Lib')
#sys.path.append('C:/Program Files/QGIS 2.18/apps/Python27/Lib/site-packages')

#import processing 
#from qgis.analysis import QgsZonalStatistics
#from PyQt4.QtCore import QFileInfo
#from qgis.core import *

#sys.path.append('C:/Program Files/QGIS 2.18/apps/qgis-ltr/python/qgis/PyQt')


#os.chdir('../parsers')
#import QSWAT_preprocess


def StringToRaster(raster):
    # Check if string is provided

    fileInfo = QFileInfo(raster)
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()

    layer = QgsRasterLayer(path, baseName)
    
    return layer

def copyshp(basefile,copyfile):
    
    shutil.copy2(files['hru_file'], copyfile)
    
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
    zonal_shape = files['output_path'] + '\zonal_shape_HRUids.shp'
    copyshp(files['hru_file'],zonal_shape)
    
    print 'Zonal_Stats of InterACTWEL_Landuse'
    zonal_lyr = QgsVectorLayer(zonal_shape, 'zonal_shape_HRUids', 'ogr')
    #processing.runalg('qgis:zonalstatistics', files['landuse_file'], 1, files['hru_file'], '_', 0, zonal_shape)
    #landuse_lyr = StringToRaster(files['landuse_file'].replace('\\','/'))
    landuse_lyr = files['landuse_file'].replace('\\','/')
    zoneStat = QgsZonalStatistics(zonal_lyr,landuse_lyr,"", 1, QgsZonalStatistics.Majority)
    zoneStat.calculateStatistics(None)
    
    
    hrusid_cdl = []
    lyr = QgsVectorLayer(zonal_shape, '', 'ogr')
    for feat in lyr.getFeatures():
        attrs = feat.attributes()
        if int(attrs[len(attrs)-1]) > 148:
            hrusid_cdl.append(attrs[6]) 
    
    print 'Zonal_Stats of NLCD'
    zonal_shape = files['output_path'] + '\zonal_shape_NLCD.shp'
    copyshp(files['hru_file'],zonal_shape)
    #processing.runalg('qgis:zonalstatistics', files['nlcd_file'], 1, files['hru_file'], '_', 0, zonal_shape)
    zonal_lyr = QgsVectorLayer(zonal_shape, 'zonal_shape_NLCD', 'ogr')
    landuse_lyr = files['nlcd_file'].replace('\\','/')
    zoneStat = QgsZonalStatistics(zonal_lyr,landuse_lyr,"", 1, QgsZonalStatistics.Majority)
    zoneStat.calculateStatistics(None)
    
    HRU_NLCDdict = dict()
    lyr = QgsVectorLayer(zonal_shape, '', 'ogr')
    for feat in lyr.getFeatures():
        attrs = feat.attributes()
        HRU_NLCDdict[attrs[6]] = int(attrs[len(attrs)-1])
    
    # Read and create dictionary of DBF tables. Helps to validate the mapping of raster value to crop type.
    fnames = os.listdir(files['cdl_path'])
    findex = []
    c = 0
#        DBF_dict = dict()
    
    for fname in fnames:
        if '.tif.' not in fname and '.tfw' not in fname and '_mf.tif' in fname:
            findex.append((c,int(fname[4:8])))
        c += 1    
    
    findex = np.asarray(findex)
    
    HRU_CDLdict = dict()
    
    for year in years: 
        print 'Zonal_Stats of ' + fnames[findex[findex[:,1]==year,0][0]]
        cdl_raster = files['cdl_path'] + '\\' + fnames[findex[findex[:,1]==year,0][0]]
        
#        (base, suffix) = os.path.splitext(os.path.basename(cdl_raster))
#        CDLFile = output_path.replace('\\','/') + '/' +  base + '_clp' + suffix
#        print("Clipping CDL to NLCD extent")
#        QSWAT_preprocess.clipraster(cdl_raster, CDLFile, landuse_file, gdal.GRA_Mode)
#        print("Done clipping")
        
        zonal_shape = files['output_path'] + '\zonal_shape_' + str(year) + '.shp'
        #processing.runalg('qgis:zonalstatistics', cdl_raster, 1, files['hru_file'], '_', 0, zonal_shape)
        
        copyshp(files['hru_file'],zonal_shape)
        #processing.runalg('qgis:zonalstatistics', files['nlcd_file'], 1, files['hru_file'], '_', 0, zonal_shape)
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

files = dict()        
files['output_path'] = 'C:\Users\sammy\Documents\GitHub\InterACTWEL\src\PySWAT\SWAT_post_process\dev\Sensitivity_Analysis\Test_Nick'
files['cdl_path'] = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\CDL_Data'
files['hru_file'] = 'C:\Users\sammy\Documents\Research\SWAT\QSWATplus\WillowSWAT12\willow_v2\Watershed\Shapes\hru1.shp'
files['landuse_file'] = 'C:\Users\sammy\Documents\Research\SWAT\QSWATplus\WillowSWAT12\WillowSWAT12_test\InterACTWEL_Landuse.tif'
files['nlcd_file'] = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\NLCD_proj.tif'

#years = range(2012,2017)
#
#HRU_CDLdict, HRU_NLCDdict, hrusid_cdl = Zonal_Statistic_CDL(files, years)
#
##%%
## Land use IDS of non-crops
## Use to convert these land uses to background
#no_crop_ids = [0,60,63,64,65,81,82,83,87,88,92,111,112,121,
#               122,123,124,131,141,142,143,152,176,190,195]
#           
## Only consider major Crops
#no_crop_ids =[no_crop_ids,range(2,7),10,11,13,22,range(25,31),range(32,36),38,39,
#              41,42,45,46,47,48,50,51,52,54,55,56,58,60,range(67,71),72,74,
#              75,76,77,204,range(206,215),range(216,228),range(229,251),254]
#
#temp = []
#for i in no_crop_ids:
#    if np.size(i) > 1:
#        for ii in i:
#            temp.append(ii)
#    else:
#        temp.append(i)
#
#no_crop_ids = temp
#
#
##%%
#temp_dict = HRU_CDLdict
#hrus = HRU_CDLdict[years[0]].keys()
#
#HRU_CDLdict = dict()
#for hruid in hrus:
#    temp_array = []
#    for year in years:
#        if temp_dict[year][hruid] not in no_crop_ids:
#            temp_array.append(temp_dict[year][hruid])
#        else:
#            temp_array.append('nan')
#    
#    HRU_CDLdict[str(hruid)] = temp_array

#%%
#print 'Writing CSV'
output_file = files['output_path'].replace('\\','/') + '/HRU_CDL_mode.csv'
#with open(output_file, mode='wb') as outputcsv:
#    outputcsv_writer = csv.writer(outputcsv, delimiter = ',', quotechar = '"', quoting=csv.QUOTE_MINIMAL)        
#    outputcsv_writer.writerow(['HRU_ID','2012','2013','2014','2015','2016'])
#    
#    for hru in HRU_CDLdict.keys():
#        if hru in hrusid_cdl:
#            temp_str = str(hru)
#            outputcsv_writer.writerow([str(hru),str(HRU_CDLdict[hru][0]),str(HRU_CDLdict[hru][1]),str(HRU_CDLdict[hru][2]),
#                                   str(HRU_CDLdict[hru][3]),str(HRU_CDLdict[hru][4])])
#        else:
#            temp_str = str(hru)
#            outputcsv_writer.writerow([str(hru),str(HRU_NLCDdict[hru]),'-','-','-','-'])
#        
#        
#outputcsv.close()
#
#print 'Finish writing CSV'


#%%
crop_seq = dict()
crop_hru_non_nan = []
all_crops = []
with open(output_file, mode='r') as outputcsv:
    csv_reader = csv.reader(outputcsv, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count > 0 and '-' not in row[2]:
            crop_seq[row[0]] = [np.float(row[1]),np.float(row[2]),np.float(row[3]),np.float(row[4]),np.float(row[5])]
            crop_hru_non_nan.append(row[0])
            all_crops.append([np.float(row[1]),np.float(row[2]),np.float(row[3]),np.float(row[4]),np.float(row[5])])
        line_count += 1

all_crops = np.asmatrix(np.asarray(all_crops))
all_crops_mat = np.unique(np.array(all_crops).flatten())
all_crops_mat = all_crops_mat[np.where(np.isnan(all_crops_mat)==False)]    

crop_seq = dict()
for ucrop in all_crops_mat:
    row_ids = np.array(np.where(all_crops[:,0] == ucrop)[0])
    temp_dict = dict()
    if len(row_ids) > 0:
        sequ, seqc = np.unique(all_crops[row_ids,:], return_index=False, return_inverse=False, return_counts=True, axis=0)
        temp_dict['Sequences'] = sequ
        temp_dict['Count'] = seqc
        crop_seq[ucrop] = temp_dict
        

#print 'Writing CSV'
output_file = files['output_path'].replace('\\','/') + '/CDL_Sequence_Data.csv'
with open(output_file, mode='wb') as outputcsv:
    outputcsv_writer = csv.writer(outputcsv, delimiter = ',', quotechar = '"', quoting=csv.QUOTE_MINIMAL)        
    outputcsv_writer.writerow(['CROP_ID','2012','2013','2014','2015','2016','Count'])
    
    for crop in crop_seq.keys():
        for seqid in range(0,len(crop_seq[crop]['Count'])):
            outputcsv_writer.writerow([crop,crop_seq[crop]['Sequences'][seqid][0],crop_seq[crop]['Sequences'][seqid][1],crop_seq[crop]['Sequences'][seqid][2],crop_seq[crop]['Sequences'][seqid][3],crop_seq[crop]['Sequences'][seqid][4],crop_seq[crop]['Count'][seqid]])

        
        
outputcsv.close()

print 'Finish writing CSV'
        
    
    
 
        