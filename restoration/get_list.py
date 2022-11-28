# -*- coding: utf-8 -*-
"""
Created on Fri Dec 31 08:44:34 2021

@author: snaeimi
"""

import os
import pandas as pd
s=os.listdir("X:./Sina Naeimi/tempresult")
res = []
for k in s:
    kk=s[0].split('.')[:-1]
    res.append(kk[0])

res = pd.Series(res)

res.to_excel('alread_done.xlsx')