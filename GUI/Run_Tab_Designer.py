# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 14:40:45 2022

@author: snaeimi
"""



class Run_Tab_Designer():
    def __init__(self):
        self.run_button.clicked.connect(self.runREWET)
    
    def runREWET(self):
        self.saveProject()
        #running code for teh project