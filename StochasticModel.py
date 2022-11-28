# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 20:19:10 2020

@author: snaeimi
"""
import wntr
import Damage
import pandas as pd
import logging
from timeline import Timeline
#from wntrplus import WNTRPlus
from wntr.utils.ordered_set import OrderedSet
from Sim.Simulation import Hydraulic_Simulation
import EnhancedWNTR.network.model


logger = logging.getLogger(__name__)

class StochasticModel():
    def __init__(self, water_network, damage_model , registry,  simulation_end_time, restoration, mode='PDD', i_restoration=True):
        if type(water_network) != wntr.network.model.WaterNetworkModel and type(water_network) != EnhancedWNTR.network.model.WaterNetworkModel:
            raise ValueError('Water_network model is not legitimate water Network Model')
        if type(damage_model) != Damage.Damage:
            raise ValueError('damage_model is not a ligitimate Damage Model')
        self.wn               = water_network
        self.damage_model     = damage_model
        self._simulation_time = simulation_end_time
        self.timeline         = Timeline(simulation_end_time)
        damage_distict_time   = self.damage_model.get_damage_distinct_time()
        self.timeline.addEventTime(damage_distict_time)
        self.timeline.checkAndAmendTime()

        
        self.simulation_mode=None
        if mode=='PDD' or mode=='DD':
            self.simulation_mode=mode
        else:
            self.simulation_mode='PDD'
        self._linear_result           = registry.result
        self.registry                 = registry 
        #self.wp                      = WNTRPlus(restoration._registry)
        self.restoration              = restoration
        self._min_correction_time     = 900
        self.simulation_time          = 0
        self.restoration_time         = 0
        self.iRestoration             = i_restoration
        self._prev_isolated_junctions = OrderedSet()
        self._prev_isolated_links     = OrderedSet()
        self.first_leak_flag          = True
        

    def runLinearScenario(self, damage, settings, worker_rank=None):
        """
        Runs a simple linear analysis of water damage scenario
        Parameters
        
        Water Network object (WN) shall not be altered in any object except restoration
        ----------
        damage : Damage Object

        Returns
        -------
        Result.

        """
        while self.timeline.iContinue():
            current_stop_time = self.timeline.getCurrentStopTime()
            print('--------------------------------------')
            print('At stop Time: ' + repr(current_stop_time/3600))
# =============================================================================
            #Restoration event Block
            if self.timeline.iCurenttimeRestorationEvent() and self.iRestoration==True:
                logger.debug('\t Restoration Event ')

                event_time_list = self.restoration.perform_action(self.wn, current_stop_time)

                self.timeline.addEventTime(event_time_list, event_type='rst')

# =============================================================================
#           Damage (earthquake) event block   
            if self.timeline.iCurrentTimeDamageEvent():
                logger.debug('\t DAMAGE EVENT')
                damage.applyPipeDamages(self.wn, current_stop_time)
                damage.applyNodalDamage(self.wn, current_stop_time)
                damage.applyPumpDamages(self.wn, current_stop_time)
                damage.applyTankDamages(self.wn, current_stop_time)
                
                if self.iRestoration == True:
                    event_time_list = self.restoration.initialize(self.wn, current_stop_time) # starts restoration
                    self.timeline.addEventTime(event_time_list, event_type='rst')
               
# =============================================================================
#           This is for updatng the pipe damage log
            self.restoration._registry.updatePipeDamageTableTimeSeries(current_stop_time)
            self.restoration._registry.updateNodeDamageTableTimeSeries(current_stop_time)
# =============================================================================
#           runing the model
            next_event_time = self.timeline.getNextTime()
            logger.debug('next event time is: '+ repr(next_event_time))

            self.wn.implicitLeakToExplicitReservoir(self.registry)
            
            print('***** Running at time '+ repr(current_stop_time/3600)+' *****')
            
            if type(worker_rank) != str:
                worker_rank = str(worker_rank)
            
            hyd_sim = Hydraulic_Simulation(self.wn, settings, current_stop_time, worker_rank, self._prev_isolated_junctions, self._prev_isolated_links)
            self.hyd_temp = hyd_sim
            duration          = self.wn.options.time.duration
            report_time_step  = self.wn.options.time.report_timestep
            try: # Run with modified EPANET V2.2
                print("Performing method 1")
                rr, i_run_successful = hyd_sim.performSimulation(next_event_time, True)
            except Exception as epa_err_1:
                if epa_err_1.args[0] == 'EPANET Error 110':
                    print("Method 1 failed. Performing method 2")
                    try: # Remove Non-Demand Node by Python-Side iterative algorythm with closing
                        #self.wn.options.time.duration        = duration
                        #self.wn.options.time.report_timestep = report_time_step
                        #hyd_sim.removeNonDemandNegativeNodeByPythonClose(1000)
                        #rr, i_run_successful = hyd_sim.performSimulation(next_event_time, False)
                        #hyd_sim.rollBackPipeClose()
                        raise
                    except Exception as epa_err_2:
                        if True: #epa_err_2.args[0] == 'EPANET Error 110':
                            try: # Extend result from teh reult at the begining of teh time step with modified EPANET V2.2
                                #print("Method 2 failed. Performing method 3")
                                self.wn.options.time.duration        = duration
                                self.wn.options.time.report_timestep = report_time_step
                                #hyd_sim.rollBackPipeClose()
                                rr, i_run_successful = hyd_sim.estimateRun(next_event_time, True)
                            except Exception as epa_err_3:
                                if epa_err_3.args[0] == 'EPANET Error 110':
                                    print("Method 3 failed. Performing method 4")
                                    try: # Extend result from teh reult at the begining of teh time step with modified EPANET V2.2
                                        self.wn.options.time.duration        = duration
                                        self.wn.options.time.report_timestep = report_time_step
                                        rr, i_run_successful = hyd_sim.performSimulation(next_event_time, False)
                                    except Exception as epa_err_4:
                                        if epa_err_4.args[0] == 'EPANET Error 110':
                                            #try:
                                            self.wn.options.time.duration        = duration
                                            self.wn.options.time.report_timestep = report_time_step
                                            print("Method 4 failed. Performing method 5")
                                            # Extend result from teh reult at the begining of teh time step with modified EPANET V2.2
                                            rr, i_run_successful = hyd_sim.estimateRun(next_event_time, False)
                                            #except Exception as epa_err_5:
                                                #if epa_err_5.args[0] == 'EPANET Error 110':
                                                    #print("Method 5 failed. Performing method 6")
                                                    #self.wn.options.time.duration        = duration
                                                    #self.wn.options.time.report_timestep = report_time_step
                                                    #rr, i_run_successful = hyd_sim.estimateWithoutRun(self._linear_result ,next_event_time)
                                                #else:
                                                    #raise epa_err_5
                                        else:
                                            raise epa_err_4
                                else:
                                    raise epa_err_3
                        else:
                            raise epa_err_2
                else:
                    raise epa_err_1
            self._prev_isolated_junctions = hyd_sim._prev_isolated_junctions
            self._prev_isolated_links     = hyd_sim._prev_isolated_links
            print('***** Finish Running at time '+ repr(current_stop_time)+'  '+repr(i_run_successful)+' *****')
            
            if i_run_successful==False:
                continue
            self.wn.updateWaterNetworkModelWithResult(rr, self.restoration._registry)
            
            self.KeepLinearResult(rr, self._prev_isolated_junctions, node_attributes=['pressure','head','demand', 'leak'], link_attributes=['status', 'setting', 'flowrate'])
            
            #self.wp.unlinkBreackage(self.registry)
            self.wn.resetExplicitLeak()

# =============================================================================
        #self.resoration._registry.updateTankTimeSeries(self.wn, current_stop_time)
        self.restoration._registry.updateRestorationIncomeWaterTimeSeries(self.wn, current_stop_time)
        
        return self._linear_result
   
    def KeepLinearResult(self, result, isolated_nodes, node_attributes=None, link_attributes=None, iCheck=False):#, iNeedTimeCorrection=False, start_time=None):
        if node_attributes == None:
            node_attributes = ['pressure','head','demand','quality']
        if link_attributes == None:
            link_attributes = ['linkquality', 'flowrate', 'headloss', 'velocity', 'status', 'setting', 'frictionfact', 'rxnrate']
        
        just_initialized_flag = False
        if self._linear_result == None:
            just_initialized_flag = True
            self._linear_result   = result
            
            self.restoration._registry.result = self._linear_result
            node_result_type_elimination_list = set(['pressure','head','demand','quality' , 'leak']) - set(node_attributes)
            link_result_type_elimination_list = set(['linkquality', 'flowrate', 'headloss', 'velocity', 'status', 'setting', 'frictionfact', 'rxnrate']) - set(link_attributes)
            
            for node_result_type in node_result_type_elimination_list:
                self._linear_result.node.pop(node_result_type)
            
            for link_result_type in link_result_type_elimination_list:
                self._linear_result.link.pop(link_result_type)
                
            self._linear_result.node['leak'] = pd.DataFrame()
        
        active_pipe_damages  = self.restoration._registry.active_pipe_damages
        
        temp_active = active_pipe_damages.copy()
        for virtual_demand_node in active_pipe_damages:
            if virtual_demand_node in isolated_nodes or active_pipe_damages[virtual_demand_node] in isolated_nodes:
                temp_active.pop(virtual_demand_node)
        
        virtual_demand_nodes = list(temp_active.keys() )
        real_demand_nodes    = list(temp_active.values() )
        
        if len(temp_active) > 0:
            result.node['demand'][real_demand_nodes] = result.node['demand'][virtual_demand_nodes]
            result.node['demand'].drop(virtual_demand_nodes, axis =1, inplace=True)
        
        active_nodal_damages = self.restoration._registry.active_nodal_damages
        temp_active = active_nodal_damages.copy()

        for virtual_demand_node in active_nodal_damages:
            if virtual_demand_node in isolated_nodes or temp_active[virtual_demand_node] in isolated_nodes:
                temp_active.pop(virtual_demand_node)
        
        virtual_demand_nodes = list(temp_active.keys() )
        real_demand_nodes    = list(temp_active.values() )
        
        if len(temp_active) > 0:
            non_isolated_pairs  = dict(zip(virtual_demand_nodes, real_demand_nodes))
            result.node['leak'] = result.node['demand'][virtual_demand_nodes].rename(non_isolated_pairs, axis=1)
        

        
            
        if just_initialized_flag == False:
            self._linear_result.maximum_trial_time.extend(result.maximum_trial_time)
            
            saved_max_time = self._linear_result.node[list(self._linear_result.node.keys())[0]].index.max()
            to_be_saved_min_time = result.node[list(result.node.keys())[0]].index.min()
            if abs(to_be_saved_min_time - saved_max_time) != 0: #>= min(self.wn.options.time.hydraulic_timestep, self.wn.options.time.report_timestep):
                #logger.error(repr(to_be_saved_min_time)+ '  ' + repr(saved_max_time))
                raise ValueError("saved result and to be saved result are not the same")
            for att in node_attributes:
                if len(active_nodal_damages) == 0 and att == 'leak':
                    continue
                _leak_flag = False

                leak_first_time_result = None
                if att == 'leak' and 'leak' in result.node: #the second condition is not needed. It's there only for assurance
                    _leak_flag = True
                    former_nodes_list = set(self._linear_result.node['leak'].columns)
                    to_add_nodes_list = set(result.node[att].columns)
                    complete_result_node_list  = (to_add_nodes_list - former_nodes_list)
                    leak_first_time_result     = result.node['leak'][complete_result_node_list].iloc[0]
                    
                result.node[att].drop(result.node[att].index[0], inplace=True)
                self._linear_result.node[att] = self._linear_result.node[att].append(result.node[att])
                
                if _leak_flag:
                    self._linear_result.node['leak'].loc[leak_first_time_result.name, leak_first_time_result.index] = leak_first_time_result
                    self._linear_result.node['leak'] = self._linear_result.node['leak'].sort_index()
                    
            for att in link_attributes:
                result.link[att].drop(result.link[att].index[0], inplace=True)
                self._linear_result.link[att] = self._linear_result.link[att].append(result.link[att])
        