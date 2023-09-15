# -*- coding: utf-8 -*-
"""
Created on Thu May  5 10:29:22 2022

@author: riversam
"""
import numpy as np
import openmdao.api as om

#class Dummy_subbasin(om.ExplicitComponent):
class Farmer():
    
    def __init__(self):
    
    #def setup(self):
        #cost of pumping gw per actor
        self.gw_cost = [0.1,0.2,0.12,1.2,1]
        #cost of pumping sw per actor
        self.sw_cost = [1,.5,.2,0.1,0.05]
        
        #Parameters of fertilized application functions per crop
        self.p_crops_a = [-.3,-.1,-.05]
        self.p_crops_b = [4000,5000,3000]
        self.f_cost = [500,400,200]

        #Sale price per unit of yield for different crops
        self.crops_price = [200,500,100]
        self.cost_fert = self.calculate_cost_fert()
        
        # % Max. Yield of crops based on irrigation amount (Water consumption per crop)
        self.w_crops = np.asarray([[0,0,0,0],[10,0,0,0],[20,60,0,200],[30,180,80,300],
                        [40,250,150,310],[50,280,300,320],[60,400,450,330],
                        [70,420,500,340],[80,460,550,350],[100,500,600,360]])
        
        # Input parameters
        self.wr_id = None
        self.area = []
        # hru_wr_maps
        self.wr_data = []
        self.hru_wr_map  = []
        
        # # Inputs
        # self.add_input('x0', 0.0)
        # self.add_input('x1', 0.0)

        # # Outputs
        # self.add_output('f', val=0.0)
        
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
    
    ############################
    
    def compute(self, inputs, outputs):
        
        x = inputs['wr']
        
        irr_amt = 0.0
        for i in range(0,len(x)):
            irr_amt = irr_amt + (x[i]/100.0)*self.wr_data[2]
        
        #cost_f = np.interp(irr_amt, range(0,101), self.cost_fert[:,x])
        #crop_yield = np.interp(irr_amt, self.w_crops[:,0], self.w_crops[:,x]) 
        
        per_yield = 1 + (0.8*-np.exp(self.p_crops_a[0]*irr_amt))
        
        profit = crop_yield*per_yield*self.crops_price[x] - (x(1,i)*gw_cost(i) + x(2,i)*sw_cost(i)) - cost_f # profit function
        envir = (1 + (0.8*-np.exp(p_crops_a[x]*irr_amt)))*self.p_crops_b[x] % enviromental cost function
        
        return per_yield
                
        
        
        
        
        #         cost_f = interp1([0:100],cost(:,x(4,i)),WR); % cost of fertilizer
        #         yield = interp1(w_crops(:,1),w_crops(:,x(3,i)),WR); % Max. Yield of crop
        #         if yield == 0
        #             cost_f = 0;
        #         end
        #         per_yield = 1 + (0.8*-exp(p_crops_a(x(3,i))*WR)); % Perc. of Max yield
        #         profit(i,1) = yield*per_yield*crops_price(x(3,i)) - (x(1,i)*gw_cost(i) + x(2,i)*sw_cost(i)) - cost_f; % profit function
        #         envir(i,1) = (1 + (0.8*-exp(p_crops_a(x(4,i))*WR))).*p_crops_b(x(4,i)); % enviromental cost function
        #     else
        #         % Penalty multipliers if violation of constraints
        #         profit(i,1) = -1000000000;
        #         envir(i,1) =   1000000000;
        #     end
        # end
        
        # total_val = sum(profit) + sum(envir);
        # rj = 0.5;
        # fitness = rj*(sum(profit)/total_val)*-1 +  (sum(envir)/total_val)*(1-rj);
        
        
        # return prof, envf


