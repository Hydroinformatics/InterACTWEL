"""A simple Deap-based driver for OpenMDAO."""

from deap import base, creator, tools, algorithms

from openmdao.core.driver import Driver
from openmdao.recorders.recording_iteration_stack import Recording
from openmdao.utils.concurrent import concurrent_eval

import copy, random
from six import iteritems
from six.moves import range

import numpy as np
from pyDOE import lhs

import multiprocessing

class DeapGADriver(Driver):
    """
    Driver for a simple genetic algorithm.

    Options
    -------
    options['elitism'] :  bool(True)
        If True, replace worst performing point with best from previous generation each iteration.
    options['max_gen'] :  int(300)
        Number of generations before termination.
    options['pop_size'] :  int(25)
        Number of points in the GA.

    Attributes
    ----------
    _desvar_idx : dict
        Keeps track of the indices for each desvar, since GeneticAlgorithm seess an array of
        design variables.
    _ga : <GeneticAlgorithm>
        Main genetic algorithm lies here.
    """

    def __init__(self):
        """
        Initialize the SimpleGADriver driver.
        """
        super(DeapGADriver, self).__init__()

        # What we support
        self.supports['integer_design_vars'] = True

        # What we don't support yet
        self.supports['inequality_constraints'] = False
        self.supports['equality_constraints'] = False
        self.supports['multiple_objectives'] = False
        self.supports['two_sided_constraints'] = False
        self.supports['linear_constraints'] = False
        self.supports['simultaneous_derivatives'] = False
        self.supports['active_set'] = False

        # User Options
        self.options.declare('bits', default={}, types=(dict),
                             desc='Number of bits of resolution. Default is an empty dict, where '
                             'every unspecified variable is assumed to be integer, and the number '
                             'of bits is calculated automatically. If you have a continuous var, '
                             'you should set a bits value as a key in this dictionary.')
        self.options.declare('elitism', default=True,
                             desc='If True, replace worst performing point with best from previous'
                             ' generation each iteration.')
        self.options.declare('max_gen', default=300,
                             desc='Number of generations before termination.')
        self.options.declare('pop_size', default=25,
                             desc='Number of points in the GA.')
        self.options.declare('run_parallel', default=False,
                             desc='Set to True to execute the points in a generation in parallel.')
        
        self.options.declare('minimize', default='minimize', desc='Sets the optimization to either minimize or maximize the objective function.')
        self.options.declare('crossover_method',default='cxTwoPoint',desc='Sets the optimization crossover method')
        self.options.declare('mutate_method', default='cxTwoPoint',desc='Sets the optimization crossover method')
        self.options.declare('mutate_prob', default = 0.05,desc='Sets the optimization crossover method')
        self.options.declare('select_method', default='selTournament',desc='Sets the optimization crossover method')
        self.options.declare('select_method_inputs', default= 3 ,desc='Sets the optimization crossover method')
        self.options.declare('weights', default= (1.0,) ,desc='Sets the optimization objectives weights')
        self.options.declare('name_opt', default = 'Test1', desc = 'Name to indentify opt problems')
        self.options.declare('print_results',default = False)
        self._desvar_idx = {}
        self._ga = None
        self._hof = None
        self._log = None
        self._pop = None
        
        
    def _setup_driver(self, problem):
        """
        Prepare the driver for execution.

        This is the final thing to run during setup.

        Parameters
        ----------
        problem : <Problem>
            Pointer to the containing problem.
        """
        super(DeapGADriver, self)._setup_driver(problem)

#        if len(self._objs) > 1:
#            msg = 'SimpleGADriver currently does not support multiple objectives.'
#            raise RuntimeError(msg)

