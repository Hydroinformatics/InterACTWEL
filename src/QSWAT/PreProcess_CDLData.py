#%%
import processing
import os
import numpy as np
from osgeo import gdal



def Save_NewRaster(array, ds, old_raster, newRaster_name, raster_NoData):
    
    [cols, rows] = old_raster.shape
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRaster_name, rows, cols, 1, gdal.GDT_Float64)
    outRaster.SetGeoTransform(ds.GetGeoTransform())
    outRaster.SetProjection(ds.GetProjection())
    outRaster.GetRasterBand(1).WriteArray(array)
    outRaster.GetRasterBand(1).SetNoDataValue(raster_NoData)
    outRaster.FlushCache()
    outRaster = None
    ds=None
    
    return

#%%
def FilterCDL(rootpath_zip, wsize):
    fnames = os.listdir(rootpath_zip)
    findex = []
    c = 0        
    for fname in fnames:
        if '.tif.' not in fname and '.tfw' not in fname and 'mf' not in fname and '.tif' in fname:
            findex.append((c,int(fname[4:8])))
        c += 1    
    
    findex = np.asarray(findex)
    years = range(min(findex[:,1]),max(findex[:,1])+1)
    c=0
    for year in years: 
        print 'Processing: ' + fnames[findex[findex[:,1]==year,0][0]]
        InputRaster = rootpath_zip + '\\' + fnames[findex[findex[:,1]==year,0][0]]
        (base,suffix) = os.path.splitext(rootpath_zip + '\\' + fnames[findex[findex[:,1]==year,0][0]])
        OutputImage = base + '_mfv2' + suffix
        processing.runalg('saga:majorityfilter', InputRaster, 0, wsize, 0, 0, OutputImage)
        print 'Done'
    
#%%
def FilterNLCD(nlcd_filen, wsize):
    print 'Processing: Filter ' + nlcd_filen
    InputRaster = nlcd_filen.replace('\\','/')
    (base,suffix) = os.path.splitext(InputRaster)
    OutputImage = base + '_mf' + suffix
    processing.runalg('saga:majorityfilter', InputRaster, 0, wsize, 0, 0, OutputImage)
    print 'Done'
    
    
    nlcd_raster_ds = gdal.Open(InputRaster, gdal.GA_ReadOnly)
    nlcd_raster = np.asarray(nlcd_raster_ds.GetRasterBand(1).ReadAsArray(),dtype=float)
    
    
    nlcd_raster_dso = gdal.Open(OutputImage, gdal.GA_ReadOnly)
    nlcd_raster_NoDatao = nlcd_raster_dso.GetRasterBand(1).GetNoDataValue()
    
    nlcd_newRaster_name = base + '_mfv2' + suffix
    
    nlcd_rastero = np.asarray(nlcd_raster_dso.GetRasterBand(1).ReadAsArray(),dtype=float)
    if nlcd_raster_NoDatao != None:
        nlcd_rastero[nlcd_rastero == nlcd_raster_NoDatao] = np.float('nan')
    
    nlcd_raster_NoData = -999.0
    
    print ('Merging Original NLCD and Filter NLCD')
    nlcd_rastero[np.where(nlcd_raster == 11.0)] = 11.0
    nlcd_rastero[np.where(nlcd_raster == 21.0)] = 21.0
    nlcd_rastero[np.where(nlcd_raster == 22.0)] = 22.0
    nlcd_rastero[np.where(nlcd_raster == 23.0)] = 23.0
    
    nlcd_rastero[np.where(np.isnan(nlcd_rastero)==True)] = nlcd_raster_NoData
    
    print ('Writing new Filter NLCD raster')
    Save_NewRaster(nlcd_rastero, nlcd_raster_dso, nlcd_raster, nlcd_newRaster_name, nlcd_raster_NoData)
    

#%%
nlcd_filen = 'C:\Users\sammy\Documents\Research\SWAT\Willow_Input_data/nlcd_proj.tif '
FilterNLCD(nlcd_filen, 2)

rootpath_zip = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\CDL_Data'
FilterCDL(rootpath_zip, 2)
