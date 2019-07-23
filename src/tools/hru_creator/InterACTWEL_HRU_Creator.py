# -*- coding: utf-8 -*-
#import rasterio, os
from matplotlib import pyplot as plt
import numpy as np
#from dbfpy import dbf
from scipy import stats, ndimage
import scipy.io as sio
import os, sys, re, pyodbc, csv
from osgeo import gdal, osr, ogr

os.chdir('..\..')

from qswat import QSWAT_preprocess, QSWAT_utils

class HRUs_Creator:
    
    def __init__(self):
        
        # Max. landused ID in SWAT crop table
        self.landuseID_max = 148
        #self.ReadInputData()
            
        # ID of watersheds to be used
        self.watershed_ids = range(0+1,24+1)
        
        # Max. number of HRUs
        self.max_hrus = 200
        self.total_hrus = 0
        
        # Min. percentage of farmland represented by HRUs
        self.min_farmland_per = 0.95
        
        # Moving filter (mode) size [height width]
        self.winSize = [3,3]
        
        #Min. HRUs area (pixels)
        self.min_hru_area_a = 10
        self.min_hru_area_b = 2
        
        # Land use IDS of non-crops
        # Use to convert these land uses to background
        no_crop_ids = [0,60,63,64,65,81,82,83,87,88,92,111,112,121,
                       122,123,124,131,141,142,143,152,176,190,195]
                   
        # Only consider major Crops
        no_crop_ids =[no_crop_ids,range(2,7),10,11,13,22,range(25,31),range(32,36),38,39,
                      41,42,45,46,47,48,50,51,52,54,55,56,58,60,range(67,71),72,74,
                      75,76,77,204,range(206,215),range(216,228),range(229,251),254]
        
        temp = []
        for i in no_crop_ids:
            if np.size(i) > 1:
                for ii in i:
                    temp.append(ii)
            else:
                temp.append(i)
        
        self.no_crop_ids = temp
        
        self.nlcd_to_cdl_classes = [71,72,73,74,81,82]
        self.missing_nlcd_classes = []
        
        #Define CDL data
        self.CDL = []
        self.CDL_org = []
        
        #Initialize LST_LlN variables
        self.LST_LlN = []
        self.LST_LlNb = []
        self.LST_LlNc = []
        self.LST_LlNd = []
        
        # Initialize hrus, soil and slope paths
        self.landuse_file = ''
        self.soil_file = ''
        self.slope_file = ''
        self.db_path = ''
        self.swat_path = ''
        self.watershed_path = ''
        self.cdl_file = ''
        
        #self.rootpath = 'Z:\Projects\INFEWS\Modeling\GIS_Data\FINAL_LAYERS'
        ## Find CDL raster files (.tif) in given directory & read .ddf (feature properties) table
        self.cdl_path = ''
        self.boundary_raster = ''
        self.watershed_raster = ''
        
        self.watersheds = None
        self.wid_array = None
        self.temp_wid = None
        

#%%
        
    def MergeNewHRUs(self, new_raster, hrus):
        
        max_hrus = np.max(hrus)
        
        hrus = hrus.reshape(self.wid_array.shape)
        temp_hrus = hrus + self.total_hrus
        
        temp_hrus[np.where(hrus == 0)] = 0
        
        new_raster[self.wdims[0]:self.wdims[1]+1,self.wdims[2]:self.wdims[3]+1] = temp_hrus
        
        self.total_hrus = self.total_hrus + max_hrus
        
        return new_raster
        
        
    def Create_HRUs(self):
        
        LSTtempb = self.LST_LlNd
        [ucrop_row, ucounts, icrops, junk] = np.unique(LSTtempb, axis=0, return_counts = True, return_index = True, return_inverse = True)
    
        # Eliminating rows with only background values
        print 'Eliminating rows with only background values'
        uia = np.unique(icrops)
        if np.sum(ucrop_row[0,:], axis=0) == 0:
            uia = uia[1:]
        
        # Find and save area/cells of blobs of unique crop rotations (HRUs)
        print 'Finding and save area/cells of blobs of unique crop rotations (HRUs)'
        ccc = 1
        icrop_ind = np.zeros(icrops.shape)
        ucrop_count = np.empty((0,3))
        ucrop_count_cells = dict()
        
        for tuia in uia:
            Ltemp = np.asarray(icrops == tuia, dtype=np.int).reshape(self.wid_array.shape)
            labeled_array, num_features = ndimage.measurements.label(Ltemp)
            labeled_area = ndimage.measurements.sum(Ltemp,labeled_array,range(1,num_features+1))
            
