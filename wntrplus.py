# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 03:17:23 2021

@author: snaeimi
"""

import pandas as pd
import numpy  as np
from collections  import OrderedDict

class WNTRPlus():
    def __init__(self):
        self.expicit_leak  = [] #pd.DataFrame(columns=['method','element1','element2','attr1'])
        self.breakage_link = pd.Series()
    
    def implicitLeakToExplicitEMitter(self, registry):
        if len(self.expicit_leak) > 0:
            raise ValueError("Explicit leak is not reset")
            
        registry.active_pipe_damages = OrderedDict()
        for node_name in self.wn.node_name_list:
            node = self.wn.get_node(node_name)
            
            if node._leak:
                
                if node_name in self.expicit_leak:
                    raise ValueError('The node name in already in leak memory: '+node_name)
                
                new_node_name = node_name+'-nn'
                new_coord     = (node.coordinates[0]+1,node.coordinates[1]+1)
                self.wn.add_junction(new_node_name, elevation=node.elevation ,coordinates=new_coord)
                new_node      = self.wn.get_node(new_node_name) 
                
                
                new_pipe_name = node_name+'-elk'
                self.wn.add_pipe(new_pipe_name, node_name, new_node_name, diameter=100, length=1, roughness=1000000, check_valve_flag=True)
                
                cd = node.leak_area*(2)**0.5 #(m^3ps/(KPa^0.5))
                cd = cd/(0.145038**0.5)  #(gpm/(Psi^0.5))
                # When writing to emitter, function from_si changes m^3ps to GPM
                
                new_node._emitter_coefficient = cd
                
                if node.demand_timeseries_list[0].base_value > 0.001:
                    raise ValueError('leak node has demand: '+node_name)
                temp={'node_name':node_name, 'method':'emitter', 'element1':new_pipe_name, 'element2':new_node_name, 'attr1':cd}
                self.expicit_leak.append(temp)
                registry.explicit_leak_node.loc[node_name] = new_node_name
                registry.active_pipe_damages.update({new_node_name:node_name})
    
    def implicitLeakToExplicitReservoir(self, registry):
        if len(self.expicit_leak) > 0:
            raise ValueError("Explicit leak is not reset")
        registry.active_pipe_damages = OrderedDict()
        for node_name in self.wn.node_name_list:
            node = self.wn.get_node(node_name)
            
            if node._leak:
                
                if node_name in self.expicit_leak:
                    raise ValueError('The node name in already in leak memory: '+node_name)
                
                new_node_name = node_name+'_nn'
                new_coord     = (node.coordinates[0]+1,node.coordinates[1]+1)
                self.wn.add_reservoir(new_node_name, base_head = node.elevation ,coordinates=new_coord)
                
                new_pipe_name = node_name+'-rlk'
                diameter      = np.sqrt(node.leak_area*4/3.14)
                self.wn.add_pipe(new_pipe_name, node_name, new_node_name, diameter=diameter, length=1, roughness=1000000, minor_loss = 1, check_valve_flag=True)
                
                if node.demand_timeseries_list[0].base_value>0.001:
                    raise ValueError('leak node has demand: '+node_name)
                temp={'node_name':node_name, 'method':'reservoir', 'element1':new_pipe_name, 'element2':new_node_name}
                self.expicit_leak.append(temp)
                registry.explicit_leak_node.loc[node_name]=new_node_name
                registry.active_pipe_damages.update({new_node_name:node_name})
    
    def resetExplicitLeak(self):
        
        for data in self.expicit_leak:            
            new_pipe_name = data['element1']
            new_node_name = data['element2']
            
            self.wn.remove_link(new_pipe_name, force=True)
            self.wn.get_node(new_node_name)._emitter_coefficient=None
            self.wn.remove_node(new_node_name, force=True)
            
        self.expicit_leak  = []
    
    def linkBreackage(self, registry):
        if len(self.breakage_link) > 0:
            raise ValueError("Breakckage is not unliked")
        self.breakage_link = pd.Series()
        pipe_damage_table = registry.getDamageData('PIPE')
        broken_pipe_damage_table = pipe_damage_table[pipe_damage_table['damage_type']=='break']
        
        for damage_node, row in broken_pipe_damage_table.iterrows():
            if registry.getPipeDamageAttribute('repair',damage_node)==True:
                continue
            pipe_A, pipe_B, orginal_pipe, node_A, node_B = registry.getBreakData(damage_node)
            
            pipe_name_list     = self.wn.pipe_name_list
            junction_name_list = self.wn.junction_name_list
            
            iPipe_A_in = pipe_A in pipe_name_list
            iPipe_B_in = pipe_B in pipe_name_list
            iNode_A_in = node_A in junction_name_list
            iNode_B_in = node_B in junction_name_list
            
            if not iPipe_A_in or not iPipe_B_in or not iNode_A_in or not iNode_B_in:
                if iPipe_A_in or iPipe_B_in or iNode_A_in or iNode_B_in:
                    raise ValueError('The damage is partially removed?: '+repr(iPipe_A_in)+', '+repr(iPipe_B_in)+', '+repr(iNode_A_in)+', '+repr(iNode_B_in)+', '+repr(damage_node))
            else:
                node1 = self.wn.get_link(pipe_A).start_node
                node2 = self.wn.get_link(pipe_B).end_node
                
                new_pipe_name = damage_node+'_BLP'
                self.wn.add_pipe(new_pipe_name, node1.name, node2.name, length=1, diameter=1*2.54/100, roughness=100)
                self.breakage_link.loc[damage_node] = new_pipe_name
    
    def unlinkBreackage(self):
        for damage_node, link_pipe_name in self.breakage_link.iteritems():
            self.wn.remove_link(link_pipe_name, force=True)

        self.breakage_link = pd.Series()
        