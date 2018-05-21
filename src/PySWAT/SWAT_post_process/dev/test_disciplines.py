import numpy as np
from openmdao.api import ExplicitComponent

class HRU77(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('SWAT')
        self.metadata.declare('Problem')
        
    def setup(self):

        # Global Design Variable
        self.add_input('IRRSC', val = 0.)

        # Local Design Variable
        self.add_input('DIVMAX', val = 0.)

#        # Coupling parameter
#        self.add_input('y2', val=1.0)

        # Coupling output
        self.add_output('y1', val=1.0)

    def compute(self, inputs, outputs):
        """
        Evaluates the equation
        y1 = z1**2 + z2 + x1 - 0.2*y2
        """
        z1 = inputs['IRRSC']
        x1 = inputs['DIVMAX']

        outputs['y1'] = z1**2 + x1
        
        
class HRU76(ExplicitComponent):
    
    def initialize(self):
        self.metadata.declare('SWAT')
        self.metadata.declare('Problem')
        
    def setup(self):

        # Global Design Variable
        self.add_input('IRRSC', val = 0.)

        # Local Design Variable
        self.add_input('DIVMAX', val = 0.)

#        # Coupling parameter
#        self.add_input('y2', val=1.0)

        # Coupling output
        self.add_output('y2', val=1.0)

    def compute(self, inputs, outputs):
        """
        Evaluates the equation
        y1 = z1**2 + z2 + x1 - 0.2*y2
        """
        z1 = inputs['IRRSC']
        x1 = inputs['DIVMAX']

        outputs['y2'] = z1**2 + x1
        