#            if np.size(labeled_area) > 5:
#                print tuia, np.size(labeled_area)
            
            for ti in range(0,len(labeled_area)):
                ucrop_count = np.vstack((ucrop_count,[tuia,ccc,labeled_area[ti]]))
                
                icrop_ind[labeled_array.flatten() == ti+1] = ccc
                ucrop_count_cells[ccc] = np.where(labeled_array.flatten() == ti+1)
                ccc = ccc + 1
        
        print 'Total # of Blobs: ' + str(ucrop_count.size)
        
        if ucrop_count.size != 0:
            temp = ucrop_count[:,2]        
            sortid = temp.argsort()[::-1][:len(temp)]
            sort_counts = ucrop_count[sortid,:]
            
            temp_sortid = []
            #temp_sort_ucrop_row = []
            temp_icrop = np.zeros(icrops.shape)
            temp_area = 0
            cc = 0
            
            for ii in range(0,len(sort_counts)):
                if sort_counts[ii,0] != 1:
                    tempi = len(ucrop_count_cells[sort_counts[ii,1]])
                    temp_icrop[ucrop_count_cells[sort_counts[ii,1]]] = sort_counts[ii,1]
                    
                    temp_area = temp_area + tempi
                    tempuia = np.unique(temp_icrop, axis=0)
                    tempuia = tempuia[np.where(tempuia != 0)]
                    temp_sortid.append(ii)
                    
                    if temp_area/np.sum(sort_counts[:,2]) >= self.min_farmland_per or len(tempuia) >= self.max_hrus:
                        break
                    cc = cc + 1
            
            print 'Per. of total area: ' + str(temp_area/np.sum(sort_counts[:,2]))
            
            ids_non_major = np.setdiff1d(range(0,len(sort_counts)), temp_sortid)
            similarity = np.zeros((len(ids_non_major),len(temp_sortid)))
            for ii in range(0,len(ids_non_major)):
                for jj in range(0,len(temp_sortid)):
                    #temp = np.zeros((0,ucrop_row.shape[1]))
                    temp = []
                    for jjj in range(0,len(ucrop_row[0,:])):
                        temp.append(np.asarray(ucrop_row[int(sort_counts[ids_non_major[ii],0]),jjj] == ucrop_row[int(sort_counts[temp_sortid[jj],0]),jjj], dtype=np.int))
                    similarity[ii,jj] = np.sum(temp)
            #maxsim = similarity.argsort()[::-1][:len(temp_sortid)]
            maxsim = np.flip(similarity.argsort(),1)
            
           
            temp_icropi = temp_icrop
            old_length = len(ids_non_major)
            new_length = 0
            iterc = 0
           
            while(new_length == 0):
                print 'Iter: ' + str(iterc)
                ids_non_major_rem = []
                ids_rem_max = []
               
                for jj in range(0,len(ids_non_major)):
                    temp_mcrop = np.zeros(icrops.shape)
                    temp_mcrop[ucrop_count_cells[sort_counts[ids_non_major[jj],1]]] = 1
                    Ltemp = temp_mcrop.reshape(self.wid_array.shape)
                    struct2 = ndimage.generate_binary_structure(2, 2)
                    P = ndimage.morphology.binary_dilation(Ltemp,structure=struct2).astype(Ltemp.dtype)
                    bound_pixels = P - Ltemp
                    blobs = np.unique(temp_icropi[bound_pixels.flatten() != 0])
                    blobs = blobs[np.where(blobs!=0)]
                   
                    #if not np.isempty(blobs):
                    if blobs.size != 0:
                        blobs_id = []
                        maxsim_id = []
#                        print jj
#                        if jj == 13:
#                            stpr = 0
                        for ii in range(0,len(blobs)):
                            #blobs_id = np.vstack((blobs_id,np.where(blobs[ii] == sort_counts[:,1])[0]))
                            blobs_id.append(np.where(blobs[ii] == sort_counts[temp_sortid,1])[0])
                            #maxsim_id = np.vstack((maxsim_id,np.where(blobs_id[ii] == maxsim[jj])[0]))
                            maxsim_id.append(np.where(blobs_id[ii][0] == maxsim[jj,:])[0])
                        
                        blob_sortingid = np.argsort(maxsim_id)
                        
                        maxsim_id = maxsim_id[int(blob_sortingid[0])]
                        blobs_id = blobs_id[int(blob_sortingid[0])]
                       
                        for ii in range(0,len(blobs_id)):
                            temp_mcrop = np.zeros(icrops.shape)
                            temp_mcrop[ucrop_count_cells[sort_counts[blobs_id[ii],1]]] = 1
                            temp_mcrop[ucrop_count_cells[sort_counts[ids_non_major[jj],1]]] = 1
                            labeled_array, num_features = ndimage.measurements.label(temp_mcrop.reshape(self.wid_array.shape))
                           
                            if num_features == 1:
                                tempi = len(ucrop_count_cells[sort_counts[ids_non_major[jj],1]])
                                temp_icropi[ucrop_count_cells[sort_counts[ids_non_major[jj],1]]] = sort_counts[blobs_id[ii],1]
                                temp_cells = np.hstack((ucrop_count_cells[sort_counts[blobs_id[ii],1]][0],ucrop_count_cells[sort_counts[ids_non_major[ii],1]][0]))
                               
                                temp_area = temp_area + tempi
                               
                                ucrop_count_cells[sort_counts[blobs_id[ii],1]] = temp_cells
                                ids_non_major_rem = np.hstack((ids_non_major_rem,ids_non_major[jj]))
                                ids_rem_max = np.hstack((ids_rem_max,jj))
                                break
                            
                ids_rem_max = np.setdiff1d(range(0,len(ids_non_major)), ids_rem_max)
                ids_non_major = np.setdiff1d(ids_non_major, ids_non_major_rem)
                
                if len(ids_non_major) != old_length:
                    maxsim = maxsim[ids_rem_max]
                    old_length = len(ids_non_major)
                    iterc = iterc + 1
                else:
                    new_length = 1
            temp_icropb = temp_icropi
            uia = np.unique(temp_icropi)
            uia = uia[np.where(uia != 0)]
            
            for i in range(0,len(uia)):
                tempLl = np.asarray(temp_icropi == uia[i], dtype=np.int).reshape(self.wid_array.shape)
                tempLl = ndimage.morphology.binary_fill_holes(tempLl,structure=struct2).astype(tempLl.dtype)
                temp_icropb[np.where(tempLl.flatten() == 1)] = i+1
            
            temp_icropc = np.asarray(temp_icropb >0 , dtype=np.int)
            for jj in range(0,len(ids_non_major)):
                temp_icropc[ucrop_count_cells[sort_counts[ids_non_major[jj],1]]] = 2
            
            Ltemp = np.asarray(temp_icropc.reshape(self.wid_array.shape) == 2, dtype=np.int)
            Ltemp = ndimage.morphology.binary_fill_holes(Ltemp,structure=struct2).astype(Ltemp.dtype)
            labeled_array, num_features = ndimage.measurements.label(Ltemp)
            labeled_area = ndimage.measurements.sum(Ltemp,labeled_array,range(1,num_features+1))
            min_area = np.where(labeled_area >= self.min_hru_area_a)[0]
            labeled_area = labeled_area[min_area]
            sidsL = labeled_area.argsort()[::-1][:len(labeled_area)]
            #sarea = labeled_area[sidsL]
            
            temp_areab = temp_area
            chru = np.max(np.unique(temp_icropb))+1
            if not np.size(min_area) > 0:
                for ii in range(0,len(min_area)):
                    temp_areab = temp_areab + labeled_area[min_area[sidsL[ii]]]
                    temp_icropb[np.where(Ltemp.flatten() == min_area[sidsL[ii]])] = chru
                    if temp_areab/np.sum(sort_counts[:,2]) >= self.min_farmland_per:
                        break
                    else:
                        chru = chru + 1
            
        return temp_icrop, temp_icropb

