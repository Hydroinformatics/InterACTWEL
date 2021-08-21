import re, os, numpy, shutil
from osgeo import gdal, ogr, osr

#%%
def Raster_row_boundaries(raster):
    
    row_sum_index = numpy.where(numpy.sum(raster,axis=1) != 0)
    top_row = row_sum_index[0][0]
    last_row = row_sum_index[0][-1]
    
    if top_row < 0:
        top_row = 0
    if last_row < 0:
        last_row = 0
        
    return top_row, last_row

def Raster_col_boundaries(raster):
    
    col_sum_index = numpy.where(numpy.sum(raster,axis=0) != 0)
    left_col = col_sum_index[0][0]
    right_col = col_sum_index[0][-1]
    
    if left_col < 0:
        left_col = 0
    if right_col < 0:
        right_col = 0
        
    return left_col, right_col

#%%
def Read_Raster(raster_file, raster_NoData = -999):
    
    raster_ds = gdal.Open(raster_file, gdal.GA_ReadOnly)
    raster_NoData = raster_ds.GetRasterBand(1).GetNoDataValue()
    raster = raster_ds.GetRasterBand(1).ReadAsArray()     
    
    return raster, raster_NoData, raster_ds

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
def Clipraster(InputRaster, OutputImage, RefImage, resample_method):
    
    InputSrc = gdal.Open(InputRaster, gdal.GA_ReadOnly)
    gdalformat = 'GTiff'
    datatype = InputSrc.GetRasterBand(1).DataType
    NoData_value = InputSrc.GetRasterBand(1).GetNoDataValue()
    if NoData_value == None:
        NoData_value = -9999
    ##########################################################
    RasterSrc = gdal.Open(RefImage, gdal.GA_ReadOnly)
    upx, xres, xskew, upy, yskew, yres = RasterSrc.GetGeoTransform()
    cols = RasterSrc.RasterXSize
    rows = RasterSrc.RasterYSize
 
    ulx = upx + 0*xres + 0*xskew
    uly = upy + 0*yskew + 0*yres
 
    llx = upx + 0*xres + rows*xskew
    lry = upy + 0*yskew + rows*yres
 
    lrx = upx + cols*xres + rows*xskew
    ury = upy + cols*yskew + rows*yres
 
    urx = upx + cols*xres + 0*xskew
    lly = upy + cols*yskew + 0*yres
    ##########################################################
    #RasterSrcClip = gdal.Open(RefImage, gdal.GA_ReadOnly)
    Projection = RasterSrc.GetProjectionRef()
    
    if lly > ury:
        old_ury = ury
        ury = lly
        lly = old_ury
        
    warp_opts = gdal.WarpOptions(
            format = gdalformat,
            outputType = datatype, 
            outputBounds = [llx, lly, urx, ury], 
            xRes = xres, 
            yRes = yres, 
            dstSRS = Projection,
            dstNodata = NoData_value,
            resampleAlg = resample_method)  
    # resampleAlg = gdal.GRA_NearestNeighbour)

    OutTile = gdal.Warp(OutputImage, InputRaster, options=warp_opts)
    OutTile = None # Close dataset

    return

#%%
def CreateTiff(InputVector, OutputImage, RefImage, attribute_str = '', burnVal = 1, RefInputVector = '', tiffExtent = '', datatype = gdal.GDT_Byte):

    gdalformat = 'GTiff'
    #burnVal = 1 #value for the output image pixels
    ##########################################################
    # Get projection info from reference image
    #print RefImage
    Image = gdal.Open(RefImage, gdal.GA_ReadOnly)
    tiffgeo_transform = Image.GetGeoTransform()
    pixel_width = tiffgeo_transform[1]
    
    # Open Shapefile
    Shapefile = ogr.Open(InputVector)
    Shapefile_layer = Shapefile.GetLayer()
    geo_transform = Shapefile_layer.GetExtent()
    
    if RefInputVector != '':
        temp_Shapefile = ogr.Open(RefInputVector)
        temp_Shapefile_layer = temp_Shapefile.GetLayer()
        geo_transform = temp_Shapefile_layer.GetExtent()

    if tiffExtent != '':        
        x_min = tiffgeo_transform[0]
        y_max = tiffgeo_transform[3]
        x_max = x_min + tiffgeo_transform[1] * Image.RasterXSize
        y_min = y_max + tiffgeo_transform[5] * Image.RasterYSize
        
        #x_max = tiffgeo_transform[1]
        #y_min = tiffgeo_transform[2]
    
        x_res = int(numpy.round((x_max - x_min)/pixel_width))
        y_res = int(numpy.round((y_max - y_min)/pixel_width))
        
    else:
        x_min = geo_transform[0]
        y_max = geo_transform[3]
        #x_max = x_min + geo_transform[1] * Image.RasterXSize
        #y_min = y_max + geo_transform[5] * Image.RasterYSize
        x_max = geo_transform[1]
        y_min = geo_transform[2]
    
        x_res = int(numpy.round((x_max - x_min)/pixel_width))
        y_res = int(numpy.round((y_max - y_min)/pixel_width))

    if tiffgeo_transform[0] > x_min or tiffgeo_transform[3] < y_max:
        msg = 'Spatial extent of DEM is smaller than subbasin shapefile. RefRaster: ' + str(OutputImage) + ' Xlims: ' + str(tiffgeo_transform[0]) + '>' + str(x_min) + 'Ylims: ' + str(tiffgeo_transform[3]) + '<' + str(y_max)
        print(msg)
        
    # Rasterise
    #print x_res, y_res
    Output = gdal.GetDriverByName(gdalformat).Create(OutputImage, x_res, y_res, 1, datatype, options=['COMPRESS=DEFLATE'])
    Output.SetProjection(Image.GetProjectionRef())
    Output.SetGeoTransform((x_min, pixel_width, 0, y_min, 0, pixel_width))

    NoData_value = -999

    # Write data to band 1
    Band = Output.GetRasterBand(1)
    Band.Fill(NoData_value)
    Band.SetNoDataValue(NoData_value)
    Band.FlushCache()
    
    if attribute_str == '':
        gdal.RasterizeLayer(Output, [1], Shapefile_layer, burn_values=[burnVal])
    else:
        gdal.RasterizeLayer(Output, [1], Shapefile_layer, options=["ATTRIBUTE=" + attribute_str])

    # Close datasets
    Band = None
    Output = None
    Image = None
    Shapefile = None

    return    
#%%