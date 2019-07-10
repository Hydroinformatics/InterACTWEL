#!/export/interactwel/bin/python
#import rasterio, os
#from matplotlib import pyplot as plt
import numpy as np
#from dbfpy import dbf
from scipy import stats, ndimage
import scipy.io as sio
import os, sys, re, argparse, pyodbc, csv, QSWAT_preprocess
from osgeo import gdal, osr, ogr

##%%
#def UnzipData(path,pathuzip):
#    #os.chdir("..")
#    folderpath = pathuzip + '/Default'
#    if os.path.isdir(folderpath):
#        shutil.rmtree(folderpath)
#    
#    print folderpath
#    os.makedirs(folderpath)
#    print path
#    with zipfile.ZipFile(path, "r") as z:
#        z.extractall(folderpath)
#    
#    os.chdir(pathuzip +'/Default/TxtInOut/')
#    #exitflag = subprocess.check_call(['swatmodel_64rel.exe'])
#    #exitflag = subprocess.check_call(['/export/swat-test/bin/swat2012Rev664Rel'])
#    exitflag = subprocess.check_call([swat_model])
#    print exitflag
#
#
#
##%% Calculate the total area for each land cover ID for all years in the CDL time series matrix
#def CropAreas(CDL):
#    Crop_Areas = dict()
#    for i in range(0,len(CDL[0,:])):
#        temp_dict = dict()
#        [unique_crops, ucounts] = np.unique(CDL[:,i], axis=0, return_counts = True)
#        temp_dict['CROP_KEYS'] = unique_crops
#        temp_dict['CROP_COUNTS'] = ucounts
#        temp_dict['TOTAL_AREA'] = sum(CDL[:,i] > 0)
#        Crop_Areas[years[i]] = temp_dict
#        
#    return Crop_Areas
#
##%% Plot change in area of crops
#def Plot_CropChange(crops,dbf,non_crops):
#    years = crops.keys()
#    years.sort()
#    crop_ids_years = []
#    for year in years:
#        for i in dbf[year].keys():
#            temp_id = np.where(crops[year]['CROP_KEYS'] == i)[0]
#            if temp_id.size > 0 and crops[year]['CROP_KEYS'][temp_id] not in crop_ids_years:
#                crop_ids_years.append(i)
#                
#    crop_ids_years = np.unique(crop_ids_years)
#    
#    cplot = 1
#    Crop_matrix = np.zeros((len(crop_ids_years),len(years)))
#    ccol = 0
#    for year in years:
#        temp_names = []
#        temp_values = []
#        crow = 0
#        for i in crop_ids_years:
#            if i not in non_crops:
#                temp_id = np.where(crops[year]['CROP_KEYS'] == i)[0]
#                temp_names.append(dbf[year][i]) 
#                if temp_id.size > 0:
#                    #print year, i, dbf[year][crops[year]['CROP_KEYS'][temp_id[0]]]
#                    temp_values.append(crops[year]['CROP_COUNTS'][temp_id[0]])
#                    Crop_matrix[crow,ccol] = crops[year]['CROP_COUNTS'][temp_id[0]]
#                else:   
#                    temp_values.append(0)
#                    Crop_matrix[crow,ccol] = 0
#                crow += 1
#        ccol += 1
#
#        axs = plt.subplot(5,2,cplot)
#        axs.bar(temp_names, temp_values)
#        axs.grid(True)
#        plt.title('Year: ' + str(year))
#        cplot += 2
#        
#        if year != 2017 and year != 2012:
#            plt.setp(axs.get_xticklabels(), visible=False)
#        else:
#            plt.setp(axs.get_xticklabels(), visible=True, rotation=90)
#            cplot = 2
#        
#    plt.show()
#    #return crop_matrix, crop_ids_years
#    return
#
##%% Check that all crop_ids and keys are constant throughout the years
#def CropID_Check(DBF_dict):
#    years = DBF_dict.keys()
#    years.sort()
#    per_similarity_dbf = np.zeros((len(years),len(years)))
#    for i in range(0,len(years)):
#        for j in range(0,len(years)):
#            if i != j:
#                per = 0
#                for crop_id in DBF_dict[years[i]].keys():
#                    print years[i], years[j]
#                    if DBF_dict[years[i]][crop_id] == DBF_dict[years[j]][crop_id]:
#                        per = per + 1
#                per_similarity_dbf[j,i] = per
#    return per_similarity_dbf
#
##%%
#    
#def ExtractCrop_Seq(CDL,dbf,ncrops,rot_years,seq_order):             
#Nrots = (len(CDL[1,:]) - rot_years) + 1
#temp_data = np.zeros((len(CDL[:,1])*Nrots,rot_years))
#row_count = 0
#for i in range(0,Nrots):
#   if seq_order:
#       # Reverse order
#       temp_data[row_count:(row_count+len(CDL[:,1])),:] = CDL[:,(Nrots-i-1):(len(CDL[1,:])-i)]
#   else:
#       # Chronological order
#       temp_data[row_count:(row_count+len(CDL[:,1])),:] = CDL[:,(Nrots-i-1):(len(CDL[1,:])-i)]
#   row_count = row_count + len(CDL[:,1])
#
#return temp_data
#    
##%%
#def parallel_coordinates(coordinates, values, labels):
#    """Plot 2d array `values` using K parallel coordinates.
#    
#    Arguments:
#
#        coordinates -- list or array of K elements containg coordinate
#            names,
#        values -- (K,N)-shaped array of N data points with K
#            coordinates, 
#        labels -- list or array of one string per data point
#            describing its class membership (category)
#    """
#
#    # SOLUTION
#    ax = plt.subplot(111)
#
#    # find names and number of different classes
#    ulabels = np.unique(labels)
#    n_labels = len(ulabels)
#    
#    # for each select distinct colors from Accent pallette
#    cmap = plt.get_cmap('hsv')
#    colors = cmap(np.arange(n_labels)*cmap.N/(n_labels+1))
#
#    # change the label strings to indices into class names array
#    class_id = np.searchsorted(ulabels, labels) 
#    lines = plt.plot(values[:,:], 'k')
#    [ l.set_color(colors[c]) for c,l in zip(class_id, lines) ]
#    
#
#    # add grid, configure labels and axes
#    ax.spines['top'].set_visible(False)
#    ax.spines['bottom'].set_position(('outward', 5))
#    ax.spines['bottom'].set_visible(False)
#    ax.yaxis.set_ticks_position('both')
#    ax.xaxis.set_ticks_position('none')
#    
#    plt.xticks(np.arange(len(coordinates)), coordinates)
#    plt.grid(axis='x', ls='-')
#
##    leg_handlers = [ lines[np.where(class_id==id)[0][0]] 
##                    for id in range(n_labels)]
##    ax.legend(leg_handlers, ulabels, frameon=False, loc='upper left',
##            ncol=len(labels),
##            bbox_to_anchor=(0, -0.03, 1, 0))

