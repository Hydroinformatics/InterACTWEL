
from Dummy_subbasins import Farmer
import matplotlib.pyplot as plt
import openmdao.api as om

 #cost of pumping gw per actor
gw_cost = {1:0.1,2:0.2} #,0.12,1.2,1]
 #cost of pumping sw per actor
sw_cost = {1:1,2:.5} #,.2,0.1,0.05]

wr_data ={1:[3,60],2:[1,25],3:[3,80],4:[1,40]}

hru_wr_map = {1:[1,2],2:[3,4,5],3:[3,6,12],4:[11],999:[7,8,9,10,13,14]}

nyears = 1


# farmer_1 = Dummy_subbasins.Farmer()
# farmer_1.wr_id = 1
# farmer_1.nyears = nyears
# farmer_1.area = [500,200]
# farmer_1.crop_seq = [1,3,1]

# farmer_1.wr_data = wr_data[farmer_1.wr_id]

# farmer_1.hru_wr_map  = hru_wr_map[farmer_1.wr_id]

# for hruid in farmer_1.hru_wr_map:
#     if farmer_1.wr_data[0] == 3:
#         farmer_1.gw_cost[hruid] = gw_cost[hruid]
#     elif farmer_1.wr_data[0] == 1: 
#         farmer_1.sw_cost[hruid] = sw_cost[hruid]


# farmer_1.nhrus = len(farmer_1.hru_wr_map)

# var_names = farmer_1.setup()

# wr_inputs = dict()
# wr_inputs[var_names[0]] = 20
# wr_inputs[var_names[1]] = 80

# wr_inputs[var_names[2]] = 1
# wr_inputs[var_names[3]] = 2

# wr_inputs[var_names[4]] = 1
# wr_inputs[var_names[5]] = 1

#profit, envir = farmer_1.compute(wr_inputs,[])

wr_id = 1

prob = om.Problem()
model = prob.model

model.add_subsystem('farmer_' + str(wr_id), Farmer(), promotes=['*'])

exec("model."+"farmer_"+str(wr_id)+".wr_id =" + str(wr_id))
exec("model."+"farmer_"+str(wr_id)+".nyears =" + str(nyears))

exec("model."+"farmer_"+str(wr_id)+".wr_data = wr_data[wr_id]")
exec("model."+"farmer_"+str(wr_id)+".hru_wr_map  = hru_wr_map[wr_id]")

temp_hru_wr = eval("model." + "farmer_" + str(wr_id) +".hru_wr_map")
temp_wr = eval("model." + "farmer_" + str(wr_id) +".wr_data")

for hruid in hru_wr_map[wr_id]:
    if wr_data[wr_id][0] == 3:
        exec("model."+"farmer_"+str(wr_id)+".gw_cost[hruid] = gw_cost[hruid]")
        
    elif wr_data[wr_id][0] == 1: 
        exec("model."+"farmer_"+str(wr_id)+".sw_cost[hruid] = sw_cost[hruid]")

exec("model."+"farmer_"+str(wr_id)+".nhrus = len(temp_hru_wr)")


# # setup the optimization
# prob.driver = om.SimpleGADriver()
# prob.driver.options['max_gen'] = 20
# prob.driver.options['bits'] = {'length': 8, 'width': 8, 'height': 8}
# prob.driver.options['penalty_parameter'] = 10.
# prob.driver.options['compute_pareto'] = True

# prob.model.add_design_var('length', lower=0.1, upper=2.)
# prob.model.add_design_var('width', lower=0.1, upper=2.)
# prob.model.add_design_var('height', lower=0.1, upper=2.)
# prob.model.add_objective('front_area', scaler=-1)  # maximize
# prob.model.add_objective('top_area', scaler=-1)  # maximize
# prob.model.add_constraint('volume', upper=1.)

# prob.setup()

