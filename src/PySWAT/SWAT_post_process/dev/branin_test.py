"""
Test objects for the single-discipline Branin (or Branin-Hoo) problem.
"""
import numpy as np
from openmdao.api import ExplicitComponent, NewtonSolver, SimpleGADriver, Problem, IndepVarComp

class Branin(ExplicitComponent):
    """
    The Branin test problem. This version is the standard version and
    contains two continuous parameters.
    """

    def setup(self):
        """
        Define the independent variables, output variables, and partials.
        """
        # Inputs
        self.add_input('x0', 0.0)
        self.add_input('x1', 0.0)
        self.add_input('x2', 0.0)
        self.add_input('x3', 0.0)

        # Outputs
        self.add_output('f', val=0.0)

#        self.declare_partials(of='f', wrt=['x0', 'x1'])

    def compute(self, inputs, outputs):
        """
        Define the function f(xI, xC).

        When Branin is used in a mixed integer problem, x0 is integer and x1 is continuous.
        """
        x0 = inputs['x0']
        x1 = inputs['x1']
        x2 = inputs['x2']
        x3 = inputs['x3']
        
#        if x2 > 5.0:
#            x0 = 100000            
        
        a = 1.0
        b = 5.1/(4.0*np.pi**2)
        c = 5.0/np.pi
        d = 6.0
        e = 10.0
        f = 1.0/(8.0*np.pi)
        
        f = a*(x1 - b*x0**2 + c*x0 - d)**2 + e*(1-f)*np.cos(x0) + e
        outputs['f'] = f
        return f

#    def compute_partials(self, inputs, partials):
#        """
#        Provide the Jacobian.
#        """
#        x0 = inputs['x0']
#        x1 = inputs['x1']
#
#        a = 1.0
#        b = 5.1/(4.0*np.pi**2)
#        c = 5.0/np.pi
#        d = 6.0
#        e = 10.0
#        f = 1.0/(8.0*np.pi)
#
#        partials['f', 'x1'] = 2.0*a*(x1 - b*x0**2 + c*x0 - d)
#        partials['f', 'x0'] = 2.0*a*(x1 - b*x0**2 + c*x0 - d)*(-2.*b*x0 + c) - e*(1.-f)*np.sin(x0)

class Branin2(ExplicitComponent):
    """
    The Branin test problem. This version is the standard version and
    contains two continuous parameters.
    """

    def setup(self):
        """
        Define the independent variables, output variables, and partials.
        """
        # Inputs
        self.add_input('x0', 0.0)
        self.add_input('x1', 0.0)
        self.add_input('x3', 0.0)
        
        self.add_output('x0o', 0.0)
        
        # Outputs
        self.add_output('f2', val=0.0)

        
#        self.declare_partials(of='*', wrt='*', method='fd')

    def compute(self, inputs, outputs):
        """
        Define the function f(xI, xC).

        When Branin is used in a mixed integer problem, x0 is integer and x1 is continuous.
        """
        x0 = inputs['x0']
        x1 = inputs['x1']
        x3 = inputs['x3']
        
        f2 = x0*x3
        
        outputs['f2'] = f2
        outputs['x0o'] = x0*5
        
#        prob = Problem()
#        model = prob.model = Group()
#        comp =IndepVarComp()
#        comp.add_output('x0',val=0.0)
#        comp.add_output('x3',val=0.0)
#        model.add_subsystem('pp1', comp)
#        prob.driver = SimpleGADriver()
#        prob.driver.options['bits'] = {'p1.xC' : 8}
#
#        prob.setup()
#        prob.run_driver()
#        
#        outputs['f'] = prob['pp1.f']
        return f2
        

class pp1(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('Var_dict')
        
    def setup(self):
        """
        Define the independent variables, output variables, and partials.
        """
        # Inputs
        self.add_input('x0', 0.0)
        self.add_input('x1', 0.0)
        self.add_input('x2', 0.0)
        
        # Outputs
        self.add_output('f', val=0.0)
        self.add_output('x0o', 0.0)

    def compute(self, inputs, outputs):
        x0 = inputs['x0']
        x1 = inputs['x1']
        
        #var_dict = self.metadata['Var_dict']
        outputs['x0o'] = x0/10
        outputs['f'] = x0*x3