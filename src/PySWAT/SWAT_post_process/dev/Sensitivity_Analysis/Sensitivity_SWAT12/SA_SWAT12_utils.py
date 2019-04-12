# -*- coding: utf-8 -*-

import os, re, zipfile, argparse, subprocess, shutil, random
import numpy as np

class SAUtils(object):
    #def __init__(self):
        
        
    #%% 
    def AdjustNameLen(temp_line,old_str,new_str):
        strid = temp_line.find(old_str)
        str_lendiff = abs(len(old_str) - len(new_str) )
        
        if len(new_str) > len(old_str):
            temp_line = new_str + temp_line[((strid+len(old_str))+str_lendiff):]
        
        elif len(new_str) < len(old_str):
            temp_line = new_str + ' ' * str_lendiff + temp_line[(strid+len(old_str)):]
        
        elif len(new_str) == len(old_str):
            temp_line = temp_line.replace(old_str,new_str)
        
        return temp_line
    
    def AdjustOpsLen(temp_line,old_str,new_str):
        strid = temp_line.find(old_str)
        str_lendiff = abs(len(old_str) - len(new_str) )
        
        if len(new_str) > len(old_str):
            temp_line = temp_line[0:(strid-str_lendiff)] + new_str + temp_line[(strid+len(old_str)):]
        
        elif len(new_str) < len(old_str):
            temp_line = temp_line[0:strid] + ' ' * str_lendiff + new_str + temp_line[(strid+len(old_str)):]
        
        elif len(new_str) == len(old_str):
            temp_line = temp_line.replace(old_str,new_str)
        
        return temp_line