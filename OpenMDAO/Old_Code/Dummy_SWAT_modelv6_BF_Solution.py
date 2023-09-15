import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from itertools import product
from pareto import eps_sort
import json

class Farmer():
    
    def __init__(self):
        
        self.farmer_id = []
        self.hrus_areas = []
        self.hrus_crops = []
        
        #Sale price per unit of yield for different crops
        self.crops_price = [200,500,100]
        
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
        self.p_crops_a = [-.3,-.1,-.05]
        self.p_crops_b = [4000,3000,2500]
        self.p_crops_c = [0.014,0.018,0.016]
        self.f_cost = [500,400,200]
        
        self.p_crops_e = [-0.022, -0.03, -0.042]
        self.p_crops_be = [2.6, 3.8, 6]
        self.p_crops_de = [76.818, 120.33, 214.278]
        
        self.f_envr_a = [0.2,0.4,0.3]
        self.f_envr_b = [2.512,6.31,3.98]
        self.f_envr_N = [5000,4000,3000]
        
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
    

    def compute(self, wr_vol, hru_irr, hru_fert):
                
        indv_profit = 0
        indv_envir = 0
        indv_costs = 0

        # if (sum(inputs['hru_irr']) - 100.0) > 0.:
        #     #outputs['indv_profit'] = - 5000000000
        #     outputs['indv_profit'] = 0.
        #     outputs['indv_costs'] = 0.
        #     #outputs['indv_envir'] = float('inf') 
        #     outputs['indv_envir'] = 0.
        #     outputs['indv_crops_yields'] = np.zeros(len(self.crops_price))
            
        #     #outputs['total_irr'] = total_irr
        #     #outputs['indv_profit'] = - abs((sum(inputs['hru_irr']) - 100.0))*100000000
        # else:
        outputs = dict()
        temp_per_yield = []
        for i in range(0,len(self.hrus_areas)):

            irr_amt = (hru_irr[i]/100.)*wr_vol
            
            crop_yield = np.interp(irr_amt, self.w_crops[:,0], self.w_crops[:,self.hrus_crops[i]]) 
            cost_f = np.interp(irr_amt, range(0,101), self.cost_fert[:,hru_fert[i]])*self.hrus_areas[i]
        
            #per_yield = 1 + (0.8*-np.exp(self.p_crops_a[self.hrus_crops[i]-1]*irr_amt))
            per_yield = ((self.p_crops_e[hru_fert[i]]*(irr_amt**2))+(self.p_crops_be[hru_fert[i]]*irr_amt))/self.p_crops_de[hru_fert[i]]
            #temp_yield = ((self.p_crops_e[self.hrus_crops[i]-1]*(irr_amt**2))+(self.p_crops_be[self.hrus_crops[i]-1]*irr_amt))
            #per_yield = 
            
            tt_pp = crop_yield*per_yield*self.hrus_areas[i]*self.crops_price[self.hrus_crops[i]-1]
            profit = crop_yield*per_yield*self.hrus_areas[i]*self.crops_price[self.hrus_crops[i]-1] - cost_f # profit function        
            
            # envir = (1 + (0.8*-np.exp(self.p_crops_a[self.hrus_crops[i]-1]*irr_amt)))*self.p_crops_b[discrete_inputs['hru_fert'][i]]
            #envir = (1.8*np.exp(self.p_crops_c[self.hrus_crops[i]-1]*irr_amt))*self.p_crops_b[hru_fert[i]]
            
            envir = ((irr_amt**self.f_envr_a[hru_fert[i]])/self.f_envr_b[hru_fert[i]])*self.f_envr_N[hru_fert[i]]
            
            indv_profit = indv_profit + profit
            indv_costs = indv_costs + cost_f
            indv_envir  = indv_envir + envir 
            #total_irr = total_irr + irr_amt
            
            #outputs['indv_crops_yields'][self.hrus_crops[i]-1] = outputs['indv_crops_yields'][self.hrus_crops[i]-1] + crop_yield*per_yield*self.hrus_areas[i]
            temp_per_yield.append(per_yield)
            
        outputs['per_yield'] = temp_per_yield
        outputs['indv_envir'] = indv_envir
        outputs['indv_profit'] = indv_profit    
        outputs['indv_costs'] = indv_costs
        outputs['irr_per'] = hru_irr.tolist()
        outputs['fert_choice'] = hru_fert.tolist()
        
        return outputs
            
        #print('OPT_Farmer_' + str(self.farmer_id) + ': ' + str(wr_vol) + ', ' + str(inputs['hru_irr']) + ', ' + str(outputs['indv_profit']))

#######################################################################################################
#%%

        
hrus_areas = {1:[20,40],2:[15,10,30],3:[20,25,5]}
hrus_crops = {1:[2,1],2:[1,1,3],3:[2,2,3]}
hru_wrs = {1:[1,50], 2:[3,50], 3:[1,20], 4:[1,20]}

farmer = Farmer()
farmer.farmer_id = 2
farmer.hrus_areas = hrus_areas[farmer.farmer_id]
farmer.hrus_crops = hrus_crops[farmer.farmer_id]

# hru_irr_per = []
# for i in range(0,100,1):
#     hru_irr_per.append([i,100-i])
# hru_irr_per.append([100,0])

items = range(0,100,1)
hru_irr_per = []
for item in product(items, repeat=len(farmer.hrus_areas)):
    if np.sum(item) <= 100:
        hru_irr_per.append(item)
        
hru_irr_per = np.asarray(hru_irr_per)

# hru_fert = []
# for i in range(0,3):
#     for ii in range(0,3):
#         hru_fert.append([i,ii])
        
