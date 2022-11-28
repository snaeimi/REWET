# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 14:49:28 2022

@author: snaeimi
"""

import pandas as pd

class base():
    def __init__(self):
        self.settings={}
    
    def __getitem__(self, key):
        return self.settings[key]
    
    def __setitem__(self, key, data):
        self.settings[key] = data

class Settings():
    def __init__(self):
        self.process  = Process_Settings()
        self.scenario = None
        
    def initializeScenarioSettings(self, scenario_index):
        self.scenario = Scenario_Settings(scenario_index, self.process)
    
class Process_Settings(base):
    def __init__(self):
        super().__init__()
        self.settings['maximun_worker_idle_time'  ] = 60
        self.settings['number_of_proccessor'      ] = 1
        """
        simulation settings
        """
        self.settings['RUN_TIME'                  ] = 10 + 24 * 0 #hours
        self.settings['simulation_time_step'      ] = 3600 #seconds # sina needs to be implemented
        self.settings['number_of_damages'         ] = 'single' #single or multiple. If single, indicate single damage files. If multiple, indicate "pipe_damage_file_list"
        self.settings['result_directory'          ] = ""
        self.settings['temp_directory'            ] = "RunFiles"
        self.settings['save_time_step'            ] = False # sina needs to be implemented
        """
        Hydraulic settings
        """
        self.settings['WN_INP'                    ] = "net3.inp"
        self.settings['demand_ratio'              ] = 1
        self.settings['solver'                    ] = 'ModifiedEPANETV2.2' # sina needs to be implemented
        self.settings['hydraulic_time_step'       ] = 3600 # sina needs to be implemented
        self.settings['solver_type'               ] = 'ModifiedEPANETV2.2'
        
        """
        Damage settings
        """
        self.settings['pipe_damage_file_list'     ] = "" #"preprocess/list2-3.xlsx" #"list_W147_6.xlsx" #'Nafiseh Damage Data/list.xlsx'
        self.settings['pipe_damage_file_directory'] = 'Nafiseh Damage Data/out' #''
        
        """
        Restoration settings
        """
        self.settings['Restoration_on'            ] = True
        self.settings['minimum_job_time'          ] = 3600 # sina needs to be implemented

        
        
        
        self.settings['dmg_rst_data_save'         ] = True
        #self.settings['ignore_damage_free'        ] = True
        self.settings['read_settings_file_name'   ] = '' #'starter/settings.xlsx' #this is for settings sensitivity analysis
        
        self.settings['mpi_resume'                ] = True #ignores the scenarios that are done
        self.settings['ignore_empty_pipe_damage'  ] = False
        self.settings['damage_method'             ] = 1
        
        self.settings['result_details'            ] = 'extended'
        self.settings['negative_node_elmination'  ] = True
        self.settings['nne_flow_limit'            ] = 0.5
        self.settings['nne_pressure_limit'        ] = -5
        self.settings['Virtual_node'              ] = True
        self.settings['damage_node_model'         ] = 'equal_diameter_reservoir'
        self.settings['pump_damage_relative_time' ] = True # sina needs to be implemented in the code
        self.settings['tank_damage_relative_time' ] = True # sina needs to be implemented in teh code
        
        
class Scenario_Settings(base):
    def __init__(self, scenario_index, process_object):
        super().__init__()
        
        """
        Hydraulic settings
        """
        self.settings['minimum_pressure'           ] = 8
        self.settings['required_pressure'          ] = 25
        self.settings['hydraulic_time_step'        ] = 3600
        
        """
        Damage settings
        """
        self.settings['Pipe_damage_input_method'   ]='excel' #excel or pickle
        #self.settings['pipe_damage_model'          ] = {"CI":{"alpha":-0.0038, "beta":0.1096, "gamma":0.0196, "a":2, "b":1 }, "DI":{"alpha":-0.0038, "beta":0.05, "gamma":0.04, "a":2, "b":1 } } # sina needs to be implemented
        self.settings['pipe_damage_model'          ] = {} # sina needs to be implemented
        self.settings['default_pipe_damage_model'  ] = {"alpha":-0.0038, "beta":0.1096, "gamma":0.0196, "a":2, "b":1 }
        self.settings['node_damage_model'          ] = {'a':0.0036, 'aa':1, 'b':0, 'bb':0, 'c':-0.877, 'cc':1, 'd':0, 'dd':0, 'e':0.0248, 'ee1':1, 'ee2':1, 'f':0, 'ff1':0, 'ff2':0, "damage_node_model": "equal_diameter_emitter"} # sina needs to be implemented
        
        """
        Restoration settings 
        """
        self.settings['Restoraion_policy_type'     ] = 'script' # sina needs to be implemented in teh code
        self.settings['Restortion_config_file'     ] = 'config.txt'
        self.settings['pipe_damage_discovery_model'] = {'method': 'leak_based', 'leak_amount': 0.025, 'leak_time': 43200} # sina needs to be implemented
        self.settings['node_damage_discovery_model'] = {'method': 'leak_based', 'leak_amount': 0.001, 'leak_time': 43200} # sina needs to be implemented
        self.settings['pump_damage_discovery_model'] = {'method': 'time_based', 'time_discovery_ratio': pd.Series([1], index = [3600*n for n in [0]])} # sina needs to be implemented
        self.settings['tank_damage_discovery_model'] = {'method': 'time_based', 'time_discovery_ratio': pd.Series([1], index = [3600*n for n in [0]])} # sina needs to be implemented
        self.settings['crew_out_of_zone_travel'    ] = False # sina needs to be implemented in teh code
        
        self.settings['equavalant_damage_diameter' ] = 1
        self.settings['pipe_damage_diameter_factor'] = 1
        
        
        if process_object['read_settings_file_name'] !=  '':
            self.readSettingsFiles(process_object['read_settings_file_name'], scenario_index)