#%%
    def Create_Operation_timeseries(self):
        # Getting unique crops
        [ucrops, ucounts] = np.unique(self.CDL.reshape((-1,1)), axis=0, return_counts = True)
        ucounts = np.asarray(ucounts,dtype=float)
        
        ucounts = ucounts[np.where(ucrops[:,0] != 0)]
        ucrops = ucrops[np.where(ucrops[:,0] != 0)]
        
        ucounts = ucounts[np.where(~np.isnan(ucrops[:,0]))]
        ucrops = ucrops[np.where(~np.isnan(ucrops[:,0]))]
        

        # Eliminating blobs of major crops with area < min_hru_area and re-create time series matrix of land unit/management areas
        print 'Eliminating blobs of major crops with area < min_hru_area'
        LST_LlN = np.zeros(self.CDL.shape)
        for i in range(0, self.CDL.shape[1]):
            count_crop = 0
            LST_Ll = dict()
            LST_area = []
            temp_CDL = self.CDL[:,i].reshape(self.wid_array.shape)
            #plt.matshow(np.flip(temp_CDL, 0))
            #plt.show()
            
            for crop in ucrops:
                labeled_array, num_features = ndimage.measurements.label(np.asarray(temp_CDL == crop[0], dtype=np.int))
                labeled_area = ndimage.measurements.sum(np.asarray(temp_CDL == crop[0], dtype=np.int),labeled_array,range(1,num_features+1))
                blobs_min_area = np.where(labeled_area >= self.min_hru_area_a)[0]
                
                if np.size(blobs_min_area) > 0:
                    for j in blobs_min_area:
                        LST_area.append(labeled_area[j])
                        LST_Ll[count_crop] = np.where(labeled_array.flatten() == j+1)
                        count_crop += 1
                        
            # Converting land use data from crop ID to unique blob IDs (i.e., HRUs)
            LST_area = np.asarray(LST_area)        
            sortid_areas = LST_area.argsort()[::-1][:len(LST_area)]
            jj = 1
            for sids in sortid_areas:
                LST_LlN[LST_Ll[sids],i] = jj
                jj = jj + 1
                
        
        # Filling "holes" in HRUs (blobs) becuse of removed noise (major crop with area < min_hru_area)
        #print 'Filling "holes" in HRUs (blobs) becuse of removed noise'
        LST_LlNb = np.zeros(self.CDL.shape)
        for i in range(0,self.CDL.shape[1]):
            print 'Filling "holes" in HRUs (blobs) becuse of removed noise. For CDL layer: ' + str(i)
            [ucrops, ucounts] = np.unique(LST_LlN[:,i], axis=0, return_counts = True)
            ucounts = np.asarray(ucounts,dtype=float)
            
            ucounts = ucounts[np.where(ucrops != 0)]
            ucrops = ucrops[np.where(ucrops != 0)]
            ucounts = ucounts[np.where(~np.isnan(ucrops))]
            ucrops = ucrops[np.where(~np.isnan(ucrops))]
            
            for uids in ucrops:
                temp_LST_LNl = np.asarray(LST_LlN[:,i] == uids, dtype=np.int64)
                temp_LST_LNl = np.asarray(ndimage.morphology.binary_fill_holes(temp_LST_LNl.reshape(self.wid_array.shape)), dtype=np.int64)
                LST_LlNb[temp_LST_LNl.flatten() == 1,i] = uids
        
        
        # Removing time series of crops (list of pixels) rotations that have not been used in the last 5 years
        print 'Removing time series of crops (list of pixels) rotations that have not been used in the last 5 years'
        LST_LlNc = LST_LlNb
        # Getting unique crops
        [ucrop_row, ucounts, icrops, junk] = np.unique(LST_LlNb, axis=0, return_counts = True, return_index = True, return_inverse = True)
        ucounts = np.asarray(ucounts,dtype=float)
        id_zeros = np.where(np.sum(np.asarray(ucrop_row[:,5:9+1] == 0, dtype=np.int), axis=1) == 5)[0]    
        for idz in id_zeros:
            LST_LlNc[icrops == idz,:] = 0
            
        id_zeros = np.intersect1d(np.where(np.sum(ucrop_row[:,5:9+1] == 0, axis=1) <= 1)[0], np.where(np.sum(ucrop_row[:,0:4+1] == 0, axis=1) == 5)[0])
        for idz in id_zeros:
            LST_LlNc[icrops == idz,:] = 0
            
        # Eliminating blobs of major crop with area < min_hru_area (Second pass because of all the prior modifications)
        LST_LlNd = LST_LlNc
        [ucrop_row, ucounts, icrops, junk] = np.unique(LST_LlNc, axis=0, return_counts = True, return_index = True, return_inverse = True)
        print 'Eliminating blobs of major crops with area < min_hru_area (Second pass): ' + str(len(ucounts))
        
        temp_per = 0
        temp_CDL = icrops.reshape(self.wid_array.shape)