#        if len(self._cons) > 0:
#            msg = 'SimpleGADriver currently does not support constraints.'
#            raise RuntimeError(msg)

        if self.options['run_parallel']:
            comm = self._problem.comm
        else:
            comm = None

        self._ga = NSGAAlgorithm(self.objective_callback, comm=comm)

    def run(self):
        """
        Excute the genetic algorithm.

        Returns
        -------
        boolean
            Failure flag; True if failed to converge, False is successful.
        """
        model = self._problem.model
        ga = self._ga
        ga.iter = self.iter_count
        ga.const = self._cons
        # Size design variables.
        desvars = self._designvars
        count = 0
        for name, meta in iteritems(desvars):
            size = meta['size']
            self._desvar_idx[name] = (count, count + size)
            count += size

        lower_bound = np.empty((count, ))
        upper_bound = np.empty((count, ))

        # Figure out bounds vectors.
        for name, meta in iteritems(desvars):
            i, j = self._desvar_idx[name]
            lower_bound[i:j] = meta['lower']
            upper_bound[i:j] = meta['upper']

        ga.elite = self.options['elitism']
        pop_size = self.options['pop_size']
        max_gen = self.options['max_gen']
        user_bits = self.options['bits']
        wghts = self.options['weights']
        optprint = self.options['print_results']
        # Bits of resolution
        bits = np.ceil(np.log2(upper_bound - lower_bound + 1)).astype(int)
        prom2abs = model._var_allprocs_prom2abs_list['output']

        for name, val in iteritems(user_bits):
            try:
                i, j = self._desvar_idx[name]
            except KeyError:
                abs_name = prom2abs[name][0]
                i, j = self._desvar_idx[abs_name]

            bits[i:j] = val

        desvar_new, obj, nfit, hof, log, pop = ga.execute_ga(lower_bound, upper_bound, bits, pop_size, max_gen, wghts, optprint)

        # Pull optimal parameters back into framework and re-run, so that
        # framework is left in the right final state
        for name in desvars:
            i, j = self._desvar_idx[name]
            val = desvar_new[i:j]
            self.set_design_var(name, val)

        with Recording('DeapGA', self.iter_count, self) as rec:
            model._solve_nonlinear()
            rec.abs = 0.0
            rec.rel = 0.0
        self.iter_count += 1
        self._hof = hof
        self._log = log
        self._pop = pop
        
        return False

    def objective_callback(self, x):
        """
        Evaluate problem objective at the requested point.

        Parameters
        ----------
        x : ndarray
            Value of design variables.
        icase : int
            Case number, used for identification when run in parallel.

        Returns
        -------
        float
            Objective value
        bool
            Success flag, True if successful
        int
            Case number, used for identification when run in parallel.
        """
        model = self._problem.model
        success = 1
        popid = self.iter_count

        penalty = []
        for name in self._designvars:
            i, j = self._desvar_idx[name]
            self.set_design_var(name, x[i:j])
            penalty.append(self.FeasiblePt(name, x[i:j][0]))
                
        # Execute the model
        with Recording('DeapGA', self.iter_count, self) as rec:
            self.iter_count += 1
            try:
                model._solve_nonlinear()
                model._outputs
#                for name, val in iteritems(model.get_design_vars()):
#                    print(val)

            # Tell the optimizer that this is a bad point.
            except AnalysisError:
                model._clear_iprint()
                success = 0
            
            obj = []
            for name, val in iteritems(self.get_objective_values()):
                obj.append(val[0])
                #break

            # Record after getting obj to assure they have
            # been gathered in MPI.
            rec.abs = 0.0
            rec.rel = 0.0
            
#        for name, val in iteritems(self.get_design_var_values()):
#            print(val)
        
        # print("Functions calculated")
        # print(x)
        # print(obj)
        return tuple(obj)
    
    def FeasiblePt(self, name, xind):
        for tconst in self._cons:
            if tconst == name:
                if xind >= self._cons[tconst]['lower'] and xind <= self._cons[tconst]['upper']:
                    return 1000
        return 0


