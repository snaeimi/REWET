# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 17:40:16 2024

@author: snaeimi
"""

from pathlib import Path
from rewet.initial import Starter
from rewet.Input.Settings import Settings
from rewet.api.REWETStatus import REWET_STATUS
from rewet.Input import Input_IO
from rewet.EnhancedWNTR.network.model import WaterNetworkModel
from rewet import Damage
from rewet.restoration.registry import Registry
from rewet.restoration.model import Restoration
from rewet import Timeline
from wntrfr.utils.ordered_set import OrderedSet
from rewet.hydraulic.Simulation import HydraulicSimulation
from rewet.Input import Input_IO
from rewet import Result
from rewet.Project import Project

# TODO: These two functions can be moved to registry thus there won't be a need
#       for their import here. Also that would make more sense
##from rewet.timeline.timeline import KeepLinearResult
##from rewet.timeline.timeline import dumpPartOfResult


class API():
    def __init__(self, input_file):
        """
        Iniriates API class.

        Parameters
        ----------
        input_file : Path
            input to the path json or pkl file.

        Returns
        -------
        API class object.

        """
        self.status = REWET_STATUS(0)
        self.input_file = input_file
        self.starter = Starter()
        self.settings = Settings()
        self.starter.read_input_file(self.settings, self.input_file)
        self.current_time = 0
        self._prev_isolated_junctions = OrderedSet()
        self._prev_isolated_links = OrderedSet()
        self._if_init = False
        self.wn = WaterNetworkModel()
        self.project = None

    def apply_damage(self, current_stop_time, damage_scale=1):
        # TODO: add this possiblity into the REWET code first

        self.damage.applyPipeDamages(self.wn, current_stop_time, damage_scale)
        self.damage.applyNodalDamage(self.wn, current_stop_time, damage_scale)
        self.damage.applyPumpDamages(self.wn, current_stop_time, damage_scale)
        self.damage.applyTankDamages(self.wn, current_stop_time, damage_scale)

    def initiate(self, current_time=None, mpi_rank=None, debug=False):
        """
        Initiates API objects. Required before running REWET.

        Returns
        -------
        status_code : Status
            Run REWETStatus.

        """
        try:
            # default error code
            error = 101
            if current_time is not None:
                if not isinstance(current_time, int):
                    self.current_time = current_time
                else:
                    error = 102
                    self.current_time = int(current_time)
                    # if the code is ran after teh alst lien it means that the
                    # input is castable, so we lest revert back the error code
                    error = 101
            if not isinstance(debug, bool):
                raise ValueError("Debug value must be either true or False.")
            self.iDebug = debug
            self.mpi_rank = mpi_rank

            # initialize the only damage scenario
            # TODO: intialize can accept the number of scn in the function -->
            # not really, because regitery is realzied per scn.
            self.settings.initializeScenarioSettings(0)

            # TODO: Change the name of the keys. they do not represent the
            #       general damages
            damage_list_path = self.settings.process["pipe_damage_file_list"]
            damage_list_dir_path = self.settings.process[
                "pipe_damage_file_directory"]
            # reads damage list
            self.damage_list = Input_IO.read_damage_list(damage_list_path,
                                                   damage_list_dir_path)
            #create project file
            self.project = Project(self.settings, self.damage_list)

            # i = 0 bc we assume one scenario is given per initialization for now
            i = 0

            (pipe_damages,
             node_damages,
             pump_damages,
             tank_damages) = Input_IO.read_damage_files(
                self.settings.process['pipe_damage_file_directory'],
                self.damage_list.loc[i, 'Pipe Damage'],
                self.damage_list.loc[i, 'Nodal Damage'],
                self.damage_list.loc[i, 'Pump Damage'],
                self.damage_list.loc[i, 'Tank Damage'],
                self.settings.scenario['Pipe_damage_input_method'])

            # Setups the WDN WNTR object
            self.wn = WaterNetworkModel(
                Input_IO.resolve_path(self.settings.process['WN_INP']))
            delta_t_h = self.settings['hydraulic_time_step']
            self.wn.options.time.hydraulic_timestep = int(delta_t_h)

            demand_ratio = self.settings.process['demand_ratio']
            for junction_name, junction in self.wn.junctions():
                if junction.demand_timeseries_list[0].base_value > 0:
                    base_value = junction.demand_timeseries_list[0].base_value
                    junction.demand_timeseries_list[0].base_value = base_value * demand_ratio

            self.damage = Damage(None, self.settings.scenario)
            self.registry = Registry(self.wn,
                                     self.settings,
                                     self.damage_list.loc[i, 'Scenario Name'],
                                     pipe_damages,
                                     node_damages,
                                     pump_damages,
                                     tank_damages,
                                     self.damage)

            self.restoration = Restoration(self.settings.scenario['Restortion_config_file'],
                                           self.registry,
                                           self.damage)

            self.timeline = Timeline(self.wn,
                                     self.damage,
                                     self.registry,
                                     self.settings.process['RUN_TIME'],
                                     self.restoration,
                                     mode='PDD',
                                     i_restoration=self.settings.process['Restoration_on'])

            self._if_init = True

        except Exception as err:
            # sets the status
            self.status = REWET_STATUS(error)
            # sets the exception value
            self.status.exception_value = err
            # if debug mode is on, then raise the exception
            if self.iDebug is True:
                raise err
        else:
            self.status = REWET_STATUS(0)

        return self.status

    def run_hydraulic_simulation(self, time_step_length, update_wn=True):
        if self._if_init == False:
            self.status = REWET_STATUS(102)

        if not isinstance(time_step_length, int):
            self.status = REWET_STATUS(151)

        if time_step_length < 0:
            self.status = REWET_STATUS(152)

        else:
            # there is no rank in API, since API is not
            # Get the next time break time from the user input

            next_break_time = self.current_time + time_step_length
            # Turn implicit Leaks (WNTR style leaks) into explicit leaks (pipe and reservoir)
            self.wn.implicitLeakToExplicitReservoir(self.registry)
            # get a HydraulicSimualtor Object
            hyd_sim = HydraulicSimulation(self.wn, self.settings,
                                          self.current_time,
                                          self.mpi_rank,
                                          self._prev_isolated_junctions,
                                          self._prev_isolated_links)

            # Perform EPANET Simulation
            rr, i_run_successful = hyd_sim.performSimulation(next_break_time,
                                                             True)
            # Update isolated junctions and links
            # TODO: this can be part of hydsim when all of the simulation is
            # kept inside the the Hydarulic_Simulation class
            self._prev_isolated_junctions = hyd_sim._prev_isolated_junctions
            self._prev_isolated_links = hyd_sim._prev_isolated_links
        if not i_run_successful:
            self.status = REWET_STATUS(200)
        else:
            #update current time to the enxt time
            self.current_time = next_break_time

            # Update the Water Network Model (WNTR's model) with the result
            if update_wn:
                self.wn.updateWaterNetworkModelWithResult(rr,
                                                          self.registry)
            # Update the result into the result in registery
            self.registry.KeepLinearResult(rr, self._prev_isolated_junctions)

            # Check if the result-file size is limited. If so, dump part of it
            if self.registry.settings["limit_result_file_size"] > 0:
                pass
            # FIXME
                ## dumpPartOfResult()
            # Reset the added explicit leak mdoels
            self.wn.resetExplicitLeak()

            self.status = REWET_STATUS(0)

        return self.status

    def get_hydraulic_result(self, project_file_path=None):

        # res_dir_path = self.registry.settings["result_directory"]
        # project_file_path = Path(res_dir_path) / "project.prj"
        # project_file_path = Input_IO.resolve_path(project_file_path)


        if project_file_path == None:
            project_object = self.project
            rewet_result = Result(project_object, iObject=True)
        else:
            project_file_path = Input_IO.resolve_path(project_file_path)
            rewet_result = Result(project_file_path)

        scn_name = self.registry.scenario_name
        try:
            r = rewet_result.getAllDetailedData(scn_name)
        except Exception as err:
            # sets the status
            self.status = REWET_STATUS(500)
            # sets the exception value
            self.status.exception_value = err
            # if debug mode is on, then raise the exception
            if self.iDebug is True:
                raise err
        else:
            self.status = REWET_STATUS(0)

        return self.status, r

    def save_result(self):
        scn_name = self.registry.scenario_name
        r = self.registry.result
        Input_IO.save_single(self.settings,
                             r,
                             scn_name,
                             self.registry)

    def get_satisfied_demand_ratio(self):
        self.result = Result(self.project,
                             ignore_not_found=False,
                             to_neglect_file=None,
                             node_col='',
                             iObject=True)

        delivered_demand_ratio = self.result.getDeliveredDemandRatio(
                                        scn_name=self.registry.scenario_name)

        return delivered_demand_ratio



    def run_restoration_simulation():
        pass