#        plt.matshow(temp_CDL)
#        plt.show()
        
        for i in range(1,len(ucounts)):
            labeled_array, num_features = ndimage.measurements.label(np.asarray(temp_CDL == i, dtype=np.int))
            labeled_area = ndimage.measurements.sum(np.asarray(temp_CDL == i, dtype=np.int), labeled_array, range(1,num_features+1))
            blobs_min_area = np.where(labeled_area <= self.min_hru_area_b)[0]
            
            #print 'Num. of Blobs: ' + str(np.size(blobs_min_area))
            if np.size(blobs_min_area) > 0:
                    for j in blobs_min_area:
                        icrops[labeled_array.flatten() == j+1] = 0
                        LST_LlNd[labeled_array.flatten() == j+1,:] = 0
            
            if round((float(i)/len(ucounts))*100) > temp_per:
                print 'Progress: ' + str(temp_per) + '%'
                temp_per = temp_per + 10
                
        #[ucrop_row, ucounts, icrops, junk] = np.unique(LST_LlNd, axis=0, return_counts = True, return_index = True, return_inverse = True) 
        sio.savemat('PythonCDL.mat', {'LST_LlNp':LST_LlN,'LST_LlNpb':LST_LlNb,'LST_LlNpc':LST_LlNc,'LST_LlNpd':LST_LlNd})
        
        self.LST_Ll = LST_Ll
        self.LST_LlNb = LST_LlNb
        self.LST_LlNc = LST_LlNc
        self.LST_LlNd = LST_LlNd

#%% 
    def CDL_NLCDtoSWATdict(self):
        
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + self.db_path + ';'
            )
        cnxn = pyodbc.connect(conn_str)
        crsr = cnxn.cursor()
        
        crsr.execute('select * from crop')
        cropdict = dict()
        for row in crsr.fetchall():
            cropdict[str(row[2])] = row[1]
            
            
        conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + self.db_path + ';'
        )
        cnxn = pyodbc.connect(conn_str)
        crsr = cnxn.cursor()
    
        crsr.execute('select * from nlcd2001_lu')
    
        nlcd_cropdict = dict()
        for row in crsr.fetchall():
            nlcd_cropdict[row[1]] = dict()
            nlcd_cropdict[row[1]]['Name'] = str(row[2])
            if str(row[2]) in cropdict.keys():
                nlcd_cropdict[row[1]]['value'] = cropdict[str(row[2])]
                
        conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + self.db_path + ';'
        )
        cnxn = pyodbc.connect(conn_str)
        crsr = cnxn.cursor()
    
        crsr.execute('select * from CDL_lu')
    
        cdl_cropdict = dict()
        for row in crsr.fetchall():
            if str(row[2]) in cropdict.keys():
                cdl_cropdict[row[1]] = cropdict[str(row[2])]
    
        self.nlcd_cropdict = nlcd_cropdict
        self.cdl_cropdict = cdl_cropdict

    def MergeNLCD_HRU(self):
        #print(self.nlcd_file)
        
        self.CDL_NLCDtoSWATdict()
        nlcd_raster_ds = gdal.Open(self.nlcd_file, gdal.GA_ReadOnly)
        nlcd_raster_NoData = nlcd_raster_ds.GetRasterBand(1).GetNoDataValue()
        
        nlcd_newRaster_name = 'InterACTWEL_landuse.tif'

        nlcd_raster = np.asarray(nlcd_raster_ds.GetRasterBand(1).ReadAsArray(),dtype=float)
        if nlcd_raster_NoData != None:
            nlcd_raster[nlcd_raster == nlcd_raster_NoData] = np.float('nan')
        nlcd_raster_NoData = -999.0
        #else:
        #    soil_raster_NoData = int(soil_raster_NoData)
        
        print ('Merging CDL & NLCD and HRU raster')
        nlcd_raster[nlcd_raster == 0.0] = np.float('nan')
        nlcd_raster[nlcd_raster > 95.0] = np.float('nan')
        
        cdl_raster_ds = gdal.Open(self.cdl_file, gdal.GA_ReadOnly)
        cdl_raster_NoData = cdl_raster_ds.GetRasterBand(1).GetNoDataValue()
        cdl_raster = np.asarray(cdl_raster_ds.GetRasterBand(1).ReadAsArray(),dtype=float)
        if cdl_raster_NoData != None:
            cdl_raster[cdl_raster == cdl_raster_NoData] = np.float('nan')
        cdl_raster[cdl_raster == 0.0] = np.float('nan')
        
        cdl_raster_org = cdl_raster
        # Convert from CDL to SWAT IDs
        ucdl= np.unique(cdl_raster.flatten())
        ucdl = ucdl[np.where(np.isnan(ucdl) == False)]
        for ud in ucdl:
            if ud in self.cdl_cropdict.keys():
                cdl_raster[np.where(cdl_raster_org == ud)] = float(self.cdl_cropdict[ud]) 
        
        # Capture NLCD pixels that are agriculture and could have CDL values
        cdl_nlcd_bin = np.zeros(nlcd_raster.shape, dtype=np.float)
        for unlcd in self.nlcd_to_cdl_classes:
            cdl_nlcd_bin[np.where(nlcd_raster == unlcd)] = 1.0
        
        # Convert NLCD to SWAT IDS and retain the classes that didn't have a crop ID (e.g., NLCD = 21)
        unlcd = np.unique(nlcd_raster.flatten())
        unlcd = unlcd[np.where(np.isnan(unlcd) == False)]
        #print unlcd
        nlcd_raster_org = nlcd_raster
        missing_nlcd_classes = []
        for un in unlcd:
            if un in self.nlcd_cropdict.keys() and 'value' in self.nlcd_cropdict[un].keys():
                nlcd_raster[np.where(nlcd_raster_org == un)] = float(self.nlcd_cropdict[un]['value']) 
            else:
                print un
                missing_nlcd_classes.append(un)

        
        # Add SWAT-CDL IDS to NLCD agriculture pixels
        nlcd_raster[np.where(cdl_nlcd_bin == 1.0)] = cdl_raster[np.where(cdl_nlcd_bin == 1.0)]

        #nlcd_raster_flat = nlcd_raster.flatten()
        
        hru_raster = gdal.Open(self.landuse_file, gdal.GA_ReadOnly)
        hru_raster_NoData = hru_raster.GetRasterBand(1).GetNoDataValue()
        hru_raster = np.asarray(hru_raster.GetRasterBand(1).ReadAsArray(),dtype=float)
        hru_raster[hru_raster == hru_raster_NoData] = np.float('nan')
        hru_raster[hru_raster < 0] = np.float('nan')
        hru_raster[hru_raster == 0.0] = np.float('nan')
        
        uhrus = np.unique(hru_raster.flatten())
        uhrus = uhrus[np.where(np.isnan(uhrus)==False)]
        #new_soil = np.ones(soil_raster.shape, dtype=np.int64)*-999
        new_hrus = np.zeros(hru_raster.shape, dtype=np.float)
        hru_counter = 1
        for hru_id in uhrus:
            new_hrus[hru_raster == hru_id] = hru_counter
            hru_counter = hru_counter + 1
        
        new_hrus[new_hrus == 0.0] = np.float('nan')
        
        #hru_raster_flat = hru_raster.flatten()        
        nlcd_raster[np.where(np.isnan(new_hrus)==False)] = new_hrus[np.where(np.isnan(new_hrus)==False)] + self.landuseID_max
        
        nlcd_raster_maxval = np.nanmax(nlcd_raster.flatten()) + 1
        
        self.missing_nlcd_classes = dict()
        for unm in missing_nlcd_classes:
            nlcd_raster[np.where(nlcd_raster == unm)] = nlcd_raster_maxval
            self.missing_nlcd_classes[nlcd_raster_maxval] = dict()
            self.missing_nlcd_classes[nlcd_raster_maxval]['Name'] = self.nlcd_cropdict[unm]['Name']
            self.missing_nlcd_classes[nlcd_raster_maxval]['value'] = unm
            nlcd_raster_maxval = nlcd_raster_maxval + 1
        
        nlcd_raster[np.where(np.isnan(nlcd_raster)==True)] = nlcd_raster_NoData
        nlcd_raster[np.where(nlcd_raster < 0)] = nlcd_raster_NoData
        
        nlcd_newRaster_name = self.swat_path + '/' + nlcd_newRaster_name
        print ('Writing new HRU raster')
        QSWAT_utils.Save_NewRaster(nlcd_raster, nlcd_raster_ds, nlcd_raster, nlcd_newRaster_name, nlcd_raster_NoData)
        self.landuse_file = nlcd_newRaster_name     

