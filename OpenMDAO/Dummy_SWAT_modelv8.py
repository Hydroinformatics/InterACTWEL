# -*- coding: utf-8 -*-
"""
Created on Thu May  5 10:29:22 2022

@author: riversam
"""
import numpy as np
import openmdao.api as om
import shutil
import json
import time
import os
#from sklearn.neighbors import KNeighborsRegressor

class FEWNexus(om.Group):
    
    def initialize(self):
        self.nactors = 1
        self.hrus_areas = []
        self.hrus_crops = []
        self.wrs_hrus = []
        self.org_wr_vols = []
        self.json_file = None
        # self.share_wr_irrvol = []
        
    
    def setup(self):
        
        # hru_prior_irrvol = []
        
        # for wrids in self.wrs_hrus.keys():
        #     for hid in self.wrs_hrus[wrids]:
        #         hru_prior_irrvol.append(hid)
                
        # hru_prior_irrvol = np.zeros(len(np.unique(hru_prior_irrvol)),dtype=int)
        
        des_vars = self.add_subsystem('wr_vols', om.IndepVarComp(), promotes=['*'])
        
        init_wr_vols = []
        for i in self.org_wr_vols.keys():
            #init_wr_vols.append(np.floor(self.org_wr_vols[i][1]/len(self.hrus_areas[i])))
            init_wr_vols.append(np.floor(self.org_wr_vols[i][1]))
        
        des_vars.add_output('wr_vols', val = init_wr_vols)
        
        
        self.add_subsystem('total_wr_con', Total_WR(), promotes=['total_wr'])
        exec("self.total_wr_con.nactors = self.nactors")
        self.connect('wr_vols','total_wr_con.wr_vols')
        
  ############ SETUP of FARMERS ###############
        
        actors_solutions = dict()
        for i in range(0,self.nactors):
            self.add_subsystem('farmer_' + str(i+1) + '_plan', FarmerOpt())                
            self.connect('wr_vols','farmer_' + str(i+1) + '_plan.wr_vol', src_indices=[i])
            
            exec("self."+"farmer_"+str(i+1)+"_plan.farmer_id = " + str(i+1))
            exec("self."+"farmer_"+str(i+1)+"_plan.hrus_areas = " + str(self.hrus_areas[i+1]))
            exec("self."+"farmer_"+str(i+1)+"_plan.hrus_crops = " + str(self.hrus_crops[i+1]))
            exec("self."+"farmer_"+str(i+1)+"_plan.wrs_hrus = " + str(self.wrs_hrus[i+1]))
            exec("self."+"farmer_"+str(i+1)+"_plan.json_file = self.json_file")
            # exec("self."+"farmer_"+str(i+1)+"_plan.hru_prior_irrvol = " + str(list(hru_prior_irrvol)))
            
            actors_solutions['farmer_' + str(i+1)] = dict()
            
        
            with open(self.json_file + str(i+1) +'_sharewr.json', 'w') as fp:
                json.dump(actors_solutions, fp)
        
   ############ SETUP of REGIONS ###############
            
        region_model = self.add_subsystem('region', Region(), promotes=['profit','envir_impact'])
        region_model.nactors = self.nactors
        self.connect('wr_vols','region.wr_vols')
        
        for i in range(0,self.nactors):
            self.connect('farmer_' + str(i+1) + '_plan.indv_profit', 'region.actor_profit_' + str(i+1))
            self.connect('farmer_' + str(i+1) + '_plan.indv_envir', 'region.actor_envir_' + str(i+1))
            
        # # for i in range(1,self.nactors):
        # #     self.connect('farmer_' + str(i) + '_plan.hru_prior_irrvol_OUT', 'farmer_' + str(i+1) + '_plan.hru_prior_irrvol_IN')
            


############################################# SUB-SYSTEM ######################################

class Total_WR(om.ExplicitComponent):
    
    def initialize(self):
        self.nactors = 1
        
    def setup(self):
        self.add_input('wr_vols',val=np.ones(self.nactors))
        self.add_output('total_wr', val=0)
        
    def compute(self, inputs, outputs):
        # print(inputs['wr_vols'], sum(inputs['wr_vols']))
        outputs['total_wr'] = sum(inputs['wr_vols'])

        
