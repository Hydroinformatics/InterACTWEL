"""
Test objects for the single-discipline Branin (or Branin-Hoo) problem.
The Branin, or Branin-Hoo, function has three global minima. The recommended
values of a, b, c, r, s and t are:
a = 1
b = 5.1/(4pi2),
c = 5/pi,
r = 6,
s = 10 and
t = 1/(8pi).
This function is usually evaluated on the square x0 ~ [-5, 10], x1 ~ [0, 15].
The global minimum can be found at f(x) = 0.397887
"""
import numpy as np

from openmdao.api import ExplicitComponent


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

        # Outputs
        self.add_output('f', val=0.0)
        self.add_output('f2', val=0.0)
        self.add_output('f3', val=0.0)
        
        self.declare_partials(of='f', wrt=['x0', 'x1'])

    def compute(self, inputs, outputs):
        """
        Define the function f(xI, xC).
        When Branin is used in a mixed integer problem, x0 is integer and x1 is continuous.
        """
        x0 = inputs['x0']
        x1 = inputs['x1']

        a = 1.0
        b = 5.1/(4.0*np.pi**2)
        c = 5.0/np.pi
        d = 6.0
        e = 10.0
        f = 1.0/(8.0*np.pi)

        f = a*(x1 - b*x0**2 + c*x0 - d)**2 + e*(1-f)*np.cos(x0) + e
        outputs['f']  = f
        
        f2 = x0**2 + c*x0*x1
        outputs['f2']  = f2
        f3 = f2 + f
        outputs['f3']  = f2 + f
        
        return f3
        

    def compute_partials(self, inputs, partials):
        """
        Provide the Jacobian.
        """
        x0 = inputs['x0']
        x1 = inputs['x1']

        a = 1.0
        b = 5.1/(4.0*np.pi**2)
        c = 5.0/np.pi
        d = 6.0
        e = 10.0
        f = 1.0/(8.0*np.pi)

        partials['f', 'x1'] = 2.0*a*(x1 - b*x0**2 + c*x0 - d)
        partials['f', 'x0'] = 2.0*a*(x1 - b*x0**2 + c*x0 - d)*(-2.*b*x0 + c) - e*(1.-f)*np.sin(x0)
        partials['f2', 'x1'] = c*x0
        partials['f2', 'x0'] = 2.0*x0 + c*x1
        
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

        # Outputs
        self.add_output('f2', val=0.0)

        self.declare_partials(of='f2', wrt=['x0', 'x1'])

    def compute(self, inputs, outputs):
        """
        Define the function f(xI, xC).
        When Branin is used in a mixed integer problem, x0 is integer and x1 is continuous.
        """
        x0 = inputs['x0']
        x1 = inputs['x1']

        a = 1.0
        b = 5.1/(4.0*np.pi**2)
        c = 5.0/np.pi
        d = 6.0
        e = 10.0
        f = 1.0/(8.0*np.pi)
        
        f = x0**2 + c*x0*x1
        outputs['f2']  = f
        
        return f
        

    def compute_partials(self, inputs, partials):
        """
        Provide the Jacobian.
        """
        x0 = inputs['x0']
        x1 = inputs['x1']

        a = 1.0
        b = 5.1/(4.0*np.pi**2)
        c = 5.0/np.pi
        d = 6.0
        e = 10.0
        f = 1.0/(8.0*np.pi)

        partials['f2', 'x1'] = c*x0
        partials['f2', 'x0'] = 2.0*x0 + c*x1