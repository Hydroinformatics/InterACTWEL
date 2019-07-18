from helper import wrtgtm_file, hruwr_file, GetOutputVars, FindCropName, GetWaterRigthHRU, csv_file_write
from hru_sub_output import HRU_SUBDict

model_num = 5   # SWAT model number 

sim_num = 1     # number of simulation to run on each model

wrtfile = 'C:\Users\ZIPPPY\ASUS Drive\Design Optimization\Water Model\williow_update_v3\watrgtwm.dat'

iter_dir = 'C:\Users\ZIPPPY\ASUS Drive\Design Optimization\Water Model\ITERS_TENyrs'

csv_file = 'C:\Users\ZIPPPY\ASUS Drive\Design Optimization\Water Model\ITERS_TENyrs\Results'
csv_file = csv_file + '\Shreyansh_Data_' + str(model_num) + '.csv'

# outpath = 'C:\Users\ZIPPPY\ASUS Drive\Design Optimization\Water Model\ITERS_TENyrs\Results'

crop_path = 'C:\Users\ZIPPPY\ASUS Drive\Design Optimization\Water Model\williow_update_v3'

cropnames = FindCropName(crop_path)

output_vars_file =  'C:\Users\ZIPPPY\ASUS Drive\Design Optimization\Water Model\data\Sensitivity_SWAT12\OutputVars_Arjan.txt'

output_vars = GetOutputVars(output_vars_file)

irr_dict = {0: 'No irrigation',1: 'Surface water', 3: 'Groundwater', 5: 'Columbia River'}

num_sim = 1

wrdict, wrsrc = wrtgtm_file(wrtfile)

for i in range(model_num, model_num+1):
    model_path = iter_dir.replace('\\','/') + '/ITER_' + str(i) + '/'
    filein = open(csv_file,'w')
    
    # range below refers to how many simulation needs to be run on particular model
    for ii in range(sim_num, sim_num+1):
        hruwr = hruwr_file(model_path)
        output_vars_data = GetWaterRigthHRU(model_path, output_vars, i, ii)

        temp_all, _, hru_sub = HRU_SUBDict(output_vars_data, cropnames, wrsrc, hruwr, irr_dict)
        ucrop = []
        for hrui in output_vars_data['LULC'].keys():
            if hrui is not 'Type' and hrui is not 'Years':
                for cropn in output_vars_data['LULC'][hrui]:
                    if cropn.islower():
                        cropn = 'AGRL'
                    if cropn not in ucrop:
                        ucrop.append(cropn)
        
        if num_sim == 1:
            csv_file_write(filein, irr_dict, cropnames, ucrop) 
        
        yr = 1
        
        for iy in output_vars_data['LULC']['Years']:                
            for wr in wrdict.keys():
                for subid in hru_sub.keys():
                
                    if subid in temp_all['Planted crops (ha)'][wr].keys():
                        if ii == 0:
                            temptxt = 'BASE,' + str(i) + ',' + str(wr) + ',' + str(wrdict[wr]) + ',' + str(iy) + ',' + str(subid) + ','
                        else:
                            temptxt = str(num_sim-1) + ',' + str(i) + ',' + str(wr) + ',' + str(wrdict[wr]) + ',' + str(iy) + ',' + str(subid) + ','
                        
                        for uc in ucrop:
                            if uc in temp_all['Planted crops (ha)'][wr][subid].keys():
                                temptxt = temptxt + str(temp_all['Planted crops (ha)'][wr][subid][uc]['Data'][yr]) + ','
                            else:
                                temptxt = temptxt + str(0.0) + ','
                                
                        for uc in ucrop:
                            if uc in temp_all['Crop yield (kg)'][wr][subid].keys():
                                temptxt = temptxt + str(temp_all['Crop yield (kg)'][wr][subid][uc]['Data'][yr]) + ','
                            else:
                                temptxt = temptxt + str(0.0) + ','
                        
                        for ir in irr_dict.keys():
                            if ir in temp_all['Irrigation (acre-ft)'][wr][subid].keys():
                                for uc in ucrop:
                                    if uc in temp_all['Irrigation (acre-ft)'][wr][subid][ir].keys():
                                        temptxt = temptxt + str(temp_all['Irrigation (acre-ft)'][wr][subid][ir][uc]['Data'][yr]) + ','
                                    else:
                                        temptxt = temptxt + str(0.0) + ','
                            
                        temptxt = temptxt + str(temp_all['N fertilizer (kg N)'][wr][subid][yr]) + ',' + str(temp_all['P fertilizer (kg N)'][wr][subid][yr]) + ','
                        temptxt = temptxt + str(temp_all['Groundwater Recharge (acre-ft)'][wr][subid][yr]) + ',' + str(temp_all['Surface runoff Nitrate (kg N)'][wr][subid][yr]) + ',' + str(temp_all['Lateral flow Nitrate (kg N)'][wr][subid][yr]) + ',' + str(temp_all['Groundwater Nitrate (kg N)'][wr][subid][yr])
                        
                        filein.write(temptxt + '\n')
            yr = yr + 1
        num_sim = num_sim + 1
    filein.close()