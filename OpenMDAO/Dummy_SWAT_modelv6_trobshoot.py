# -*- coding: utf-8 -*-
"""
Created on Thu May  5 10:29:22 2022

@author: riversam
"""
import numpy as np
import openmdao.api as om
import shutil

class FEWNexus(om.Group):
    
    def initialize(self):
        self.nactors = 1
    
    def setup(self):
        
        des_vars = self.add_subsystem('wr_vols', om.IndepVarComp(), promotes=['*'])
        des_vars.add_output('wr_vols', val=[10,20])
        
        ######## SETUP of REGIONS ###############
            
        # region_model = self.add_subsystem('region', Region(), promotes=['profit','wr_vols','actors_wr_vols'])
        
        # ######## SETUP of FARMERS ###############
    
        for i in range(0,self.nactors):
            self.add_subsystem('farmer_' + str(i+1) + '_plan', FarmerOpt())   
            exec("self."+"farmer_"+str(i+1)+"_plan.farmer_id =" + str(i+1))
            self.connect('wr_vols','farmer_' + str(i+1) + '_plan.wr_vol', src_indices=[i])
        
        region_model = self.add_subsystem('region', Region(), promotes=['profit'])
        region_model.nactors = self.nactors
        self.connect('wr_vols','region.wr_vols')
        
        for i in range(0,self.nactors):
            self.connect('farmer_' + str(i+1) + '_plan.indv_yield', 'region.actor_yield_' + str(i+1))
        
############################################# SUB-SYSTEM ######################################

class Region(om.ExplicitComponent):
    
    def initialize(self):
        self.nactors = 1
        self.profits = [80,28,34]
        
    def setup(self):
        
        self.add_input('wr_vols', val=np.ones(self.nactors))
        for i in range(0,self.nactors):
            self.add_input('actor_yield_'+ str(i+1), val=0.0)
        
        #self.add_output('actors_wr_vols',val=np.ones(self.nactors))
        self.add_output('profit', val=0.0)
    
    def setup_partials(self):
        self.declare_partials('profit', 'wr_vols', method='fd')
        #self.declare_partials('profit', 'actor_profit_1', method='fd')
        
    def compute(self, inputs, outputs):
        
        print(inputs['actor_yield_1'][0],inputs['actor_yield_2'][0])
        
        total_profit = 0
        for i in range(0,self.nactors):
            #print(inputs['actor_profit_'+ str(i+1)])
            
            #total_profit = total_profit + inputs['actor_profit_'+ str(i+1)][0]
            #total_profit = total_profit + inputs['wr_vols'][i]*self.profits[i]*inputs['actor_yield_'+ str(i+1)]
            total_profit = total_profit + (self.profits[i]*inputs['actor_yield_'+ str(i+1)])#/inputs['wr_vols'][i]
            
        outputs['profit'] = total_profit  
        #outputs['actors_wr_vols'] = inputs['wr_vols']
        
############################################# SUB-SYSTEM ACTOR ######################################   

class FarmerOpt(om.ExplicitComponent):
    
    def initialize(self):
        self.farmer_id = None
        self.farmers_yield = [2,5,3]
    
    def setup(self):
        
        #self.add_input('wr_vol', val=np.ones(2)) 
        self.add_input('wr_vol', val=1.0) 
        self.add_output('indv_yield', val=0.0)

    def setup_partials(self):
        self.declare_partials('indv_yield', 'wr_vol', method='fd')
    
    def compute(self, inputs, outputs):
    
        #print('subopt ' + str(self.farmer_id) + ' wr_vol: ' + str(inputs['wr_vol']))
        #outputs['indv_yield'] = self.farmers_yield[self.farmer_id-1]*int(inputs['wr_vol'][self.farmer_id-1])
        
        outputs['indv_yield'] = self.farmers_yield[self.farmer_id-1]*int(inputs['wr_vol'][0])
