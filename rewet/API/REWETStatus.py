# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 18:50:57 2024

@author: snaeimi
"""
from enum import Enum

REWET_STATUS = ["Successful", "Unsuccessful"]

class REWETStatus(Enum):
    
    def __init__(self, code=1):
        super().__init__("REWET Status", REWET_STATUS)
        self._rewet_status = self(code)
        
# =============================================================================
#     def __repr__(self):
#         return repr(self._code)
#     
#     @property
#     def code(self):
#         return self._code
#     
#     @property
#     def message(self):
#         return self._message
#     
#     @code.setter
#     def code(self, value):
#         if value and not isinstance(value, (float, int)):
#             raise ValueError('code must be an int or float')
#         self._code = self._code_enum(value)
# =============================================================================
