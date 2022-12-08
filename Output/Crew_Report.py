# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 15:45:10 2022

@author: snaeimi
"""

import pandas as pd

class Crew_Report():
    def __init__(self):
        pass
    
    def getCrewForTime(self, scn_name, time):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        
        crew_table = reg.restoration_log_book._agent_state_log_book
        crew_table = crew_table.set_index('Time')
        crew_table = crew_table.loc[time]
        return crew_table
    
    def getCrewTableAt(self, scn_name, time, crew_type_name, crew_zone=None):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        res = self.data[scn_name]
        #crew_type  = self.getCrewForTime(scn_name, time)
        crew_table = reg.restoration_log_book.crew_history[time]
        typed_crew_table = crew_table[crew_table['type']==crew_type_name]
        
        if crew_zone != None:
            typed_crew_table = typed_crew_table[typed_crew_table['group']==crew_zone]
            
        return typed_crew_table
    
    def getCrewAvailabilityThroughTime(self, scn_name, crew_type_name, crew_zone=None):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        crew_table = reg.restoration_log_book.crew_history
        time_list = list(crew_table.keys())
        time_list.sort()
        
        crew_number = pd.Series()
        
        for time in time_list:
            crew_table_time       = self.getCrewTableAt(scn_name, time, crew_type_name, crew_zone)
            total_number          = len(crew_table_time)
            available_number_time = crew_table_time[(crew_table_time['available']==True) | (crew_table_time['active']==True)]
            crew_number.loc[time] = len(available_number_time)
        
        return total_number, crew_number
    
    def getCrewOnShiftThroughTime(self, scn_name, crew_type_name, crew_zone=None, not_on_shift=False):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        crew_table = reg.restoration_log_book.crew_history
        time_list = list(crew_table.keys())
        time_list.sort()
        
        crew_number = pd.Series()
        
        for time in time_list:
            crew_table_time       = self.getCrewTableAt(scn_name, time, crew_type_name, crew_zone)
            total_number          = len(crew_table_time)

            if not_on_shift==False:
                available_number_time = crew_table_time[crew_table_time['active']==True]
            elif not_on_shift==True:
                available_number_time = crew_table_time[crew_table_time['active']==False]
            else:
                raise ValueError("Unnown not on shift" + repr(not_on_shift))
            crew_number.loc[time] = len(available_number_time)
        
        return total_number, crew_number
    
    def getCrewWorkingThroughTime(self, scn_name, crew_type_name, crew_zone=None, not_on_working=False):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        crew_table = reg.restoration_log_book.crew_history
        time_list = list(crew_table.keys())
        time_list.sort()
        
        crew_number = pd.Series()
        
        for time in time_list:
            crew_table_time       = self.getCrewTableAt(scn_name, time, crew_type_name, crew_zone)
            total_number          = len(crew_table_time)
            #available_number_time = crew_table_time[crew_table_time['available']==True]
            available_number_time = crew_table_time[crew_table_time['active']==True]
            if not_on_working==False:
                available_number_time = available_number_time[available_number_time['ready']==False]
            elif not_on_working==True:
                available_number_time = available_number_time[available_number_time['ready']==True]
            else:
                raise ValueError("Unnown not on shift" + repr(not_on_working))
            crew_number.loc[time] = len(available_number_time)
        
        return total_number, crew_number
    
    
    
        