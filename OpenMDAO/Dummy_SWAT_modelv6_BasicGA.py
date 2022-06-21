# -*- coding: utf-8 -*-
"""
Created on Thu May  5 10:29:22 2022

@author: riversam
"""
import numpy as np
import openmdao.api as om

class Farmers(om.ExplicitComponent):
    
    def initialize(self):

        self.hrus_areas = {1:[20,40],2:[15,10,30],3:[20,25,5]}
        self.hrus_crops = {1:[2,1],2:[1,1,3],3:[2,2,3]}
        self.nactors = 1
        self.hru_wrs = {1:[1,50], 2:[3,50], 3:[1,20], 4:[1,20]}
        
        #Sale price per unit of yield for different crops
        self.crops_price = [200,500,100]
        
        # % Max. Yield of crops based on irrigation amount (Water consumption per crop)
        self.w_crops = np.asarray([[0,0,0,0],[10,0,0,0],[20,60,0,200],[30,180,80,300],
                        [40,250,150,310],[50,280,300,320],[60,400,450,330],
                        [70,420,500,340],[80,460,550,350],[100,500,600,360]])
    
        # #Parameters of fertilized application functions per crop
        self.p_crops_a = [-.3,-.1,-.05]
        self.p_crops_b = [4000,5000,3000]
        self.f_cost = [500,400,200]
        self.cost_fert = self.calculate_cost_fert()

    ################################
        
    def calculate_cost_fert(self):
        #Cost of fertilizer as a function of total irrigation amount
        cost = np.asarray(np.zeros((101,3)))
        for i in range(0,3):
            for ii in range(0,101):
                if np.round((1 + (0.8*-np.exp(self.p_crops_a[i]*ii)))) != 1: 
                    cost[ii][i] = ii*self.f_cost[i]
                else:
                    cost[ii][i] = cost[ii-1][i]
                    
        return cost
    
    ################################
    
    def setup(self):
        
        len_ga = 0
        for i in range(0,self.nactors):
            #for j in self.hrus_crops[i+1].keys():
            len_ga = len_ga + len(self.hrus_crops[i+1])
        
        self.add_input('wr_vols', val=np.ones(self.nactors))
        self.add_input('hru_irr', val=np.ones(len_ga))
        self.add_discrete_input('hru_fert', val=np.zeros(len_ga).astype('int'))

        self.add_output('indv_profit', val=np.zeros(self.nactors))
        self.add_output('indv_costs', val=np.zeros(self.nactors))
        self.add_output('profit', val=0.0)
        #self.add_output('indv_crops_yields', val=np.zeros(len(self.crops_price)))
        
    def setup_partials(self):
        self.declare_partials('profit', 'wr_vols*', method='fd')
        #self.declare_partials('indv_profit', 'hru_fert*', method='fd')
    
    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        
        
        for wrids in range(0,len(inputs['wr_vols'])):
            
            wr_vol = inputs['wr_vols'][wrids]
            
            hru_ids = 0
            indv_hru_irr = []
            indv_hru_irr_ids = []
            
            for i in self.hrus_areas.keys():
                if wrids+1 == int(i):
                    for ii in range(0,len(self.hrus_areas[wrids+1])):
                        indv_hru_irr.append(inputs['hru_irr'][hru_ids])
                        indv_hru_irr_ids.append(hru_ids)
                        
                        hru_ids = hru_ids + 1
                        
                hru_ids = hru_ids + 1
            
            indv_profit = 0
            indv_costs = 0
            indv_envir = 0
            total_hru_irr = sum(indv_hru_irr)
                
            #if abs((total_hru_irr - inputs['wr_vols'][wrids])) > 0.0:
            #if (total_hru_irr - inputs['wr_vols'][wrids]) > 0.0:
            if (total_hru_irr - 100.) > 0.0:
                #outputs['indv_profit'][wrids] = - 5000000000
                outputs['indv_profit'][wrids] = 0
                outputs['indv_costs'][wrids] = 0.
                #outputs['indv_crops_yields'] = np.zeros(len(self.crops_price))
                
                #outputs['total_irr'] = total_irr
                #outputs['indv_profit'] = - abs((sum(inputs['hru_irr']) - 100.0))*100000000
            else:
                for i in range(0,len(self.hrus_areas[wrids+1])):
    
                    irr_amt = (indv_hru_irr[i]/100.)*wr_vol
                    crop_yield = np.interp(irr_amt, self.w_crops[:,0], self.w_crops[:,self.hrus_crops[wrids+1][i]]) 
                    cost_f = np.interp(irr_amt, range(0,101), self.cost_fert[:,discrete_inputs['hru_fert'][indv_hru_irr_ids[i]]])*self.hrus_areas[wrids+1][i]
                
                    per_yield = 1 + (0.8*-np.exp(self.p_crops_a[self.hrus_crops[wrids+1][i]-1]*irr_amt))
                    profit = crop_yield*per_yield*self.hrus_areas[wrids+1][i]*self.crops_price[self.hrus_crops[wrids+1][i]-1] - cost_f # profit function       
                    
                    envir = 1 + (0.8*-np.exp(self.p_crops_a[self.hrus_crops[wrids+1][i]-1]*irr_amt))*self.p_crops_b[discrete_inputs['hru_fert'][i]]
    
                    indv_profit = indv_profit + profit
                    indv_costs = indv_costs + cost_f
                    indv_envir  = indv_envir + envir
                    #total_irr = total_irr + irr_amt
                    
                    #outputs['indv_crops_yields'][self.hrus_crops[i]-1] = outputs['indv_crops_yields'][self.hrus_crops[i]-1] + crop_yield*per_yield*self.hrus_areas[i]
                
                outputs['indv_envir'] = indv_envir
                outputs['indv_profit'][wrids] = indv_profit    
                outputs['indv_costs'][wrids] = indv_costs
                
            
        total_profit = 0
        for i in range(0,len(inputs['wr_vols'])):
            total_profit = total_profit + outputs['indv_profit'][i]
                
        outputs['profit'] = total_profit
        
        print(inputs['wr_vols'], inputs['hru_irr'], outputs['profit'])

#######################################################################################################