#%%
#def Mode_Filter(input):
#    temp_mode = stats.mode(input,axis=None,nan_policy='omit')
#    
#    return temp_mode[0]


class Create_InterACTWEL_HRUs:
    
    def __init__(self):
        #self.rootpath = 'Z:\Projects\INFEWS\Modeling\GIS_Data\FINAL_LAYERS'
        ## Find CDL raster files (.tif) in given directory & read .ddf (feature properties) table
        #self.rootpath_zip = 'Z:\Projects\INFEWS\Modeling\FEW_Data\Crops\USDA_CDL\Region_CDL\Projected'
        #self.boundary_lyr = 'System_boundary.tif'
        #self.watershed_lyr = 'Watersheds.tif'
        
        # Max. landused ID in SWAT crop table
        self.landuseID_max = 148
        #self.ReadInputData()
            
        # ID of watersheds to be used
        self.watershed_ids = range(0+1,24+1)
        
        # Max. number of HRUs
        self.max_hrus = 200
        
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
        
        

#%%
    def Create_HRUs(self):
        LSTtempb = self.LST_LlNd
        [ucrop_row, ucounts, icrops, junk] = np.unique(LSTtempb, axis=0, return_counts = True, return_index = True, return_inverse = True)
    
        # Eliminate row with only background values
        uia = np.unique(icrops)
        if np.sum(ucrop_row[0,:], axis=0) == 0:
            uia = uia[1:]
        
        # Find and save area/cells of blobs of unique crop rotations (HRUs)
        ccc = 0
        icrop_ind = np.zeros(icrops.shape)
        ucrop_count = np.empty((0,3))
        ucrop_count_cells = dict()
        
        for tuia in uia:
            Ltemp = np.asarray(icrops == tuia, dtype=np.int).reshape(self.wid_array.shape)
            labeled_array, num_features = ndimage.measurements.label(Ltemp)
            labeled_area = ndimage.measurements.sum(Ltemp,labeled_array,range(1,num_features+1))
            
            for ti in range(0,len(labeled_area)):
                ucrop_count = np.vstack((ucrop_count,[tuia,ccc,labeled_area[ti]]))
                
                icrop_ind[Ltemp.flatten() == ti+1] = ccc
                ucrop_count_cells[ccc] = np.where(Ltemp.flatten() == ti+1)
                ccc = ccc + 1
                
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
            
            print str(temp_area/np.sum(sort_counts[:,2]))
            
            ids_non_major = np.setdiff1d(range(0,len(sort_counts)), temp_sortid)
            similarity = np.zeros((len(ids_non_major),len(temp_sortid)))
            for ii in range(0,len(ids_non_major)):
                for jj in range(0,len(temp_sortid)):
                    #temp = np.zeros((0,ucrop_row.shape[1]))
                    temp = []
                    for jjj in range(0,len(ucrop_row[0,:])):
                        temp.append(np.asarray(ucrop_row[int(sort_counts[ids_non_major[ii],0]),jjj] == ucrop_row[int(sort_counts[temp_sortid[jj],0]),jjj], dtype=np.int))
                    similarity[ii,jj] = np.sum(temp)
            maxsim = similarity.argsort()[::-1][:len(temp)]
           
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
                        for ii in range(0,len(blobs)):
                            #blobs_id = np.vstack((blobs_id,np.where(blobs[ii] == sort_counts[:,1])[0]))
                            blobs_id.append(np.where(blobs[ii] == sort_counts[:,1])[0])
                            #maxsim_id = np.vstack((maxsim_id,np.where(blobs_id[ii] == maxsim[jj])[0]))
                            maxsim_id.append(np.where(blobs_id[ii] == maxsim[jj,:])[0])
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
            if not np.isempty(min_area):
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
        # Get unique crops
        [ucrops, ucounts] = np.unique(self.CDL.reshape((-1,1)), axis=0, return_counts = True)
        ucounts = np.asarray(ucounts,dtype=float)
        #ucrops = np.asarray(ucrops,dtype=int)
        
        ucounts = ucounts[np.where(ucrops[:,0] != 0)]
        ucrops = ucrops[np.where(ucrops[:,0] != 0)]
        ucounts = ucounts[np.where(~np.isnan(ucrops[:,0]))]
        ucrops = ucrops[np.where(~np.isnan(ucrops[:,0]))]
        
        # Eliminate blobs of major crop with area < min_hru_area and re-create time series matrix of land unit/management areas
        LST_LlN = np.zeros(self.CDL.shape)
        for i in range(0,self.CDL.shape[1]):
            count_crop = 0
            LST_Ll = dict()
            LST_area = []
            temp_CDL = self.CDL[:,i].reshape(self.wid_array.shape)
                    
            for crop in ucrops:
                labeled_array, num_features = ndimage.measurements.label(np.asarray(temp_CDL == crop[0], dtype=np.int))
                labeled_area = ndimage.measurements.sum(np.asarray(temp_CDL == crop[0], dtype=np.int),labeled_array,range(1,num_features+1))
                blobs_min_area = np.where(labeled_area >= self.min_hru_area_a)[0]
                
                if np.size(blobs_min_area) > 0:
                    #print str(crop[0]) + ',' + str(len(blobs_min_area))
                    for j in blobs_min_area:
                        LST_area.append(labeled_area[j])
                        LST_Ll[count_crop] = np.where(labeled_array.flatten() == j+1)
                        count_crop += 1
                        
            # Convert land use data from crop ID to unique blob IDs (i.e., HRUs)
            LST_area = np.asarray(LST_area)        
            sortid_areas = LST_area.argsort()[::-1][:len(LST_area)]
            jj = 1
            for sids in sortid_areas:
                LST_LlN[LST_Ll[sids],i] = jj
                jj = jj + 1
        
        # Fill "holes" in HRUs (blobs) becuse of removed noise (major crop with area < min_hru_area)
        LST_LlNb = np.zeros(self.CDL.shape)
        for i in range(0,self.CDL.shape[1]):
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
        
        # Remove time series of crops (list of pixels) rotations that have not been used in the last 5 years
        LST_LlNc = LST_LlNb
        # Get unique crops
        #[ucrop_row, ucounts, icrops] = np.unique(LST_LlNb, axis=0, return_counts = True, return_index = True)
        [ucrop_row, ucounts, icrops, junk] = np.unique(LST_LlNb, axis=0, return_counts = True, return_index = True, return_inverse = True)
        ucounts = np.asarray(ucounts,dtype=float)
        id_zeros = np.where(np.sum(np.asarray(ucrop_row[:,5:9+1] == 0, dtype=np.int), axis=1) == 5)[0]    
        for idz in id_zeros:
            LST_LlNc[icrops == idz,:] = 0
            
        id_zeros = np.intersect1d(np.where(np.sum(ucrop_row[:,5:9+1] == 0, axis=1) <= 1)[0], np.where(np.sum(ucrop_row[:,0:4+1] == 0, axis=1) == 5)[0])
        for idz in id_zeros:
            LST_LlNc[icrops == idz,:] = 0
            
        # Eliminate blobs of major crop with area < min_hru_area (Second pass because of all the prior modifications)
        LST_LlNd = LST_LlNc
        [ucrop_row, ucounts, icrops, junk] = np.unique(LST_LlNc, axis=0, return_counts = True, return_index = True, return_inverse = True)
        
        for i in range(1,len(ucounts)):
            temp_CDL = icrops.reshape(self.wid_array.shape)
            labeled_array, num_features = ndimage.measurements.label(np.asarray(temp_CDL == i, dtype=np.int))
            labeled_area = ndimage.measurements.sum(np.asarray(temp_CDL == i, dtype=np.int),labeled_array,range(1,num_features+1))
            blobs_min_area = np.where(labeled_area <= self.min_hru_area_b)[0]
            
            if np.size(blobs_min_area) > 0:
                    for j in blobs_min_area:
                        icrops[temp_CDL.flatten() == j] = 0
                        LST_LlNd[temp_CDL.flatten() == j,:] = 0
        
        #sio.savemat('PythonCDL.mat', {'LST_LlNp':LST_LlN,'LST_LlNpb':LST_LlNb,'LST_LlNpc':LST_LlNc,'LST_LlNpd':LST_LlNd})
        
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
        #print nlcd_raster_NoData
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
        self.Save_NewRaster(nlcd_raster, nlcd_raster_ds, nlcd_raster, nlcd_newRaster_name, nlcd_raster_NoData)
        self.landuse_file = nlcd_newRaster_name     

