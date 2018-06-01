#from deap import base
#from deap import creator
#from deap import tools
#from deap import algorithms
#
#import random, numpy
#
#def evalOneMax(individual):
#    return sum(individual),
#    
#creator.create("FitnessMax", base.Fitness, weights=(1.0,))
#creator.create("Individual", list, fitness=creator.FitnessMax)  
#
#toolbox = base.Toolbox()
#toolbox.register("evaluate", evalOneMax)
#toolbox.register("mate", tools.cxTwoPoint)
#toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
#toolbox.register("select", tools.selTournament, tournsize=3)
#
#toolbox.register("attr_bool", random.randint, 0, 1)
##toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 50)
#IND_SIZE=1
##toolbox.register("indices", random.sample, range(IND_SIZE), IND_SIZE)
#toolbox.register("indices", random.randint, 5, 23)
#toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.indices, toolbox.attr_bool), n=1)
#
#toolbox.register("population", tools.initRepeat, list, toolbox.individual)
#
#pop = toolbox.population(n=300)
#hof = tools.HallOfFame(10)
#
#pf = tools.ParetoFront()
#
#stats = tools.Statistics(lambda ind: ind.fitness.values)
#stats.register("avg", numpy.mean)
#stats.register("std", numpy.std)
#stats.register("min", numpy.min)
#stats.register("max", numpy.max)
#pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, 
#                           stats=stats, halloffame=hof, verbose=True)

import numpy as np

from openmdao.api import ExplicitComponent

import random
from deap import base
from deap import creator
from deap import tools
from deap import algorithms

def evalOneMax(individual):
    return sum(individual),

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
toolbox = base.Toolbox()
toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 2)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evalOneMax)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

pop = toolbox.population(n=300)
hof = tools.HallOfFame(1)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("max", np.max)

pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, stats=stats, halloffame=hof, verbose=True)

        