class NSGAAlgorithm():
    """
    Simple Genetic Algorithm.

    This is the Simple Genetic Algorithm implementation based on 2009 AAE550: MDO Lecture notes of
    Prof. William A. Crossley. It can be used standalone or as part of the OpenMDAO Driver.


    Attributes
    ----------
    comm : MPI communicator or None
        The MPI communicator that will be used objective evaluation for each generation.
    elite : bool
        Elitism flag.
    lchrom : int
        Chromosome length.
    npop : int
        Population size.
    objfun : function
        Objective function callback.
    """

    def __init__(self, objfun, comm=None):
        """
        Initialize genetic algorithm object.

        Parameters
        ----------
        objfun : function
            Objective callback function.
        comm : MPI communicator or None
            The MPI communicator that will be used objective evaluation for each generation.
        """
        self.objfun = objfun
        self.const = False
        self.comm = comm

        self.lchrom = 0
        self.npop = 0
        self.elite = True
        self.iter = 0

    def execute_ga(self, vlb, vub, bits, pop_size, max_gen, wghts, optprint):
        """
        Perform the genetic algorithm.

        Parameters
        ----------
        vlb : ndarray
            Lower bounds array.
        vub : ndarray
            Upper bounds array.
        bits : ndarray
            Number of bits to encode the design space for each element of the design vector.
        pop_size : int
            Number of points in the population.
        max_gen : int
            Number of generations to run the GA.

        Returns
        -------
        ndarray
            Best design point
        float
            Objective value at best design point.
        int
            Number of successful function evaluations.
        """
        
        creator.create("FitnessMin", base.Fitness, weights=wghts)
        #creator.create("FitnessMin", base.Fitness, weights=(1.0,1.0))
        creator.create("Individual", list, fitness=creator.FitnessMin)  
       
        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(processes=2)
        toolbox = base.Toolbox()
        
        toolbox.register("map", pool.map)
        #toolbox.register("map", self.comm.map)
        toolbox.register("evaluate", self.objfun)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        #toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("select", tools.selNSGA2)
        

        
        #toolbox.register("attr_bool", random.randint, 0, 1)
        #toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 100)
        for varid in range(0,len(bits)):
            if bits[varid] == 8:
                toolbox.register("attr_flt", random.uniform, vlb[varid], vub[varid])
            else:
                toolbox.register("attr_int", random.randint, vlb[varid], vub[varid])
        toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.attr_int, toolbox.attr_flt), n=1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        
        #toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 100.0))
        
        pop = toolbox.population(n=pop_size)
        #hof = tools.HallOfFame(100)
        hof = tools.ParetoFront()
        if optprint:
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", np.mean)
            stats.register("std", np.std)
            stats.register("min", np.min)
            stats.register("max", np.max)
            stats.register("ParetoFront", lambda x: copy.deepcopy(hof))
        
        #logbook = tools.Logbook()
        #logbook.header = "gen", "evals", "std", "min", "avg", "max"
        
            pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, 
                                   stats=stats, halloffame=hof, verbose=True)
        else:
            pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, 
                                   halloffame=hof, verbose=False)
        
#        xopt = copy.deepcopy(vlb)
#        fopt = np.inf
#        self.lchrom = int(np.sum(bits))
#
#        if np.mod(pop_size, 2) == 1:
#            pop_size += 1
#        self.npop = int(pop_size)
#        fitness = np.zeros((self.npop, ))
#
#        Pc = 0.5
#        Pm = (self.lchrom + 1.0) / (2.0 * pop_size * np.sum(bits))
#        elite = self.elite
#
#        # TODO: from an user-supplied intial population
#        # new_gen, lchrom = encode(x0, vlb, vub, bits)
#        new_gen = np.round(lhs(self.lchrom, self.npop, criterion='center'))
#
#        # Main Loop
#        nfit = 0
#        for generation in range(max_gen + 1):
#            old_gen = copy.deepcopy(new_gen)
#            x_pop = self.decode(old_gen, vlb, vub, bits)
#
#            # Evaluate points in this generation.
#            if self.comm is not None:
#                # Parallel
#                cases = [((item, ii), None) for ii, item in enumerate(x_pop)]
#
#                results = concurrent_eval(self.objfun, cases, self.comm, allgather=True)
#
#                fitness[:] = np.inf
#                for result in results:
#                    returns, traceback = result
#
#                    if returns:
#                        val, success, ii = returns
#                        if success:
#                            fitness[ii] = val
#                            nfit += 1
#
#                    else:
#                        # Print the traceback if it fails
#                        print('A case failed:')
#                        print(traceback)
#
#            else:
#                # Serial
#                for ii in range(self.npop):
#                    x = x_pop[ii]
#
#                    fitness[ii], success, _ = self.objfun(x, 0)
#
#                    if success:
#                        nfit += 1
#                    else:
#                        fitness[ii] = np.inf
#
#            # Elitism means replace worst performing point with best from previous generation.
#            if elite and generation > 0:
#                max_index = np.argmax(fitness)
#                old_gen[max_index] = min_gen
#                x_pop[max_index] = min_x
#                fitness[max_index] = min_fit
#
#            # Find best performing point in this generation.
#            min_fit = np.min(fitness)
#            min_index = np.argmin(fitness)
#            min_gen = old_gen[min_index]
#            min_x = x_pop[min_index]
#
#            if min_fit < fopt:
#                fopt = min_fit
#                xopt = min_x
#
#            # Evolve new generation.
#            new_gen = self.tournament(old_gen, fitness)
#            new_gen = self.crossover(new_gen, Pc)
#            new_gen = self.mutate(new_gen, Pm)
        
        gen_keys = log.select('gen','min')
        #fopt = gen_keys[1][gen_keys[0][-1]]
        nfit = gen_keys[0][-1]
        #fits = [ind.fitness.values for ind in pop]
        
        return hof[0], hof[0].fitness.values, nfit, hof, log, pop
        
