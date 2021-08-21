# -*- coding: utf-8 -*-
import os, argparse, sys, numpy

os.chdir('..\src')
print os.getcwd()
sys.path.append(os.getcwd())

from qswat import QSWAT_preprocess, QSWAT_utils
from tools.hru_creator.InterACTWEL_HRU_Creator import HRUs_Creator

from matplotlib import pyplot as plt
import scipy.io as sio

#%%    
#if __name__ == '__main__':
#    
###%% Parse Path to DEM File
#    parser = argparse.ArgumentParser(description='Inputs File')
#    parser.add_argument('path', metavar='-p', type=str, nargs='+',
#                        help='Path to text file with list of input Files')
#    args = parser.parse_args()
#    user_cwd = os.getcwd()

path = r'C:\Users\sammy\Documents\GitHub\InterACTWEL\data\Willow_HRUs.txt'

preprocess = QSWAT_preprocess.Data_Preprocess()
preprocess.ReadInputFile(path.replace('\\','/'))
preprocess.DissolveWatersheds()
preprocess.Clip_Rasters()

IHRU_path = r'C:\Users\sammy\Documents\GitHub\InterACTWEL\data\WillowStep1_2.txt'

IHRUs = HRUs_Creator()
IHRUs.ReadInputFile(IHRU_path)

#IHRUs.swat_path = ''
IHRUs.soil_file = preprocess.clip_soil
#IHRUs.landuse_file = ''
IHRUs.nlcd_file = preprocess.clip_nlcd 
IHRUs.watershed_raster = preprocess.watershed_raster
#IHRUs.cdl_file = ''
IHRUs.cdl_path = preprocess.cld_clip_path
IHRUs.boundary_raster = preprocess.boundary_raster

IHRUs.Read_Watershed_Raster()

#newHRUs = numpy.zeros(IHRUs.watersheds.shape)
#newHRUs_B = numpy.zeros(IHRUs.watersheds.shape)

#%%

CDL_org = IHRUs.ReadCDL()
#% Convert to background non-crop data. Required inputs: Raster values of no-crop data 
for noncrop in IHRUs.no_crop_ids:
    CDL_org[CDL_org==noncrop] = 0
   
IHRUs.CDL_org = CDL_org

un_water = numpy.unique(IHRUs.watersheds.flatten())
un_water = un_water[numpy.where(un_water != 0)]

##for wid in range(23,24):
#for wid in un_water:
#    IHRUs.temp_wid = wid
#    temp_watershed = numpy.asarray(IHRUs.watersheds == wid, dtype=numpy.int64)
#
#    left_col, right_col = QSWAT_utils.Raster_col_boundaries(temp_watershed)
#    top_row, last_row = QSWAT_utils.Raster_row_boundaries(temp_watershed) 
#    IHRUs.wdims = [top_row,last_row,left_col,right_col]
#
#    temp_watershed = temp_watershed[top_row:last_row+1,left_col:right_col+1]
#    IHRUs.wid_array = temp_watershed
#    
#    IHRUs.CDL = IHRUs.Watershed_CDL()
#    IHRUs.Create_Operation_timeseries()
#    
##    temp = sio.loadmat('C:/Users/sammy/Documents/Research/SWAT/Umatilla_Input_data/PythonCDL.mat')
##    
##    IHRUs.LST_Ll = temp['LST_LlNp']
##    IHRUs.LST_LlNb = temp['LST_LlNpb']
##    IHRUs.LST_LlNc = temp['LST_LlNpc']
##    IHRUs.LST_LlNd = temp['LST_LlNpd']
#    
##        temp_mat = IHRUs.LST_LlNd[:,0].reshape(IHRUs.wid_array.shape)
##        plt.matshow(temp_mat)
##        plt.show()
#    
#    if numpy.sum(IHRUs.LST_LlNd.flatten()) > 0:
#        temp_icrop, temp_icropb = IHRUs.Create_HRUs()
#        IHRUs.newHRUs = IHRUs.MergeNewHRUs(IHRUs.newHRUs, temp_icrop)
#        IHRUs.newHRUs_B = IHRUs.MergeNewHRUs(IHRUs.newHRUs_B, temp_icropb)
#        
#        #plt.matshow(newHRUs)
#        #plt.show()
#    
##sio.savemat('Sub22_IHRUs.mat', {'LST_LlNpd':IHRUs.LST_LlNd,'LST_LlNpc':IHRUs.LST_LlNc,'LST_LlNpb':IHRUs.LST_LlNb,'LST_LlNp':IHRUs.LST_Ll})
#sio.savemat('Willow_HRUs_MajorCrops.mat', {'newHRUs': IHRUs.newHRUs,'newHRUs_B': IHRUs.newHRUs_B})
#
##%%
##temp = sio.loadmat('C:/Users/sammy/Documents/GitHub/Region_HRUs.mat')
#
#file_paths, file_name = os.path.split(IHRUs.soil_file)
#
#new_landuse_raster = file_paths + '/HRUs_Willow_MajCrops.tif'
#
#boundary, boundary_NoData, boundary_ds = QSWAT_utils.Read_Raster(IHRUs.boundary_raster)
##QSWAT_utils.Save_NewRaster(temp['newHRUs_B'], boundary_ds, boundary, new_landuse_raster, -999)
#QSWAT_utils.Save_NewRaster(IHRUs.newHRUs_B, boundary_ds, boundary, new_landuse_raster, -999)

#new_landuse_raster = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\Umatilla_Output_data_TEST\HRUs_Umatilla_MajCrops.tif' # Latest working

#new_landuse_raster = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Zonal_Stats\WR_Tiffs\UHRUs_WR_Region_Latest_Clip.tif'
new_landuse_raster = r'C:\Users\sammy\Documents\Research\SWAT\QSWAT_Input_Data\Umatilla\HRUs_Meghna\Zonal_Stats\WR_Tiffs\UHRUs_WR_Region_Latest_Clip_V3.tif'

IHRUs.landuse_file = new_landuse_raster

#%%
IHRUs.db_path = IHRUs.swat_path.replace('\\','/') + '/QSWATRef2012.mdb'
IHRUs.MergeNLCD_HRU()

# ## Simplify Slopes and Soils
IHRUs.SimplifySoils()
IHRUs.SimplifySlopes()

##%% Create LU Lookup 
IHRUs.CreateLU_LookupTable() 
import numpy as np  
new_hrus_dict = np.asarray(IHRUs.new_hrus_dict)