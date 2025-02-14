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
import pandas as pd
#from sklearn.neighbors import KNeighborsRegressor
import FEW_SWAT_utils as swat_utils
    
#%%

class FEWNexus(om.Group):
    
    def initialize(self):
        self.nactors = 1
        self.wrs_hrus = []
        self.org_wr_vols = []
        self.json_file = None
        self.org_yield = []
        self.wrs_map_key = []
        self.org_wr_data = []
        self.max_wrid = []
        self.swat_paths = []
        self.swat_exec = None

    
    def setup(self):
        
        des_vars = self.add_subsystem('wr_vols', om.IndepVarComp(), promotes=['*'])
    
        init_wr_vols = []
        with open("demofile.txt", "w") as f:
            for i in self.org_wr_vols.keys():
                init_wr_vols.append(np.floor(self.org_wr_vols[i]))
                f.write(str(i) + ' ' + str(int(np.floor(self.org_wr_vols[i]))) + '\n')
        
        f.close()
        
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
            exec("self."+"farmer_"+str(i+1)+"_plan.org_yield = " + str(self.org_yield[i+1]))
            exec("self."+"farmer_"+str(i+1)+"_plan.wrs_hrus = " + str(self.wrs_hrus[i+1]))
            exec("self."+"farmer_"+str(i+1)+"_plan.json_file = self.json_file")
            
            exec("self."+"farmer_"+str(i+1)+"_plan.org_wr_data = " + str(self.org_wr_data[i+1].values.tolist()[0]))
            exec("self."+"farmer_"+str(i+1)+"_plan.max_wrid = " + str(self.max_wrid))
            exec("self."+"farmer_"+str(i+1)+"_plan.org_wrid = " + str(self.wrs_map_key[i+1]))
            
            exec("self."+"farmer_"+str(i+1)+"_plan.swat_paths = self.swat_paths")
            exec("self."+"farmer_"+str(i+1)+"_plan.swat_exec = self.swat_exec")
            
            actors_solutions['farmer_' + str(i+1)] = dict()
            
            with open(self.json_file + str(i+1) +'_sharewr.json', 'w') as fp:
                json.dump(actors_solutions, fp)
        
   ############ SETUP of REGIONS ###############
            
        region_model = self.add_subsystem('region', Region(), promotes=['profit'])
        region_model.nactors = self.nactors
        region_model.wrs_hrus = self.wrs_hrus
        region_model.max_wrid = self.max_wrid
        region_model.org_wr_data = self.org_wr_data
        region_model.swat_paths = self.swat_paths
        region_model.wrs_map_key = self.wrs_map_key
        
        self.connect('wr_vols','region.wr_vols')
        
        for i in range(0,self.nactors):
            self.connect('farmer_' + str(i+1) + '_plan.indv_profit', 'region.actor_profit_' + str(i+1))
            self.connect('farmer_' + str(i+1) + '_plan.opt_hru_irr', 'region.actor_opt_hru_irr_' + str(i+1))
            
            
############################################# SUB-SYSTEM ######################################

class Total_WR(om.ExplicitComponent):
    
    def initialize(self):
        self.nactors = 1
        
    def setup(self):
        self.add_input('wr_vols',val=np.ones(self.nactors))
        self.add_output('total_wr', val=0)
        
    def compute(self, inputs, outputs):
        outputs['total_wr'] = sum(inputs['wr_vols'])

        
############################################# SUB-SYSTEM ######################################

