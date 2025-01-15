# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 22:55:06 2024

@author: naeim
"""
import logging
from rewet.hydraulic.Simulation import HydraulicSimulation

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

def run_hydraulics_EPANET(wn,
                   settings,
                   cur_time,
                   next_event_time,
                   prev_isolated_junctions,
                   prev_isolated_links,
                   linear_result):

    worker_rank = None
    hyd_sim = HydraulicSimulation(wn,
                                  settings,
                                  cur_time,
                                  worker_rank,
                                  prev_isolated_junctions,
                                  prev_isolated_links)

    #self.hyd_temp     = hyd_sim
    duration         = wn.options.time.duration
    report_time_step = wn.options.time.report_timestep

    try: # Run with modified EPANET V2.2
        logger.info("Performing method 1")
        rr, i_run_successful = hyd_sim.performSimulation(next_event_time,
                                                         True)
    except Exception as epa_err_1:
        if epa_err_1.args[0] == 'EPANET Error 110':
            logger.info("Method 1 failed. Performing method 2")
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
                        wn.options.time.duration        = duration
                        wn.options.time.report_timestep = report_time_step
                        #hyd_sim.rollBackPipeClose()
                        rr, i_run_successful = hyd_sim.estimateRun(next_event_time, True)
                    except Exception as epa_err_3:
                        if epa_err_3.args[0] == 'EPANET Error 110':
                            logger.info("Method 3 failed. Performing method 4")
                            try: # Extend result from teh reult at the begining of teh time step with modified EPANET V2.2
                                wn.options.time.duration        = duration
                                wn.options.time.report_timestep = report_time_step
                                rr, i_run_successful = hyd_sim.performSimulation(next_event_time, False)
                            except Exception as epa_err_4:
                                if epa_err_4.args[0] == 'EPANET Error 110':
                                    try:
                                        wn.options.time.duration        = duration
                                        wn.options.time.report_timestep = report_time_step
                                        logger.info("Method 4 failed. Performing method 5")
                                        # Extend result from teh reult at the begining of teh time step with modified EPANET V2.2
                                        rr, i_run_successful = hyd_sim.estimateRun(next_event_time, False)
                                    except Exception as epa_err_5:
                                        if epa_err_5.args[0] == 'EPANET Error 110':
                                            try:
                                                print("Method 5 failed. Performing method 6")
                                                wn.options.time.duration        = duration
                                                wn.options.time.report_timestep = report_time_step
                                                rr, i_run_successful = hyd_sim.estimateWithoutRun(linear_result,
                                                                                                  next_event_time)
                                            except Exception as epa_err_6:
                                                logger.info("ERROR in rank="+repr(worker_rank)+" and time="+repr(cur_time))
                                                raise epa_err_6
                                        else:
                                            raise epa_err_5
                                else:
                                    raise epa_err_4
                        else:
                            raise epa_err_3
                else:
                    raise epa_err_2
        else:
            raise epa_err_1
    prev_isolated_junctions = hyd_sim._prev_isolated_junctions
    prev_isolated_links     = hyd_sim._prev_isolated_links
    logger.info('***** Finish Running at time '+ repr(cur_time)+'  '+repr(i_run_successful)+' *****')
