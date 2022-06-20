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
        
        self.hrus_areas = {1:[20,40],2:[15,10,30],3:[20,25,5]}
        self.hrus_crops = {1:[2,1],2:[1,1,3],3:[2,2,3]}
        self.nactors = 1
        
        self.hru_wrs = {1:[1,50], 2:[3,50], 3:[1,20], 4:[1,20]}
    
    def setup(self):
        
        des_vars = self.add_subsystem('wr_vols', om.IndepVarComp(), promotes=['*'])
        des_vars.add_output('wr_vols', val=np.ones(self.nactors)*20)
        
        ######## SETUP of FARMERS ###############
    
        for i in range(0,self.nactors):
            self.add_subsystem('farmer_' + str(i+1) + '_plan', FarmerOpt())                
            self.connect('wr_vols','farmer_' + str(i+1) + '_plan.wr_vol', src_indices=[i])
            
            exec("self."+"farmer_"+str(i+1)+"_plan.farmer_id =" + str(i+1))
            #exec("self."+"farmer_"+str(i+1)+"_plan.hrus = [10,20]")
            exec("self."+"farmer_"+str(i+1)+"_plan.hrus_areas =" + str(self.hrus_areas[i+1]))
            exec("self."+"farmer_"+str(i+1)+"_plan.hrus_crops =" + str(self.hrus_crops[i+1]))
        
        ######## SETUP of REGIONS ###############
            
        region_model = self.add_subsystem('region', Region(), promotes=['profit'])
        region_model.nactors = self.nactors
        self.connect('wr_vols','region.wr_vols')
        
        for i in range(0,self.nactors):
            self.connect('farmer_' + str(i+1) + '_plan.indv_crops_yields','region.actor_crops_' + str(i+1))
            self.connect('farmer_' + str(i+1) + '_plan.indv_profit', 'region.actor_profit_' + str(i+1))
            self.connect('farmer_' + str(i+1) + '_plan.indv_costs', 'region.actor_costs_' + str(i+1))
            
        #self.connect('wr_vols','region.wr_vols')

        
############################################# SUB-SYSTEM ######################################

class Region(om.ExplicitComponent):
    
    def initialize(self):
        self.nactors = 1
        
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
        
        self.add_input('wr_vols',val=np.ones(self.nactors))
        for i in range(0,self.nactors):
            self.add_input('actor_crops_'+ str(i+1), val=np.zeros(3))
            self.add_input('actor_profit_'+ str(i+1),val=0.0)
            self.add_input('actor_costs_'+ str(i+1),val=0.0)
        
        self.add_output('profit', val=0.0)
        #self.add_output('actors_wr_vols',val=np.ones(self.nactors)*20)
        #self.add_output('enviro_region', val=0.0)
    
    def setup_partials(self):
        self.declare_partials('profit', 'wr_vols*', method='fd')
        
    def compute(self, inputs, outputs):
        
        total_profit = 0
        for i in range(0,self.nactors):
            for ii in range(0,len(inputs['actor_crops_' + str(i+1)])):
                total_profit = total_profit + inputs['actor_profit_'+ str(i+1)]
                
        outputs['profit'] = total_profit
        #outputs['actors_wr_vols'] = inputs['wr_vols']
        
############################################# SUB-SYSTEM ACTOR ######################################   

