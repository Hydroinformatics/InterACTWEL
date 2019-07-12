# -*- coding: utf-8 -*-
import os, argparse, sys, numpy

os.chdir('..\src')
sys.path.append(os.getcwd())

from qswat import QSWAT_preprocess, QSWAT_utils
from tools.hru_creator.InterACTWEL_HRU_Creator import HRUs_Creator

#%%    
if __name__ == '__main__':
    
##%% Parse Path to DEM File
    parser = argparse.ArgumentParser(description='Inputs File')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                        help='Path to text file with list of input Files')
    args = parser.parse_args()
    user_cwd = os.getcwd()
    
    preprocess = QSWAT_preprocess.Data_Preprocess()
    preprocess.ReadInputFile(args.path[0].replace('\\','/'))
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
    for wid in range(5,6):
        IHRUs.temp_wid = wid
        temp_watershed = numpy.asarray(IHRUs.watersheds == wid, dtype=numpy.int64)
        left_col, right_col = QSWAT_utils.Raster_col_boundaries(temp_watershed)
        top_row, last_row = QSWAT_utils.Raster_row_boundaries(temp_watershed) 
        IHRUs.wdims = [top_row,last_row,left_col,right_col]
        
        temp_watershed = temp_watershed[top_row:last_row+1,left_col:right_col+1]
        IHRUs.wid_array = temp_watershed
        
        CDL_org = IHRUs.ReadCDL()
        #% Convert to background non-crop data. Required inputs: Raster values of no-crop data 
        for noncrop in IHRUs.no_crop_ids:
            CDL_org[CDL_org==noncrop] = 0
            
        IHRUs.CDL_org = CDL_org
        IHRUs.CDL = IHRUs.Watershed_CDL()
        IHRUs.Create_Operation_timeseries()
