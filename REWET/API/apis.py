# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 17:40:16 2024

@author: snaeimi
"""

from rewet.initial        import Starter
from rewet.Input.Settings import Settings

class API():
    def init(self, input_file):
        """
        Iniriates API class. 

        Parameters
        ----------
        input_file : Path
            input to the path json or pkl file.

        Returns
        -------
        API class object.

        """
        self.input_file = input_file
        self.starter    = Starter()
        
    def initiate(self):
        """
        Initiates API objects. Required before running REWET.

        Returns
        -------
        status_code : Status
            Run Status.

        """
        try:
            
            self.starter.read_input_file(self.settings, self.input_file)
        except:
            status_code = 0
        return status_code
    
    def runHydraulicSimulation():
        pass
    
    def runRestorationSimulation():
        pass
    
