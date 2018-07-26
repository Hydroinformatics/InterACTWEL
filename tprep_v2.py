#import pandas as pd
import numpy as np
import argparse


if __name__ == '__main__':
    
##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
    parser = argparse.ArgumentParser(description='SWAT temp/date parser')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                    help='Path to file with raw temperature data')
    parser.add_argument('range', metavar='-p', type=str, nargs='+',
                    help='Starting date (dd/mm/yyyy)')
    
    args = parser.parse_args()
    
    print args.path[0]
    print args.range[0]
    
#    tin = args[0]
#    new_headers = ['max','min',]
#    mm = pd.read_csv(tin,index_col=0, skiprows=1,names=new_headers)
#    mm.head()
#    #int("Temperature data ")
#    print(mm)