############################################# SUB-SYSTEM ######################################

class Region(om.ExplicitComponent):
    
    def initialize(self):
        self.nactors = 1
        
    def setup(self):
        
        self.add_input('wr_vols',val=np.ones(self.nactors))
        for i in range(0,self.nactors):
            self.add_input('actor_profit_'+ str(i+1),val=0.0)
            self.add_input('actor_envir_'+ str(i+1),val=0.0)
        
        self.add_output('profit', val=0.0)
        self.add_output('envir_impact', val=0.0)
        #self.add_output('total_wr', val=0.0)
    
    def setup_partials(self):
        self.declare_partials('profit', 'wr_vols*', method='fd')
        
    def compute(self, inputs, outputs):
        
        total_profit = 0
        total_envir = 0
        for i in range(0,self.nactors):
            for ii in range(0,len(inputs['actor_profit_' + str(i+1)])):
                total_profit = total_profit + inputs['actor_profit_'+ str(i+1)]
                total_envir = total_envir + inputs['actor_envir_'+ str(i+1)]
                
        
        outputs['profit'] = total_profit
        outputs['envir_impact'] = total_envir
        
        #outputs['profit'] = sum(inputs['wr_vols'])
        #outputs['envir_impact'] = -1*sum(inputs['wr_vols'])/20
        #outputs['total_wr'] = sum(inputs['wr_vols'])
        
        print('Regional: ' + str(inputs['wr_vols']) + ', ' + str(sum(inputs['wr_vols'])) + ', [' + "{:,.2f}".format(total_profit[0]) 
              + '], [' + "{:,.2f}".format(total_envir[0]) + ']')
        
        
############################################# SUB-SYSTEM ACTOR ######################################   

