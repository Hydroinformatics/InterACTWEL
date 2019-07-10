# -*- coding: utf-8 -*-
import os, argparse
from shutil import copy2

#SWATEditor_path = 'C:\Users\sammy\Desktop\Nick_Analysis\SWATEditor'

#%% Files to replace in QSWAT

def UpdateFiles(SWATEditor_path):
    files = ['ui_hrus.py','QSWATUtils.py','InterACTWEL_SWAT.py','hrus.py','delineation.py']
    for f in files:
        
        copy2(os.getcwd().replace('\\','/') + '/QSWAT/' + f, SWATEditor_path)
    
#%% 
    
if __name__ == '__main__':
    
##%% Parse Path to SWATEditor folder
    parser = argparse.ArgumentParser(description='Path to QSWAT Folder')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                        help='Path to QSWAT Folder')
    
    args = parser.parse_args()
    user_cwd = os.getcwd()
    
    UpdateFiles(args.path[0].replace('\\','/'))