# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 18:50:57 2024

@author: snaeimi
"""
from enum import IntEnum

# REWET_STATUS = ["Successful", "Unsuccessful"]
ERROR_MESSAGES = {
    0: "Successful.",
    101: "REWET initialization faced an error. This happneded before running "
         "timeline. Please report this bug.",
    102: "REWET initialization faced an error. This happneded before running "
         "timeline because of the input. Please check the exception value "
         "for more information.",
    103: "REWET API is not initialized. Please Run REWET.initalzie first.",
    151: "REWET API failed because of wrong input type. "
         "Please check the exception value for more information.",
    152: "REWET API failed because of wrong input value. "
         "Please check the exception value for more information.",
    200: "Hydraulic Simulation failed.",
    500: "REWET's result processing failed. Please check the exception value "
         "for more information.",
            }


class REWET_STATUS(IntEnum):
    SUCCESSFUL = 0
    FAILED = 2
    INTIALIZATION_FAILED = 101
    INTIALIZATION_FAILED_BC_INPUT = 102
    NOT_INITIALIZED_FAILURE = 103
    WRONG_INPUT_TYPE_IN_API = 151
    WRONG_INPUT_VALUE_IN_API = 152
    HYDRAULIC_SIM_FAILED = 200
    RESULT_OUTPUT_PROCESS_FAILED = 500

    @property
    def exception(self):
        self.exception_value

    @exception.setter
    def exception(self, value):
        self.exception_value = value

    #def __init__(self, value):
        #super().__init__()
        #self.exception_value = None

    def __repr__(self):
        if self.value < 100:
            return f"REWET status is {self.name}.\n"
        else:
            error_message = ERROR_MESSAGES[self.value]
            return_msg = (f"REWET status is {self.name}.\n\t{error_message}" +
                          f"\nIf you  believe that this is a bug, please " +
                          f"report this problem to the developer via email " +
                          f"or submit an issue on the git repository: " +
                          "https://www.github.com/snaeimi/REWET")

            return return_msg

# =============================================================================
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
