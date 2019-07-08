import os, argparse, re, subprocess, sys
from osgeo import gdal

os.chdir('..\src')
sys.path.append(os.getcwd())

from tools.qswat import QSWAT_preprocess

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
    
    (base,suffix) = os.path.splitext(subbasinsFile.replace('\\','/'))
    
    temp_ind = base.rfind('/')
    base_name = base[temp_ind+1:]

    if suffix == '.shp':
        #processing.runalg('qgis:dissolve', self.watershed_lyr.replace('\\','/'), True, '', base + '_boundary.shp')
        boundary_shp = output_path + '/' + base_name + '_boundary.shp'
        
        commandtxt = 'ogr2ogr ' + boundary_shp + ' ' + subbasinsFile + ' -dialect sqlite -sql "SELECT ST_Union(geometry) AS geometry FROM ' + base_name + '"'
        
        exitflag = os.system(commandtxt)
        if exitflag == 0:
            print("Successful Dissolve of subbasins")
        else:
            sys.exit()
    
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
    
##%% Parse Path to DEM File
    parser = argparse.ArgumentParser(description='Inputs File')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                        help='Path to text file with list of input Files')
    args = parser.parse_args()
    user_cwd = os.getcwd()
    
    print args.path[0]
    ClipDEM(args.path[0].replace('\\','/'))
    
#path = 'C:\Users\sammy\Documents\GitHub\InterACTWEL_Dev\PySWAT\SWAT_post_process\parsers\WillowDEM.txt'
#ClipDEM(path.replace('\\','/'))
#    