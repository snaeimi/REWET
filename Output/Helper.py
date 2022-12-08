# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 18:10:31 2022

@author: snaeimi
"""

import numba
import numpy as np

def hhelper(x):
    if x<0:
        return 0
    else:
        return x
    
@numba.jit()
def EPHelper(prob_mat):
    ep_mat = np.ndarray(prob_mat.size)
    for i in np.arange(prob_mat.size):
        j=0
        pi_one_minus_p = 1
        while j <= i:
            p = prob_mat[j]
            one_minus_p = 1 - p
            pi_one_minus_p *= one_minus_p
            j += 1
        ep_mat[i] = 1- pi_one_minus_p
    return ep_mat

def helper_outageMap(pandas_list):
    false_found_flag = False
    b_list = pandas_list.tolist()
    i = 0
    for b_value in b_list:
       if b_value == False:
           false_found_flag = True
           break
       i += 1
   
    return  false_found_flag, i-1

def hhelper(x):
    if x<0:
        return 0
    else:
        return x