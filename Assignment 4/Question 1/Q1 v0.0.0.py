# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:51:52 2020

@author: s159774
"""
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_excel('Assignment4 Data.xlsx', parse_dates = True, header = None, names= ["start", "end"] )

data["duration"] = data["end"] - data["start"]
duration = data["duration"].astype('float')

plt.hist(duration, bins = 20, density = True)
plt.show()







 



