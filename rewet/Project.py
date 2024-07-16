# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 09:03:57 2023

@author: snaeimi
"""

import os
import pickle
from rewet.Input.Input_IO import resolve_path

class Project():
    def __init__(self, project_settings, scenario_list):
        self.scenario_list    = scenario_list
        self.project_settings = project_settings

    @classmethod
    def createProjectFile(cls,
                          project_settings,
                          damage_list,
                          project_file_name):

        project = cls(project_settings, damage_list)
        project_file_addr = os.path.join(
            project_settings.process['result_directory'],
            project_file_name)

        # resolve the project file path
        project_file_addr = resolve_path(project_file_addr)
        with open(project_file_addr, 'wb') as f:
            pickle.dump(project, f)
