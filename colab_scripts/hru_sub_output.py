import numpy as np

def HRU_SUBDict(output_vars_data, cropnames, wrsrc, hruwr, irr_dict):
    
    hru_sub = dict()
    
    for hrui in output_vars_data['SUB'].keys():
        if output_vars_data['SUB'][hrui][0] not in hru_sub.keys() and hrui is not 'Type' and hrui is not 'Years':
            hru_sub[int(output_vars_data['SUB'][hrui][0])] = []
            
        if hrui is not 'Type' and hrui is not 'Years':
            hru_sub[int(output_vars_data['SUB'][hrui][0])].append(hrui)
           
    temp_all = dict()
    temp_basin = dict()
    
    if 'LULC' in output_vars_data.keys() and 'AREAkm2' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][sub_id] = dict()


            sub_id = output_vars_data['SUB'][str(hrui)][0]
            
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cropn.islower():
                    cropn = 'AGRL'
                ##print temp_dict[hruwr[hrui]].keys()
                if cropn not in temp_dict[hruwr[hrui]][sub_id]:
                    temp_dict[hruwr[hrui]][sub_id][cropn] = dict()
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Name'] = cropnames[cropn]
                    
#                    temp_dict[hruwr[hrui]][cropn]['Data'] = 0
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Data'] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][i+1] = 0
                if cmons <= 12:
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][cyear] =  temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][cyear] + round(output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                    
        temp_all['Planted crops (ha)'] = temp_dict
        temp_all['Planted crops (ha)']['Description'] = 'Total area of planted crops in sub-basin (ha).'            
        
        
    if 'LULC' in output_vars_data.keys() and 'YLDt' in output_vars_data.keys():
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][output_vars_data['SUB'][str(hrui)][0]] = dict()
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cropn.islower():
                    cropn = 'AGRL'
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                
                if cropn not in temp_dict[hruwr[hrui]][sub_id]:
                    temp_dict[hruwr[hrui]][sub_id][cropn] = dict()
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Name'] = cropnames[cropn]
                    
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Data'] = dict()
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][i+1] = 0
                
                if cmons <= 12:
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][cyear] =  round(temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][cyear],2) + round(output_vars_data['YLDt'][str(hrui)][yieldc]*907.185*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1


        temp_all['Crop yield (kg)'] = temp_dict
        temp_all['Crop yield (kg)']['Description'] = 'Total yield of planted crops in sub-basin (kg).'


    if 'LULC' in output_vars_data.keys() and 'NAUTO' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][output_vars_data['SUB'][str(hrui)][0]] = dict()
                
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cropn.islower():
                    cropn = 'AGRL'
                if cropn not in temp_dict[hruwr[hrui]][sub_id]:
                    temp_dict[hruwr[hrui]][sub_id][cropn] = dict()
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Name'] = cropnames[cropn]
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Data'] = dict()
                    
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cropn.islower():
                    cropn = 'AGRL'
                    
                if cmons <= 12:
                    temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][cyear] =  round(temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][cyear],2) + round(output_vars_data['NAUTO'][str(hrui)][yieldc]*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['N fertilizer (kg N)'] = temp_dict
        temp_all['N fertilizer (kg N)']['Description'] = 'Amount of N fertilizer applied automatically in sub-basin (kg N).'
        

    if 'LULC' in output_vars_data.keys() and 'PAUTO' in output_vars_data.keys():
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][output_vars_data['SUB'][str(hrui)][0]] = dict()
                
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][sub_id][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_dict[hruwr[hrui]][sub_id][cyear] =  round(temp_dict[hruwr[hrui]][sub_id][cyear],2) + round(output_vars_data['PAUTO'][str(hrui)][yieldc]*output_vars_data['AREAkm2'][str(hrui)][0]*100.0,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['P fertilizer (kg N)'] = temp_dict
        temp_all['P fertilizer (kg N)']['Description'] = 'Amount of P fertilizer applied automatically in sub-basin (kg N).'
        
        
    if 'LULC' in output_vars_data.keys() and 'IRRmm' in output_vars_data.keys():
        
        uwrsrc = []
        for src in wrsrc.keys():
            uwrsrc.append(wrsrc[src])
            
        uwrsrc = np.unique(uwrsrc)
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][output_vars_data['SUB'][str(hrui)][0]] = dict()
                
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                
            for uwr in uwrsrc:
                if uwr not in temp_dict[hruwr[hrui]][sub_id].keys():
                    temp_dict[hruwr[hrui]][sub_id][uwr] = dict()
                    temp_dict[hruwr[hrui]][sub_id][uwr]['Name'] = irr_dict[uwr]
                    
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cropn.islower():
                    cropn = 'AGRL'
                            
                if cropn not in temp_dict[hruwr[hrui]][sub_id][wrsrc[hruwr[hrui]]]:
                    temp_dict[hruwr[hrui]][sub_id][wrsrc[hruwr[hrui]]][cropn] = dict()
                    temp_dict[hruwr[hrui]][sub_id][wrsrc[hruwr[hrui]]][cropn]['Name'] = cropnames[cropn]
            
                    temp_dict[hruwr[hrui]][sub_id][wrsrc[hruwr[hrui]]][cropn]['Data'] = dict()
                    
                    for i in range(len(output_vars_data['LULC']['Years'])):
                        temp_dict[hruwr[hrui]][sub_id][wrsrc[hruwr[hrui]]][cropn]['Data'][i+1] = 0
        
#                cmons = 1
#                cyear = 1
#                for cropn in output_vars_data['LULC'][str(hrui)]:
#                    if cropn.islower():
#                        cropn = 'AGRL'
#                    ##print temp_dict[hruwr[hrui]].keys()
#                    if cropn not in temp_dict[hruwr[hrui]][sub_id]:
#                        temp_dict[hruwr[hrui]][sub_id][cropn] = dict()
#                        temp_dict[hruwr[hrui]][sub_id][cropn]['Name'] = cropnames[cropn]
#                        
#    #                    temp_dict[hruwr[hrui]][cropn]['Data'] = 0
#                        temp_dict[hruwr[hrui]][sub_id][cropn]['Data'] = dict()
#                        for i in range(len(output_vars_data['LULC']['Years'])):
#                            temp_dict[hruwr[hrui]][sub_id][cropn]['Data'][i+1] = 0

            cmons = 1
            cyear = 1
            counter = 0
            #for irrsrc in output_vars_data['IRRmm'][str(hrui)]:
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cropn.islower():
                    cropn = 'AGRL'
                    
                if hruwr[hrui] != 999 and cmons <= 12:
                    temp_val = round(output_vars_data['IRRmm'][str(hrui)][counter]*0.001* output_vars_data['AREAkm2'][str(hrui)][0]*1000000.0, 2)
                    temp_val = temp_val * (35.3147 / 43560.)
                    temp_dict[hruwr[hrui]][sub_id][wrsrc[hruwr[hrui]]][cropn]['Data'][cyear] =  round(temp_dict[hruwr[hrui]][sub_id][wrsrc[hruwr[hrui]]][cropn]['Data'][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
    
                counter = counter + 1

        
        temp_all['Irrigation (acre-ft)'] = temp_dict
        temp_all['Irrigation (acre-ft)']['Description'] = 'Total irrigation volume applied automatically in sub-basin (acre-ft)'

   
    if 'GW_RCHGmm' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][output_vars_data['SUB'][str(hrui)][0]] = dict()
                
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][sub_id][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_val = round(output_vars_data['GW_RCHGmm'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0*10.0, 2)
                    temp_val = temp_val * 35.3147 * (1. / 43560.)
                    temp_dict[hruwr[hrui]][sub_id][cyear] =  round(temp_dict[hruwr[hrui]][sub_id][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['Groundwater Recharge (acre-ft)'] = temp_dict
        temp_all['Groundwater Recharge (acre-ft)']['Description'] = 'Amount of water entering both aquifers (acre-ft).'
        
    if 'NSURQ' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][output_vars_data['SUB'][str(hrui)][0]] = dict()
                
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][sub_id][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_val = round(output_vars_data['NSURQ'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                    temp_dict[hruwr[hrui]][sub_id][cyear] =  round(temp_dict[hruwr[hrui]][sub_id][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['Surface runoff Nitrate (kg N)'] = temp_dict
        temp_all['Surface runoff Nitrate (kg N)']['Description'] = 'NO3 contributed by HRU in surface runoff to reach (kg N).'
    
    if 'NLATQ' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][output_vars_data['SUB'][str(hrui)][0]] = dict()
                
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][sub_id][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_val = round(output_vars_data['NLATQ'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                    temp_dict[hruwr[hrui]][sub_id][cyear] =  round(temp_dict[hruwr[hrui]][sub_id][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['Lateral flow Nitrate (kg N)'] = temp_dict
        temp_all['Lateral flow Nitrate (kg N)']['Description'] = 'NO3 contributed by HRU in lateral flow to reach (kg N)'
        
    if 'NO3GW' in output_vars_data.keys():
        
        temp_dict = dict()
        for hrui in hruwr.keys():
            if hruwr[hrui] not in temp_dict.keys():
                temp_dict[hruwr[hrui]] = dict()
                
            if output_vars_data['SUB'][str(hrui)][0] not in temp_dict[hruwr[hrui]].keys():
                temp_dict[hruwr[hrui]][output_vars_data['SUB'][str(hrui)][0]] = dict()
                
                sub_id = output_vars_data['SUB'][str(hrui)][0]
                
                for i in range(len(output_vars_data['LULC']['Years'])):
                    temp_dict[hruwr[hrui]][sub_id][i+1] = 0
                
            yieldc = 0
            cmons = 1
            cyear = 1
            for cropn in output_vars_data['LULC'][str(hrui)]:
                if cmons <= 12:
                    temp_val = round(output_vars_data['NO3GW'][str(hrui)][yieldc] * output_vars_data['AREAkm2'][str(hrui)][0]*100.0, 2)
                    temp_dict[hruwr[hrui]][sub_id][cyear] =  round(temp_dict[hruwr[hrui]][sub_id][cyear],2) + round(temp_val,2)
                    cmons = cmons + 1
                else:
                    cmons = 1
                    cyear = cyear + 1
                yieldc = yieldc + 1
        
        temp_all['Groundwater Nitrate (kg N)'] = temp_dict
        temp_all['Groundwater Nitrate (kg N)']['Description'] = 'NO3 contributed by HRU in groundwater flow to reach (kg N)'
    
    return temp_all, temp_basin, hru_sub