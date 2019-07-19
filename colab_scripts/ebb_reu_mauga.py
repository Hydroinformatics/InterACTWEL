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
#    
path = 'C:\Users\sammy\Documents\Research\SWAT\Umatilla_Input_data\Umatilla_Data.txt'
preprocess = QSWAT_preprocess.Data_Preprocess()
preprocess.ReadInputFile(path.replace('\\','/'))
preprocess.DissolveWatersheds()
preprocess.Clip_Rasters()

IHRUs = HRUs_Creator()
IHRUs.swat_path = ''
IHRUs.soil_file = preprocess.clip_soil
IHRUs.landuse_file = ''
IHRUs.nlcd_file = preprocess.clip_nlcd
IHRUs.watershed_raster = preprocess.watershed_raster
IHRUs.cdl_file = ''
IHRUs.cdl_path = preprocess.cld_clip_path
IHRUs.boundary_raster = preprocess.boundary_raster

IHRUs.Read_Watershed_Raster()

newHRUs = numpy.zeros(IHRUs.watersheds.shape)
newHRUs_B = numpy.zeros(IHRUs.watersheds.shape)

#%%

CDL_org = IHRUs.ReadCDL()
#% Convert to background non-crop data. Required inputs: Raster values of no-crop data 
for noncrop in IHRUs.no_crop_ids:
    CDL_org[CDL_org==noncrop] = 0
   
IHRUs.CDL_org = CDL_org

for wid in range(5,7):
    IHRUs.temp_wid = wid
    temp_watershed = numpy.asarray(IHRUs.watersheds == wid, dtype=numpy.int64)
    
    plt.matshow(temp_watershed)
    plt.show()

    left_col, right_col = QSWAT_utils.Raster_col_boundaries(temp_watershed)
    top_row, last_row = QSWAT_utils.Raster_row_boundaries(temp_watershed) 
    IHRUs.wdims = [top_row,last_row,left_col,right_col]

    temp_watershed = temp_watershed[top_row:last_row+1,left_col:right_col+1]
    IHRUs.wid_array = temp_watershed
    
    IHRUs.CDL = IHRUs.Watershed_CDL()
    IHRUs.Create_Operation_timeseries()
    
#    temp = sio.loadmat('C:/Users/sammy/Documents/Research/SWAT/Umatilla_Input_data/PythonCDL.mat')
#    
#    IHRUs.LST_Ll = temp['LST_LlNp']
#    IHRUs.LST_LlNb = temp['LST_LlNpb']
#    IHRUs.LST_LlNc = temp['LST_LlNpc']
#    IHRUs.LST_LlNd = temp['LST_LlNpd']
    
#        temp_mat = IHRUs.LST_LlNd[:,0].reshape(IHRUs.wid_array.shape)
#        plt.matshow(temp_mat)
#        plt.show()
    
    temp_icrop, temp_icropb = IHRUs.Create_HRUs()
    newHRUs = IHRUs.MergeNewHRUs(newHRUs, temp_icrop)
    newHRUs_B = IHRUs.MergeNewHRUs(newHRUs_B, temp_icropb)
    
    plt.matshow(newHRUs)
    plt.show()
    
