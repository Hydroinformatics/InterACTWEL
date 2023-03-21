# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 11:03:51 2023

@author: riversam
"""


def Write_new_wrdata(org_file_path, new_file_path, actorid, wrvol)
                   
    txt_file = temp_path + '/wrdata_' + str(actorid) + '.dat'

    
    file_org = open(org_file_path, 'r')
    Lines = file_org.readlines()
    
    filein = open(new_file_path,'w')
    
    for line in Lines:
        linesplit = line.split()
        if 'year' not in linesplit[0].lower():
            atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
            atxt = atxt + str(int(linesplit[1])).rjust(5) + ''.rjust(3)
            atxt = atxt + str(int(linesplit[2])).rjust(4) + ''.rjust(3)
            
            if int(linesplit[1]) == actorid:
                atxt = atxt + str(wrvol).rjust(6) + ''.rjust(3)
            else:
                atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
                    
            atxt = atxt + str(int(linesplit[4])).rjust(4) + ''.rjust(3)
            atxt = atxt + str(int(linesplit[5])).rjust(4)
            filein.write(atxt + '\n') 
            
        else:
            filein.write(line) 
    
    
    file_org.close()
    filein.close()
    