#%%
    def ReadCDL(self):
        # Read and create dictionary of DBF tables. Helps to validate the mapping of raster value to crop type.
        fnames = os.listdir(self.rootpath_zip)
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
            print fnames[findex[findex[:,1]==year,0][0]]
            #new_raster = rasterio.open(self.rootpath_zip + '\\' + fnames[findex[findex[:,1]==year,0][0]])
            #new_raster = new_raster.read(1)
            new_raster = gdal.Open(self.rootpath_zip + '\\' + fnames[findex[findex[:,1]==year,0][0]])
            new_raster_NoData = new_raster.GetRasterBand(1).GetNoDataValue()
            new_raster = np.asarray(new_raster.GetRasterBand(1).ReadAsArray(),dtype=float)
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
    def Raster_row_boundaries(self,raster):
        row_sum_index = np.where(np.sum(raster,axis=1) != 0)
        top_row = row_sum_index[0][0]
        last_row = row_sum_index[0][-1]
        
        if top_row < 0:
            top_row = 0
        if last_row < 0:
            last_row = 0
            
        return top_row, last_row
    
    def Raster_col_boundaries(self,raster):
        
        col_sum_index = np.where(np.sum(raster,axis=0) != 0)
        left_col = col_sum_index[0][0]
        right_col = col_sum_index[0][-1]
        
        if left_col < 0:
            left_col = 0
        if right_col < 0:
            right_col = 0
            
        return left_col, right_col

