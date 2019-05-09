import sys, os, numpy, pyodbc, ctypes
from osgeo import gdal, ogr, osr

#%%
def clipraster(InputRaster,OutputImage,RefImage,resample_method):
    #InputRaster = 'C:/Users/sammy/Documents/Research/SWAT/willow_final/DEM_proj_30m.tif'
    #OutputImage = 'C:/Users/sammy/Documents/Research/SWAT/TestResult_DEM.tif'
    #RefImage = 'C:/Users/sammy/Documents/Research/SWAT/TestResult.tif'
    #resample_method = gdal.GRA_Bilinear
    
    InputSrc = gdal.Open(InputRaster, gdal.GA_ReadOnly)
    gdalformat = 'GTiff'
    datatype = InputSrc.GetRasterBand(1).DataType
    NoData_value = -999999
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
    RasterSrcClip = gdal.Open(RefImage, gdal.GA_ReadOnly)
    Projection = RasterSrc.GetProjectionRef()

    warp_opts = gdal.WarpOptions(
            format=gdalformat,
            outputType=datatype, 
            outputBounds=[llx, lly, urx, ury], 
            xRes=xres, 
            yRes=yres, 
            dstSRS=Projection, 
            resampleAlg = resample_method)  
    # resampleAlg = gdal.GRA_NearestNeighbour)

    OutTile = gdal.Warp(OutputImage, InputRaster, options=warp_opts)
    OutTile = None # Close dataset

    return

#%%
def CreateSubbasinTiff(InputVector,OutputImage,RefImage):
    #InputVector = 'C:/Users/sammy/Documents/Research/SWAT/willow_final/Watershed/Shapes/subbasin.shp'
    #OutputImage = 'C:/Users/sammy/Documents/Research/SWAT/TestResult.tif'
    #RefImage = 'C:/Users/sammy/Documents/Research/SWAT/willow_final/DEM_proj_30m.tif'

    gdalformat = 'GTiff'
    datatype = gdal.GDT_Byte
    burnVal = 1 #value for the output image pixels
    ##########################################################
    # Get projection info from reference image
    print RefImage
    Image = gdal.Open(RefImage, gdal.GA_ReadOnly)
    tiffgeo_transform = Image.GetGeoTransform()
    pixel_width = tiffgeo_transform[1]
    # Open Shapefile
    Shapefile = ogr.Open(InputVector)
    Shapefile_layer = Shapefile.GetLayer()
    geo_transform = Shapefile_layer.GetExtent()

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
        #ctypes.windll.user32.MessageBoxW(0, msg, "Warning", 1)
        print(msg)
        #return

    # Rasterise
    Output = gdal.GetDriverByName(gdalformat).Create(OutputImage, x_res, y_res, 1, datatype, options=['COMPRESS=DEFLATE'])
    Output.SetProjection(Image.GetProjectionRef())
    Output.SetGeoTransform((x_min, pixel_width, 0, y_min, 0, pixel_width))
    #Output.SetGeoTransform(tiffgeo_transform)

    NoData_value = -999999

    # Write data to band 1
    Band = Output.GetRasterBand(1)
    Band.SetNoDataValue(NoData_value)
    Band.FlushCache()
    gdal.RasterizeLayer(Output, [1], Shapefile_layer, burn_values=[burnVal])

    # Close datasets
    Band = None
    Output = None
    Image = None
    Shapefile = None

    # Build image overviews
    # subprocess.call("gdaladdo --config COMPRESS_OVERVIEW DEFLATE "+OutputImage+" 2 4 8 16 32 64", shell=True)
    
    return    
    