class FarmerOpt(om.ExplicitComponent):
    
    def initialize(self):
        self.farmer_id = None
        self.hrus_areas = []
        self.hrus_crops = []
    
    def setup(self):
        
        self.add_input('wr_vol', val = 1)
        #self.add_input('hru_irr', val=np.ones(2))
        
        self.add_output('indv_profit', val=0.0)
        self.add_output('indv_costs', val=0.0)
        #self.add_output('total_irr', val=0.0)
        self.add_output('indv_crops_yields', val=np.zeros(3))
        
        #self.declare_partials('indv_profit', ['wr_vol'], method='fd', step=1e-4, step_calc='abs')
        self.declare_partials('indv_crops_yields', ['wr_vol'], method='fd', step=1e-4, step_calc='abs')
        
        self.prob = p = om.Problem()
        
        #params = p.model.add_subsystem('params', om.IndepVarComp(), promotes=['*'])
        #params.add_output('wr_vol', val=1.)
        
        des_vars = p.model.add_subsystem('des_vars', om.IndepVarComp(), promotes=['*'])
        des_vars.add_output('hru_irr', val=np.ones(len(self.hrus_areas)))
        des_vars.add_discrete_output('hru_fert', val=np.zeros(len(self.hrus_areas)).astype('int'))
        
        p.model.add_subsystem('farmer', Farmer())
        #p.model.add_subsystem('con_cmp2', om.ExecComp('con2 = sum(hru_irr) - 100.0'), promotes=['con2'])
        
        p.model.farmer.hrus_areas = self.hrus_areas
        p.model.farmer.hrus_crops = self.hrus_crops
        p.model.farmer.farmer_id = self.farmer_id
    
        p.driver = om.SimpleGADriver()
        p.driver.options['max_gen'] = 10
        p.driver.options['pop_size'] = 1000
        p.driver.options['penalty_parameter'] = 200.
        p.driver.options['penalty_exponent'] = 5.
        p.driver.options['compute_pareto'] = True
        
        p.model.connect('hru_irr','farmer.hru_irr')
        p.model.connect('hru_fert','farmer.hru_fert')
        
        p.model.add_design_var('hru_irr', lower=0, upper=100)
        p.model.add_design_var('hru_fert', lower=0, upper=2)
        
        p.model.add_objective('farmer.indv_profit', scaler=-1)
        #p.model.add_constraint('con2', lower=-1., upper=1.)
        
        p.setup()
        p.final_setup()
    
    def compute(self, inputs, outputs):
        
        with open("temp.txt", "w") as ftemp:
        
            with open("demofile.txt", "r") as f:
                #Lines = [line.rstrip() for line in f]
                for line in f:
                    line = line.rstrip()
                    if int(line.split()[0]) == self.farmer_id:
                        ftemp.write(str(self.farmer_id) + ' ' + str(int(inputs['wr_vol'][0])) + '\n')
                    else:
                        ftemp.write(line + '\n')
        ftemp.close()
        
        f.close()
        shutil.copy("temp.txt","demofile.txt")
        
        p = self.prob

        #run the optimization 
        print('subopt ' + str(self.farmer_id) + ' wr_vol: ' + str(inputs['wr_vol']))
        p.run_driver()

        # pull the values back up into the output array
        #print(p.get_val('farmer.indv_profit'))
      
        outputs['indv_profit'] = p['farmer.indv_profit']
        outputs['indv_costs'] = p['farmer.indv_costs']
        #outputs['total_irr'] = p['farmer.total_irr']
        outputs['indv_crops_yields'] = p['farmer.indv_crops_yields']


############################################# SUB-SYSTEM FARMER ######################################  

class Farmer(om.ExplicitComponent):
    
    def initialize(self):

        self.hrus_areas = []
        self.hrus_crops = []
        self.farmer_id = []
        
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
        
        #self.add_input('wr_vol', val=0.0)
        self.add_input('hru_irr', val=np.ones(len(self.hrus_areas)))
        self.add_discrete_input('hru_fert', val=np.zeros(len(self.hrus_areas)).astype('int'))

        self.add_output('indv_profit', val=0.0)
        self.add_output('indv_costs', val=0.0)
        #self.add_output('total_irr', val=0.0)
        self.add_output('indv_crops_yields', val=np.zeros(len(self.crops_price)))
        
    def setup_partials(self):
        self.declare_partials('indv_profit', 'hru_irr*', method='fd')
        #self.declare_partials('indv_profit', 'hru_fert*', method='fd')
    
    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        
        with open("demofile.txt", "r") as f:
            for line in f:
                line = line.rstrip()
                if int(line.split()[0]) == self.farmer_id:
                    wr_vol = float(line.split()[1])
        f.close()
        
        indv_profit = 0
        indv_costs = 0
        #total_irr = 0

        if abs((sum(inputs['hru_irr']) - 100.0)) > 0.0:
            outputs['indv_profit'] = - 5000000000
            outputs['indv_costs'] = 0.
            outputs['indv_crops_yields'] = np.zeros(len(self.crops_price))
            
            #outputs['total_irr'] = total_irr
            #outputs['indv_profit'] = - abs((sum(inputs['hru_irr']) - 100.0))*100000000
        else:
            for i in range(0,len(self.hrus_areas)):

                irr_amt = (inputs['hru_irr'][i]/100.)*wr_vol
                crop_yield = np.interp(irr_amt, self.w_crops[:,0], self.w_crops[:,self.hrus_crops[i]]) 
                cost_f = np.interp(irr_amt, range(0,101), self.cost_fert[:,discrete_inputs['hru_fert'][i]])*self.hrus_areas[i]
            
                per_yield = 1 + (0.8*-np.exp(self.p_crops_a[self.hrus_crops[i]-1]*irr_amt))
                profit = crop_yield*per_yield*self.hrus_areas[i]*self.crops_price[self.hrus_crops[i]-1] - cost_f # profit function        

                indv_profit = indv_profit + profit
                indv_costs = indv_costs + cost_f
                #total_irr = total_irr + irr_amt
                
                outputs['indv_crops_yields'][self.hrus_crops[i]-1] = outputs['indv_crops_yields'][self.hrus_crops[i]-1] + crop_yield*per_yield*self.hrus_areas[i]
                
            outputs['indv_profit'] = indv_profit    
            outputs['indv_costs'] = indv_costs

#######################################################################################################