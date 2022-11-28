import pandas as pd

acceptable_keys = ['Restortion_config_file', 'Pipe_damage_input_method', 'number_of_damages',
         'equavalant_damage_diameter', 'pump_restoration_time_file', 'pump_damage_list',
         'minimum_pressure','required_pressure', 'pipe_damage_diameter_factor']

class base():
    def __init__(self):
        self.settings={}
    
    def __getitem__(self, key):
        return self.settings[key]

class Settings():
    def __init__(self):
        self.process  = Process_Settings()
        self.scenario = None
    
    def __setitem__(self, key, data):
        self.settings[key] = data

    def initializeScenarioSettings(self, scenario_index):
        self.scenario = Scenario_Settings(scenario_index, self.process)
        
    
    
class Process_Settings(base):
    def __init__(self):
        super().__init__()
        self.settings['number_of_proccessor']=1
        
        self.settings['temp_directory'            ] = "RunFiles"
        self.settings['result_directory'          ] = "Net3//Result"
        self.settings['maximun_worker_idle_time'  ] = 60
        self.settings['RUN_TIME'                  ] = 5 + 24 * 10 #hours
        self.settings['WN_INP'                    ] = "Net3/Net3.inp"
        self.settings['pipe_damage_file_list'     ] = "Net3/list.xlsx"
        self.settings['pipe_damage_file_directory'] = "Net3"
        self.settings['Restoration_on'            ] = True
        self.settings['dmg_rst_data_save'         ] = True
        self.settings['read_settings_file_name'   ] = '' #this is for settings sensitivity analysis
        self.settings['number_of_damages'         ] = 'single' #single or multiple. If single, indicate single damage files. If multiple, indicate "pipe_damage_file_list"
        self.settings['mpi_resume'                ] = True #ignores the scenarios that are done
        self.settings['ignore_empty_pipe_damage'  ] = False
        self.settings['damage_method'             ] = 1
        self.settings['demand_ratio'              ] = 1
        self.settings['result_details'            ] = 'extended'
        self.settings['negative_node_elmination'  ] = True
        self.settings['nne_flow_limit'            ] = 0.5 # This does not apply currently.
        self.settings['nne_pressure_limit'        ] = -5 # This does not apply currently
        self.settings['Virtual_node'              ] = True
        self.settings['damage_node_model'         ] = 'equal_diameter_emitter'
        self.settings['pump_damage_relative_time' ] = True #needs to be implemented in the code
        self.settings['tank_damage_relative_time' ] = True #needs to be implemented in teh code
        
        
class Scenario_Settings(base):
    def __init__(self, scenario_index, process_object):
        super().__init__()
        self.settings['Restortion_config_file'    ]='Net3/config.txt'
        self.settings['Pipe_damage_input_method'  ]='excel' #excel or pickle

        self.settings['minimum_pressure'           ] = 8
        self.settings['required_pressure'          ] = 25
        self.settings['equavalant_damage_diameter' ] = 1
        self.settings['pipe_damage_diameter_factor'] = 1
        
        
        if process_object['read_settings_file_name'] !=  '':
            self.readSettingsFiles(process_object['read_settings_file_name'], scenario_index)
        
    def readSettingsFiles(self, file_name, scenario_index):
        data = pd.read_excel(file_name)
#        data = data.set_index('Scenario Name')
        
        for key_ID, col in data.iteritems():
            if not key_ID in acceptable_keys:
                raise ValueError('key ID not recognized: ' + str(key_ID))
            self.settings[key_ID] = data.loc[scenario_index, key_ID]
            

