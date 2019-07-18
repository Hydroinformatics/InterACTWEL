import re

def Get_output_wql(tfile, var, varcol):
    #output_data = dict()
    data_array = dict()
    data_array['Years'] = []
    data_array['Type'] = 'RCH'
    varbool = 0
    
    with open(tfile) as search:
        for line in search:
            if varbool == 0:
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                    
                data_array[linesplit[1]].append(float(linesplit[varcol-1])) 
                        
    return data_array

def Get_output_rch(tfile, var, varcol):
    #output_data = dict()
    data_array = dict()
    data_array['Years'] = []
    data_array['Type'] = 'RCH'
    varbool = 0

    with open(tfile) as search:
        for line in search:
            if 'RCH'.lower() in line.lower():    
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                    
                if len(linesplit[3].split('.')) < 2:
                    if int(linesplit[3]) < 13:
                        data_array[linesplit[1]].append(float(linesplit[varcol-1])) 
                    elif int(linesplit[3]) not in data_array['Years']:
                        data_array['Years'].append(int(linesplit[3]))
                        
    return data_array

def Get_output_std(tfile, table, var, varcol):
    #output_data = dict()
    data_array = dict()
    varbool = 0
    if 'Annual Summary for Watershed'.lower() in table.lower():
        data_array['Years'] = []
        data_array['Type'] = 'BSN'
        data_array['Data'] = []
        with open(tfile) as search:
            for line in search:
                if table in line:
                    line = search.next()
                    line = search.next()
                    line = search.next()
                    line = search.next()
                    varbool = 1
                
                elif varbool == 1:
                    linesplit = re.split('\s',line)
                    linesplit = [e for e in linesplit if e != '']
                    
                    if len(linesplit) < 2 and len(linesplit) > 1:
                        line = search.next()
                        linesplit = re.split('\s',line)
                        linesplit = [e for e in linesplit if e != '']
                        if len(linesplit[0]) == 4:
                            data_array['Years'].append(int(linesplit[0]))
                        varbool = 0
                    elif len(linesplit) < 1:
                        varbool = 0
                    else:
                        if len(linesplit[0]) < 4 and len(linesplit) > 1:
                            data_array['Data'].append(float(linesplit[varcol-1]))
    
    return data_array

def Get_output_hru(tfile, var, varcol):
    hru_sub = dict()
    data_array = dict()
    data_array['Years'] = []
    data_array['Type'] = 'HRU'
    varbool = 0
    # print(tfile)
    # print(var)
    # print(varcol)
    # os._exit()
    with open(tfile) as search:
        for line in search:
            if 'HRU'.lower() in line.lower():    
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []
                    hru_sub[linesplit[1]] = linesplit[3]

                #try:
                if len(linesplit[5].split('.')) < 3: # NEEDS to be chceck the HRU file is not displaying a month. ERROR IN SWAT
                    if int(linesplit[5].split('.')[0]) < 13 and varcol == 6:
                        data_array[linesplit[1]].append(float('0.'+ linesplit[5].split('.')[1]))
                    elif int(linesplit[5].split('.')[0]) < 13 and varcol != 6:
                        if varcol == 1:
                            data_array[linesplit[1]].append(linesplit[varcol-1])
                        else:
                            data_array[linesplit[1]].append(float(linesplit[varcol-1]))
                        
                    elif int(linesplit[5].split('.')[0]) not in data_array['Years']:
                        data_array['Years'].append(int(linesplit[5].split('.')[0]))

    return data_array, hru_sub

def Get_output_sub(tfile, var, varcol):
    data_array = dict()
    data_array['Years'] = []
    data_array['Type'] = 'SUB'
    varbool = 0
    with open(tfile) as search:
        for line in search:
            if 'SUB'.lower() in line.lower():    
                varbool = 1
                
            elif varbool == 1:
                linesplit = re.split('\s',line)
                linesplit = [e for e in linesplit if e != '']
                
                if linesplit[1] not in data_array.keys():
                    data_array[linesplit[1]] = []

                #try:
                if len(linesplit[3].split('.')) < 3: # NEEDS to be chceck the HRU file is not displaying a month. ERROR IN SWAT
                    if int(linesplit[3].split('.')[0]) < 13 and varcol == 6:
                        data_array[linesplit[1]].append(float(linesplit[3].split('.')[1]))
                        
                    elif int(linesplit[3].split('.')[0]) < 13 and varcol != 6:
                        data_array[linesplit[1]].append(float(linesplit[varcol-1]))
                        
                    elif int(linesplit[3].split('.')[0]) not in data_array['Years']:
                        data_array['Years'].append(int(linesplit[3].split('.')[0]))

    return data_array