#%%
    def ReadCDL(self):
        # Read and create dictionary of DBF tables. Helps to validate the mapping of raster value to crop type.
        fnames = os.listdir(self.cdl_path)
        self.fnames = fnames
        findex = []
        c = 0
#        DBF_dict = dict()
        
        for fname in fnames:
            if '.tif.' not in fname and '.tfw' not in fname:
                findex.append((c,int(fname[4:8])))
#            elif 'dbf' in fname:
#                db = dbf.Dbf(self.rootpath_zip + '\\' + fname)
#                temp = dict()
#                for rec in db:
#                    temp[rec['VALUE']] = rec['CLASS_NAME']
#                DBF_dict[int(fname[4:8])] = temp
            c += 1    
        
        # Create a matrix of crop rotation time series CDL data (each row is a pixel, each column is a year)        
        CDL_org = np.zeros((len(self.bnd_array.flatten()),10))
        
        findex = np.asarray(findex)
        self.findex = findex
        years = range(min(findex[:,1]),max(findex[:,1])+1)
        self.cdl_years = years
        c=0
        for year in years: 
            print 'Reading: ' + fnames[findex[findex[:,1]==year,0][0]]
            if year == years[-1]:
                self.cdl_file = self.cdl_path + '\\' + fnames[findex[findex[:,1]==year,0][0]]
            new_raster, new_raster_NoData = QSWAT_utils.Read_Raster(self.cdl_path + '\\' + fnames[findex[findex[:,1]==year,0][0]])
            new_raster = np.flip(new_raster,0)
            new_raster = np.asarray(new_raster,dtype=float)
            new_raster[new_raster == new_raster_NoData] = np.float('nan')
            new_raster[new_raster == 0.0] = np.float('nan')

            
            new_raster = new_raster[self.bdims[0]:self.bdims[1]+1,self.bdims[2]:self.bdims[3]+1]
            new_raster[self.bnd_array == 0] = np.float('nan')
            
            #apply the mask to limit the collection of data to only the specify region by the mask's raster  
            CDL_org[:,c] = new_raster.flatten()*self.bnd_array.flatten()
            c += 1
            
        #return CDL_org, DBF_dict
        return CDL_org


