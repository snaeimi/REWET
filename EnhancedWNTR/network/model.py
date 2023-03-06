"""
The wntr.network.model module includes methods to build a water network
model.

.. rubric:: Contents

.. autosummary::

    WaterNetworkModel
    PatternRegistry
    CurveRegistry
    SourceRegistry
    NodeRegistry
    LinkRegistry

"""
import logging
import pandas as pd
import numpy  as np
from collections           import OrderedDict
from wntr.network.base     import LinkStatus
from wntr.network.elements import Pump
from wntr.network.elements import Valve
from ..epanet.io           import InpFile

from wntr.network          import WaterNetworkModel


logger = logging.getLogger(__name__)


class WaterNetworkModel(WaterNetworkModel):
    """
    Water network model class.

    Parameters
    -------------------
    inp_file_name: string (optional)
        Directory and filename of EPANET inp file to load into the
        WaterNetworkModel object.
    """

    def __init__(self, inp_file_name=None):

        super().__init__(None) # None so that we manually run inpread only for once
        self._inpfile = None
        if inp_file_name:
            self.read_inpfile(inp_file_name)
        
        self.breakage_link = pd.Series()
        self.expicit_leak  = []
        
        #For WNTR Version 0.2.2.1. After WNTR Version 0.2.3 we won't need this/ Sina
        self.demand_model = 'DDA'
        self.options.hydraulic.minimum_pressure  = 0
        self.options.hydraulic.required_pressure = 0.07
        self.options.hydraulic.pressure_exponent = 0.5
    
    def updateWaterNetworkModelWithResult(self, result , registry, latest_simulation_time = None):
        """
        Updates Water Netwrok Model consistent with result model. must be only
        used with EPANET solver or just in case you really know what you are
        doing.

        Parameters
        ----------
        result : Water Netwrok Result
       
        latest_simulation_time : int
            latest time of simulation(duration of the latest run), to be
            checked with time in result. Defaylt None.
        
        Raises
        ------
        ValueError
            When simulation object is not of type EpanetSimulator    
            When latest simulation time is provided and is not consistent with
            latest time in result.
            When Tank level gets less than zero
            
        
        Returns
        -------
        None.

        """
                                  
        
        max_time = result.node['head'].index.max()
        if latest_simulation_time == None:
            latest_simulation_time = max_time
        else:
            if latest_simulation_time != max_time:
                raise ValueError('Provided LATEST SIMULATION TIME id not consistnt with teh latest time in RESULT')
            
        
        for tank_name in self.tank_name_list:
            tank_level = None
            head       = None
            
            cur_node = self.get_node(tank_name)
            if cur_node._is_isolated:
                continue
            head = result.node['head'][tank_name][max_time]
                                                   
            tank_level = head - cur_node.elevation
            if tank_level < 0:
                tank_level=0
            if tank_level < cur_node.min_level:
                                                         
                tank_level = cur_node.min_level

                                                                                                   
            if tank_level - cur_node.max_level > 0:
                #if not overflow_permitted:
                    #print(tank_level)
                    #print(cur_node.max_level)
                         
                                                  
                    #raise ValueError('Tank Level for ' + tank_name + ' is more than max level')

                tank_level = cur_node.max_level
            
            cur_node.init_level = abs(tank_level)
            #cur_node.level     = abs(tank_level)
            cur_node.head       = head
            #logger.error('tank_level= '+ repr(tank_level))
        #except Exception as myerr:
            #logger.error(tank_name + ' exist in WaterNetwork but does not exist in result')
            #print(myerr)
            #raise ValueError(tank_name + ' exist in WaterNetwork but does not exist in result')
        #if tank_name=='10':
            #logger.error(tank_level)
            if tank_level < 0.0:
                logger.error('head= '+ repr(head))
                logger.error('elevation= '+ repr(cur_node.elevation))
                logger.error('tank_level= '+ repr(tank_level))
                raise ValueError('Tank Level for ' + tank_name + ' is less than zero')
        #i = 0
        for link_name in self.link_name_list:
            link = self.get_link(link_name)
            setting = None
            status  = None
            try:
                setting = result.link['setting'][link_name][max_time]
                status  = result.link['status'][link_name][max_time]
            except:
                #logger.error(link_name + ' exist in WaterNetwork but does not exist in result')
                #raise ValueError(link_name + ' exist in WaterNetwork but does not exist in result')
                continue
            if isinstance(link, Valve):
                link.settings        = float(setting)
                #link.initial_setting = float(setting)
            elif isinstance(link, Pump):
                link.setting.base_value = float(setting)
                #link.initial_setting    = float(setting)
            if status == 0:
                link.status = LinkStatus.Closed
                #link.initial_status = LinkStatus.Closed
            elif status == 1:
                link.status = LinkStatus.Open
                #link.initial_status = LinkStatus.Open
            elif status == 2:
                link.status = LinkStatus.Active
                #link.initial_status = LinkStatus.Active
            else:
                logger.error('Element type is: '+repr(type(link)))
                logger.error('Status is : ' + repr(status))
                #i +=1
                #raise ValueError("Unrecognized status" + repr(status))
        #print(i)
        #print(len(self.link_name_list))
    def read_inpfile(self, filename):
        """
        Defines water network model components from an EPANET INP file

        Parameters
        ----------
        filename : string
            Name of the INP file.

        """
        inpfile = InpFile()
        inpfile.read(filename, wn=self)
        self._inpfile = inpfile

    def write_inpfile(self, filename, units=None):
        """
        Writes the current water network model to an EPANET INP file

        Parameters
        ----------
        filename : string
            Name of the inp file.
        units : str, int or FlowUnits
            Name of the units being written to the inp file.

        """
        if self._inpfile is None:
            logger.warning('Writing a minimal INP file without saved non-WNTR options (energy, etc.)')
            self._inpfile = InpFile()
        if units is None:
            units = self._options.hydraulic.en2_units
        self._inpfile.write(filename, self, units=units)
    
    def implicitLeakToExplicitEMitter(self, registry):
        if len(self.expicit_leak) > 0:
            raise ValueError("Explicit leak is not reset")
            
        registry.active_pipe_damages = OrderedDict()
        for node_name in self.node_name_list:
            node = self.get_node(node_name)
            
            if node._leak:
                
                if node_name in self.expicit_leak:
                    raise ValueError('The node name in already in leak memory: '+node_name)
                
                new_node_name = node_name+'-nn'
                new_coord     = (node.coordinates[0]+1,node.coordinates[1]+1)
                self.add_junction(new_node_name, elevation=node.elevation ,coordinates=new_coord)
                new_node      = self.get_node(new_node_name) 
                
                
                new_pipe_name = node_name+'-elk'
                self.add_pipe(new_pipe_name, node_name, new_node_name, diameter=100, length=1, roughness=1000000, check_valve_flag=True)
                
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
        for node_name in self.node_name_list:
            node = self.get_node(node_name)
            
            if node._leak:
                
                if node_name in self.expicit_leak:
                    raise ValueError('The node name in already in leak memory: '+node_name)
                
                new_node_name = node_name+'_nn'
                new_coord     = (node.coordinates[0]+1,node.coordinates[1]+1)
                self.add_reservoir(new_node_name, base_head = node.elevation ,coordinates=new_coord)
                
                new_pipe_name = node_name+'-rlk'
                diameter      = np.sqrt(node.leak_area*4/3.14)
                self.add_pipe(new_pipe_name, node_name, new_node_name, diameter=diameter, length=1, roughness=1000000, minor_loss = 1, check_valve_flag=True)
                
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
            
            self.remove_link(new_pipe_name, force=True)
            self.get_node(new_node_name)._emitter_coefficient=None
            self.remove_node(new_node_name, force=True)
            
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
            
            pipe_name_list     = self.pipe_name_list
            junction_name_list = self.junction_name_list
            
            iPipe_A_in = pipe_A in pipe_name_list
            iPipe_B_in = pipe_B in pipe_name_list
            iNode_A_in = node_A in junction_name_list
            iNode_B_in = node_B in junction_name_list
            
            if not iPipe_A_in or not iPipe_B_in or not iNode_A_in or not iNode_B_in:
                if iPipe_A_in or iPipe_B_in or iNode_A_in or iNode_B_in:
                    raise ValueError('The damage is partially removed?: '+repr(iPipe_A_in)+', '+repr(iPipe_B_in)+', '+repr(iNode_A_in)+', '+repr(iNode_B_in)+', '+repr(damage_node))
            else:
                node1 = self.get_link(pipe_A).start_node
                node2 = self.get_link(pipe_B).end_node
                
                new_pipe_name = damage_node+'_BLP'
                self.add_pipe(new_pipe_name, node1.name, node2.name, length=1, diameter=1*2.54/100, roughness=100)
                self.breakage_link.loc[damage_node] = new_pipe_name
    
    def unlinkBreackage(self):
        for damage_node, link_pipe_name in self.breakage_link.iteritems():
            self.remove_link(link_pipe_name, force=True)

        self.breakage_link = pd.Series()