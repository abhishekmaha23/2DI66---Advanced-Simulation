# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:51:52 2020

@author: s159774
"""
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import datetime as dt
import numpy as np
from scipy import stats

data = pd.read_excel('initialdata.xlsx', parse_dates = True, header = None, names= ["start", "end"] )

# Sort by start date
data = data.sort_values(by=['start'])
# Add interarrival rates between start times
data["delta_end_start"] = data['start']-data['end'].shift()

new_data = []
for i, row in data.iterrows():
    new_row = dict()
    if(not pd.isnull(row['delta_end_start']) and row['delta_end_start'].total_seconds() < 0):
        new_data[-1]['end'] = row['end']
    else:
        new_row['start'] = row['start']
        new_row['end'] = row['end']
        new_data.append(new_row)
new_df = pd.DataFrame(new_data)
#data = new_df
data["duration"] = data["end"] - data["start"]

# Sort by start date
data = data.sort_values(by=['start'])
# Add interarrival rates between start times
data["delta"] = data['start']-data['start'].shift()
data["delta_end_start"] = data['start']-data['end'].shift()

# SUMMARY STATISTICS
# Plot a graph with the beginning hours of an incident
data.groupby(data['start'].dt.hour).count()['start'].plot(kind='bar')

# Now do it for every day seperatly
for name, group in data.groupby(data['start'].dt.weekday):
    print("Plotting day No: " + str(calendar.day_name[name]))
    group.groupby(group['start'].dt.hour).count()['start'].plot(kind='bar', ylim=(0,18))
    plt.xlabel("Hour of day")
    plt.ylabel("Total number of incidents")
    plt.show()

# Number of incidents per weekday
data.groupby(data['start'].dt.weekday).count()['start'].plot(kind='bar')

# Number of incidents per day of month
data.groupby(data['start'].dt.day).count()['start'].plot(kind='bar')

# Number of incidents per month
data.groupby(data['start'].dt.month).count()['start'].plot(kind='bar')
plt.xlabel("Month")
plt.ylabel("Total number of incidents")
bars = ('January', 'Febrary', 'March', 'April', 'May')
y_pos = np.arange(len(bars))
plt.xticks(y_pos, bars)
plt.show()

# Plot a graph with the duration of an incidenter
round(data["duration"].dt.total_seconds() / 60).plot.hist(bins = 100)
plt.xlabel("Duration in minutes")
plt.plot()

# Plot a graph with all interarrival times in minutes
round(data['delta'].dt.total_seconds() / 60).plot.hist(bins = 3000)
data.groupby(round(data['delta'].dt.total_seconds() / 60)).count()

# TO DO: Discuss if duration = 1 should be filtered out.

# FITTING THE DATA
total_minutes = data['duration'].dt.seconds/60
histogram = total_minutes.hist(bins = 100, density = True)

total_minutes_new = total_minutes[total_minutes != 1]
mean_duration = total_minutes.mean() # first moment
var_duration = total_minutes.var() # second moment
skewness_duration = total_minutes.skew() # third moment
kurtosis_duration = total_minutes.kurtosis() # fourth moment

mean_duration2 = total_minutes_new.mean()
var_duration2 = total_minutes_new.var()
skewness_duration2 = total_minutes_new.skew()
kurtosis_duration2 = total_minutes_new.kurtosis()

delta_in_minutes = data["delta"].dt.seconds[1:]/60

mean_delta = delta_in_minutes.mean()
var_delta = delta_in_minutes.var()

print("first moment: " + str(mean_duration)
+"\nsecond moment: " + str(var_duration)
+"\nthird moment: " + str(skewness_duration)
+"\nfourth moment:" + str(kurtosis_duration))

# fitting gamma distribution

alpha = (mean_duration**2)/(var_duration - mean_duration**2) # formula 5.8
beta = alpha/mean_duration # formula 5.9

alpha2 = (mean_duration2**2)/(var_duration2 - mean_duration2**2) # formula 5.8
beta2 = alpha2/mean_duration2 # formula 5.9

xlambda = 1/mean_delta

exponDist_delta = stats.expon(xlambda)


n = 1000000
gammaDist = stats.gamma(alpha , scale = 1/beta)
gammaDist_new = stats.gamma(alpha2, scale = 1/beta2)
poissonDist = stats.poisson(mean_duration)
exponDist = stats.expon(1/mean_duration)


stats.kstest(delta_in_minutes, exponDist_delta.cdf)


stats.kstest(total_minutes , gammaDist.cdf)
stats.kstest(total_minutes_new , gammaDist_new.cdf)
stats.kstest(total_minutes, poissonDist.cdf)
stats.kstest(total_minutes, exponDist.cdf)



def plot():
    plt.plot(exponDist.rvs(100))
    
"""   
xs = np.arange(min(total_minutes), max(total_minutes), 0.1)
ys1 = gammaDist.pdf(xs)
ys2 = plt.hist(total_minutes, density = True, bins = 40)
plt.plot(xs, ys1, color = 'red')
plt.plot(xs, ys2, '--', color ='blue')
plt.legend([ 'Actual distribution', 'Fitted distribution'])
plt.show ()
"""
n = len(total_minutes_new)
ys = np.arange(1/n , 1+1/n , 1/n)
xs = sorted(total_minutes_new)
plt.figure()
plt.step(xs, ys, color = 'black')
plt.plot(xs, gammaDist_new.cdf(xs), color = 'red') 
plt.show()   

data2 = data[data['start'].dt.weekday == 1] 