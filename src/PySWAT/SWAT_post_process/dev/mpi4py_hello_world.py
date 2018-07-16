###!/usr/bin/env python
##
##from __future__ import print_function
##from mpi4py import MPI
##
##
##comm = MPI.COMM_WORLD
##
##print("Hello! I'm rank %d from %d running in total..." % (comm.rank, comm.size))
##
##comm.Barrier() # wait for everybody to synchronize _here_
#
##%%
##import multiprocessing
##import time
##
##data = (
##    ['a', '2'], ['b', '4'], ['c', '6'], ['d', '8'],
##    ['e', '1'], ['f', '3'], ['g', '5'], ['h', '7']
##)
##
##def mp_worker((inputs, the_time)):
##    print " Processs %s\tWaiting %s seconds" % (inputs, the_time)
##    time.sleep(int(the_time))
##    print " Process %s\tDONE" % inputs
##
##def mp_handler():
##    p = multiprocessing.Pool(2)
##    p.map(mp_worker, data)
##
##if __name__ == '__main__':
##    mp_handler()
#    
##%%
##!/usr/bin/env python2.7
##    This file is part of DEAP.
##
##    DEAP is free software: you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as
##    published by the Free Software Foundation, either version 3 of
##    the License, or (at your option) any later version.
##
##    DEAP is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
##    GNU Lesser General Public License for more details.
##
##    You should have received a copy of the GNU Lesser General Public
##    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.
#
#import array
#import multiprocessing
#import random
#import sys
#import functools
#
#if sys.version_info < (2, 7):
#    print("mpga_onemax example requires Python >= 2.7.")
#    exit(1)
#
#import numpy
#
#from deap import algorithms
#from deap import base
#from deap import creator
#from deap import tools
#
##from scoop import futures
#
##%%
##def evalOneMaxb(individual):
##    print sum(individual)
##    return sum(individual),
#
#def _instance_method_alias(obj, arg):
#    """
#    Alias for instance method that allows the method to be called in a 
#    multiprocessing pool
#    """
#    #arg = list(arg)
#    #print arg
#    fit_val = obj.evalOneMax(arg)
#    
#    return fit_val
#
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
#
##%%
##creator.create("FitnessMax", base.Fitness, weights=(1.0,))
##creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)
##
##toolbox = base.Toolbox()
##
### Attribute generator
##toolbox.register("attr_bool", random.randint, 0, 1)
##
### Structure initializers
##toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 100)
##toolbox.register("population", tools.initRepeat, list, toolbox.individual)
##
##funct = FunCT()
##bound_instance_method_alias = functools.partial(_instance_method_alias, funct)
##toolbox.register("evaluate", bound_instance_method_alias)
###toolbox.register("evaluate", funct.evalOneMax())
###toolbox.register("evaluate", evalOneMaxb)
##
##toolbox.register("mate", tools.cxTwoPoint)
##toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
##toolbox.register("select", tools.selTournament, tournsize=3)
##
##if __name__ == "__main__":
##    random.seed(64)
##    
##    # Process Pool of 4 workers
##    pool = multiprocessing.Pool(processes = 2)
##    toolbox.register("map", pool.map)
##        
##    #toolbox.register("map", futures.map)
##    
##    pop = toolbox.population(n=300)
##    hof = tools.HallOfFame(1)
##    stats = tools.Statistics(lambda ind: ind.fitness.values)
##    stats.register("avg", numpy.mean)
##    stats.register("std", numpy.std)
##    stats.register("min", numpy.min)
##    stats.register("max", numpy.max)
##
##    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, stats=stats, halloffame=hof)
##    pool.close()
##   

#%%

import multiprocessing

def f(x):
    #created = multiprocessing.Process()
    current = multiprocessing.current_process()
#    print 'running:', current.name, current._identity[0], current._identity[1]
#    print 'created:', created.name, created._identity[0], current._identity[1]
    #print 'running:', current.name, current._identity[0]
    #print 'created:', created.name, created._identity
    print multiprocessing.current_process()
    
    return x * x

p = multiprocessing.Pool()
print p.map(f, range(6))
p.close()    