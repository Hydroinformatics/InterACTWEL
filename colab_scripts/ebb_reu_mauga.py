# -*- coding: utf-8 -*-
import os, argparse, sys

os.chdir('..\src')
sys.path.append(os.getcwd())

from qswat import QSWAT_preprocess

#%%    
if __name__ == '__main__':
    
##%% Parse Path to DEM File
    parser = argparse.ArgumentParser(description='Inputs File')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                        help='Path to text file with list of input Files')
    args = parser.parse_args()
    user_cwd = os.getcwd()
    
    preprocess = QSWAT_preprocess.Data_Preprocess()
    preprocess.ReadInputFile(args.path[0].replace('\\','/'))
    preprocess.DissolveWatersheds()
    preprocess.Clip_Rasters()
    