#%%    
    def Watershed_CDL(self):
        # Create a matrix of crop rotation time series CDL data (each row is a pixel, each column is a year)        
        CDL = np.zeros((len(self.wid_array.flatten()),10))
        c=0
        for year in self.cdl_years: 
            print 'Extracting CDL for watershed ' + str(self.temp_wid) + ' :' + self.fnames[self.findex[self.findex[:,1]==year,0][0]]
            new_raster = self.CDL_org[:,c].reshape(self.bnd_array.shape)
            
            #temp_CDL = self.CDL_org[:,c].reshape(self.bnd_array.shape)
            #temp_CDL[self.watersheds==self.temp_wid] = 999
            #plt.matshow(temp_CDL)
            #plt.show()
            
            new_raster = new_raster[self.wdims[0]:self.wdims[1]+1,self.wdims[2]:self.wdims[3]+1]
            
            #apply the mask to limit the collection of data to only the specify region by the mask's raster  
                        
            #plt.matshow(new_raster)
            #plt.show()
                        
            #plt.matshow(self.wid_array)
            #plt.show()
            CDL[:,c] = new_raster.flatten()*self.wid_array.flatten()
            c += 1
            
        return CDL

    
    #%% Read System boundary mask (raster: 0-no data, 1-area of study)
    def ReadInputData(self):  

        (base,suffix) = os.path.splitext(self.watershed_lyr.replace('\\','/'))
        if suffix == '.shp':
            #processing.runalg('qgis:dissolve', self.watershed_lyr.replace('\\','/'), True, '', base + '_boundary.shp')
            # ogr2ogr output_dissolved.shp input.shp -dialect sqlite -sql "SELECT ST_Union(geometry) AS geometry FROM input"
            fnames = os.listdir(self.cdl_path)
            findex = []
            c = 0
            for fname in fnames:
                if '.tif.' not in fname and '.tfw' not in fname and c == 0:
                    findex = fname
                c = c + 1
        QSWAT_preprocess.CreateSubbasinTiff(base + '_boundary.shp',base + '.tif',self.cdl_path + '/' + fname)
            
        print self.boundary_lyr.replace('\\','/')
        boundary = gdal.Open(self.boundary_lyr.replace('\\','/'), gdal.GA_ReadOnly)
        boundary_NoData = boundary.GetRasterBand(1).GetNoDataValue()
        boundary = boundary.GetRasterBand(1).ReadAsArray()
        
        top_row, last_row = self.Raster_row_boundaries(boundary)   
        left_col, right_col = self.Raster_col_boundaries(boundary)
               
        self.bdims = [top_row,last_row,left_col,right_col]
        self.bnd_array = boundary[top_row:last_row+1,left_col:right_col+1]
        #bnd_array = boundary.flatten()     
        
        #watersheds = rasterio.open(self.rootpath + '\\' + self.watershed_lyr)
        #watersheds = np.asarray(watersheds.read(1), dtype = np.int64)
        #watersheds[watersheds == 127] = -999 # Needed because of ArcGis data convertion steps
        #watersheds = gdal.Open(self.rootpath + '\\' + self.watershed_lyr)
        
        watersheds = gdal.Open(self.watershed_raster.replace('\\','/'))
        watersheds_NoData = watersheds.GetRasterBand(1).GetNoDataValue()
        watersheds = np.asarray(watersheds.GetRasterBand(1).ReadAsArray(), dtype = np.int64)
        watersheds[watersheds == watersheds_NoData] = -999 # Needed because of ArcGis data convertion steps
        
        watersheds = watersheds[top_row:last_row+1,left_col:right_col+1] + 1 #added +1 to avoid confusion if watershed ID = 0
        watersheds[watersheds < 0] = 0
        watersheds[self.bnd_array == boundary_NoData] = 0
        self.watersheds = watersheds

#        #watersheds = watersheds.flatten()
#        # Find CDL raster files (.tif) in given directory & read .ddf (feature properties) table
#        rootpath_zip = 'Z:\Projects\INFEWS\Modeling\FEW_Data\Crops\USDA_CDL\Region_CDL\Projected';
#        #try:
#        #    print 'Unziping data to: ' + str(pathuzip)
#        #except:
#        #    print 'Unziping data to: ' + str(path)
#        #    pathunzip = path
#        #    

    def Read_Watershed_Raster(self):
        
        boundary, boundary_NoData = QSWAT_utils.Read_Raster(self.boundary_raster)
        top_row, last_row = QSWAT_utils.Raster_row_boundaries(boundary)   
        left_col, right_col = QSWAT_utils.Raster_col_boundaries(boundary)
               
        self.bdims = [top_row, last_row, left_col, right_col]
        self.bnd_array = boundary[top_row:last_row+1, left_col:right_col+1]
        
        #plt.matshow(self.bnd_array)
        #plt.show()
        
        watersheds, watersheds_NoData = QSWAT_utils.Read_Raster(self.watershed_raster)
        watersheds = np.asarray(watersheds, dtype = np.int64)
        watersheds[watersheds == watersheds_NoData] = -999 # Needed because of different GIS tools data convertion steps
        
        watersheds[watersheds <= 0] = -999
        
        watersheds = watersheds[top_row:last_row+1,left_col:right_col+1] + 1 #added +1 to avoid confusion if watershed ID = 0
        watersheds[watersheds < 0] = 0
        watersheds[self.bnd_array == boundary_NoData] = 0
        
        self.watersheds = watersheds
        #plt.matshow(self.watersheds)
        #plt.show()

