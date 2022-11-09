# -*- coding: utf-8 -*-
"""
Created on Thu May  5 10:29:22 2022

@author: riversam
"""
import numpy as np
import openmdao.api as om
import os
import json 

class Farmers(om.ExplicitComponent):
    
    def initialize(self):
        
        self.farmer_id = None
        self.wrs_hrus = []
        self.hrus_areas = []
        self.hrus_crops = []
        self.json_file = None
        self.org_wr_vols = []
        self.nyears = 1

        #self.hrus_areas = {1:[20,40],2:[15,10,30],3:[20,25,5]}
        #self.hrus_crops = {1:[2,1],2:[1,1,3],3:[2,2,3]}
        self.nactors = 1
        #self.hru_wrs = {1:[1,50], 2:[3,50], 3:[1,20], 4:[1,20]}
        
        #Sale price per unit of yield for different crops
        self.crops_price = [200, 500, 100]
        
        # % Max. Yield of crops based on irrigation amount (Water consumption per crop)
        self.w_crops = np.asarray([[0,0,0,50],
                                   [10,0,0,100],
                                   [20,80,0,200],
                                   [30,180,80,260],
                                   [40,250,180,310],
                                   [50,310,300,320],
                                   [60,400,450,330],
                                   [70,430,500,340],
                                   [80,450,550,350],
                                   [100,480,600,360]])
    
        # #Parameters of fertilized application functions per crop
        self.p_crops_a = [-.3, -.1, -.05]
        self.p_crops_b = [4000, 3000, 2500]
        self.p_crops_c = [0.014, 0.018, 0.016]
        self.f_cost = [500, 400, 200]
        
        self.p_crops_e = [-0.022, -0.03, -0.042]
        self.p_crops_be = [2.6, 3.8, 6]
        self.p_crops_de = [76.818, 120.33, 214.278]
        
        self.f_envr_a = [0.2, 0.4, 0.3]
        self.f_envr_b = [2.512, 6.31, 3.98]
        self.f_envr_N = [5000, 4000, 3000]
        
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
            for yi in range(0,self.nyears):
                len_ga = len_ga + len(self.hrus_crops[i+1][yi])
            
            
        init_wr_vols = []
        for i in self.org_wr_vols.keys():
            init_wr_vols.append(np.floor(self.org_wr_vols[i][1]))
        
        self.add_input('wr_vols', val=init_wr_vols)
        self.add_input('hru_irr', val=np.ones(len_ga))
        self.add_discrete_input('hru_fert', val=np.zeros(len_ga).astype('int'))

        self.add_output('indv_profit', val=np.zeros(self.nactors))
        self.add_output('indv_envir', val=np.zeros(self.nactors))
        self.add_output('profit', val=0.0)
        self.add_output('envir_impact', val=0.0)
        self.add_output('total_wr', val=0)
        self.add_output('const_per', val=np.ones(self.nactors))
        
        
        for i in range(0,self.nactors):
            actors_solutions = dict()
            actors_solutions['farmer_' + str(i+1)] = dict()
            with open(self.json_file + str(i+1) +'_sharewr.json', 'w') as fp:
                      json.dump(actors_solutions, fp)
        
    def setup_partials(self):
        self.declare_partials('profit', 'wr_vols*', method='fd')
        #self.declare_partials('indv_profit', 'hru_fert*', method='fd')
    
    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        
        
        for wrids in range(0,len(inputs['wr_vols'])):
            
            if os.path.exists(self.json_file + str(wrids+1) +'_sharewr.json'):
                with open(self.json_file + str(wrids+1) +'_sharewr.json') as json_file:
                    actors_solutions = json.load(json_file)
            else:
                actors_solutions = dict()
                
                
                
            if 'farmer_' + str(wrids+1) not in actors_solutions.keys():
                actors_solutions['farmer_' + str(wrids+1)] = dict()
            
           
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
                

            if (total_hru_irr - 100.) > 0.0:

                outputs['indv_profit'][wrids] = -500000000.
                outputs['indv_envir'] = 500000000.
                outputs['const_per'][wrids] = total_hru_irr
                
            else:
                for i in range(0,len(self.hrus_areas[wrids+1])):
    
                    irr_amt = (indv_hru_irr[i]/100.)*wr_vol
                    
                    crop_yield = np.interp(irr_amt, self.w_crops[:,0], self.w_crops[:,self.hrus_crops[wrids+1][i]]) 
                    cost_f = np.interp(irr_amt, range(0,101), self.cost_fert[:,discrete_inputs['hru_fert'][indv_hru_irr_ids[i]]])*self.hrus_areas[wrids+1][i]

                
                    per_yield = ((self.p_crops_e[discrete_inputs['hru_fert'][i]]*(irr_amt**2))+(self.p_crops_be[discrete_inputs['hru_fert'][i]]*irr_amt))/self.p_crops_de[discrete_inputs['hru_fert'][i]]
                
                    profit = crop_yield*per_yield*self.hrus_areas[wrids+1][i]*self.crops_price[self.hrus_crops[wrids+1][i]-1] - cost_f # profit function        
                    
                    envir = ((irr_amt**self.f_envr_a[discrete_inputs['hru_fert'][i]])/self.f_envr_b[discrete_inputs['hru_fert'][i]])*self.f_envr_N[discrete_inputs['hru_fert'][i]]*self.hrus_areas[wrids+1][i]
        
                    indv_profit = indv_profit + profit
                    indv_costs = indv_costs + cost_f
                    indv_envir  = indv_envir + envir 
                    
                    #outputs['indv_crops_yields'][self.hrus_crops[i]-1] = outputs['indv_crops_yields'][self.hrus_crops[i]-1] + crop_yield*per_yield*self.hrus_areas[i]
                
                outputs['indv_envir'] = indv_envir
                outputs['indv_profit'][wrids] = indv_profit    
                #outputs['indv_costs'][wrids] = indv_costs
                outputs['const_per'][wrids] = total_hru_irr
                
                
                
                if str(wr_vol) not in actors_solutions['farmer_' + str(wrids+1)].keys():
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)] = dict()
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['profit'] = []
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['envir'] = []
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['profit'].append(indv_profit)
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['envir'].append(indv_envir)
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['hru_irr'] = list(np.asarray(indv_hru_irr).astype(float))
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['hru_fert'] = list(np.asarray(discrete_inputs['hru_fert'][indv_hru_irr_ids]).astype(float))
                else:
                    
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['profit'].append(indv_profit)
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['envir'].append(indv_envir)
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['hru_irr'].append(list(np.asarray(indv_hru_irr).astype(float)))
                    actors_solutions['farmer_' + str(wrids+1)][str(wr_vol)]['hru_fert'].append(list(np.asarray(discrete_inputs['hru_fert'][indv_hru_irr_ids]).astype(float)))
                    
                
                with open(self.json_file + str(wrids+1) +'_sharewr.json', 'w') as fp:
                    json.dump(actors_solutions, fp)
                    
        total_profit = 0
        total_envir = 0
        for i in range(0,len(inputs['wr_vols'])):
            total_profit = total_profit + outputs['indv_profit'][i]
            total_envir = total_envir + outputs['indv_envir'][i]
                
        outputs['profit'] = total_profit
        outputs['envir_impact'] = total_envir
        outputs['total_wr'] = sum(inputs['wr_vols'])
        
        #print(inputs['wr_vols'], '[' + str(sum(inputs['wr_vols'])) + ']', outputs['const_per'], outputs['profit'], outputs['envir_impact'])
        print('[' + str(sum(inputs['wr_vols'])) + ']', outputs['const_per'], outputs['profit'], outputs['envir_impact'])

#######################################################################################################

# class Total_WR(om.ExplicitComponent):
    
#     def initialize(self):
#         self.nactors = 1
        
#     def setup(self):
#         self.add_input('wr_vols',val=np.ones(self.nactors))
#         self.add_output('total_wr', val=0)
        
#     def compute(self, inputs, outputs):
#         # print(inputs['wr_vols'], sum(inputs['wr_vols']))
#         outputs['total_wr'] = sum(inputs['wr_vols'])