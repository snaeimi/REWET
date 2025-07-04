# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 14:30:01 2022

@author: snaeimi
"""

import pandas as pd
import numpy as np
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
        pump_damage      = reg.input_pump_damages
        pump_damage_time = pump_damage.index

        time_action_done = {}
        for time in time_list:
            done_list    = pump_damage_time[pump_damage_time>=time]
            time_action_done[time] = len(done_list) / len(pump_damage_time)

        return pd.Series(time_action_done)

    def getTankStatus(self, scn_name):
        res = self.data[scn_name]
        self.loadScneariodata(scn_name)
        reg = self.registry[scn_name]
        time_list = res.node['demand'].index
        tank_damage = reg.input_tank_damages
        tank_damage_time = tank_damage.index

        time_action_done = {}
        for time in time_list:
            done_list = tank_damage_time[tank_damage_time>=time]
            time_action_done[time] = len(done_list) / len(tank_damage_time)

        return pd.Series(time_action_done)

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
        sum_amount = 0
        try:
            res = res.node['leak']
            sum_amount = res.sum(axis=1)
        except:
            sum_amount = 0
        return sum_amount
    
    def getDetailedWaterLeakFromPipeInformation(self, scn_name):
        self.loadScneariodata(scn_name)
        res = self.data[scn_name]
        reg = self.registry[scn_name]
        wn = self.wn
        
        damage_data = []
        for damage_location, row in reg._pipe_damage_table.iterrows():
            damage_type = row["damage_type"]
            pipe_id = row["Orginal_element"]
            pipe_diameter = wn.get_link(pipe_id).diameter
            
            if damage_type=="break":
                try:
                    node_A = reg._pipe_break_history.loc[damage_location, "Node_A"]
                except:
                    node_A = 0
                try:
                    node_B = reg._pipe_break_history.loc[damage_location, "Node_B"]
                except:
                    node_B = 0
                try:
                    pipe_A = reg._pipe_break_history.loc[damage_location, "Pipe_A"]
                except:
                    pipe_A = 0
                try:
                    pipe_B = reg._pipe_break_history.loc[damage_location, "Pipe_B"]
                except:
                    pipe_B = 0
                try:
                    pipe_eod = wn.get_link(pipe_A).diameter
                except:
                    pipe_eod = pipe_diameter
                try:
                    pressure_a = res.node["pressure"].loc[:, node_A].iloc[0]
                except:
                    pressure_a = 0
                try:
                    pressure_b = res.node["pressure"].loc[:, node_B].iloc[0] * 1.422
                except:
                    pressure_b = 0
                try:
                    dicharge_a = res.node["demand"].loc[:, node_A].iloc[0]
                except:
                    dicharge_a = 0
                try:
                    dicharge_b = res.node["demand"].loc[:, node_B].iloc[0] * 2118.88 / 60
                except:
                    dicharge_b = 0
                    
            elif damage_type=="leak":
                try:
                    node_A = reg._pipe_leak_history.loc[:, damage_location, "Node_name"]
                except:
                    node_A = 0
                try:
                    pipe_A = reg._pipe_leak_history.loc[:, damage_location, "Pipe_A"]
                except:
                    pipe_A = 0
                try:
                    pipe_B = reg._pipe_leak_history.loc[:, damage_location, "Pipe_B"]
                except:
                    pipe_B = 0
                try:
                    pipe_eod = wn.get_link(pipe_B).diameter
                except:
                    pipe_eod = 0
                try:
                    pressure_a = res.node["pressure"].loc[:, node_A].iloc[0]
                except:
                    pressure_a = 0
                try:
                    dicharge_a = res.node["demand"].loc[:, node_A].iloc[0]
                except:
                    dicharge_a = 0
                pressure_b = None
                dicharge_b = None
            
            cur_pipe_data = {"Pipe ID": pipe_id,
                             "Damage Type": damage_type,
                             "Diamater": pipe_diameter * 100 / 2.54,
                             "EoD": pipe_eod * 100 / 2.54,
                             "Pressure1": pressure_a * 1.422,
                             "Dischareg1": dicharge_a * 2118.88 / 60,
                             "Pressure2": pressure_b,
                             "Dischareg2": dicharge_b,
                             }
            
            damage_data.append(cur_pipe_data)
        
        damage_data = pd.DataFrame.from_dict(damage_data)
    
        return damage_data
        
        
                
            
        

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

        leak_from_pipe      = res.node['demand'][list(available_nodes)]

        leak = leak_from_pipe < -0.1
        if leak.any().any():
            raise ValueError("There is negative leak")
        
        return leak_from_pipe
        return leak_from_pipe.sum(axis=1)

    def getSystemServiceabilityIndexCurve(self, scn_name, iPopulation="No"):
        self.loadScneariodata(scn_name)
        s4 = self.getRequiredDemandForAllNodesandtime(scn_name)
        sat_node_demands = self.data[scn_name].node['demand'].filter(self.demand_node_name_list)
        sat_node_demands = sat_node_demands.applymap(hhelper)

        if iPopulation=="Yes":
            s4               = s4 * self._population_data
            sat_node_demands = sat_node_demands * self._population_data
        elif iPopulation=="No":
            pass
        else:
            raise ValueError("unknown iPopulation value: "+repr(iPopulation))

        s = sat_node_demands.sum(axis=1) / s4.sum(axis=1)

        for time_index, val in s.items():
            if val < 0:
                val = 0
            elif val > 1:
                val = 1
            s.loc[time_index] = val

        return s

    def getBSCIndexPopulation_4(self, scn_name, bsc="DL", iPopulation=False, ratio= False, consider_leak=False, leak_ratio=1):
        if bsc == "DL":
            return self.getDLIndexPopulation_4(scn_name,
                                               iPopulation=iPopulation,
                                               ratio= ratio,
                                               consider_leak=consider_leak,
                                               leak_ratio=leak_ratio)
        elif bsc == "QN":
            return self.getQNIndexPopulation_4(scn_name,
                                               iPopulation=iPopulation,
                                               ratio=ratio,
                                               consider_leak=consider_leak,
                                               leak_ratio=leak_ratio)
        else:
            raise ValueError(f"BSC input is not recognizable: {bsc}")

    def getDLIndexPopulation_4(self,
                               scn_name,
                               iPopulation="No",
                               ratio= False,
                               consider_leak=False,
                               leak_ratio=1):

        if type(leak_ratio) != float:
            leak_ratio = float(leak_ratio)

        self.loadScneariodata(scn_name)
        res = self.data[scn_name]

        if type(self._population_data) == type(None) or iPopulation==False:
            pop = pd.Series(index=self.demand_node_name_list, data=1)
        elif type(self._population_data) == type(None) and iPopulation==True:
            raise ValueError("Population data is not available")
        else:
            pop = self._population_data

        total_pop = pop.sum()

        result = []
        shared_demand_nodes = set(self.demand_node_name_list).intersection(res.node['demand'].columns.tolist())
        shared_demand_nodes = list(shared_demand_nodes)
        refined_result = res.node['demand'][shared_demand_nodes]
        demands = self.getRequiredDemandForAllNodesandtime(scn_name)
        demands = demands[shared_demand_nodes]

        union_ = set(res.node['leak'].columns).union(set(self.demand_node_name_list)) -(set(res.node['leak'].columns)  - set(self.demand_node_name_list)) - (set(self.demand_node_name_list) - set(res.node['leak'].columns))
        union_ = list(union_)
        leak_res    = res.node['leak'][union_]

        leak_data = []

        if consider_leak:
            for name in leak_res:
                demand_name = demands[name]
                leak_res_name = leak_res[name].dropna()
                time_list = set(leak_res[name].dropna().index)
                time_list_drop = set(demands.index) - time_list
                demand_name = demand_name.drop(time_list_drop)
                leak_more_than_criteria = leak_res_name >=  leak_ratio * demand_name
                if leak_more_than_criteria.any(0):
                    leak_data.append(leak_more_than_criteria)
        leak_data = pd.DataFrame(leak_data).transpose()

        s = refined_result > demands * 0.01
        for name in s:
            if name in leak_data.columns:
                leak_data_name = leak_data[name]
                for time in leak_data_name.index:
                    if leak_data_name.loc[time] == True:
                        s.loc[time, name] = False

        s = s * pop[s.columns]

        if ratio==False:
            total_pop = 1
        else:
            total_pop = pop.sum()

        result = s.sum(axis=1)/total_pop

        return result

    def getQNIndexPopulation_4(self, scn_name, iPopulation=False, ratio=False, consider_leak=False, leak_ratio=0.75):
        if type(leak_ratio) != float:
            leak_ratio = float(leak_ratio)

        self.loadScneariodata(scn_name)
        res = self.data[scn_name]

        if type(self._population_data) == type(None) or iPopulation==False:
            pop = pd.Series(index=self.demand_node_name_list, data=1)
        elif type(self._population_data) == type(None) and iPopulation==True:
            raise ValueError("Population data is not available")
        else:
            pop = self._population_data

        result = []
        
        shared_demand_nodes = set(self.demand_node_name_list).intersection(res.node['demand'].columns.tolist())
        shared_demand_nodes = list(shared_demand_nodes)
        
        union_ = set(res.node['leak'].columns).union(set(self.demand_node_name_list)) -(set(res.node['leak'].columns)  - set(self.demand_node_name_list)) - (set(self.demand_node_name_list) - set(res.node['leak'].columns))
        union_ = list(union_)
        
        refined_result = res.node['demand'][shared_demand_nodes]
        demands = self.getRequiredDemandForAllNodesandtime(scn_name)
        demands        = demands[shared_demand_nodes]

        leak_res    = res.node['leak'][union_]
        leak_data = []
        if consider_leak:
            for name in leak_res:
                demand_name = demands[name]
                leak_res_name = leak_res[name].dropna()
                time_list = set(leak_res_name.index)
                time_list_drop = set(demands.index) - time_list
                demand_name = demand_name.drop(time_list_drop)
                leak_more_than_criteria = leak_res_name >= leak_ratio * demand_name
                if leak_more_than_criteria.any(0):
                    leak_data.append(leak_more_than_criteria)
        leak_data = pd.DataFrame(leak_data).transpose()

        s = refined_result + 0.00000001 >= demands  #sina bug

        for name in s:
            if name in leak_data.columns:
                leak_data_name = leak_data[name]
                for time in leak_data_name.index:
                    if leak_data_name.loc[time] == True:
                        s.loc[time, name] = False

        s = s * pop[s.columns]
        if ratio==False:
            total_pop = 1
        else:
            total_pop = pop.sum()

        result = s.sum(axis=1) / total_pop

        return result

    def getQuantityExceedanceCurve(self, iPopulation="No", ratio=False, consider_leak=False, leak_ratio=0.75, result_type='mean', daily=False, min_time=0, max_time=999999999999999):
        all_scenarios_qn_data = self.AS_getQNIndexPopulation(iPopulation="No", ratio=ratio, consider_leak=consider_leak, leak_ratio=leak_ratio)
        exceedance_curve      = self.PR_getCurveExcedence(all_scenarios_qn_data, result_type=result_type, daily=daily, min_time=min_time, max_time=max_time)
        columns_list          = exceedance_curve.columns.to_list()

        dmg_vs_ep_list = {}

        for i in range(0, len(columns_list), 2):
            dmg_col = columns_list[i]
            ep_col  = columns_list[i+1]
            dmg_vs_ep_list[dmg_col] = ep_col
        res = {}

        for dmg_col in dmg_vs_ep_list:
            ep_col                = dmg_vs_ep_list[dmg_col]
            exceedance_curve_temp = exceedance_curve.set_index(dmg_col)
            exceedance_curve_temp = exceedance_curve_temp[ep_col]
            res[dmg_col]          = exceedance_curve_temp

        return res

    def getDeliveryExceedanceCurve(self, iPopulation="No", ratio=False, consider_leak=False, leak_ratio=0.75, result_type='mean', daily=False, min_time=0, max_time=999999999999999):
        all_scenarios_qn_data = self.AS_getDLIndexPopulation(iPopulation=iPopulation, ratio=ratio, consider_leak=consider_leak, leak_ratio=leak_ratio)
        exceedance_curve      = self.PR_getCurveExcedence(all_scenarios_qn_data, result_type=result_type, daily=daily, min_time=min_time, max_time=max_time)
        columns_list          = exceedance_curve.columns.to_list()

        dmg_vs_ep_list = {}

        for i in range(0, len(columns_list), 2):
            dmg_col = columns_list[i]
            ep_col  = columns_list[i+1]
            dmg_vs_ep_list[dmg_col] = ep_col
        res = {}

        for dmg_col in dmg_vs_ep_list:
            ep_col                = dmg_vs_ep_list[dmg_col]
            exceedance_curve_temp = exceedance_curve.set_index(dmg_col)
            exceedance_curve_temp = exceedance_curve_temp[ep_col]
            res[dmg_col]          = exceedance_curve_temp

        return res

    def getDeliveredDemandRatio(self, scn_name):
        self.loadScneariodata(scn_name)
        res = self.data[scn_name]
        map_res = pd.Series(data=0,
                            index=self.demand_node_name_list,
                            dtype=np.int64)

        required_demand = self.getRequiredDemandForAllNodesandtime(scn_name)
        delivered_demand = res.node['demand']
        common_nodes_demand = list( set(delivered_demand.columns).intersection(
            set(self.demand_node_name_list)))
        
        left_overs = list(set(self.demand_node_name_list) - set(common_nodes_demand))
        

        delivered_demand    = delivered_demand[common_nodes_demand]
        required_demand     = required_demand[common_nodes_demand]

        required_demand.sort_index(inplace=True)
        delivered_demand.sort_index(inplace=True)

        delivered_demand_ratio = delivered_demand / required_demand
        delivered_demand_ratio.loc[:, left_overs] = 0.0

        return delivered_demand_ratio
