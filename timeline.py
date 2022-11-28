# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 02:00:40 2020

@author: snaeimi
"""

import pandas as pd
import numpy
import logging

logger = logging.getLogger(__name__)

EVENT_TYPE=['dmg','rpr','rst'] #event types are defined here
class Timeline():
    
# =============================================================================
# This classs has many functions that can make a lot of exceptions.
# We need to modify their codes, so their usage be safe and bug-free.
# =============================================================================

    def __init__(self, simulation_end_time):
        if  simulation_end_time<0:
            raise ValueError('simulation end time must be zero or bigger than zero')
        self._current_time = 0
        self._event_time_register = pd.DataFrame(dtype = 'bool') #craete event at time 0 with No event marked as True
        self._event_time_register = self._event_time_register.append(pd.DataFrame(data = False , index = [0], columns = EVENT_TYPE)) #create event at time 0 with No event marked as True
        self._event_time_register = self._event_time_register.append(pd.DataFrame(data = False , index = [simulation_end_time], columns = EVENT_TYPE)) #create event at time simulation end time with No event marked as True
        
        self._simulation_end_time = simulation_end_time
        self._ending_Event_ignore_time = 100 # in seconds - events in less than this value is ignored
        self._iFirst_time_zero = True
        self._current_time_indexOfIndex = 0
        
    def iContinue(self):
        if self._current_time==0 and self._iFirst_time_zero == True: #So that the other condition happens
            self._iFirst_time_zero = False
            return True
        else:
            self._current_time               = self.getNextTime()
            self._current_time_indexOfIndex += 1
            if abs(self._simulation_end_time - self._current_time) < abs(self._ending_Event_ignore_time):
                return False
            else:
                return True
            
    def getNextTime(self):
        if not self._event_time_register.index.is_monotonic_increasing: # for just in case if the index of event time register is not sorted
            self._event_time_register.sort_index()
                
        if self._event_time_register.index[self._current_time_indexOfIndex]\
            !=self._current_time:
            raise RuntimeError('A possible violation of time in timeline event variables and/or event time registry')
        next_time = self._event_time_register.index[self._current_time_indexOfIndex+1]
        return next_time
    
    def getCurrentStopTime(self):
        return int(self._current_time)
    
    def iCurrentTimeRepairEvent(self):
        return self._event_time_register['rpr'].loc[self._current_time]
    
    def iCurenttimeRestorationEvent(self):
        print("current_time is= "+str(self._current_time) )
        print(self._event_time_register['rst'].loc[self._current_time])
        return self._event_time_register['rst'].loc[self._current_time]
    
    def iCurrentTimeDamageEvent(self):
        return self._event_time_register['dmg'].loc[self._current_time]
    
    def addEventTime(self, event_distinct_time, event_type='dmg'):
        """
        This function is a low-level function to add event type in an already-
        existing event_time in event_time_register. FOR NOW TEH DISTICT TIMES
        CAN BE A LIST OR A LIST. MAYBE IN THE FUTURE WE CAN DECIDE WETHER IT
        SHOULD BE LEFT THE WAY IT IS OR IT SHOULD BE MODIFIED IN A SINGLE
        VARIABLE OR LIST VARIABLE.
        Parameters
        ----------
        event_distinct_time : numpy.float64 or int or float or list
            This variable is either a list or a seriest of data to represent
            time of an specified event
            
        event_type : str, optional
            Evenet type. FOR CURRENT VERSSION AN EVENT COULD BE EIOTHER
            dmg(damage) or rpr(repair). The default is 'dmg'.

        Raises
        ------
        ValueError
            If the input variable for distinct time or the type of event is not
            recognizabe, a Valueerrorr exception is raised
            Also if the damage typeis  not recognized

        Returns
        -------
        None.

        """
        if type(event_distinct_time)!=pd.core.series.Series:
            if type(event_distinct_time) == numpy.float64 or type(event_distinct_time) == int or type(event_distinct_time) == float or type(event_distinct_time) == list:
                event_distinct_time = pd.Series(data=event_distinct_time)
            else:
                print(type(event_distinct_time))
                raise ValueError('event_distinct_time must be pandas.Series type')
        
        if event_type not in EVENT_TYPE:
            raise ValueError('unrecognized value for event_type')
        
        #check for duplicate in time index. if there is duplicate, we will only change the true and false value in the DataFrame
        temp_to_pop = []
        logger.debug("event distinct time "+ repr(event_distinct_time))
        
        for i, i_time in event_distinct_time.items():
            if i_time in self._event_time_register.index:
                self._event_time_register[event_type].loc[i_time]=True #attention here
                self.checkAndAmendTime()
                temp_to_pop.append(i_time)
        logger.debug('temp_to_pop'+repr(temp_to_pop))
        
        for i_time in temp_to_pop:
            ind = event_distinct_time[event_distinct_time==i_time].index[0]
            event_distinct_time.pop(ind)
        
        if len(event_distinct_time) != 0:
            dataframe_temp = pd.DataFrame(data = False, index = event_distinct_time, columns = EVENT_TYPE)
            self._event_time_register = self._event_time_register.append(dataframe_temp)
            for i, i_time in event_distinct_time.items():
                self._event_time_register[event_type].loc[i_time]=True
            self._event_time_register = self._event_time_register.sort_index()
            self.checkAndAmendTime()
            
    def iEventTypeAt(self, begin_time, event_type):
        """
        Checks if an event type is in event registry at the time of begin_time
        ----------
        begin_time : int
            begining time
        event_type : str
            damage type

        Returns
        -------
        bool
            rResult if such data exist or not

        """
        
        if not begin_time in self._event_time_register.index:
            return False
        if self._event_time_register[event_type].loc[begin_time]:
            return True
        else:
            return False
    
    def checkAndAmendTime(self):
        """
        Checks if the time of event is higher than the sim time.Also checks
        if the the ending event has any thing event(nothings must be true). 
        
        Parameters
        ----------
        None.

        Returns
        -------
        None.

        """
        
        first_length=len(self._event_time_register.index)
        self._event_time_register = self._event_time_register[self._event_time_register.index <= self._simulation_end_time]
        if first_length>len(self._event_time_register):
            print("here was " + repr(first_length - len(self._event_time_register)) + "amended")
        if self._event_time_register[self._event_time_register.index==self._simulation_end_time].empty==True:
            self._event_time_register=self._event_time_register.append(pd.DataFrame(data = False , index = [self._simulation_end_time], columns = EVENT_TYPE))

    # These functions are no longer used
    ##def getEventTimeList(self):
    ##    """
    ##    gets event time in a series
##
    ##    Returns
    ##    -------
     ##   Panda Series
    ##        Event Times
##
   ##    """
  ##      return pd.Series(self._event_time_register.index)
    
    #def add_repair(self, time_of_repair, sim_end_time):
        #self.addEventTime(time_of_repair, event_type = 'rpr')
        