class FarmerOpt(om.ExplicitComponent):
    
    def initialize(self):
        self.farmer_id = None
        self.wrs_hrus = []
        self.hrus_areas = []
        self.hrus_crops = []
        self.json_file = None
        # self.hru_prior_irrvol = []
        
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
        
        self.add_input('wr_vol', val = 1)
        # self.add_input('hru_prior_irrvol_IN', val = self.hru_prior_irrvol)
        
        self.add_output('indv_profit', val = 0.0)
        self.add_output('indv_envir', val = 0.0)
        # self.add_output('hru_prior_irrvol_OUT', val = self.hru_prior_irrvol)
        
   ################# OPT SETUP ###################################     
       
        # recorder = om.SqliteRecorder('farmer_' + str(self.farmer_id) + '.sql')
        
        self.prob = p = om.Problem()

        des_vars = p.model.add_subsystem('des_vars', om.IndepVarComp(), promotes=['*'])
        inper = np.floor(100.0/len(self.hrus_areas))
        des_vars.add_output('hru_irr', val=np.ones(len(self.hrus_areas))*inper)
        des_vars.add_discrete_output('hru_fert', val=np.zeros(len(self.hrus_areas)).astype('int'))
        
        p.model.add_subsystem('farmer', Farmer())
        # p.model.add_subsystem('con_cmp2', om.ExecComp('con2 = sum(hru_irr)'), promotes=['con2'])
        
        p.model.farmer.hrus_areas = self.hrus_areas
        p.model.farmer.hrus_crops = self.hrus_crops
        p.model.farmer.farmer_id = self.farmer_id
        # p.model.farmer.hru_prior_irrvol = self.hru_prior_irrvol
        p.model.farmer.wrs_hrus = self.wrs_hrus
        
        #Sale price per unit of yield for different crops
        p.model.farmer.crops_price = self.crops_price
        
        # % Max. Yield of crops based on irrigation amount (Water consumption per crop)
        p.model.farmer.w_crops = self.w_crops
    
        # #Parameters of fertilized application functions per crop
        p.model.farmer.p_crops_a = self.p_crops_a
        p.model.farmer.p_crops_b = self.p_crops_b
        p.model.farmer.p_crops_c = self.p_crops_c
        p.model.farmer.f_cost = self.f_cost
        
        p.model.farmer.p_crops_e = self.p_crops_e
        p.model.farmer.p_crops_be = self.p_crops_be
        p.model.farmer.p_crops_de = self.p_crops_de
        
        p.model.farmer.f_envr_a = self.f_envr_a
        p.model.farmer.f_envr_b = self.f_envr_b
        p.model.farmer.f_envr_N = self.f_envr_N
        
        p.model.farmer.cost_fert = self.cost_fert
        
        # p.add_recorder(recorder)
        
        p.driver = om.SimpleGADriver()
        p.driver.options['max_gen'] = 100
        p.driver.options['Pm'] =0.1
        #p.driver.options['pop_size'] = 50
        p.driver.options['pop_size'] = 50*len(self.hrus_areas)
        p.driver.options['penalty_parameter'] = 2000.
        p.driver.options['penalty_exponent'] = 5.
        p.driver.options['compute_pareto'] = True
        
        p.model.connect('hru_irr','farmer.hru_irr')
        p.model.connect('hru_fert','farmer.hru_fert')
        
        # p.model.connect('hru_prior_irrvol_IN','farmer.hru_prior_irrvol_IN')
        # p.model.connect('hru_prior_irrvol_OUT','farmer.hru_prior_irrvol_OUT')
        
        p.model.add_design_var('hru_irr', lower=0, upper=100)
        p.model.add_design_var('hru_fert', lower=0, upper=2)
        
        p.model.add_objective('farmer.indv_profit', scaler=-1)
        p.model.add_objective('farmer.indv_envir', scaler=1)
        
        p.model.add_constraint('farmer.const_per', lower=100, upper=100)
        
        # p.driver.add_recorder(recorder)
        
        p.setup()
        p.final_setup()
  
  ################# END OF OPT SETUP ###################################   
    
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
        
        
        if os.path.exists(self.json_file + str(self.farmer_id) +'_sharewr.json'):
        
            with open(self.json_file + str(self.farmer_id) +'_sharewr.json') as json_file:
                actors_solutions = json.load(json_file)
        else:
            actors_solutions = dict()
        
        profit_bool = 0
        envir_bool = 0
        
        if 'farmer_' + str(self.farmer_id) in actors_solutions.keys():
            if str(inputs['wr_vol'][0]) in actors_solutions['farmer_' + str(self.farmer_id)].keys():
                profit_bool = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['stop_bool']
                envir_bool = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['stop_bool']
                
        
        if profit_bool == 1 and envir_bool == 1:
            
            temp_indv_profit = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Value']
            temp_indv_envir = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Value']
        else:
        
            p = self.prob
    
            #run the optimization 
            
            # if self.farmer_id > 1:
            #     p.model.farmer.hru_prior_irrvol = np.zeros(len(self.hrus_areas)).astype('int')
            
            
            p.run_driver()
    
            obj_nd = np.asarray(p.driver.obj_nd)
            des_var = np.asarray(p.driver.desvar_nd)
            
            if len(obj_nd) > 1:
                obj_nd = obj_nd[np.where(abs(np.sum(obj_nd,axis=1)) > 0)[0],:]
                des_var = des_var[np.where(abs(np.sum(obj_nd,axis=1)) > 0)[0],:]
            
            sorted_obj_profit = obj_nd[obj_nd[:, 0].argsort()]
            profit_sort_index = np.argsort(obj_nd[:, 0])
            
            temp_indv_profit = sorted_obj_profit[0][0]
            temp_indv_profit_envir = sorted_obj_profit[0][1]
            temp_indv_profit_desvar = des_var[profit_sort_index[0],:]
            
            sorted_obj = obj_nd[obj_nd[:, 1].argsort()]
            envir_sort_index = np.argsort(obj_nd[:, 1])
            
            temp_indv_envir = sorted_obj[0][1]
            temp_indv_envir_profit = sorted_obj[0][0]
            temp_indv_envir_desvar = des_var[envir_sort_index[0],:]
            
       
            if 'farmer_' + str(self.farmer_id) not in actors_solutions.keys():
                actors_solutions['farmer_' + str(self.farmer_id)] = dict()
            
            if str(inputs['wr_vol'][0]) not in actors_solutions['farmer_' + str(self.farmer_id)].keys():
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]] = dict()
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit'] = dict()
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Value'] = temp_indv_profit
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Envir'] = temp_indv_profit_envir
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Vars'] = str(temp_indv_profit_desvar)
                
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Mean'] = np.mean(sorted_obj_profit[:,0])
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Nsamples'] = len(sorted_obj_profit[:,0])
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['stop_bool'] = 0 
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['per_change'] = 0 
                
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir'] = dict()
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Value'] = temp_indv_envir
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Profit'] = temp_indv_envir_profit
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Vars'] = str(temp_indv_envir_desvar)
                
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Mean'] = np.mean(sorted_obj[:,0])
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Nsamples'] = len(sorted_obj[:,0])
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['stop_bool'] = 0 
                actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['per_change'] = 0 
            
            else:
                
                old_profit = float(actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Value'])
                old_envir = float(actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Value'])
                
                old_mean_profit  = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Mean']
                old_Nsample_profit = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Nsamples']
                
                old_mean_envir  = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Mean']
                old_Nsample_envir = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Nsamples']
                
                if temp_indv_profit < old_profit:
                    actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Value'] = temp_indv_profit
                    actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Envir'] = temp_indv_profit_envir
                    actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Vars'] = str(temp_indv_profit_desvar)
                else:
                    temp_indv_profit = old_profit
                
                
                new_mean_profit = old_mean_profit             
                for xprofit in sorted_obj_profit[:,0]:
                    old_Nsample_profit = old_Nsample_profit + 1
                    new_mean_profit = new_mean_profit + ((xprofit - new_mean_profit)/old_Nsample_profit)
                    
                actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Mean'] = new_mean_profit
                actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Nsamples'] = old_Nsample_profit
                
                per_change_profit = ((new_mean_profit - old_mean_profit)/old_mean_profit)*100
                actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['per_change'] = per_change_profit
                
                if per_change_profit < 5:
                    actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['stop_bool'] = 1
                
                if temp_indv_envir < old_envir:
                    actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Value'] = temp_indv_envir
                    actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Profit'] = temp_indv_envir_profit
                    actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Vars'] = str(temp_indv_envir_desvar)
                else:
                    temp_indv_envir = old_envir
                    
            
                new_mean_envir = old_mean_envir            
                for xenvir in sorted_obj[:,0]:
                    old_Nsample_envir = old_Nsample_envir + 1
                    new_mean_envir = new_mean_envir + ((xenvir - new_mean_envir)/old_Nsample_envir)
                    
                actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Mean'] = new_mean_envir
                actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Nsamples'] = old_Nsample_envir
                
                per_change_envir = ((new_mean_envir - old_mean_envir)/old_mean_envir)*100
                actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['per_change'] = per_change_envir
                
                if per_change_envir < 5:
                    actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['stop_bool'] = 1
        
        # outputs['hru_prior_irrvol_OUT'] = p.get_val('farmer.hru_prior_irrvol_OUT')
        outputs['indv_profit'] = temp_indv_profit
        outputs['indv_envir'] = temp_indv_envir
        

        with open(self.json_file + str(self.farmer_id) +'_sharewr.json', 'w') as fp:
            json.dump(actors_solutions, fp)
        

############################################# SUB-SYSTEM FARMER ######################################  

class Farmer(om.ExplicitComponent):
    
    def initialize(self):
        self.wrs_hrus = []
        self.hrus_areas = []
        self.hrus_crops = []
        self.farmer_id = []
        # self.hru_prior_irrvol = []
        
        #Sale price per unit of yield for different crops
        self.crops_price = []
        
        # % Max. Yield of crops based on irrigation amount (Water consumption per crop)
        self.w_crops = []
    
        # #Parameters of fertilized application functions per crop
        self.p_crops_a = []
        self.p_crops_b = []
        self.p_crops_c = []
        self.f_cost = []
        
        self.p_crops_e = []
        self.p_crops_be = []
        self.p_crops_de = []
        
        self.f_envr_a = []
        self.f_envr_b = []
        self.f_envr_N = []
        
        self.cost_fert = []
    
    def setup(self):
        
        #self.add_input('wr_vol', val=0.0)
        inper = np.floor(100.0/len(self.hrus_areas))
        self.add_input('hru_irr', val = np.ones(len(self.hrus_areas))*inper)
        self.add_discrete_input('hru_fert', val = np.zeros(len(self.hrus_areas)).astype('int'))
        # self.add_input('hru_prior_irrvol_IN', val = self.hru_prior_irrvol)

        self.add_output('indv_profit', val=0.0)
        self.add_output('indv_costs', val=0.0)
        self.add_output('indv_envir', val=0.0)
        self.add_output('const_per', val=0.0)
        self.add_output('indv_crops_yields', val = np.zeros(len(self.crops_price)))
        # self.add_output('hru_prior_irrvol_OUT', val = self.hru_prior_irrvol)
        
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
        indv_envir = 0
        indv_costs = 0
        

        if (sum(inputs['hru_irr']) - 100.0) > 0.:
            #outputs['indv_profit'] = - 5000000000
            outputs['indv_profit'] = 0.
            outputs['indv_costs'] = 0.
            #outputs['indv_envir'] = float('inf') 
            outputs['indv_envir'] = 500000000.
            outputs['indv_crops_yields'] = np.zeros(len(self.crops_price))
            
            #outputs['total_irr'] = total_irr
            #outputs['indv_profit'] = - abs((sum(inputs['hru_irr']) - 100.0))*100000000
        else:
                
            for i in range(0,len(self.hrus_areas)):
                
                irr_amt = ((inputs['hru_irr'][i]/100.)*wr_vol)

                # indv_irr_amt = ((inputs['hru_irr'][i]/100.)*wr_vol)
                # irr_amt = indv_irr_amt + inputs['hru_prior_irrvol_IN'][self.wrs_hrus[i]-1]
                
                crop_yield = np.interp(irr_amt, self.w_crops[:,0], self.w_crops[:,self.hrus_crops[i]]) 
                cost_f = np.interp(irr_amt, range(0,101), self.cost_fert[:,discrete_inputs['hru_fert'][i]])*self.hrus_areas[i]
            
                per_yield = ((self.p_crops_e[discrete_inputs['hru_fert'][i]]*(irr_amt**2))+(self.p_crops_be[discrete_inputs['hru_fert'][i]]*irr_amt))/self.p_crops_de[discrete_inputs['hru_fert'][i]]
            
                profit = crop_yield*per_yield*self.hrus_areas[i]*self.crops_price[self.hrus_crops[i]-1] - cost_f # profit function        
                
                envir = ((irr_amt**self.f_envr_a[discrete_inputs['hru_fert'][i]])/self.f_envr_b[discrete_inputs['hru_fert'][i]])*self.f_envr_N[discrete_inputs['hru_fert'][i]]*self.hrus_areas[i]
    
                indv_profit = indv_profit + profit
                indv_costs = indv_costs + cost_f
                indv_envir  = indv_envir + envir 
                
                # outputs['hru_prior_irrvol_OUT'][self.wrs_hrus[i]-1] = irr_amt
                outputs['indv_crops_yields'][self.hrus_crops[i]-1] = outputs['indv_crops_yields'][self.hrus_crops[i]-1] + crop_yield*per_yield*self.hrus_areas[i]
        

        outputs['indv_envir'] = indv_envir
        outputs['indv_profit'] = indv_profit    
        outputs['indv_costs'] = indv_costs
        outputs['const_per'] = sum(inputs['hru_irr'])
            
        #print('OPT_Farmer_' + str(self.farmer_id) + ': ' + str(wr_vol) + ', ' + str(inputs['hru_irr']) + ', ' + str(outputs['indv_profit']))

#######################################################################################################