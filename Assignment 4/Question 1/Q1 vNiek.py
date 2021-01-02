# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 20:18:53 2020

@author: s159774
"""


import matplotlib.pyplot as plt

import datetime as dt
import numpy as np
from scipy import stats
import pandas as pd


data = pd.read_excel('initialdata.xlsx', parse_dates = True, header = None, names= ["start", "end"] )



############################
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
data = new_df
data["duration"] = data["end"] - data["start"]

# Sort by start date
data = data.sort_values(by=['start'])
# Add interarrival rates between start times
data["delta"] = data['start']-data['start'].shift()
data["delta_end_start"] = data['start']-data['end'].shift()

#############################

data["duration"] = data["end"] - data["start"]
data["duration"] = data.duration.dt.seconds/60
data.sort_values(by=['start'])

data["delta"] = data.delta.dt.seconds/60






data_weekdays0 = data[data['start'].dt.weekday == 0]
data_weekdays1 = data[data['start'].dt.weekday == 1]
data_weekdays2 = data[data['start'].dt.weekday == 2]
data_weekdays3 = data[data['start'].dt.weekday == 3]
data_weekdays4 = data[data['start'].dt.weekday == 4]
data_weekdays = pd.concat([data_weekdays0, data_weekdays1, data_weekdays2, data_weekdays3, data_weekdays4])
data_weekdays1 = data_weekdays.dropna()
data_weekdays1.sort_values(by=['start'])
data_weekdays5 = data[data['start'].dt.weekday == 5]
data_weekdays6 = data[data['start'].dt.weekday == 6]
data_weekends = pd.concat([data_weekdays5, data_weekdays6])
data_weekends.sort_values(by=['start'])


#data = data[data.duration != 1] # all observations of 1 are assumed to be inaccurate measures

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


duration_dict = dict()
delta_dict = dict()
for i in range(0,7):
    weekday = data[data['start'].dt.weekday == i]
    duration_dict[i] = weekday.duration
    delta_dict[i] = weekday[1:].delta  # 1: because first value is nan
    
def get_moments(data):
    moment1 = data.mean()
    moment2 = data.var()
    moment3 = data.skew()
    moment4 = data.kurtosis()
    return moment1, moment2, moment3, moment4
    
def fit_expon(data):
    loc, scale = stats.expon.fit(data) # fits parameters based on MLE 
    exponDist = stats.expon(loc, scale)
    return exponDist

def fit_gamma(data):
    est_alpha, loc, scale = stats.gamma.fit(data)
    gammaDist = stats.gamma(est_alpha, loc, scale)
    return gammaDist

def fit_weibull(data):
    shape, loc, scale = stats.weibull_min.fit(data)
    weibullDist = stats.weibull_min(shape, loc, scale)
    return weibullDist

def fit_lognorm(data):
    s, loc, scale = stats.lognorm.fit(data)
    lognormDist = stats.lognorm(s, loc, scale)
    return lognormDist
    

def GOF(data, dist):
    kstest = stats.kstest(data, dist.cdf)
    return kstest

#==========================RESULTS=========================================
#========Results DURATION==================================================
def duration_stats(data):
    print('results Goodness of Fit for duration data\n')
    exponDist = fit_expon(data.duration)  
    gammaDist = fit_gamma(data.duration)
    weibullDist = fit_weibull(data.duration)
    lognormDist = fit_lognorm(data.duration)
    fig = plt.figure()
    xs = np.arange(min(data.duration),max(data.duration), 0.01)
    ys1 = exponDist.pdf(xs)
    ys2 = gammaDist.pdf(xs)
    ys3 = weibullDist.pdf(xs)
    ys4 = lognormDist.pdf(xs)
    plt.title('duration all data')
    plt.plot(xs, ys1, color = 'red')
    plt.plot(xs, ys2, color = 'blue')
    plt.plot(xs, ys3, color = 'yellow')
    plt.plot(xs, ys4, color = 'cyan')
    plt.hist(data.duration, bins = 20, rwidth = 0.8, density  = True)
    plt.ylim(0,0.03)
    plt.xlim(0,350)
    plt.legend(['exponential distribution', 'gamma distribution', 'weibull distribution', 'lognorm'])
    plt.show()
    print('all data' +"-expon-  " + str(GOF(data.duration, exponDist)))
    print('all data' +"-gamma-  "+ str(GOF(data.duration, gammaDist)))
    print('all data' +"-weibull-  "+ str(GOF(data.duration, weibullDist)))
    print('all data' +"-lognorm-  "+ str(GOF(data.duration, lognormDist)))
    print('\n')
    return

def duration_stats_weekday(data):
    for i in range(0,7):
        exponDist = fit_expon(duration_dict[i])
        gammaDist = fit_gamma(duration_dict[i])
        weibullDist = fit_weibull(duration_dict[i])
        lognormDist = fit_lognorm(duration_dict[i])
        print('mean duration' + str(duration_dict[i].mean()))
        fig = plt.figure()
        xs = np.arange(min(duration_dict[i]),max(duration_dict[i]), 0.1)
        ys1 = exponDist.pdf(xs)
        ys2 = gammaDist.pdf(xs)
        ys3 = weibullDist.pdf(xs)
        ys4 = lognormDist.pdf(xs)
        plt.title('duration')
        plt.plot(xs, ys1, color = 'red')
        plt.plot(xs, ys2, color = 'blue')
        plt.plot(xs, ys3, color = 'yellow')
        plt.plot(xs, ys4, color = 'cyan')
        plt.hist(duration_dict[i], bins = 10, rwidth = 0.8, density  = True)
        plt.ylim(0,0.05)
        plt.legend(['exponential distribution', 'gamma distribution', 'weibull distribution', 'lognorm'])
        plt.show()
        print(weekdays[i] +"-expon-  " + str(GOF(duration_dict[i], exponDist)))
        print(weekdays[i] +"-gamma-  "+ str(GOF(duration_dict[i], gammaDist)))
        print(weekdays[i] +"-weibull-  "+ str(GOF(duration_dict[i], weibullDist)))
        print(weekdays[i] +"-lognorm-  "+ str(GOF(duration_dict[i], lognormDist)))
        print('\n')
    return
#======results INTERARRIVAL================================================= 
def interarrival_stats(data): 
    print('results Goodness of Fit for interarrival data\n')  
    exponDist = fit_expon(data[1:].delta)  
    gammaDist = fit_gamma(data[1:].delta)
    weibullDist = fit_weibull(data[1:].delta)
    lognormDist = fit_lognorm(data[1:].delta)
    fig = plt.figure()
    xs = np.arange(min(data[1:].delta),max(data[1:].delta), 0.1)
    ys1 = exponDist.pdf(xs)
    ys2 = gammaDist.pdf(xs)
    ys3 = weibullDist.pdf(xs)
    ys4 = lognormDist.pdf(xs)
    
    plt.title('interarrival all data')
    plt.plot(xs, ys1, color = 'red')
    plt.plot(xs, ys2, color = 'blue')
    plt.plot(xs, ys3, color = 'yellow')
    plt.plot(xs, ys4, color = 'cyan')
    
    plt.hist(data[1:].delta, bins = 10, rwidth = 0.8, density  = True)
    plt.ylim(0,0.015)
    
    plt.legend(['exponential distribution', 'gamma distribution', 'weibull distribution', 'lognorm'])
    plt.show()
    plt.close()
    
    print('GOF all Data - expon:  ' + str(GOF(data.delta[1:], exponDist)))
    print('GOF all Data - gamma:  ' + str(GOF(data.delta[1:], gammaDist)))
    print('GOF all Data -weibull- '+ str(GOF(data.delta[1:], weibullDist)))
    print('GOF all Data -lognorm- ' + str(GOF(duration_dict[i], lognormDist)))
    
def interarrival_stats_weekday(data):
    for i in range(0,7):
        exponDist = fit_expon(delta_dict[i])
        gammaDist = fit_gamma(delta_dict[i])
        weibullDist = fit_weibull(delta_dict[i])
        lognormDist = fit_lognorm(delta_dict[i])
        print('mean interarival' + str(delta_dict[i].mean()))
        fig = plt.figure()
        plt.hist(delta_dict[i], bins = 10, rwidth = 0.8, density  = True)
        xs = np.arange(min(delta_dict[i]),max(delta_dict[i]), 0.1)
        ys1 = exponDist.pdf(xs)
        ys2 = gammaDist.pdf(xs)
        ys3 = weibullDist.pdf(xs)
        ys4 = lognormDist.pdf(xs)
        plt.plot(xs, ys1, color = 'red')
        plt.plot(xs, ys2, color = 'blue')
        plt.plot(xs, ys3, color = 'yellow')
        plt.plot(xs, ys4, color = 'cyan')
        plt.title('interarrival')
        plt.hist(delta_dict[i], bins = 20, rwidth = 0.8, density  = True)
        plt.ylim(0,0.015)
        plt.legend(['exponential distribution', 'gamma distribution', 'weibull distribution', 'lognorm'])
        plt.show()
        plt.close()
        print(weekdays[i] +"-expon-  " + str(GOF(delta_dict[i], exponDist)))
        print(weekdays[i] +"-gamma-  "+ str(GOF(delta_dict[i], gammaDist)))
        print(weekdays[i] +"-weibull-  "+ str(GOF(delta_dict[i], weibullDist)))
        print(weekdays[i] +"-lognorm-  "+ str(GOF(delta_dict[i], lognormDist)))
        print('\n')
    return
 
# all data    
print('results duration all data')
duration_stats(data)
print('resutls interarrival all data')
interarrival_stats(data)

# seperate weekdays
print('results duration seperate weekdays') 
duration_stats_weekday(data)
print('results interarrival seperate weekdays')
interarrival_stats_weekday(data)

# workingdays
print('results duration mondays - fridays')
duration_stats(data_weekdays1) 
print('results interarrival mondays- fridays')
interarrival_stats(data_weekdays1)

# weekends
print('results duration weekends')
duration_stats(data_weekends)
print('results interarrival weekends')
interarrival_stats(data_weekends)
    
    
    
    