#%%
    def FunMode(self,a):
        try:
            modev = stats.mode(a, axis=None, nan_policy = 'omit')
            modev = modev[0] 
        except:
            modev = 0.0
        return np.float(modev[0])
    
    def Watershed_CDL(self):
        # Create a matrix of crop rotation time series CDL data (each row is a pixel, each column is a year)        
        CDL = np.zeros((len(self.wid_array.flatten()),10))
        c=0
        for year in self.cdl_years: 
            print self.fnames[self.findex[self.findex[:,1]==year,0][0]]
            new_raster = self.CDL_org[:,c].reshape(self.bnd_array.shape)
            new_raster = new_raster[self.wdims[0]:self.wdims[1]+1,self.wdims[2]:self.wdims[3]+1]
            print 'Started filter'
            new_raster = ndimage.generic_filter(new_raster,self.FunMode,footprint=np.ones((3,3)), mode='reflect')
            #new_raster = self.Mode_Filter(new_raster)
            
            #apply the mask to limit the collection of data to only the specify region by the mask's raster  
            CDL[:,c] = new_raster.flatten()*self.wid_array.flatten()
            c += 1
            
        return CDL
    
    
    def Mode_Filter(self,raster):
        winSize = self.winSize
        wind = int(np.floor(winSize[0]/2))
    
        top_row, last_row = self.Raster_row_boundaries(raster) 
        mraster = np.asarray(raster, dtype = float)
        mraster[mraster == 0] = float('nan')
        fraster = raster     
                   
        if last_row >= int(raster.shape[0]-wind-1):
            last_row = int(raster.shape[0]-wind-1)
        #for i in range(top_row, raster.shape[0]-winSize+1):
        for i in range(top_row, last_row+1):
            if i % 200 == 0:
                print('Progress: ' + str((float(i)/raster.shape[0])*100))
    
            left_col, right_col = self.Raster_col_boundaries(raster[i:i+winSize[0],])
            if right_col >= int(raster.shape[1]-wind-1):
                right_col = int(raster.shape[1]-wind-1)
            #for j in range(left_col, raster.shape[1]-winSize+1):
            for j in range(left_col, right_col+1):
                row_array = range(i,i+winSize[0])
                col_array = range(j,j+winSize[0])
                window = mraster[i:i+winSize[0],j:j+winSize[0]].reshape((-1,1)) # each individual window
                fraster[row_array[wind],col_array[wind]] = stats.mode(window).mode[0][0]
        
        return fraster
    
    #%% Read System boundary mask (raster: 0-no data, 1-area of study)
    def ReadInputData(self):  
        #boundary = rasterio.open(self.rootpath + '\\' + self.boundary_lyr)
        #boundary = boundary.read(1)
        boundary = gdal.Open(self.rootpath + '\\' + self.boundary_lyr, gdal.GA_ReadOnly)
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
        watersheds = gdal.Open(self.rootpath + '\\' + self.watershed_lyr)
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

