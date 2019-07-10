import os, argparse, re, QSWAT_preprocess
from osgeo import gdal

#subbasinsFile = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\Watershed\Shapes\watershed2.shp'
#demFile = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\DEM_proj_30m.tif'
#output_path = 'C:\Users\sammy\Documents\Research\SWAT\QSWATplus\WillowSWAT12'

#%%

def ClipDEM(file_path):
    
    with open(file_path,'rb') as search:
        for line in search:
            if 'subbasinsFile' in line:
                linesplit = re.split('\s',line)
                subbasinsFile = linesplit[2].replace('\\','/')
            elif 'demFile' in line:
                linesplit = re.split('\s',line)
                demFile = linesplit[2].replace('\\','/')
            elif 'output_path' in line:
                linesplit = re.split('\s',line)
                output_path = linesplit[2].replace('\\','/')
                
    search.close()
    
    (base, suffix) = os.path.splitext(os.path.basename(subbasinsFile))
    SubbasinRaster = output_path.replace('\\','/') + '/' + base + '.tif'
    
    print("Rasterising subbasin shapefile...")
    print demFile
    QSWAT_preprocess.CreateSubbasinTiff(subbasinsFile, SubbasinRaster, demFile)
    exists = os.path.isfile(SubbasinRaster)
    print("Done creating Subbasin Raster")
    
    if exists:
        (base, suffix) = os.path.splitext(os.path.basename(demFile))
        CropDem = output_path.replace('\\','/') + '/' +  base + '_clp' + suffix
        print("Clipping DEM to subbasin extent")
        QSWAT_preprocess.clipraster(demFile, CropDem, SubbasinRaster, gdal.GRA_Bilinear)
        print("Done clipping")


#%%    
if __name__ == '__main__':
    
##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
    parser = argparse.ArgumentParser(description='Inputs File')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                        help='Path to text file with list of input Files')
    args = parser.parse_args()
    user_cwd = os.getcwd()
    
    print args.path[0]
    ClipDEM(args.path[0].replace('\\','/'))

#path = 'C:\Users\sammy\Desktop\Nick_Analysis\SWATEditor\WillowDEM.txt'
#ClipDEM(path.replace('\\','/'))
    
    