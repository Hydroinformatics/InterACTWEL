# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 09:58:22 2019

@author: Nick
"""

import sys
import os
sys.path.append('../..')

from SALib.analyze import rbd_fast
from SALib.sample import latin
from SALib.test_functions import Ishigami
from SALib.util import read_param_file

import numpy as np
import pandas as pd
import random

# Read the parameter range file and generate samples
your_path = "data_nick\rbd_test_pars.txt" ################ This is where i'm testing the paths
pathtest = os.getcwd() + '\\data_nick\\rbd_test_pars.txt'

problem = read_param_file(pathtest)
data_path = os.getcwd() + '\\data_nick\\'
#np.savetxt(data_path+'param_values_lhc.txt', problem)

wr_vars_path = data_path+'wr_vars.csv'
wr_vars = pd.read_csv(wr_vars_path)

i = 1
np.savetxt(data_path+'watrgt_i\watrgt_'+str(i)+'.txt', wr_vars, fmt='%s')
