# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 18:00:55 2022

@author: snaeimi
"""

class Result_Time():
    def __init__():
        pass
    
    def convertTimeSecondToDay(self, data, column, time_shift=0):
        data.loc[:, column] = data.loc[:, column] - time_shift
        data.loc[:, column] = data.loc[:, column] / 24 / 3600
    
    def convertTimeSecondToHour(self, data, column, time_shift=0):
        data.loc[:, column] = data.loc[:, column] - time_shift
        data.loc[:, column] = data.loc[:, column] / 3600