# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 13:31:59 2024

@author: naeim
"""

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=0)
#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logging.basicConfig(filename='myapp.log', level=logging.INFO)

def f():
    print("Kheyli")
    #logger.info("Kheyli")
    
if __name__ == "__main__":
    f()