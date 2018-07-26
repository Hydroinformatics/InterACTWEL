import pandas as pd
import numpy as np

tin = input('Input raw temperature data here: ')
#drange = input('Starting Date')

new_headers = ['max','min',]
mm = pd.read_csv(tin,index_col=0, skiprows=1,names=new_headers)
mm.head()
#int("Temperature data ")
print(mm)