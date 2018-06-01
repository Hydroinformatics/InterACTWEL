#p.model.add_subsystem('circle', ExecComp('area=pi*r**2'))
#
## this subsystem provides the area of circle as the equation of the form with x and y points in space.
#p.model.add_subsystem('r_con', ExecComp('g=x**2 + y**2 - r',
#                                        g=np.ones(SIZE), x=np.ones(SIZE), y=np.ones(SIZE)))
#thetas = np.linspace(0, np.pi/4, SIZE)
#
#p.model.add_subsystem('theta_con', ExecComp('g=arctan(y/x) - theta',
#                                            g=np.ones(SIZE), x=np.ones(SIZE), y=np.ones(SIZE),
#                                            theta=thetas))
#p.model.add_subsystem('delta_theta_con', ExecComp('g = arctan(y/x)[::2]-arctan(y/x)[1::2]',
#                                                  g=np.ones(SIZE//2), x=np.ones(SIZE),
#                                                  y=np.ones(SIZE)))
#
#p.model.add_subsystem('l_conx', ExecComp('g=x-1', g=np.ones(SIZE), x=np.ones(SIZE)))

import numpy as np
import math
from openmdao.api import ExplicitComponent

class circle(ExplicitComponent):

    def setup(self):
        """
        Define the independent variables, output variables, and partials.
        """
        # Inputs
        self.add_input('r', 0.0)

        # Outputs
        self.add_output('area', val=0.0)

    def compute(self, inputs, outputs):

        r = inputs['r']
        area = math.pi*r**2
        outputs['area'] = area
        
        return 

class r_con(ExplicitComponent):

    def setup(self):
        """
        Define the independent variables, output variables, and partials.
        """
        # Inputs
        self.add_input('x', val=np.ones(10))
        self.add_input('y', val=np.ones(10))
        self.add_input('r', val=0.0)

        # Outputs
        self.add_output('g', val=np.ones(10))

    def compute(self, inputs, outputs):

        x = inputs['x']
        y = inputs['y']
        r = inputs['r']
        
        g = np.abs(x**2 + y**2 - r)
        outputs['g'] = np.max(g)*-1000
        
#        return
    
class theta_con(ExplicitComponent):

    def setup(self):
        """
        Define the independent variables, output variables, and partials.
        """
        # Inputs
        self.add_input('x', val=np.ones(10))
        self.add_input('y', val=np.ones(10))

        # Outputs
        self.add_output('g', val=np.ones(10))

    def compute(self, inputs, outputs):

        x = inputs['x']
        y = inputs['y']
        thetas = np.linspace(0, math.pi/4, 10)
        g = np.arctan(y/x) - thetas
        outputs['g'] = np.sum(g)
        
        return
    
class delta_theta_con(ExplicitComponent):

    def setup(self):
        """
        Define the independent variables, output variables, and partials.
        """
        # Inputs
        self.add_input('x', val=np.ones(10))
        self.add_input('y', val=np.ones(10))

        # Outputs
        self.add_output('g', val=np.ones(10))

    def compute(self, inputs, outputs):

        x = inputs['x']
        y = inputs['y']
        g = np.arctan(y/x)[::2] - np.arctan(y/x)[1::2]
        outputs['g'] = np.sum(g)
        
        return

class l_conx(ExplicitComponent):

    def setup(self):
        """
        Define the independent variables, output variables, and partials.
        """
        # Inputs
        self.add_input('x', val=np.ones(10))

        # Outputs
        self.add_output('g', val=np.ones(10))

    def compute(self, inputs, outputs):

        x = inputs['x']
        g=x-1
        outputs['g'] = np.sum(g)
        
        return