class Region(om.ExplicitComponent):
    
    def initialize(self):
        self.nactors = 1
        self.wrs_hrus = []
        self.max_wrid = None
        self.org_wr_data = None
        self.swat_paths = []
        self.wrs_map_key = []
        
    def setup(self):
        
        self.add_input('wr_vols',val=np.ones(self.nactors))
        for i in range(0,self.nactors):
            self.add_input('actor_profit_'+ str(i+1),val=0.0)
            self.add_input('actor_opt_hru_irr_'+ str(i+1),val=np.ones(len(self.wrs_hrus[i+1])))
        
        self.add_output('profit', val=0.0)

    
    def setup_partials(self):
        self.declare_partials('profit', 'wr_vols*', method='fd')
        
        
    def compute(self, inputs, outputs):
        
        new_hru_wr = dict()
        #hrulist = []
        #cc = 0
        for i in range(0,len(inputs['wr_vols'])):
            temp_wr_vol = inputs['wr_vols'][i]
            
            for ii in range(0,len(inputs['actor_opt_hru_irr_'+ str(i+1)])):
                #new_hru_wr[cc] = dict()
                #new_hru_wr[cc]['hruid'] = self.wrs_hrus[i+1][ii]
                #new_hru_wr[cc]['new_wrvol'] = (inputs['actor_opt_hru_irr_'+ str(i+1)][ii]/100.0)*temp_wr_vol
                new_hru_wr[self.wrs_hrus[i+1][ii]] = dict()
                new_hru_wr[self.wrs_hrus[i+1][ii]]['new_wrvol'] = (inputs['actor_opt_hru_irr_'+ str(i+1)][ii]/100.0)*temp_wr_vol
                
                #cc = cc + 1
        
        
        org_file_path = self.swat_paths[0] + '/wrdata.dat'
        new_file_path = self.swat_paths[1] + '/wrdata.dat'

        file_org = open(org_file_path, 'r')
        Lines = file_org.readlines()

        filein = open(new_file_path,'w')

        new_temp_wrs_ids = []

        for line in Lines:
            linesplit = line.split()
            if 'year' not in linesplit[0].lower():
                atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
                atxt = atxt + str(int(linesplit[1])).rjust(5) + ''.rjust(3)
                atxt = atxt + str(int(linesplit[2])).rjust(4) + ''.rjust(3)
                atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
                        
                atxt = atxt + str(int(linesplit[4])).rjust(4) + ''.rjust(3)
                atxt = atxt + str(int(linesplit[5])).rjust(4)
                filein.write(atxt + '\n') 
                
                if int(linesplit[1]) == self.max_wrid:
                    ii = 0
                    for hruid in new_hru_wr.keys():
                        new_temp_wrs_ids.append(int(self.max_wrid + ii + 1))
                        atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
                        atxt = atxt + str(int(self.max_wrid + ii + 1)).rjust(5) + ''.rjust(3)
                        
                        new_hru_wr[hruid]['new_wrid'] = int(self.max_wrid + ii + 1)
                        temp_org_wr_data = self.org_wr_data[ii+1].values.tolist()[0]
                        
                        atxt = atxt + str(int(self.temp_org_wr_data[2])).rjust(4) + ''.rjust(3)
                        atxt = atxt + str(int(new_hru_wr[hruid]['new_wrvol'])).rjust(6) + ''.rjust(3)
                        atxt = atxt + str(int(self.temp_org_wr_data[4])).rjust(4) + ''.rjust(3)
                        atxt = atxt + str(int(self.temp_org_wr_data[5])).rjust(4)
                        filein.write(atxt + '\n') 
                        
                        ii = ii + 1
                        
            else:
                filein.write(line) 

        file_org.close()
        filein.close()
        
        
        hrwwr_dat_df = pd.read_table(self.swat_paths[0] + '/hruwr.dat', sep='\s+', header=None)
        new_temp_wrs_ids = np.asarray(new_temp_wrs_ids)

        new_file = self.swat_paths[1] + '/hruwr.dat'
        filein = open(new_file,'w')
        
        org_wrid = np.asarray(list(self.wrs_map_key.items()))[:,1]

        hrucounter = 0
        for i in range(len(hrwwr_dat_df)):
            
            if hrwwr_dat_df.loc[i][0] in new_hru_wr.keys() and hrwwr_dat_df.loc[i][1] in org_wrid:
                hruid = int(hrwwr_dat_df.loc[i][0])
                atxt = str(hrwwr_dat_df.loc[i][0]).rjust(6) + ''.rjust(3)
                atxt = atxt + str(new_hru_wr[hruid]['new_wrid']).rjust(6) + ''.rjust(3)
                atxt = atxt + str(hrwwr_dat_df.loc[i][2]).rjust(4) + ''.rjust(3)
                atxt = atxt + str(hrwwr_dat_df.loc[i][4]).rjust(4) + ''.rjust(3)
                atxt = atxt + str(hrwwr_dat_df.loc[i][3]).rjust(4)
                
                hrucounter += 1
                
            else:
                atxt = str(hrwwr_dat_df.loc[i][0]).rjust(6) + ''.rjust(3)
                atxt = atxt + str(hrwwr_dat_df.loc[i][1]).rjust(6) + ''.rjust(3)
                atxt = atxt + str(hrwwr_dat_df.loc[i][2]).rjust(4) + ''.rjust(3)
                atxt = atxt + str(hrwwr_dat_df.loc[i][4]).rjust(4) + ''.rjust(3)
                atxt = atxt + str(hrwwr_dat_df.loc[i][3]).rjust(4)

            filein.write(atxt + '\n') 
        filein.close()
        
        
        swat_utils.run_SWAT(self.swat_paths[1], self.swat_exec)

        hru_outputs = swat_utils.Get_hru_output(self.swat_paths[1])

        # Should consider only crops that we are concerned with.
        temp_total_yield = 0
        for hruid in new_hru_wr.keys():
            temp_total_yield = temp_total_yield  + np.sum(hru_outputs[hruid]['Total_Yield'])
       
        
        df = pd.read_table(self.swat_paths[1] + '/wrs_use.out', sep='\s+', header=0)
        wrs_use = list(df.loc[df['WRID'] == self.org_wrid]['WATER(acre-ft)']) 
        
                  
        outputs['profit'] = temp_total_yield
        
        print('Regional: ' + str(inputs['wr_vols']) + ', ' + str(sum(inputs['wr_vols'])) + ', [' + "{:,.2f}".format(temp_total_yield) + ']')
        
