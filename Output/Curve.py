# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 14:30:01 2022

@author: snaeimi
"""

import pandas as pd
from .Helper import hhelper

class Curve():
    def __init__():
        pass
    
    def getPipeStatusByAction(self, scn_name ,action):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        sequence = reg.retoration_data['sequence']["PIPE"]
        if action not in sequence:
            raise ValueError("the action is not in the sequence: "+str(action))
        pipe_damage_table_time_series = reg._pipe_damage_table_time_series
        time_action_done = {}
        for  time in pipe_damage_table_time_series:
            current_pipe_damage_table = pipe_damage_table_time_series[time]
            current_action_damage     = current_pipe_damage_table[action]
            number_of_all             = len(current_action_damage)
            if number_of_all < 1:
                continue
            current_action_damage            = current_action_damage[~current_action_damage.isna()]
            current_action_damage_true       = current_action_damage[current_action_damage==True]
            unique_done_orginal_element_list = (current_pipe_damage_table.loc[current_action_damage_true.index]["Orginal_element"]).unique().tolist()
            current_pipe_damage_table        = current_pipe_damage_table.set_index("Orginal_element")
            current_action_damage            = current_pipe_damage_table.loc[unique_done_orginal_element_list]
            
            number_of_done             = len(current_action_damage)
            time_action_done[time]     = number_of_done / number_of_all
        
        return pd.Series(time_action_done)
    
    def getNodeStatusByAction(self, scn_name, action):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        sequence = reg.retoration_data['sequence']["DISTNODE"]
        if action not in sequence:
            raise ValueError("the action is not in the sequence: "+str(action))
        node_damage_table_time_series = reg._node_damage_table_time_series
        time_action_done = {}
        for time in node_damage_table_time_series:
            current_node_damage_table = node_damage_table_time_series[time]
            current_action_damage     = current_node_damage_table[action]
            number_of_all             = len(current_action_damage)
            if number_of_all < 1:
                continue
            current_action_damage            = current_action_damage[~current_action_damage.isna()]
            current_action_damage_true       = current_action_damage[current_action_damage==True]
            unique_done_orginal_element_list = (current_node_damage_table.loc[current_action_damage_true.index]["Orginal_element"]).unique().tolist()
            current_node_damage_table        = current_node_damage_table.set_index("Orginal_element")
            current_action_damage            = current_node_damage_table.loc[unique_done_orginal_element_list]
            
            number_of_done             = len(current_action_damage)
            time_action_done[time]     = number_of_done / number_of_all
        
        return pd.Series(time_action_done)
    
    def getPumpStatus(self, scn_name):
        self.loadScneariodata(scn_name)
        res              = self.data[scn_name]
        reg              = self.registry[scn_name]
        time_list        = res.node['demand'].index
        pump_damage      = reg.damage.damaged_pumps
        pump_damage_time = pump_damage.index
        
        time_action_done = {}
        for time in time_list:
            done_list    = pump_damage_time[pump_damage_time>=time]
            time_action_done[time] = len(done_list) / len(pump_damage_time)
        
        return pd.Series(time_action_done)
    
    def getTankStatus(self, scn_name):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        time_list = reg.time_list
        tank_damage = reg.damage.tamk_damage
        tank_damage_time = tank_damage.index
        
        time_action_done = {}
        for time in time_list:
            done_list = tank_damage_time[tank_damage_time>=time]
            time_action_done[time] = len(done_list) / len(tank_damage_time)
        
        return pd.Series(time_action_done)
    
    def temp(self, scn_name):
        reservoir_name_list = self.wn.reservoir_name_list
        res = self.data[scn_name]
        our_res = set()
        for reservoir_name in reservoir_name_list:
            if reservoir_name in res.node['demand'].columns:
                flow_in_time = res.node['demand'][reservoir_name]
            else:
                continue
            for time, flow in flow_in_time.iteritems():
                if abs(flow) > 1:
                    our_res.add(reservoir_name)
        return our_res
    
    def getInputWaterFlowCurve(self, scn_name, tank_name_list=None, reservoir_name_list = None, mode='all'):
        self.loadScneariodata(scn_name)
        res = self.data[scn_name]
        
        if tank_name_list==None:
            tank_name_list = self.wn.tank_name_list
        
        not_known_tank = set(tank_name_list) - set(self.wn.tank_name_list)
        if len(not_known_tank) > 0:
            raise ValueError("The folliwng tanks in the input are not known in the water network" + repr(tank_name_list))
        
        if reservoir_name_list==None:
            reservoir_name_list = self.wn.reservoir_name_list
        
        not_known_reservoir = set(reservoir_name_list) - set(self.wn.reservoir_name_list)
        if len(not_known_reservoir) > 0:
            raise ValueError("The folliwng reservoirs in the input are not known in the water network" + repr(reservoir_name_list))
            
        outbound_flow = pd.Series(0, index=res.node['demand'].index)
        inbound_flow  = pd.Series(0, index=res.node['demand'].index)
        #inbound_flow  = 0
        #outbound_flow = 0
        
        waterFlow = None
        
        for tank_name in tank_name_list:
            if tank_name in res.node['demand'].columns:
                flow_in_time = res.node['demand'][tank_name]
            else:
                continue
            for time, flow in flow_in_time.iteritems():
                #print(flow)
                if flow > 0:
                    outbound_flow.loc[time] += -1 * flow
                elif flow < 0:
                    inbound_flow.loc[time]  += -1 * flow
                
                if mode == "all":
                    waterFlow = outbound_flow + inbound_flow
                elif mode == 'out':
                    waterFlow = outbound_flow
                elif mode == 'in':
                    waterFlow = inbound_flow
                else:
                    raise ValueError("Unnown mode: "+repr(mode))
            
        for reservoir_name in reservoir_name_list:
            if reservoir_name in res.node['demand'].columns:
                flow_in_time = res.node['demand'][reservoir_name]
            else:
                continue
            for time, flow in flow_in_time.iteritems():
                #print(flow)
                if flow > 0:
                    outbound_flow.loc[time] += -1 * flow
                elif flow < 0:
                    inbound_flow.loc[time]  += -1 * flow
                
                if mode == "all":
                    waterFlow = outbound_flow + inbound_flow
                elif mode == 'out':
                    waterFlow = outbound_flow
                elif mode == 'in':
                    waterFlow = inbound_flow
                else:
                    raise ValueError("Unnown mode: "+repr(mode))
                
        return waterFlow
    
    def getOveralDemandSatisfied(self, scn_name, pure=False):
        self.loadScneariodata(scn_name)
        if pure == False:
            demand_node_name_list = self.demand_node_name_list
        else:
            demand_node_name_list = []
            for node_name in self.wn.junction_name_list:
                if self.wn.get_node(node_name).demand_timeseries_list[0].base_value > 0:
                    demand_node_name_list.append(node_name)
        
        sat_node_demands = self.data[scn_name].node['demand'].filter(demand_node_name_list)
        #sat_node_demands = sat_node_demands.applymap(hhelper)
        s = sat_node_demands.sum(axis=1)
             
        return s

    def getWaterLeakingFromNode(self, scn_name):
        self.loadScneariodata(scn_name)
        res = self.data[scn_name]

        return res.sum(axis=1)
    
    def getWaterLeakingFromPipe(self, scn_name, mode='all'):
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        res = self.data[scn_name]
        
        damage_location_list = reg._pipe_damage_table
        
        if mode == 'leak':
            damage_location_list = damage_location_list[damage_location_list['damage_type'] == mode]
        elif mode == 'break':
            damage_location_list = damage_location_list[damage_location_list['damage_type'] == mode]
        elif mode == 'all':
            pass
        else:
            raise ValueError("The mode is not recognized: " + repr(mode) )
            
        
        break_damage_table = damage_location_list[damage_location_list['damage_type']=='break']
        pipe_B_list = self.registry[scn_name]._pipe_break_history.loc[break_damage_table.index, 'Node_B']
        
        damage_location_list = damage_location_list.index
        wanted_nodes = pipe_B_list.to_list()
        wanted_nodes.extend(damage_location_list.to_list())
        
        available_nodes = set( res.node['demand'].columns )
        wanted_nodes    = set( wanted_nodes )
        
        not_available_nodes = wanted_nodes - available_nodes
        available_nodes     = wanted_nodes - not_available_nodes
        
        leak_from_pipe      = res.node['demand'][available_nodes]
        
        leak = leak_from_pipe < 0
        if leak.any().any():
            raise ValueError("There is negative leak")
        
        return leak_from_pipe.sum(axis=1)
        
    def getSystemServiceabilityIndexCurve(self, scn_name, iPlot=False):
        #scn_name = list(self.data.keys())[file_index]
        s4 = self.getRequiredDemandForAllNodesandtime(scn_name)
        sat_node_demands = self.data[scn_name].node['demand'].filter(self.demand_node_name_list)
        sat_node_demands = sat_node_demands.applymap(hhelper)
        s=sat_node_demands.sum(axis=1)/s4.sum(axis=1)
        
        last_valid_value = None
        for time_index, val in s.iteritems():
            if not (val < 0 or val >1):
                last_valid_value= val
            else:
                print('problem in time: '+repr(time_index)+ ' -> '+repr(val))
                if val < 0:
                    val = 0
                elif val > 1:
                    val = 1
            s.loc[time_index] = val
                
        if iPlot == False:
            return s
        else:
            s.index=s.index/3600
            s.plot()
            