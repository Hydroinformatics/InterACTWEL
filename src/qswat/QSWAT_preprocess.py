# -*- coding: utf-8 -*-
import re, os, sys
from osgeo import gdal, ogr, osr
import numpy as np

os.chdir('..\src')
sys.path.append(os.getcwd())

import QSWAT_utils


#%%
class Data_Preprocess:
    
    def __init__(self):
        
        # Moving filter (mode) size [height width]
        self.winSize = [3,3]
        
        #Define CDL data
        self.CDL = []
        self.CDL_org = []
        
        # Initialize hrus, soil and slope paths
        self.dem_file = ''
        self.nlcd_file = ''
        self.soil_file = ''
        self.watershed_file = ''
        self.output_path = ''
        
        ## Find CDL raster files (.tif) in given directory & read .ddf (feature properties) table
        self.cdl_path = ''
        self.boundary_lyr = ''
        self.boundary_raster = ''
        self.clip_dem = ''
        self.clip_nlcd = ''
        self.clip_soil = ''

#%%
# Parse file paths of data that needs pre-processing.
# The analysis uses as a reference for extent and proj. the sub-basins shapefile.

    def ReadInputFile(self,file_path):
        subbasinsFile = ''
        output_path = ''
        
        with open(file_path,'rb') as search:
            for line in search:
                if 'subbasinsFile' in line:
                    linesplit = re.split('\s',line)
                    self.watershed_file = linesplit[2].replace('\\','/')
                    
                elif 'demFile' in line:
                    linesplit = re.split('\s',line)
                    self.dem_file = linesplit[2].replace('\\','/')
                
                elif 'nlcdFile' in line:
                    linesplit = re.split('\s',line)
                    self.nlcd_file = linesplit[2].replace('\\','/')
                    
                elif 'soilFile' in line:
                    linesplit = re.split('\s',line)
                    self.soil_file = linesplit[2].replace('\\','/')
                                                                    
                elif 'cdlPath' in line:
                    linesplit = re.split('\s',line)
                    self.cdl_path = linesplit[2].replace('\\','/')
                    
                elif 'output_path' in line:
                    linesplit = re.split('\s',line)
                    self.output_path = linesplit[2].replace('\\','/')
                        
        search.close()
    
        if self.watershed_file == '':
            print('Error: A sub-basin shapefile must be provided.')
            sys.exit()
            
        if self.output_path == '':
            print('Warning: An output path was not provided. The results will be saved at: ' + os.getcwd())
            self.output_path = os.getcwd()

#%%
    # Dissolves all sub-basins into a single polygon that demarks the boundary of the region.
    # It also creates a tif file of the region if needed
    def DissolveWatersheds(self, tif_bool=1):
        
        (base,suffix) = os.path.splitext(self.watershed_file)
        
        temp_ind = base.rfind('/')
        base_name = base[temp_ind+1:]
    
        # Dissolves all sub-basins into one large regional boundary
        if suffix == '.shp':
            print("Dissolving subbasins into a single polygon.")
            #processing.runalg('qgis:dissolve', self.watershed_lyr.replace('\\','/'), True, '', base + '_boundary.shp')
            boundary_shp = self.output_path + '/' + base_name + '_boundary.shp'
            
            commandtxt = 'ogr2ogr ' + boundary_shp + ' ' + self.watershed_file + ' -dialect sqlite -sql "SELECT ST_Union(geometry) AS geometry FROM ' + base_name + '"'
            exitflag = os.system(commandtxt)
            
            if exitflag == 0:
                print("Successful Dissolve of subbasins")
                self.boundary_lyr = boundary_shp
            else:
                print("Unable to Dissolve subbasins into a single polygon.")
                sys.exit()
        
        if tif_bool == 1:
            # Uses the extent of the regional boundary to create a binary raster (uses the same CSR as the sub-basins shapefile)
            (base, suffix) = os.path.splitext(os.path.basename(self.watershed_file))
            SubbasinRaster = self.output_path + '/' + base + '.tif'
            
            boundary_buffer_shp = self.output_path + '/' + base_name + '_buffer.shp'
            commandtxt = 'ogr2ogr ' + boundary_buffer_shp + ' ' + self.watershed_file + ' -dialect sqlite -sql "SELECT ST_Union(ST_buffer(geometry,500)) AS geometry FROM ' + base_name + '"'
            exitflag = os.system(commandtxt)
            
            self.boundary_lyr = boundary_buffer_shp
            
            print("Rasterising boundary shapefile...")
            BoundaryRaster = self.output_path + '/' + base + '_boundary.tif'
            QSWAT_utils.CreateTiff(self.boundary_lyr, BoundaryRaster, self.dem_file)
            self.boundary_raster = BoundaryRaster
            print("Done creating boundary Raster")
            
            print("Rasterising subbasin shapefile...")
            QSWAT_utils.CreateTiff(self.watershed_file, SubbasinRaster, self.dem_file,'PolygonID',0, self.boundary_lyr)
            self.watershed_raster = SubbasinRaster
            print("Done creating Subbasin Raster")
    