#%%  
    def Save_NewRaster(self, array, ds, old_raster, newRaster_name, raster_NoData):
        
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
        self.Save_NewRaster(new_soil, soil_raster_ds, soil_raster, soil_newRaster_name, soil_raster_NoData)
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
        self.Save_NewRaster(new_slope, slope_raster_ds, slope_raster, slope_newRaster_name, slope_raster_NoData)
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
            
            for missing_nlcd in self.missing_nlcd_classes.keys():
                outputcsv_writer.writerow([int(missing_nlcd),self.missing_nlcd_classes[missing_nlcd]['Name']])
            
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
               
#%% Inputs  
        
#swat_path = 'C:\Users\sammy\Documents\Research\SWAT\QSWATplus\WillowSWAT12\WillowSWAT12_test'
#nlcdFile = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\NLCD_proj.tif'
#subbasinsFile = 'C:\Users\sammy\Documents\Research\SWAT\QSWATplus\WillowSWAT12\willow_v1\willow_v1\Source\Willow_Proj.shp'
#landuseFile = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\HRUs_LU.tif' # In theory this file would be part of the outputs of the whole script, thus not needed
#soilFile = 'C:\Users\sammy\Documents\Research\SWAT\willow_final\Soils_30m.tif'

#%% Find paths to all files in project folder

