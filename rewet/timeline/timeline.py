# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 20:19:10 2020

@author: snaeimi
"""
import os
import pickle
import sys
import logging
import pandas as pd
import wntrfr
import json
import rewet.EnhancedWNTR.network.model
from wntrfr.utils.ordered_set import OrderedSet
from rewet import Damage
from rewet.timeline.time_register import TimeRegister
from rewet.hydraulic.Simulation import HydraulicSimulation
from rewet.EnhancedWNTR.sim.results import SimulationResults
from wntrfr.network.model import LinkStatus


logger = logging.getLogger(__name__)
logger.setLevel(50)

class Timeline():
    def __init__(self, water_network, damage_model , registry,  simulation_end_time, restoration, mode='PDD', i_restoration=True):
        if type(water_network) != wntrfr.network.model.WaterNetworkModel and type(water_network) != rewet.EnhancedWNTR.network.model.WaterNetworkModel:
            raise ValueError('Water_network model is not legitimate water Network Model')
        if type(damage_model) != Damage:
            raise ValueError('damage_model is not a ligitimate Damage Model')
        self.wn               = water_network
        self.damage_model     = damage_model
        self._simulation_time = simulation_end_time
        self.timeline         = TimeRegister(simulation_end_time, restoration, registry)
        damage_distict_time   = self.damage_model.get_damage_distinct_time()
        self.timeline.addEventTime(damage_distict_time)
        self.timeline.checkAndAmendTime()


        self.simulation_mode=None
        if mode=='PDD' or mode=='DD':
            self.simulation_mode=mode
        else:
            self.simulation_mode='PDD'
        # .self._linear_result           = registry.result
        self.registry                 = registry
        self.restoration              = restoration
        self._min_correction_time     = 900
        self.simulation_time          = 0
        self.iRestoration             = i_restoration
        self._prev_isolated_junctions = OrderedSet()
        self._prev_isolated_links     = OrderedSet()
        self.first_leak_flag          = True
        self.hydraulic_solver_priority = {
            1: "EPANET",
            2: "Enhanced_EPANET"
            }


    def runLinearScenario(self, damage, settings, worker_rank=None):
        """
        Runs WDN simulation timeline with a gievn damage scneario and simulation
        policy and then saves the result in the directory defiend in settings
        object with a predefined naming fashion.

        ----------
        damage : Damage Object
        settings: Settings object
        worker_rank: the rank of the worker if MPI is setup. Otehrwise, None.

        Returns
        -------
        None.

        """
        # TODO: Add REWET status Teh function must returnb REWETStatus

        while self.timeline.iContinue():
            sys.stdout.flush()  # flush print
            current_stop_time = self.timeline.getCurrentStopTime()
            current_stop_time_hour = current_stop_time / 3600
            print(f"---------- At stop Time: {current_stop_time_hour} ----------")

# =============================================================================
            #Restoration event Block

            if (self.timeline.iCurenttimeRestorationEvent()
                and self.iRestoration==True):

                logger.debug('\t Restoration Event ')
                event_time_list = self.restoration.perform_action(self.wn,
                                                                  current_stop_time)

                self.timeline.addEventTime(event_time_list,
                                           event_type='rst')

# =============================================================================
#           Damage (earthquake) event block

            #The following if block calculate teh effect of hydrualic significance
            if self.timeline.iCurrentTimeDamageEvent():
                self.registry.if_first_event_occured = True
                logger.debug('\t DAMAGE EVENT')

                if (self.iRestoration==True and
                    len(self.restoration.getHydSigPipeList() ) > 0):
                    # end of condition
                    last_demand_node_pressure = None
                    pipe_list = damage.getPipeDamageListAt(current_stop_time)
                    for pipe_name in pipe_list:
                        # next if block gets the "last_demand_node_pressure"
                        # for the first time
                        if type(last_demand_node_pressure) == type(None):
                            time_index = self.registry.result.node["pressure"].index
                            time_index = list(set(time_index) - set(self.registry.result.maximum_trial_time))
                            time_index.sort()
                            if len(time_index) > 0:
                                time_index = time_index[-1]
                            else:
                                self.registry.hydraulic_significance.loc[pipe_name] = -1000
                                continue
                                time_index = current_stop_time
                            demand_node_list = self.registry.demand_node_name_list
                            demand_node_list = set(demand_node_list).intersection(self.registry.result.node["pressure"].columns)
                            last_demand_node_pressure = self.registry.result.node["pressure"].loc[time_index, list(demand_node_list)]
                            last_demand_node_pressure.loc[last_demand_node_pressure[last_demand_node_pressure < 0].index] = 0

                        pipe = self.wn.get_link(pipe_name)
                        initial_pipe_status = pipe.initial_status
                        if initial_pipe_status == LinkStatus.Closed:
                            continue

                        pipe.initial_status = LinkStatus.Closed
                        hyd_sim = HydraulicSimulation(self.wn, settings, current_stop_time, worker_rank, self._prev_isolated_junctions, self._prev_isolated_links)
                        #self.hyd_temp = hyd_sim
                        duration          = self.wn.options.time.duration
                        report_time_step  = self.wn.options.time.report_timestep
                        try: # Run with modified EPANET V2.2
                            logger.info("Performing method 1")
                            rr, i_run_successful = hyd_sim.performSimulation(current_stop_time, True)
                            #if current_stop_time in rr.maximum_trial_time:
                                #pass
                                #self.registry.hydraulic_significance.loc[pipe_name] = -20000
                                #pipe.initial_status = initial_pipe_status
                                #self._prev_isolated_junctions = hyd_sim._prev_isolated_junctions
                                #self._prev_isolated_links     = hyd_sim._prev_isolated_links
                                #continue
                            demand_node_list  = self.registry.demand_node_name_list
                            demand_node_list  = set(demand_node_list).intersection(rr.node["pressure"].columns)
                            new_node_pressure = rr.node["pressure"].loc[current_stop_time, list(demand_node_list)]
                            new_node_pressure.loc[new_node_pressure[new_node_pressure < 0].index] = 0

                            hydraulic_impact  = (last_demand_node_pressure - new_node_pressure).mean()
                            self.registry.hydraulic_significance.loc[pipe_name] = hydraulic_impact

                        except Exception as epa_err_1:
                            raise
                            if epa_err_1.args[0] == 'EPANET Error 110':
                                logger.info("Method 1 failed. Performing method 2")
                                self.wn.options.time.duration        = duration
                                self.wn.options.time.report_timestep = report_time_step
                                self.registry.hydraulic_significance.loc[pipe_name] = -1
                        pipe.initial_status = initial_pipe_status
                        self._prev_isolated_junctions = hyd_sim._prev_isolated_junctions
                        self._prev_isolated_links     = hyd_sim._prev_isolated_links
                        self.wn.options.time.duration        = duration
                        self.wn.options.time.report_timestep = report_time_step

                #Apply pipe, nodal, Pump, and Tank damage
                damage.applyPipeDamages(self.wn, current_stop_time)
                damage.applyNodalDamage(self.wn, current_stop_time)
                damage.applyPumpDamages(self.wn, current_stop_time)
                damage.applyTankDamages(self.wn, current_stop_time)

                #initialize the teh restoration only when the restroatiopn is requested
                if self.iRestoration == True:
                    event_time_list = self.restoration.initialize(self.wn, current_stop_time) # starts restoration
                    self.timeline.addEventTime(event_time_list, event_type='rst')

# =============================================================================
#           This is for updatng the pipe damage log
            if settings["record_damage_table_logs"] == True:
                self.registry.updatePipeDamageTableTimeSeries(current_stop_time)
                self.registry.updateNodeDamageTableTimeSeries(current_stop_time)
# =============================================================================
#           runing hydraulic simulation

            #getthe next time break from timeline registar
            next_event_time = self.timeline.getNextTime()

            logger.debug('next event time is: '+ repr(next_event_time))
            logger.info('***** Running hydraulic *****')

            #The next section runs the epanet.

            #changes the implicit wntr type leak to explicit leak in epanet style
            self.wn.implicitLeakToExplicitReservoir(self.registry)

            # Creates Hydraulic simulation Object
            if type(worker_rank) != str:
                worker_rank = str(worker_rank)

            hyd_sim = HydraulicSimulation(self.wn, settings, current_stop_time, worker_rank, self._prev_isolated_junctions, self._prev_isolated_links)

            #self.hyd_temp     = hyd_sim
            duration          = self.wn.options.time.duration
            report_time_step  = self.wn.options.time.report_timestep
            
            successful_run = False
            epanet_exception = None
            for hydraulic_solver_i in range(1, 5, 1):
                if hydraulic_solver_i in self.hydraulic_solver_priority:
                    hydraulic_solver_name = (
                        self.hydraulic_solver_priority[hydraulic_solver_i]
                        )
                else:
                    continue
                
                print(f"method {hydraulic_solver_i}: {hydraulic_solver_name}")
                
                self.wn.options.time.duration = duration
                self.wn.options.time.report_timestep = report_time_step
                
                i_run_successful = None
                try:
                    successful_run = True
                    if hydraulic_solver_name == "Enhanced_EPANET":
                        logger.info("Performing method Enhanced_EPANET")
                        rr, i_run_successful = hyd_sim.performSimulation(
                            next_event_time,
                            True
                            )
                    
                    elif hydraulic_solver_name == "EPANET":
                        logger.info("Performing method EPANET")
                        rr, i_run_successful = hyd_sim.performSimulation(
                            next_event_time,
                            False
                            )
                        
                    elif hydraulic_solver_name == "ESTIMATERUNENHANCED":
                        logger.info("Performing method Estimate Run Enhanced")
                        rr, i_run_successful = hyd_sim.estimateRun(
                            next_event_time,
                            True
                            )
                    
                    elif hydraulic_solver_name == "ESTIMATERUN":
                        logger.info("Performing method Estimate Run")
                        rr, i_run_successful = hyd_sim.estimateRun(
                            next_event_time,
                            False
                            )
                    
                    elif hydraulic_solver_name == "ESTIMATEWITHOUT":
                        logger.info("Performing method Estimate Without Run")
                        rr, i_run_successful = hyd_sim.estimateWithoutRun(
                            self.registry.result,
                            next_event_time
                            )
                        
                except Exception as epa_err:
                    successful_run = False
                    epanet_exception = epa_err
                    print(epa_err.args[0])
                    if epa_err.args[0] == 'EPANET Error 110':
                        logger.info(f"Method {hydraulic_solver_name} "
                                    "failed.")
                
                if successful_run is True:
                    break
                
            if successful_run is False:
                raise epanet_exception 
                
                        
           
            self._prev_isolated_junctions = hyd_sim._prev_isolated_junctions
            self._prev_isolated_links     = hyd_sim._prev_isolated_links
            logger.info('***** Finish Running at time '+ repr(current_stop_time)+'  '+repr(i_run_successful)+' *****')

            #if the running is successful, then update teh WDn object with new
            #results and update the result in registery
            if i_run_successful==True:
                self.wn.updateWaterNetworkModelWithResult(rr, self.registry)
                self.registry.KeepLinearResult(rr, self._prev_isolated_junctions, node_attributes=['pressure','head','demand', 'leak'], link_attributes=['status', 'setting', 'flowrate'])
                if self.registry.settings["limit_result_file_size"] > 0:
                    self.dumpPartOfResult()
                #self.wp.unlinkBreackage(self.registry)
                self.wn.resetExplicitLeak()

# =============================================================================
        #self.resoration._registry.updateTankTimeSeries(self.wn, current_stop_time)
        #TODO: This section either must be expanded to all elemnt types or must be deleted
        self.registry.updateRestorationIncomeWaterTimeSeries(self.wn, current_stop_time)

        return self.registry.result



    def dumpPartOfResult(self):
        limit_size = self.registry.settings["limit_result_file_size"]
        limit_size_byte = limit_size * 1024 * 1024

        total_size = 0

        for att in self._linear_result.node:
            att_size = sys.getsizeof(self._linear_result.node[att] )
            total_size += att_size

        for att in self._linear_result.link:
            att_size = sys.getsizeof(self._linear_result.link[att] )
            total_size += att_size

        print("total size= "+repr(total_size/1024/1024))

        if total_size >= limit_size_byte:
            dump_result = SimulationResults()
            dump_result.node = {}
            dump_result.link = {}
            for att in self._linear_result.node:
                #just to make sure. it obly add tens of micro seconds for each
                #att

                self._linear_result.node[att].sort_index(inplace=True)
                att_result       = self._linear_result.node[att]
                if att_result.empty:
                    continue
                #first_time_index = att_result.index[0]
                last_valid_time  = []
                att_time_index   = att_result.index.to_list()
                last_valid_time  = [cur_time for cur_time in att_time_index if cur_time not in self._linear_result.maximum_trial_time]
                last_valid_time.sort()

                if len(last_valid_time) > 0:
                    last_valid_time = last_valid_time[-2]
                else:
                    print(att_time_index)
                    last_valid_time = att_time_index[-2]

                dump_result.node[att] = att_result.loc[:last_valid_time]
                last_valid_time_index = att_result.index.searchsorted(last_valid_time)
                self._linear_result.node[att].drop(att_result.index[:last_valid_time_index+1], inplace=True)

            for att in self._linear_result.link:
                #just to make sure. it obly add tens of micro seconds for each
                #att
                self._linear_result.link[att].sort_index(inplace=True)
                att_result       = self._linear_result.link[att]
                if att_result.empty:
                    continue
                #first_time_index = att_result.index[0]
                last_valid_time  = []
                att_time_index   = att_result.index.to_list()
                last_valid_time  = [cur_time for cur_time in att_time_index if cur_time not in self._linear_result.maximum_trial_time]
                last_valid_time.sort()

                if len(last_valid_time) > 0:
                    last_valid_time = last_valid_time[-2]
                else:
                    last_valid_time = att_time_index[-2]

                dump_result.link[att] = att_result.loc[:last_valid_time]
                last_valid_time_index = att_result.index.searchsorted(last_valid_time)
                self._linear_result.link[att].drop(att_result.index[:last_valid_time_index+1], inplace=True)

            dump_file_index = len(self.registry.result_dump_file_list) + 1

            if dump_file_index >= 1:
                list_file_opening_mode = "at"
            else:
                list_file_opening_mode = "wt"

            result_dump_file_name = self.registry.scenario_name + ".part"+str(dump_file_index)
            result_dump_file_dst  = os.path.join(self.registry.settings.process['result_directory'], result_dump_file_name)

            with open(result_dump_file_dst, "wb") as resul_file:
                pickle.dump(dump_result, resul_file)

            dump_list_file_name = self.registry.scenario_name + ".dumplist"
            list_file_dst       = os.path.join(self.registry.settings.process['result_directory'], dump_list_file_name)

            with open(list_file_dst, list_file_opening_mode) as part_list_file:
                part_list_file.writelines([result_dump_file_name])


            self.registry.result_dump_file_list.append(result_dump_file_name)