#%%
    def Clip_Rasters(self):
        exists = os.path.isfile(self.boundary_raster)
        # Uses the extent of the regional boundary/raster to clip DEM (and reproject if needed to the same CSR as the sub-basins shapefile)
        if exists:
            if self.dem_file != '':
                (base, suffix) = os.path.splitext(os.path.basename(self.dem_file))
                ClipDem = self.output_path + '/' +  base + '_clp' + suffix
                print("Clipping DEM to subbasin extent")
                QSWAT_utils.Clipraster(self.dem_file, ClipDem, self.boundary_raster, gdal.GRA_Bilinear)
                print("Done clipping DEM")
                self.clip_dem = ClipDem
            
            if self.nlcd_file != '':
                (base, suffix) = os.path.splitext(os.path.basename(self.nlcd_file))
                landuseRaster = self.output_path + '/' +  base + '_clp' + suffix
                print("Clipping NLCD to subbasin extent")
                QSWAT_utils.Clipraster(self.nlcd_file, landuseRaster, self.boundary_raster, gdal.GRA_Mode)
                print("Done clipping NLCD")
                self.clip_nlcd = landuseRaster
        
            if self.soil_file != '':
                (base, suffix) = os.path.splitext(os.path.basename(self.soil_file))
                SoilRaster = self.output_path + '/' + base + '_clp' + suffix
                print("Clipping Soil to subbasin extent")
                QSWAT_utils.Clipraster(self.soil_file, SoilRaster, self.boundary_raster, gdal.GRA_Mode)
                print("Done clipping Soil Raster")
                self.clip_soil = SoilRaster 
                
            if self.cdl_path != '':
                
                if not os.path.isdir(self.output_path + '/CDL_Clip'):
                    os.mkdir(self.output_path + '/CDL_Clip')
                    
                self.cld_clip_path = self.output_path + '/CDL_Clip'
                fnames = os.listdir(self.cdl_path)
                findex = []
                c = 0        
                for fname in fnames:
                    if '.tif.' not in fname and '.tfw' not in fname and '.tif' in fname:
                        findex.append((c,int(fname[4:8])))
                    c += 1    
                
                findex = np.asarray(findex)
                years = range(min(findex[:,1]),max(findex[:,1])+1)
                c=0
                for year in years: 
                    print 'Clipping: ' + fnames[findex[findex[:,1]==year,0][0]]
                    (base, suffix) = os.path.splitext(os.path.basename(fnames[findex[findex[:,1]==year,0][0]]))
                    CDLRaster = self.output_path + '/CDL_Clip/' + base + '_clp' + suffix
                    QSWAT_utils.Clipraster(self.cdl_path + '/' + fnames[findex[findex[:,1]==year,0][0]], CDLRaster, self.boundary_raster, gdal.GRA_Mode)
                
                
        else:
            print("A raster of the region is needed to clip the DEM. Please use the DissolveWatersheds function to create a raster of the region.")
            sys.exit()
            