#%%          
    def SimplifySoils(self):
        
        soil_raster_ds = gdal.Open(self.soil_file, gdal.GA_ReadOnly)
        soil_raster_NoData = soil_raster_ds.GetRasterBand(1).GetNoDataValue()
        #print str(self.soil_file)
        
        soil_newRaster_name = 'InterACTWEL_soils.tif'
        if sys.platform.startswith('win'):
            slash_index = [i for i in range(len(self.soil_file)) if self.soil_file.startswith('/', i)]
        else:
            slash_index = [i for i in range(len(self.soil_file)) if self.soil_file.startswith('\\', i)]
        
        soil_raster = np.asarray(soil_raster_ds.GetRasterBand(1).ReadAsArray(),dtype=float)
        if soil_raster_NoData != None:
            soil_raster[soil_raster == soil_raster_NoData] = np.float('nan')
        soil_raster_NoData = -999.0
        #else:
        #    soil_raster_NoData = int(soil_raster_NoData)
        print ('Reading old soil raster')
        soil_raster[soil_raster == 0.0] = np.float('nan')
        #soil_raster = soil_raster[self.bdims[0]:self.bdims[1]+1,self.bdims[2]:self.bdims[3]+1]
        #soil_raster[self.bnd_array == 0] = np.float('nan')
        soil_raster_flat = soil_raster.flatten()
        
        hru_raster = gdal.Open(self.landuse_file, gdal.GA_ReadOnly)
        hru_raster_NoData = hru_raster.GetRasterBand(1).GetNoDataValue()
        hru_raster = np.asarray(hru_raster.GetRasterBand(1).ReadAsArray(),dtype=float)
        hru_raster[hru_raster == hru_raster_NoData] = np.float('nan')
        hru_raster[hru_raster == 0.0] = np.float('nan')
        #hru_raster = hru_raster[self.bdims[0]:self.bdims[1]+1,self.bdims[2]:self.bdims[3]+1]
        #hru_raster[self.bnd_array == 0] = np.float('nan')
        hru_raster_flat = hru_raster.flatten()
        
        uhrus = np.unique(hru_raster.flatten())
        uhrus = uhrus[np.where(uhrus > self.landuseID_max)]
        #new_soil = np.ones(soil_raster.shape, dtype=np.int64)*-999
        new_soil = np.zeros(soil_raster.shape, dtype=np.int64)
        new_soil[np.where(np.isnan(soil_raster)==False)] = soil_raster[np.where(np.isnan(soil_raster)==False)]
        for hru_id in uhrus:
            temp_soils = stats.mode(soil_raster_flat[np.where(hru_raster_flat == hru_id)], axis=None, nan_policy = 'omit')
            #temp_soils = stats.mode(soil_raster_flat[np.where(hru_raster_flat == hru_id)], axis=None)
            #mode_temp_soils = temp_soils[0]
            new_soil[hru_raster == hru_id] = temp_soils[0]
        
        new_soil[new_soil == 0.0] = soil_raster_NoData
        new_soil[np.where(np.isnan(hru_raster)==True)] = soil_raster_NoData
        
        soil_newRaster_name = self.soil_file[0:slash_index[-1]+1] + soil_newRaster_name
        print ('Writing new simplified soil raster')
        QSWAT_utils.Save_NewRaster(new_soil, soil_raster_ds, soil_raster, soil_newRaster_name, soil_raster_NoData)
        self.soil_file = soil_newRaster_name
        
    def SimplifySlopes(self):
    
        slope_raster_ds = gdal.Open(self.slope_file, gdal.GA_ReadOnly)
        slope_raster_NoData = slope_raster_ds.GetRasterBand(1).GetNoDataValue()
        #print str(self.slope_file)
        
        slope_newRaster_name = 'InterACTWEL_slopes.tif'
        if sys.platform.startswith('win'):
            slash_index = [i for i in range(len(self.slope_file)) if self.slope_file.startswith('/', i)]
        else:
            slash_index = [i for i in range(len(self.slope_file)) if self.slope_file.startswith('\\', i)]

        slope_raster = np.asarray(slope_raster_ds.GetRasterBand(1).ReadAsArray(),dtype=float)
        if slope_raster_NoData != None:
            slope_raster[slope_raster == slope_raster_NoData] = np.float('nan')
        slope_raster_NoData = -999.0

#        slope_raster[slope_raster == 0.0] = np.float('nan')
        slope_raster_flat = slope_raster.flatten()
        
        hru_raster = gdal.Open(self.landuse_file, gdal.GA_ReadOnly)
        hru_raster_NoData = hru_raster.GetRasterBand(1).GetNoDataValue()
        hru_raster = np.asarray(hru_raster.GetRasterBand(1).ReadAsArray(),dtype=float)
        hru_raster[hru_raster == hru_raster_NoData] = np.float('nan')
        hru_raster[hru_raster == 0.0] = np.float('nan')
        hru_raster_flat = hru_raster.flatten()
        
        uhrus = np.unique(hru_raster.flatten())
        uhrus = uhrus[np.where(uhrus > self.landuseID_max)]
        
        new_slope = np.ones(slope_raster.shape, dtype=np.float)*slope_raster_NoData
        #new_slope[new_slope == slope_raster_NoData] = np.float('nan')
        new_slope[np.where(np.isnan(slope_raster)==False)] = slope_raster[np.where(np.isnan(slope_raster)==False)]
        
        for hru_id in uhrus:
            #print slope_raster_flat[np.where(hru_raster_flat == hru_id)]
            temp_slope = np.nanmean(slope_raster_flat[np.where(hru_raster_flat == hru_id)])
            #temp_slope = [np.mean([l for l in slope_raster_flat[np.where(hru_raster_flat == hru_id)] if not np.isnan(l)]) ]
            #mode_temp_soils = temp_soils[0]
            new_slope[hru_raster == hru_id] = temp_slope
            
        new_slope[np.where(np.isnan(new_slope)==True)] = slope_raster_NoData
        new_slope[np.where(np.isnan(hru_raster)==True)] = slope_raster_NoData
        
        slope_newRaster_name = self.slope_file[0:slash_index[-1]+1] + slope_newRaster_name
        print ('Writing new simplified slope raster')
        QSWAT_utils.Save_NewRaster(new_slope, slope_raster_ds, slope_raster, slope_newRaster_name, slope_raster_NoData)
        self.slope_file = slope_newRaster_name