############################################# SUB-SYSTEM ACTOR ######################################   

class FarmerOpt(om.ExplicitComponent):
    
    def initialize(self):
        self.farmer_id = None
        self.wrs_hrus = []
        self.json_file = None
        self.org_yield = []
        self.org_wr_data = []
        self.max_wrid = []
        self.org_wrid = None
        self.swat_paths = []
        self.swat_exec = None
        
    ################################
    
    def setup(self):
        
        self.add_input('wr_vol', val = 1)
        self.add_output('indv_profit', val = 0.0)
        self.add_output('opt_hru_irr', val=np.ones(len(self.wrs_hrus)))
        
   ################# OPT SETUP ###################################     
            
        self.prob = p = om.Problem()

        des_vars = p.model.add_subsystem('des_vars', om.IndepVarComp(), promotes=['*'])
        iniper = np.floor(100.0/len(self.wrs_hrus))
        des_vars.add_output('hru_irr', val=np.ones(len(self.wrs_hrus))*iniper)
    
        p.model.add_subsystem('farmer', Farmer())

        p.model.farmer.farmer_id = self.farmer_id
        p.model.farmer.wrs_hrus = self.wrs_hrus
        p.model.farmer.org_wr_data = self.org_wr_data
        p.model.farmer.max_wrid = self.max_wrid
        p.model.farmer.org_wrid = self.org_wrid
        p.model.farmer.swat_paths = self.swat_paths
        p.model.farmer.swat_exec = self.swat_exec
        
        p.driver = om.SimpleGADriver()
        #p.driver.options['max_gen'] = 100
        p.driver.options['max_gen'] = 2
        p.driver.options['Pm'] =0.1
        # p.driver.options['pop_size'] = 50*len(self.wrs_hrus)
        p.driver.options['pop_size'] = 2
        p.driver.options['penalty_parameter'] = 2000.
        p.driver.options['penalty_exponent'] = 5.
        p.driver.options['compute_pareto'] = True
        
        p.model.connect('hru_irr','farmer.hru_irr')
        p.model.add_design_var('hru_irr', lower=0, upper=100)
        p.model.add_objective('farmer.indv_profit', scaler=-1)
        #p.model.add_constraint('farmer.const_per', lower=100, upper=100)
            
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
        
    
        
        # if os.path.exists(self.json_file + str(self.farmer_id) +'_sharewr.json'):
        
        #     with open(self.json_file + str(self.farmer_id) +'_sharewr.json') as json_file:
        #         actors_solutions = json.load(json_file)
        # else:
        #     actors_solutions = dict()
        
        # profit_bool = 0
        # envir_bool = 0
        
        # if 'farmer_' + str(self.farmer_id) in actors_solutions.keys():
        #     if str(inputs['wr_vol'][0]) in actors_solutions['farmer_' + str(self.farmer_id)].keys():
        #         profit_bool = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['stop_bool']
        #         envir_bool = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['stop_bool']
                
        
        # if profit_bool == 1 and envir_bool == 1:
            
        #     temp_indv_profit = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Value']
        #     temp_indv_envir = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Value']
        # else:
        
        p = self.prob

        #run the optimization 
        
        # if self.farmer_id > 1:
        #     p.model.farmer.hru_prior_irrvol = np.zeros(len(self.hrus_areas)).astype('int')
        
        
        p.run_driver()

        obj_nd = np.asarray(p.driver.obj_nd)
        des_var = np.asarray(p.driver.desvar_nd)
        
        # if len(obj_nd) > 1:
        #     obj_nd = obj_nd[np.where(abs(np.sum(obj_nd,axis=1)) > 0)[0],:]
        #     des_var = des_var[np.where(abs(np.sum(obj_nd,axis=1)) > 0)[0],:]
        
        # sorted_obj_profit = obj_nd[obj_nd[:, 0].argsort()]
        # profit_sort_index = np.argsort(obj_nd[:, 0])
        
        # temp_indv_profit = sorted_obj_profit[0][0]
        # #temp_indv_profit_envir = sorted_obj_profit[0][1]
        # temp_indv_profit_desvar = des_var[profit_sort_index[0],:]
        

            # if 'farmer_' + str(self.farmer_id) not in actors_solutions.keys():
            #     actors_solutions['farmer_' + str(self.farmer_id)] = dict()
            
            # if str(inputs['wr_vol'][0]) not in actors_solutions['farmer_' + str(self.farmer_id)].keys():
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]] = dict()
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit'] = dict()
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Value'] = temp_indv_profit
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Envir'] = temp_indv_profit_envir
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Vars'] = str(temp_indv_profit_desvar)
                
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Mean'] = np.mean(sorted_obj_profit[:,0])
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['Nsamples'] = len(sorted_obj_profit[:,0])
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['stop_bool'] = 0 
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['profit']['per_change'] = 0 
                
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir'] = dict()
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Value'] = temp_indv_envir
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Profit'] = temp_indv_envir_profit
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Vars'] = str(temp_indv_envir_desvar)
                
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Mean'] = np.mean(sorted_obj[:,0])
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['Nsamples'] = len(sorted_obj[:,0])
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['stop_bool'] = 0 
            #     actors_solutions['farmer_' + str(self.farmer_id)][inputs['wr_vol'][0]]['envir']['per_change'] = 0 
            
            # else:
                
            #     old_profit = float(actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Value'])
            #     old_envir = float(actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Value'])
                
            #     old_mean_profit  = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Mean']
            #     old_Nsample_profit = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Nsamples']
                
            #     old_mean_envir  = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Mean']
            #     old_Nsample_envir = actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Nsamples']
                
            #     if temp_indv_profit < old_profit:
            #         actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Value'] = temp_indv_profit
            #         actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Envir'] = temp_indv_profit_envir
            #         actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Vars'] = str(temp_indv_profit_desvar)
            #     else:
            #         temp_indv_profit = old_profit
                
                
            #     new_mean_profit = old_mean_profit             
            #     for xprofit in sorted_obj_profit[:,0]:
            #         old_Nsample_profit = old_Nsample_profit + 1
            #         new_mean_profit = new_mean_profit + ((xprofit - new_mean_profit)/old_Nsample_profit)
                    
            #     actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Mean'] = new_mean_profit
            #     actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['Nsamples'] = old_Nsample_profit
                
            #     per_change_profit = ((new_mean_profit - old_mean_profit)/old_mean_profit)*100
            #     actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['per_change'] = per_change_profit
                
            #     if per_change_profit < 5:
            #         actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['profit']['stop_bool'] = 1
                
            #     if temp_indv_envir < old_envir:
            #         actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Value'] = temp_indv_envir
            #         actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Profit'] = temp_indv_envir_profit
            #         actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Vars'] = str(temp_indv_envir_desvar)
            #     else:
            #         temp_indv_envir = old_envir
                    
            
            #     new_mean_envir = old_mean_envir            
            #     for xenvir in sorted_obj[:,0]:
            #         old_Nsample_envir = old_Nsample_envir + 1
            #         new_mean_envir = new_mean_envir + ((xenvir - new_mean_envir)/old_Nsample_envir)
                    
            #     actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Mean'] = new_mean_envir
            #     actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['Nsamples'] = old_Nsample_envir
                
            #     per_change_envir = ((new_mean_envir - old_mean_envir)/old_mean_envir)*100
            #     actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['per_change'] = per_change_envir
                
            #     if per_change_envir < 5:
            #         actors_solutions['farmer_' + str(self.farmer_id)][str(inputs['wr_vol'][0])]['envir']['stop_bool'] = 1
        
        # outputs['hru_prior_irrvol_OUT'] = p.get_val('farmer.hru_prior_irrvol_OUT')
        # outputs['indv_profit'] = temp_indv_profit
        # outputs['opt_hru_irr'] = temp_indv_profit_desvar
        
        outputs['indv_profit'] = obj_nd
        outputs['opt_hru_irr'] = des_var
        
        print('Farmer ' + str(self.farmer_id) + str(obj_nd))
        # with open(self.json_file + str(self.farmer_id) +'_sharewr.json', 'w') as fp:
        #     json.dump(actors_solutions, fp)

