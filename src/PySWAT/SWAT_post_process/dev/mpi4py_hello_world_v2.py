import array
import multiprocessing
import random
import sys
import functools

if sys.version_info < (2, 7):
    print("mpga_onemax example requires Python >= 2.7.")
    exit(1)

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

#from scoop import futures

#%%
#def evalOneMaxb(individual):
#    print sum(individual)
#    return sum(individual),

def _instance_method_alias(obj, arg):
    """
    Alias for instance method that allows the method to be called in a 
    multiprocessing pool
    """
    #arg = list(arg)
    #print arg
    fit_val = obj.evalOneMax(arg)
    
    return fit_val
#%%

#class FunCT(object):
#    def __init__(self):
#        pass
#    
#    def evalOneMax(self,individual):
##        print sum(individual)
#        return sum(individual),
#    
##    def __call__(self, x):
##        return self.evalOneMax(x)

  
class FunCT():

    def evalOneMax(self,individual):
#        print sum(individual)
        return sum(individual),
    
#%%
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_bool", random.randint, 0, 1)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 100)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

funct = FunCT()
#bound_instance_method_alias = functools.partial(_instance_method_alias, funct)
#toolbox.register("evaluate", bound_instance_method_alias)

toolbox.register("evaluate", _instance_method_alias, funct)

#toolbox.register("evaluate", funct.evalOneMax())
#toolbox.register("evaluate", evalOneMaxb)

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

if __name__ == "__main__":
    random.seed(64)
    
    # Process Pool of 4 workers
    pool = multiprocessing.Pool(processes = 2)
    toolbox.register("map", pool.map)
        
    #toolbox.register("map", futures.map)
    
    pop = toolbox.population(n=300)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, stats=stats, halloffame=hof)
    pool.close()
   
    