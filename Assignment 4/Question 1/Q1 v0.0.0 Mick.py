# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:51:52 2020

@author: s159774
"""
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_excel('Assignment4 Data.xlsx', parse_dates = True, header = None, names= ["start", "end"] )

data["duration"] = data["end"] - data["start"]


# SUMMARY STATISTICS
# Plot a graph with the beginning hours of an incident
data.groupby(data['start'].dt.hour).count()['start'].plot(kind='bar')

# Number of incidents per weekday
data.groupby(data['start'].dt.weekday).count()['start'].plot(kind='bar')

# Number of incidents per day of month
data.groupby(data['start'].dt.day).count()['start'].plot(kind='bar')

# Number of incidents per month
data.groupby(data['start'].dt.month).count()['start'].plot(kind='bar')

# Plot a graph with the duration of an incidenter
round(data["duration"].dt.total_seconds() / 60).plot.hist(bins = 600, xlim=(0,50))
# TO DO: Discuss if duration = 1 should be filtered out.


# FITTING THE DATA