############################################# SUB-SYSTEM FARMER ######################################  

class Farmer(om.ExplicitComponent):
    
    def initialize(self):
        self.wrs_hrus = []
        self.farmer_id = []
        self.org_wr_data = []
        self.max_wrid = []
        self.org_wrid = None
        self.swat_paths = []
        self.swat_exec = None
        

    def setup(self):
        
        iniper = np.floor(100.0/len(self.wrs_hrus))
        self.add_input('hru_irr', val = np.ones(len(self.wrs_hrus))*iniper)
        self.add_output('indv_profit', val=0.0)
        #self.add_output('const_per', val=0.0)
        
    def setup_partials(self):
        self.declare_partials('indv_profit', 'hru_irr*', method='fd')
    
    def compute(self, inputs, outputs):
        
        with open("demofile.txt", "r") as f:
            for line in f:
                line = line.rstrip()
                if int(line.split()[0]) == self.farmer_id:
                    wr_vol = float(line.split()[1])
        f.close()
        
        indv_profit = 0

        if (sum(inputs['hru_irr']) - 100.0) > 0.:
            outputs['indv_profit'] = 0.
            # outputs['indv_envir'] = 500000000.
            # outputs['indv_crops_yields'] = np.zeros(len(self.crops_price))
            
        else:
            
            iter_wr_vol = []
            for i in range(0,len(self.wrs_hrus)):
                iter_wr_vol.append((inputs['hru_irr'][i]/100.)*wr_vol)
                
            iter_wr_vol = np.asarray(iter_wr_vol)
            
            org_file_path = self.swat_paths[0] + '/wrdata.dat'
            new_file_path = self.swat_paths[1] + '/wrdata.dat'

            file_org = open(org_file_path, 'r')
            Lines = file_org.readlines()

            filein = open(new_file_path,'w')

            new_temp_wrs_ids = []

            for line in Lines:
                linesplit = line.split()
                if 'year' not in linesplit[0].lower():
                    atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(int(linesplit[1])).rjust(5) + ''.rjust(3)
                    atxt = atxt + str(int(linesplit[2])).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(int(linesplit[3])).rjust(6) + ''.rjust(3)
                            
                    atxt = atxt + str(int(linesplit[4])).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(int(linesplit[5])).rjust(4)
                    filein.write(atxt + '\n') 
                    
                    if int(linesplit[1]) == self.max_wrid:
                        for ii in range(0,len(iter_wr_vol)):
                            new_temp_wrs_ids.append(int(self.max_wrid + ii + 1))
                            atxt = str(int(linesplit[0])).rjust(4) + ''.rjust(3)
                            atxt = atxt + str(int(self.max_wrid + ii + 1)).rjust(5) + ''.rjust(3)                            
                            atxt = atxt + str(int(self.org_wr_data[2])).rjust(4) + ''.rjust(3)
                            atxt = atxt + str(int(iter_wr_vol[ii])).rjust(6) + ''.rjust(3)
                            atxt = atxt + str(int(self.org_wr_data[4])).rjust(4) + ''.rjust(3)
                            atxt = atxt + str(int(self.org_wr_data[5])).rjust(4)
                            filein.write(atxt + '\n') 
                            
                else:
                    filein.write(line) 

            file_org.close()
            filein.close()
            
            
            hrwwr_dat_df = pd.read_table(self.swat_paths[0] + '/hruwr.dat', sep='\s+', header=None)
            new_temp_wrs_ids = np.asarray(new_temp_wrs_ids)

            new_file = self.swat_paths[1] + '/hruwr.dat'
            filein = open(new_file,'w')

            hrucounter = 0
            for i in range(len(hrwwr_dat_df)):
                
                if hrwwr_dat_df.loc[i][0] in self.wrs_hrus and self.org_wrid == hrwwr_dat_df.loc[i][1]:
                    
                    atxt = str(hrwwr_dat_df.loc[i][0]).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(new_temp_wrs_ids[hrucounter]).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(hrwwr_dat_df.loc[i][2]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(hrwwr_dat_df.loc[i][4]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(hrwwr_dat_df.loc[i][3]).rjust(4)
                    
                    hrucounter += 1
                    
                else:
                    atxt = str(hrwwr_dat_df.loc[i][0]).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(hrwwr_dat_df.loc[i][1]).rjust(6) + ''.rjust(3)
                    atxt = atxt + str(hrwwr_dat_df.loc[i][2]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(hrwwr_dat_df.loc[i][4]).rjust(4) + ''.rjust(3)
                    atxt = atxt + str(hrwwr_dat_df.loc[i][3]).rjust(4)

                filein.write(atxt + '\n') 
            filein.close()
            

            #swat_utils.run_SWAT(self.swat_paths[1], './' + self.swat_exec)

            hru_outputs = swat_utils.Get_hru_output(self.swat_paths[1])

            # Should consider only crops that we are concerned with.
            temp_total_yield = 0
            for hruid in self.wrs_hrus:
                temp_total_yield = temp_total_yield  + np.sum(hru_outputs[hruid]['Total_Yield'])

            indv_profit = temp_total_yield*np.random.randint(100)
            
            
        df = pd.read_table(self.swat_paths[1] + '/wrs_use.out', sep='\s+', header=0)
        wrs_use = list(df.loc[df['WRID'] == self.org_wrid]['WATER(acre-ft)']) 
        
        penalty = wr_vol*len(wrs_use) - sum(wrs_use)
        
        outputs['indv_profit'] = indv_profit - penalty
        #outputs['const_per'] = sum(inputs['hru_irr'])
            

#######################################################################################################