items = range(0,3)
hru_fert = []
for item in product(items, repeat=len(farmer.hrus_areas)):
        hru_fert.append(item)
        
hru_fert = np.asarray(hru_fert)


results = dict()
for wrvols in range(1,101,1):
    print(wrvols)
    results[wrvols] = dict()
    for i in range(0,len(hru_irr_per)):
        results[wrvols][i] = dict()
        for f in range(0,len(hru_fert)):
            results[wrvols][i][f] = farmer.compute(wrvols, hru_irr_per[i], hru_fert[f])


with open('Farmer_1_ALL_Solutions.json', 'w') as fp:
    json.dump(results, fp)
    
#%%
# #cmap = plt.cm.jet
# #cmaplist = [cmap(i) for i in range(len(results.keys()))]

# jet = cm = plt.get_cmap('jet')
# cNorm  = colors.Normalize(vmin=0, vmax=len(results.keys()))
# scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

# temp_res = []
# cc = 0
# for ii in [100]:
# #for ii in results.keys():
#     #plt.figure()
#     for iii in range(0,len(results[ii])):
#         colorVal = scalarMap.to_rgba(cc)
#         for f in range(0,len(hru_fert)):
#         #plt.scatter(results[ii][iii]['indv_profit']*-1, results[ii][iii]['indv_envir'], c=np.array([cmaplist[cc]]))
#             plt.scatter(results[ii][iii][f]['indv_profit'], results[ii][iii][f]['indv_envir'], color=np.asarray(colorVal))
#             temp_res.append([hru_irr_per[iii],hru_fert[f],results[ii][iii][f]['indv_profit'],results[ii][iii][f]['indv_envir']])
#     cc = cc + 1
#     plt.title('WVOL: ' + str(ii))
        
# #%%

# jet = cm = plt.get_cmap('jet')
# cNorm  = colors.Normalize(vmin=0, vmax=len(results.keys()))
# scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
# plt.figure()
# cc = 0
# for ii in results.keys():
#     #plt.figure()
#     for iii in range(0,len(results[ii])):
#         colorVal = scalarMap.to_rgba(cc)
#         for f in range(0,len(hru_fert)):
#         #plt.scatter(results[ii][iii]['indv_profit']*-1, results[ii][iii]['indv_envir'], c=np.array([cmaplist[cc]]))
#             plt.scatter(ii, results[ii][iii][f]['indv_envir'], color=np.asarray(colorVal))
            
#     cc = cc + 1
#     plt.title('WVOL: ' + str(ii))        
        
    
# #%%
# plt.figure()
# cc = 1
# for ii in [5,25,50,75,100]:
#     plt.subplot(2,3,cc)
#     for f in range(0,len(hru_fert)):
#         for oo in range(0,2):
#             temp = []
#             for iii in range(0,len(results[ii])):
#                 temp.append([ii*hru_irr_per[iii][oo]/100.0, results[ii][iii][f]['per_yield'][oo]])
            
#             temp = np.asarray(temp)
#             plt.plot(temp[:,0], temp[:,1],'-o')
#         plt.title('IRR AMT: ' + str(ii))
#     cc = cc + 1

#%%

temp_data = []
for i in results.keys():
    for ii in results[i].keys():
        for iii in results[i][ii].keys():
            temp_data.append([i,results[i][ii][iii]['indv_profit']*-1,results[i][ii][iii]['indv_envir']])

temp_data = np.asarray(temp_data)
plt.plot(temp_data[:,1]*-1, temp_data[:,2],'.')

ss = eps_sort(temp_data,[1,2])
ss = np.asarray(ss)
ss = ss[ss[:,1].argsort()]
plt.plot(ss[:,1]*-1, ss[:,2],'-o')


#%%
# plt.figure()
# cc = 1
# for ii in [25]:
# #for ii in [5,25,50,75,100]:
#     plt.subplot(2,3,cc)
#     for f in range(0,len(hru_fert)):

#         temp = []
#         for iii in range(0,len(results[ii])):
#             temp.append([ii*hru_irr_per[iii][0]/100.0, results[ii][iii][f]['indv_profit']])
#         temp = np.asarray(temp)
#         plt.scatter(temp[:,0], temp[:,1],cmap='jet')
        
#         plt.title('IRR AMT: ' + str(ii))
#     cc = cc + 1

 
#%%

# from mpl_toolkits import mplot3d
# import numpy as np
# import matplotlib.pyplot as plt

# # Define Function

# def function_z(x,y,c):
#     #return (((-0.042*(x**2))+(6*x)) + y**2)
#     if c == 1:
#         return ((-0.042*(y**2))+(6*y))+((-0.042*(x**2))+(6*x))
#     elif c == 2:
#         return ((-0.03*(y**2))+(3.8*y))+((-0.03*(x**2))+(3.8*x))
#     elif c == 3:
#         return ((-0.022*(y**2))+(2.6*y))+((-0.022*(x**2))+(2.6*x))

# # Define Data

# x_val = np.linspace(0, 100, 100)
# y_val = np.linspace(0, 100, 100)

# X, Y = np.meshgrid(x_val, y_val)

# # Create figure

# fig = plt.figure(figsize =(10,6))
# ax = plt.axes(projection='3d')

# # Create surface plot

# for c in [3]:
# #for c in [1,2,3]:
#     z = function_z(X, Y,c)
#     z = z/max(z.flatten())
#     ax.plot_surface(X, Y, z)

# # Display
# plt.xlabel('x')
# ax.set_xlim(100, 0) 
# plt.show()