#%%
    def AlphaNumericDic(self,text):
        nums = [str(chr(122-int(x))) for x in text.lower()]
        return "".join(nums)

    def CreateLU_LookupTable(self):
        hru_raster = gdal.Open(self.landuse_file, gdal.GA_ReadOnly)
        hru_raster_NoData = hru_raster.GetRasterBand(1).GetNoDataValue()
        hru_raster = np.asarray(hru_raster.GetRasterBand(1).ReadAsArray(),dtype=float)
        hru_raster[hru_raster == hru_raster_NoData] = np.float('nan')
        hru_raster[hru_raster == 0.0] = np.float('nan')
        hru_raster_flat = hru_raster.flatten()

        uhrus = np.unique(hru_raster.flatten())
        uhrus = uhrus[np.where(uhrus > self.landuseID_max)]
        
        max_num2str = len(str(int(uhrus.max())))
        lu_names = dict()
        for hruid in uhrus:
            if len(str(int(hruid))) < max_num2str:
                diff_num2str = len(str(int(hruid))) < max_num2str
                text_num = '0'*diff_num2str + str(int(hruid))
            else:
                text_num = str(int(hruid))
            
            lu_names[hruid] = self.AlphaNumericDic(text_num)
            
        conn_str = (
                r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                r'DBQ=' + self.db_path + ';'
                )
        cnxn = pyodbc.connect(conn_str)
        crsr = cnxn.cursor()
            
        crsr.execute('select * from crop where ICNUM = 1')
    
        for row in crsr.fetchall():
            agrl_row = row
            
        crsr.execute('SELECT COUNT(OBJECTID) FROM crop')
        for row in crsr.fetchall():
            num_records = int(row[0])
        
        counter = num_records + 1
        for hrus in lu_names.keys():
            mod_row = agrl_row
            mod_row[0] = counter
            mod_row[1] = counter
            #mod_row[1] = str(hrus)
            mod_row[2] = lu_names[hrus]
            for ind in range(len(mod_row)):
                mod_row[ind] = str(mod_row[ind])
            sql_text = '''INSERT INTO crop VALUES ''' + str(mod_row)

            crsr.execute(sql_text)
            counter = counter + 1
            
        cnxn.commit()
        
        crsr.execute('select ICNUM, CPNM from crop')
        # Create CSV Lookup Table
        csv_file = 'InterACTWEL_Landuses.csv'
        with open(self.swat_path + '/' + csv_file, mode='wb') as outputcsv:
            outputcsv_writer = csv.writer(outputcsv, delimiter = ',', quotechar = '"', quoting=csv.QUOTE_MINIMAL)
            outputcsv_writer.writerow(['LANDUSE_ID','SWAT_CODE'])
            for row in crsr.fetchall():
                outputcsv_writer.writerow([row[0],row[1]])
        outputcsv.close()   
        return

#%%        
#    def CheckNoDataHRUs(self):
#        print('Check NoData of Landuse')
#        hru_raster_ds = gdal.Open(self.landuse_file, gdal.GA_ReadOnly)
#        hru_raster_NoData = hru_raster_ds.GetRasterBand(1).GetNoDataValue()
#        if hru_raster_NoData != 0:
#            hru_raster = np.asarray(hru_raster_ds.GetRasterBand(1).ReadAsArray(),dtype=float)
#            hru_raster[hru_raster == hru_raster_NoData] = 0.0
#            hru_raster[hru_raster < 0.0] = 0.0
#            print('re-writing Landuse Raster')
#            self.Save_NewRaster(hru_raster, hru_raster_ds, hru_raster, self.landuse_file, 0)
#        return
               
#%% Find paths to all files in project folder

    def ReadInputFile(self,file_path):
        with open(file_path,'rb') as search:
            for line in search:
                if 'swat_path' in line:
                    linesplit = re.split('\s',line)
                    swat_path = linesplit[2].replace('\\','/')
                    
                elif 'nlcdFile' in line:
                    linesplit = re.split('\s',line)
                    nlcdFile = linesplit[2].replace('\\','/')
                    
                elif 'subbasinsFile' in line:
                    linesplit = re.split('\s',line)
                    subbasinsFile = linesplit[2].replace('\\','/')
                    
                elif 'landuseFile' in line:
                    linesplit = re.split('\s',line)
                    landuseFile = linesplit[2].replace('\\','/')
                    
                elif 'soilFile' in line:
                    linesplit = re.split('\s',line)
                    soilFile = linesplit[2].replace('\\','/')
                    
                elif 'cdlFile' in line:
                    linesplit = re.split('\s',line)
                    cdlFile = linesplit[2].replace('\\','/')
                    
                elif 'cdlPath' in line:
                    linesplit = re.split('\s',line)
                    cdlFile = linesplit[2].replace('\\','/')
                    
                elif 'cdlFile' in line:
                    linesplit = re.split('\s',line)
                    cdlFile = linesplit[2].replace('\\','/')
                    
                    
            if sys.platform.startswith('win'):
                self.swat_path = swat_path.replace('\\','/')
                self.soil_file = soilFile.replace('\\','/')
                self.landuse_file = landuseFile.replace('\\','/')
                self.nlcd_file = nlcdFile.replace('\\','/')
                self.watershed_path = subbasinsFile.replace('\\','/')
                self.cdl_file = cdlFile.replace('\\','/')
                self.cdl_path = ''
                self.boundary_lyr = ''
            
            else:
                self.swat_path = swat_path
                self.soil_file = soilFile
                self.landuse_file = landuseFile
                self.nlcd_file = nlcdFile
                self.watershed_path = subbasinsFile
                self.cdl_file = cdlFile
                self.cdl_path = ''
                self.boundary_lyr = ''