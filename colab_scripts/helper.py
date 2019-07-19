from helper_output import Get_output_hru, Get_output_rch, Get_output_std, Get_output_sub, Get_output_wql
import re, pyodbc

def FindString(startstr, endstr, line):
    
    temp_id_a = line.find(startstr) 
    temp_id_b = line.find(endstr)
    tempstr = line[temp_id_a+1:temp_id_b]
    
    return tempstr

def GetOutputVars(output_vars_file):
    
    output_varsb = dict()
    line_bool = 0
    with open(output_vars_file,'rb') as search:
        for line in search:
            if '#' in line:
                line_bool = 1
                temp_dict = dict()
                outputs_id = "".join(line.split())
                outputs_id = outputs_id.strip('#')
                #opschd_id = re.split(':',linesplit)[1]
                #opschd_counter = 0
            
            elif '#' not in line and line_bool == 1 and len(line.strip()) > 0:
                linesplit = "".join(line.split())
                file_id = re.split('=',linesplit)
                temp_dict = dict()
                temp_dict['File'] = file_id[0]
                output_varsb[outputs_id] = temp_dict
                param_values = FindString('{','}',linesplit)
                param_values = re.split(';',param_values)
                temp_dict = dict()
                for parvals in param_values:
                    temp_var = parvals.split(':')
                    
                    temprange = temp_var[1]
                    temprange = temprange.strip('[')
                    temprange = temprange.strip(']')
                    if temp_var[0].lower() != 'table':
                        temp_dict[temp_var[0]] = int(temprange)
                    else:
                        templine = re.split('=',line)
                        templine = FindString('{','}',templine[1])
                        templine = re.split(';',templine )
                        templine = templine[0].split(':')
                        templine = templine[1].strip('[')
                        templine = templine.strip(']')
                        
                        temp_dict[temp_var[0]] = templine


            elif len(line.strip()) == 0:
                line_bool = 0
                output_varsb[outputs_id]['Vars']  = temp_dict
                
    search.close()
    
    if line_bool == 1:
        line_bool = 0
        output_varsb[outputs_id]['Vars'] = temp_dict
    
    return output_varsb

def FindCropName(model_path):
    db_path = model_path + '\QSWATRef2012.mdb'
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=' + db_path + ';'
        )
    cnxn = pyodbc.connect(conn_str)
    crsr = cnxn.cursor()
    
    crsr.execute('select * from crop')
    cropdict = dict()
    for row in crsr.fetchall():
        cropdict[str(row[2])] = row[4]
    
    cropdict['NOCR'] = 'No Crops'
    
    return cropdict

def wrtgtm_file(wrtfile):
    wrdict = dict()
    wrsrc = dict()
    hru_wsrc = dict()
    wsrc_sum = dict()
    
    with open(wrtfile,'rb') as search:
        for line in search:
            linesplit = re.split('\s',line)
            linesplit = [t for t in linesplit if len(t) > 0]
            
            if int(linesplit[2]) not in wsrc_sum and int(linesplit[2]) != 0:
                    wsrc_sum[int(linesplit[2])] = 0
                    hru_wsrc[int(linesplit[2])] = []
                    
            if len(linesplit) > 0 and int(linesplit[0]) != 999 and int(linesplit[0])==1:
                wrdict[int(linesplit[1])] = int(linesplit[3])
                wrsrc[int(linesplit[1])] = int(linesplit[2])
                
                
            if int(linesplit[2]) != 0 and int(linesplit[0])==1:
                wsrc_sum[int(linesplit[2])] = wsrc_sum[int(linesplit[2])] + int(linesplit[3])
                hru_wsrc[int(linesplit[2])].append(int(linesplit[1]))
                
        search.close()
        
        return wrdict, wrsrc

def hruwr_file(model_path):
        hruwr = dict()
        
        with open(model_path + 'Scenarios/Default/TxtInOut/hruwr.dat','rb') as search:
            for line in search:
                linesplit = re.split('\s',line)
                linesplit = [t for t in linesplit if len(t) > 0]
                if len(linesplit) > 0:
                    #temp_dict[int(linesplit[1])] = wrdict[int(linesplit[3])]
                     hruwr[int(linesplit[3])] = int(linesplit[1])
        search.close()
        
        return hruwr

def GetWaterRigthHRU(model_path, output_vars, itern, sim_num):
    outpath = 'C:\Users\ZIPPPY\ASUS Drive\Design Optimization\Water Model\ITERS_TENyrs\Results'
    
    output_vars_data = dict()
    
    for outfile in output_vars:
        tfile = model_path + output_vars[outfile]['File']
        tfile = outpath + '/' + output_vars[outfile]['File'] + '_' + str(itern) +'_'+ str(sim_num) + '.' + tfile[len(tfile)-3:len(tfile)]
        
        if tfile[len(tfile)-3:len(tfile)] == 'hru':
            print('Reading output.hru')
            for varkey in output_vars[outfile]['Vars'].keys():
                data_array, hru_sub = Get_output_hru(tfile, varkey, output_vars[outfile]['Vars'][varkey])
                output_vars_data[varkey] = data_array
                
        elif tfile[len(tfile)-3:len(tfile)] == 'sub':
            print('Reading output.sub')
            for varkey in output_vars[outfile]['Vars'].keys():
                data_array = Get_output_sub(tfile, varkey, output_vars[outfile]['Vars'][varkey])
                output_vars_data[varkey] = data_array
        
        elif tfile[len(tfile)-3:len(tfile)] == 'rch':
            print('Reading output.rch')
            for varkey in output_vars[outfile]['Vars'].keys():
                output_vars_data[varkey] = Get_output_rch(tfile, varkey, output_vars[outfile]['Vars'][varkey])

        elif tfile[len(tfile)-3:len(tfile)] == 'wql':
            print('Reading output.wql')
            for varkey in output_vars[outfile]['Vars'].keys():
                output_vars_data[varkey] = Get_output_wql(tfile, varkey, output_vars[outfile]['Vars'][varkey])

        elif tfile[len(tfile)-3:len(tfile)] == 'std':
            print('Reading output.std')
            table = output_vars[outfile]['Vars']['Table']
            for varkey in output_vars[outfile]['Vars'].keys():
                if varkey.lower() != 'table':
                    output_vars_data[varkey] = Get_output_std(tfile, table, varkey, output_vars[outfile]['Vars'][varkey])
    
    return output_vars_data

def csv_file_write(filein, irr_dict, cropnames, ucrop):
    
    # filein = open(csv_file,'w')
    # Format of HRU and Sub-basin csv
    atxt = 'ITER, MODEL ID, WR ID, WR AMT, YEAR, SUBBASIN ID,'
    for n in range(0,2):
        for u in ucrop:
            atxt = atxt + str(cropnames[u]) + ','
    for u in ucrop:
        for irrid in irr_dict.keys():
            atxt = atxt + cropnames[u] + '_' + str(irr_dict[irrid]) + ','
    for u in ucrop:
        atxt = atxt + 'N Fertilizer' + '_' + cropnames[u] + ','
    atxt = atxt + 'P Fertilizer, Groundwater Recharge (acre-ft),	Surface runoff Nitrate (kg N), Lateral flow Nitrate (kg N), Groundwater Nitrate (kg N),'
    for u in ucrop:
            atxt = atxt + 'Profit ' + str(cropnames[u]) + ','
    
    atxt = atxt + 'Crop Profit ($), Costs ($), Total Profit ($),'
    filein.write(atxt + '\n')