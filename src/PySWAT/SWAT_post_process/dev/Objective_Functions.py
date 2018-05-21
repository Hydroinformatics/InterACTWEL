import numpy as np
from openmdao.api import ExplicitComponent

class Fitness_Function(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('SWAT')
        self.metadata.declare('Problem')
        
    def setup(self):
#        self.optproblem_data = OptProblem
#        self.swatmodel = SWATmodel
        # Inputs
        self.add_input('x0', 0.0)
        self.add_input('x1', 0.0)
        #self.add_input('x2', 0.0)
        #self.add_input('x3', 0.0)
        #self.output_data = self.objectives_data
        # Outputs
        self.add_output('f', val=0.0)
        
        #self.o
        
    def compute(self, inputs, outputs):
        """
        Define the function f(xI, xC).

        When Branin is used in a mixed integer problem, x0 is integer and x1 is continuous.
        """
        x0 = inputs['x0']
        x1 = inputs['x1']
        optproblem = self.metadata['Problem']
        data = optproblem.objectives_data
        outputs['f'] = x1*x0

    def Get_fitness_region(problem,SWAT,output_data):
        fitness = dict()
        temp_years = np.asarray(SWAT.timeseries['YEAR'])
        temp_mon = np.asarray(SWAT.timeseries['MONTH'])
        
        for obj_id in problem.objectives.keys():
            for var_key in problem.objectives[obj_id]['BVAR']:
                temp = []
                var = problem.objectives[obj_id]['BVAR'][var_key]
                
                for levels in problem.objectives[obj_id]['LEVEL']:
    
                    if problem.objectives[obj_id]['LEVEL'][levels].lower() == 'region':
                        
                        for years in np.unique(temp_years):
                            temp_fitness = 0.0
                            temp_base = 0.0
                            for hru_key in problem.objectives_data[var].keys():
                                temp_data_base = np.asarray(problem.objectives_data[var][hru_key])
                                temp_data_out = np.asarray(output_data[var][hru_key])
                                id_year = np.where(temp_years == years)
                                if 'yld' in var.lower():
                                    temp_fitness = temp_fitness + np.sum(temp_data_out[id_year])
                                    temp_base = temp_base + np.sum(temp_data_base[id_year])
                                        
                                elif 'st' in var.lower():
                                     temp_fitness = temp_fitness + temp_data_out[id_year[0][-1]]
                                     temp_base = temp_base + temp_data_base[id_year[0][-1]]
                                    
                            temp.append(temp_fitness - temp_base)
                            
                        fitness[var] = np.dot(temp,(max(np.unique(temp_years))+1)/np.arange(max(np.unique(temp_years))+1,0,-1))
                
        return fitness
    
    
    
    def Get_fitness_sub(problem,SWAT,output_data,input_sub):
        fitness = dict()
        temp_years = np.asarray(SWAT.timeseries['YEAR'])
        temp_mon = np.asarray(SWAT.timeseries['MONTH'])
        
        for obj_id in problem.objectives.keys():
            for var_key in problem.objectives[obj_id]['BVAR']:
                temp = []
                var = problem.objectives[obj_id]['BVAR'][var_key]
                
                for levels in problem.objectives[obj_id]['LEVEL']:
    
                    if problem.objectives[obj_id]['LEVEL'][levels].lower() == 'sub':
                        
                        hru_keys = [sub_hru for sub_hru in SWAT.HRUs if SWAT.HRUs[sub_hru]['SUB'] == input_sub and sub_hru in problem.objectives_data[var].keys()]
                        
                        for years in np.unique(temp_years):
                            temp_fitness = 0.0
                            temp_base = 0.0
                            for hru_key in hru_keys:
                                temp_data_base = np.asarray(problem.objectives_data[var][hru_key])
                                temp_data_out = np.asarray(output_data[var][hru_key])
                                id_year = np.where(temp_years == years)
                                if 'yld' in var.lower():
                                    temp_fitness = temp_fitness + np.sum(temp_data_out[id_year])
                                    temp_base = temp_base + np.sum(temp_data_base[id_year])
                                        
                                elif 'st' in var.lower():
                                     temp_fitness = temp_fitness + temp_data_out[id_year[0][-1]]
                                     temp_base = temp_base + temp_data_base[id_year[0][-1]]
                                    
                            temp.append(temp_fitness - temp_base)
                            
                        fitness[var] = np.dot(temp,(max(np.unique(temp_years))+1)/np.arange(max(np.unique(temp_years))+1,0,-1))
                
        return fitness
    
    
    def Get_fitness_hru(problem,SWAT,output_data,input_hru):
        fitness = dict()
        temp_years = np.asarray(SWAT.timeseries['YEAR'])
        temp_mon = np.asarray(SWAT.timeseries['MONTH'])
        
        for obj_id in problem.objectives.keys():
            for var_key in problem.objectives[obj_id]['BVAR']:
                temp = []
                var = problem.objectives[obj_id]['BVAR'][var_key]
                
                for levels in problem.objectives[obj_id]['LEVEL']:
    
                    if problem.objectives[obj_id]['LEVEL'][levels].lower() == 'hru':
                        
                        #hru_keys = [sub_hru for sub_hru in SWAT.HRUs if SWAT.HRUs[sub_hru]['SUB'] == input_sub and sub_hru in problem.objectives_data[var].keys()]
                        
                        for years in np.unique(temp_years):
                            temp_fitness = 0.0
                            temp_base = 0.0
    
                            temp_data_base = np.asarray(problem.objectives_data[var][str(input_hru)])
                            temp_data_out = np.asarray(output_data[var][str(input_hru)])
                            id_year = np.where(temp_years == years)
                            if 'yld' in var.lower():
                                temp_fitness = temp_fitness + np.sum(temp_data_out[id_year])
                                temp_base = temp_base + np.sum(temp_data_base[id_year])
                                        
                            elif 'st' in var.lower():
                                temp_fitness = temp_fitness + temp_data_out[id_year[0][-1]]
                                temp_base = temp_base + temp_data_base[id_year[0][-1]]
                                    
                            temp.append(temp_fitness - temp_base)
                            
                        fitness[var] = np.dot(temp,(max(np.unique(temp_years))+1)/np.arange(max(np.unique(temp_years))+1,0,-1))
                
        return fitness