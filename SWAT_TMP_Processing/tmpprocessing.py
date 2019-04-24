import pandas as pd
import numpy as np
import argparse
from datetime import datetime

if __name__ == '__main__':
    
##%% Parse Path to Zip file, Uzip and run SWAT Baseline model
    parser = argparse.ArgumentParser(description='SWAT temp/date parser')
    parser.add_argument('path', metavar='-p', type=str, nargs='+',
                    help='Path to file with raw temperature data')
    parser.add_argument('start', metavar='-p', type=str, nargs='+',
                    help='Starting date (dd/mm/yyyy)')
    parser.add_argument('end', metavar='-p', type=str, nargs='+',
                    help='End date (dd/mm/yyyy)')
    parser.add_argument('station', metavar='-p', type=str, nargs='+',
                    help='TMP station id (ex: 12345)')
    
    args = parser.parse_args()

    tin = args.path[0]
    sd = args.start[0]
    ed = args.end[0]
    st = args.station[0]
    tin = str(tin)
    tin = "D:\\Nick\\Documents\\GitHub\\InterACTWEL\\SWAT_TMP_Processing\\tmp_raw\\" + tin + ".csv"




# mma.head()
#
# mm = mma[['max', 'min']]
#


    new_headers = ['station', 'name', 'lat', 'long', 'elev', 'max', 'min']
    mma = pd.read_csv(tin,index_col=5, skiprows=1,names=new_headers)
    mma.head()
    mm = mma[['max', 'min']]

    idx = pd.date_range(sd, ed)
    #
    mm.index = pd.DatetimeIndex(mm.index)
    mm = mm.reindex(idx, fill_value=-99)
    # print(mm)

    #
    # mmnn = [Date, Max, Min] with NaN values = -99
    mmnn = mm.fillna(-99)
    # print(mmnn)

    # Write to TMP_output.cvs
    sd = '01/01/1940'
    datetimeobject = datetime.strptime(sd,'%m/%d/%Y')
    initiald = datetimeobject.strftime('%Y%m%d')


    sta = "D:\\Nick\\Documents\\GitHub\\InterACTWEL\\SWAT_TMP_Processing\\tmp\\" + str(st) + ".txt"

    mmnn.to_csv('tmpNOHEADER.txt', header=False, index=None, mode='w')
    c= open('tmpNOHEADER.txt')
    f= open(sta,"w+")
    f.write(initiald + '\n')
    f.close()

    f= open(sta, "a")
    f.write(c.read())
    f.close()
    c.close()
# tmp file
    info = mma[['station', 'lat','long', 'elev']]
    station = info.loc[['1/1/1940'], 'station']
    lat = info.loc[['1/1/1940'], 'lat']
    long = info.loc[['1/1/1940'], 'long']
    elev = info.loc[['1/1/1940'], 'elev']

    f = open(r'D:\\Nick\\Documents\\GitHub\\InterACTWEL\\SWAT_TMP_Processing\\tmp\\tmp.txt', "a")
    for i, l in enumerate(f):
            pass
    lnum = i + 1
    f.write(i + '\n')
    f.close()

    print("{}.txt processed and saved to tmp file.".format(st))