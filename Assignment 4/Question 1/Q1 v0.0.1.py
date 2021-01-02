# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:51:52 2020

@author: s159774
"""
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
from scipy import stats

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
total_minutes = data['duration'].dt.seconds/60
histogram = total_minutes.hist(bins = 100, density = True)

mean_duration = total_minutes.mean() # first moment
var_duration = total_minutes.var() # second moment
skewness_duration = total_minutes.skew() # third moment
kurtosis_duration = total_minutes.kurtosis() # fourth moment

print("first moment: " + str(mean_duration)
+"\nsecond moment: " + str(var_duration)
+"\nthird moment: " + str(skewness_duration)
+"\nfourth moment:" + str(kurtosis_duration))

# fitting gamma distribution

alpha = (mean_duration**2)/(var_duration - mean_duration**2) # formula 5.8
beta = alpha/mean_duration # formula 5.9


n = 1000000
gammaDist = stats.gamma(alpha , scale = 1/beta)
poissonDist = stats.poisson(mean_duration)
exponDist = stats.expon(1/mean_duration)





stats.kstest(total_minutes , gammaDist.cdf)
stats.kstest(total_minutes, poissonDist.cdf)
stats.kstest(total_minutes, exponDist.cdf)



def plot():
    plt.plot(exponDist.rvs(100))
    