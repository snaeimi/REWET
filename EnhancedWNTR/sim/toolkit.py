# -*- coding: utf-8 -*-
"""
Created on Wed May 26 16:11:36 2021

@author: snaeimi
"""
import wntr.epanet.toolkit
import numpy as np
import ctypes
import os, sys
from pkg_resources import resource_filename

import logging
logger = logging.getLogger(__name__)

class EpanetException(Exception):
    pass

class ENepanet(wntr.epanet.toolkit.ENepanet):
    def __init__(self, inpfile='', rptfile='', binfile='', changed_epanet=False):
        if changed_epanet==False or changed_epanet==True:
            self.changed_epanet=changed_epanet
        else:
            raise ValueError('changed_epanet must be a boolean value')
            
        if changed_epanet==False:
            super().__init__(inpfile, rptfile, binfile)
            return
        try:
            if os.name in ['nt','dos']:
            
                libepanet = resource_filename(__name__,'epanet/windows.dll')
                self.ENlib = ctypes.windll.LoadLibrary(libepanet)
            elif sys.platform in ['darwin']:
                libepanet = resource_filename(__name__,'epanet/mac.dylib')
                self.ENlib = ctypes.cdll.LoadLibrary(libepanet)
            else:
                libepanet = resource_filename(__name__,'epanet/linux.so')
                self.ENlib = ctypes.cdll.LoadLibrary(libepanet)
            return # OK!
        except Exception as E1:
            print(E1)
            raise E1
                
                        
    def ENn(self, inpfile=None, rptfile=None, binfile=None):
        """
        Opens an EPANET input file and reads in network data

        Parameters
        ----------
        inpfile : str
            EPANET INP file (default to constructor value)
        rptfile : str
            Output file to create (default to constructor value)
        binfile : str
            Binary output file to create (default to constructor value)
            
        """
        inpfile = inpfile.encode('ascii')
        rptfile = rptfile.encode('ascii') #''.encode('ascii')
        binfile = binfile.encode('ascii')
        s = "s"
        self.errcode = self.ENlib.EN_runproject(inpfile, rptfile, binfile, s)
        self._error()
        if self.errcode < 100:
            self.fileLoaded = True
        return    
        
            
    
    def ENSetIgnoreFlag(self, ignore_flag=0):
        if abs(ignore_flag - np.round(ignore_flag))>0.00001 or ignore_flag<0:
            logger.error('ignore_flag must be int value and bigger than zero'+str(ignore_flag))
        flag=ctypes.c_int(int(ignore_flag))
        #print('++++++++++++++++++++++')
        #self.ENlib.ENEXTENDEDsetignoreflag(flag)