def ReadInputs(file_path):
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
                
        if sys.platform.startswith('win'):
            InterACTWEL_HRUs.swat_path = swat_path.replace('\\','/')
            InterACTWEL_HRUs.soil_file = soilFile.replace('\\','/')
            InterACTWEL_HRUs.landuse_file = landuseFile.replace('\\','/')
            InterACTWEL_HRUs.nlcd_file = nlcdFile.replace('\\','/')
            InterACTWEL_HRUs.watershed_path = subbasinsFile.replace('\\','/')
            InterACTWEL_HRUs.cdl_file = cdlFile.replace('\\','/')
        
        else:
            InterACTWEL_HRUs.swat_path = swat_path
            InterACTWEL_HRUs.soil_file = soilFile
            InterACTWEL_HRUs.landuse_file = landuseFile
            InterACTWEL_HRUs.nlcd_file = nlcdFile
            InterACTWEL_HRUs.watershed_path = subbasinsFile
            InterACTWEL_HRUs.cdl_file = cdlFile

#%%               
##for wid in watershed_ids:
#for wid in range(12,13):
#    temp_watershed = np.asarray(InterACTWEL_HRUs.watersheds == wid, dtype=np.int64)
#    left_col, right_col = InterACTWEL_HRUs.Raster_col_boundaries(temp_watershed)
#    top_row, last_row = InterACTWEL_HRUs.Raster_row_boundaries(temp_watershed) 
#    InterACTWEL_HRUs.wdims = [top_row,last_row,left_col,right_col]
#    
#    temp_watershed = temp_watershed[top_row:last_row+1,left_col:right_col+1]
#    #plt.matshow(temp_watershed)
#    InterACTWEL_HRUs.wid_array = temp_watershed
#    
#    CDL_org = InterACTWEL_HRUs.ReadCDL()
#    #% Convert to background non-crop data. Required inputs: Raster values of no-crop data 
#    for noncrop in InterACTWEL_HRUs.no_crop_ids:
#        CDL_org[CDL_org==noncrop] = 0
#    InterACTWEL_HRUs.CDL_org = CDL_org
#    InterACTWEL_HRUs.CDL = InterACTWEL_HRUs.Watershed_CDL()
#    #sio.savemat('PythonCDL.mat', {'data':InterACTWEL_HRUs.CDL},{'data_org':InterACTWEL_HRUs.CDL_org})
#    InterACTWEL_HRUs.Create_Operation_timeseries()
#    temp_icrop, temp_icropb = InterACTWEL_HRUs.Create_HRUs()
# 

#%%

#%%    
if __name__ == '__main__':
    
