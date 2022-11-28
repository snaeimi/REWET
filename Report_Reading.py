# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 16:07:24 2022

@author: snaeimi
"""

import io
import time
import datetime

class Report_Reading():
    def __init__(self, file_addr):
        self.file_data = {}
        self.maximum_trial_time = []
        with io.open(file_addr, 'r', encoding='utf-8') as f:
            lnum = 0
            for line in f:
                #self.file_data[lnum] = line
                if "Maximum trials exceeded at" in line:
                    time_str = line.split("WARNING: Maximum trials exceeded at ")[1].split(" hrs")[0]
                    x = time.strptime(time_str.split(',')[0],'%H:%M:%S')
                    time_sec = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
                    time_sec = int(time_sec)
                    self.maximum_trial_time.append(time_sec)
                elif "System unbalanced at" in line:
                    time_str = line.split("System unbalanced at ")[1].split(" hrs")[0]
                    x = time.strptime(time_str.split(',')[0],'%H:%M:%S')
                    time_sec = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
                    time_sec = int(time_sec)
                    self.maximum_trial_time.append(time_sec)
                lnum += 1