##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
    parser = argparse.ArgumentParser(description='Inputs File')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                        help='Path to text file with list of input Files')
    args = parser.parse_args()
    user_cwd = os.getcwd()
    
    print args.path[0]
    InterACTWEL_HRUs = Create_InterACTWEL_HRUs()
             
    ReadInputs(args.path[0].replace('\\','/'))        
            
    file_list = os.listdir(InterACTWEL_HRUs.swat_path + '/Source')
    for f in file_list:
        if 'slp.tif' == f[-7:]:
            InterACTWEL_HRUs.slope_file = InterACTWEL_HRUs.swat_path + '/Source/' + f
            
        (base, suffix) = os.path.splitext(os.path.basename(InterACTWEL_HRUs.watershed_path))
        SubbasinRaster = InterACTWEL_HRUs.swat_path.replace('\\','/') + '/' + base + '.tif'
        exists = os.path.isfile(SubbasinRaster)
    
    if not exists:
        print("Rasterising subbasin shapefile...")
        QSWAT_preprocess.CreateSubbasinTiff(InterACTWEL_HRUs.watershed_path, SubbasinRaster, InterACTWEL_HRUs.slope_file)
        exists = os.path.isfile(SubbasinRaster)
        print("Done creating Subbasin Raster")
    
    InterACTWEL_HRUs.watershed_lyr = SubbasinRaster
    
    if exists:
    
        print("Clipping Landuse to subbasin extent")
        (base, suffix) = os.path.splitext(os.path.basename(InterACTWEL_HRUs.nlcd_file))
        landuseRaster = InterACTWEL_HRUs.swat_path.replace('\\','/') + '/' +  base + '_clp' + suffix
        QSWAT_preprocess.clipraster(InterACTWEL_HRUs.nlcd_file, landuseRaster, SubbasinRaster, gdal.GRA_Mode)   
    
        print("Clipping Soil to subbasin extent")
        (base, suffix) = os.path.splitext(os.path.basename(InterACTWEL_HRUs.soil_file))
        SoilRaster = InterACTWEL_HRUs.swat_path.replace('\\','/') + '/' + base + '_clp' + suffix
        QSWAT_preprocess.clipraster(InterACTWEL_HRUs.soil_file, SoilRaster, SubbasinRaster, gdal.GRA_Mode)
        
        print("Clipping InterACTWEL HRUs to subbasin extent")
        (base, suffix) = os.path.splitext(os.path.basename(InterACTWEL_HRUs.landuse_file))
        hruRaster = InterACTWEL_HRUs.swat_path.replace('\\','/') + '/' + base + '_clp' + suffix
        QSWAT_preprocess.clipraster(InterACTWEL_HRUs.landuse_file, hruRaster, SubbasinRaster, gdal.GRA_Mode)
        
        print("Clipping CDL Layer to subbasin extent")
        (base, suffix) = os.path.splitext(os.path.basename(InterACTWEL_HRUs.cdl_file))
        cdlRaster = InterACTWEL_HRUs.swat_path.replace('\\','/') + '/' + base + '_clp' + suffix
        QSWAT_preprocess.clipraster(InterACTWEL_HRUs.cdl_file, cdlRaster, SubbasinRaster, gdal.GRA_Mode)
    
    InterACTWEL_HRUs.nlcd_file = landuseRaster
    InterACTWEL_HRUs.landuse_file = hruRaster
    InterACTWEL_HRUs.soil_file = SoilRaster
    InterACTWEL_HRUs.cdl_file = cdlRaster
    
    InterACTWEL_HRUs.db_path = InterACTWEL_HRUs.swat_path.replace('\\','/') + '/QSWATRef2012.mdb'
    
    InterACTWEL_HRUs.MergeNLCD_HRU()
    
    #%%
    
    #file_list = os.listdir(swat_path + '/Source/crop')
    #for f in file_list:
    #    if '.tif' == f[-4:]: 
    #        InterACTWEL_HRUs.landuse_file = swat_path + '/Source/crop/' + f
    #
    #file_list = os.listdir(swat_path + '/Source/soil')
    #for f in file_list:
    #    if '.tif' == f[-4:]:
    #        InterACTWEL_HRUs.soil_file = swat_path + '/Source/soil/' + f
            
    #%% 
    ## Simplify Slopes and Soils
    InterACTWEL_HRUs.SimplifySoils()
    InterACTWEL_HRUs.SimplifySlopes()
    
    #%% Create LU Lookup 
    
    InterACTWEL_HRUs.CreateLU_LookupTable()

