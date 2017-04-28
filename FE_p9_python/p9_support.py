# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 18:07:43 2016

@author: Comandini Leonardo, Nicoletti Antea, Schiavon Andrea
"""

#Library for Project9 including the functions that 'generic' support the code

# 1)  xldate_to_datetime
# 2)  str_to_date
# 3)  yearfrac
# 4)  interp_bootstrap
# 5)  BPV_fixed            3)
# 6)  BPV_float            3)
# 7)  pay_fixed
# 8)  pay_float
# 9)  filter_pay_fix
# 10) filter_pay_flo
# 11) find_t0

#--start------------------------------import-----------------------------------
import datetime                          # 1) 2) 3)
import numpy as np                       #          4)       7)
from p9_business import (busday,         #          4)
                         monthdelta,     #                         9)
                         monthdeltaMF)   #                   7) 8)
 
#---end-------------------------------import-----------------------------------

#--start-------------------------xldate_to_datetime----------------------------
#Change the format from the Excel serial number format to datetime.date

# INPUT:
#xldate = date in the serial excel format          [int]
# OUTPUT:
#temp+delta = date in datetime.date format         [datetime.date]

def xldate_to_datetime(xldate):
    #temp = datetime.datetime(1900, 1, 1)
    temp = datetime.date(1899, 12, 30) #Check which is the correct one
    delta = datetime.timedelta(days=xldate)
    return temp+delta
#---end--------------------------xldate_to_datetime----------------------------

#--start----------------------------str_to_date--------------------------------
#Convert from string format '%d/%m/%Y' to datetime.date

# INPUT:
#str = date in string format                  [string]
# OUTPUT:
#      date in datetime.date format           [datetime.date]

def str_to_date(str):
    return (datetime.datetime.strptime(str,'%d/%m/%Y')).date()
#---end-----------------------------str_to_date--------------------------------

#--start------------------------------yearfrac---------------------------------
#Compute the year fraction between first_date and second_date with the 'flag' 
#convention    

# INPUT:
#t1 = first date                  [datetime] or [datetime.date]
#t2 = second date  (t1<t2)        [datetime] or [datetime.date]
#flag = convention                [1=act365 , 2=act360 , 3 = 30/360
#                             4=act/act (datetime.date), 41=act/act (datetime)]
# OUTPUT: 
#yearfrac                         [real]

def yearfrac(t1,t2,flag):
    
    if flag is 1:  #act/365
        return (t2-t1).days/365
                    
    if flag is 2:  #act/360
        return (t2-t1).days/360
                    
    if flag is 3:  #30/360
        years = t2.year - t1.year
        if t2.month < t1.month or (t2.month is t1.month and t2.day < t1.day):
            years = years-1 #now years are the years fully passed between t1,t2
        months = t2.month - t1.month #<=0 iff the previous if was true
        days = t2.day - t1.day
        if t2.day < t1.day:
            months = months - 1
            days = days+30
        if months < 0:
            months = 12+months
        return (360*years+30*months+days)/360
       
    if flag is 4: #act/act     #for datetime.date
        t1plus1y = datetime.date(t1.year+1,t1.month,t1.day)
        return (t2-t1).days/(t1plus1y-t1).days
        
    if flag is 41: #act/act    #for datetime
        t1plus1y = datetime(t1.year+1,t1.month,t1.day)
        return (t2-t1).days/(t1plus1y-t1).days
    
#---end-------------------------------yearfrac--------------------------------- 

#--start--------------------------interp_bootstrap-----------------------------
# INPUT:
#dates, zero_rates = a row of the original dataframe [dataframe]   
#   dates      = self.dates.loc[[t0], :]
#   zero_rates = self.zero_rates.loc[[t0], :]
#new_dates = dates in which the B has to be computed [LIST! of datetime.date] 
#  REM: new_dates has to be increasing
# OUTPUT:
#B = list of discount factor                    [list of real]
def interp_bootstrap(dates,zero_rates,new_dates):
    ST = busday(dates.index[0],2) #settlement date
    
    #list of distances in days from the settlement
    dates_list = [(i-ST).days for i in dates.loc[dates.index[0]].tolist()]
    dates_list = [0] + dates_list
    new_dates_list = [(i-ST).days for i in new_dates]
    zr_list = zero_rates.loc[dates.index[0]].tolist() #suboptimal
    zr_list = [zr_list[0]] + zr_list
    #including the dates before the 1 month                       
    z_interp = [np.interp(i, dates_list, zr_list) for i in new_dates_list]
    B = [np.exp(-z_interp[i]*new_dates_list[i]/365) #act/365
         for i in range(np.size(new_dates))]
    return B #[list]

#---end---------------------------interp_bootstrap-----------------------------
    
#--start-----------------------------BPV_fixed---------------------------------
#compute the BPV of the fixed leg
    
# INPUT:
#dates =                                             [list of datetime.date]
#[t_{-1} t_1 ... M] 
#B = discount factor corresponding to dates          [list of real]
#c = coupon                                          [real]
#
# OUTPUT:
#BPV = basis point value                             [real]
# USES:
#yearfrac

def BPV_fixed(dates,B,c):
    return B[-1]+c*sum([B[i]*yearfrac(dates[i],dates[i+1],4) 
                        for i in range(np.size(dates)-1)]) #act/act

#---end------------------------------BPV_fixed---------------------------------  
    
#--start-----------------------------BPV_float---------------------------------
#compute the BPV of the float leg
    
# INPUT:
#dates =                                             [list of datetime.date]
#[t_0 t_1 ... M] 
#B = discount factor corresponding to dates          [list of real]
#
# OUTPUT:
#BPV = basis point value                             [real]
# USES:
#yearfrac

def BPV_float(dates,B):
    return sum([B[i]*yearfrac(dates[i],dates[i+1],2) 
                for i in range(np.size(dates)-1)]) #act/360
 
#---end------------------------------BPV_float---------------------------------    

#--start----------------------------pay fixed----------------------------------
#The dates in which the fixed payments occur are computed.
#Starting from the maturity and going back of 12/freq months each time, until 
#the first coupon date is reached. 
#Each payment date is a business day computed with the convention 'modified 
#follow'.
#Then the settlement date is attached because it may be useful in the 
#computation of BPV_fixed and in the accrual
#REM: it may occurs that going back the first coupon date is not reached. 
#     We do the reasonable assumption that if we don't reach it precisely we 
#     arrive 'very close' to it, i.e. there exist k€N+ such that 
#     (FC-(M-k*MB)).days is almost zero days (k=(NB)*MB) 
#
# INPUT:
#M    = maturity          [datetime.date]
#FC   = first coupon date [datetime.date]
#ST   = settlement date   [datetime.date] #we need it to compute the accrual
#freq = frequency         [real]  REM: works better if freq|12
# OUTPUT:
#payments = dates in which the fixed payments occurs [list of datetime.date]
#         = [ST  FC  FC+MB   ...  M-MB  M] 
#            REM: payments[1] is 'almost' FC (most of the times it is)
# USES:
#monthdeltaMF

def pay_fixed(M,FC,ST,freq):
    #'//' integer division
    MB = 12//freq                            #Number of months back
    #different sintax because some approx could occur    
    NB = int(np.round((M-FC).days/365*freq)) #Number of times back 
    #inizialize the list assign at each element the value of the last
    payments = (NB+1)*[M] 
    #assign the value from the second last to the first
    for i in range(1,NB+1):
        payments[NB-i] = monthdeltaMF(M, -i*MB)
    payments = [ST] + payments
    return payments  

#---end-----------------------------pay fixed----------------------------------

#--start----------------------------pay float----------------------------------
#The dates in which the floating payments occurs are computed.
#Starting from the maturity and going back of 12/freq months each time, until 
#the last date strictly after the settlement. 
#Each payment date is a business day computed with the convention 'modified 
#follow'.
#
# INPUT:
#M    = maturity          [datetime.date]
#ST   = settlement date   [datetime.date]
#freq = frequency         [real]  REM: works better if 12|freq
# OUTPUT:
#payments = dates in which the fixed payments occurs [list of datetime.date]
#         = [t*  t*+MB   ...  M-MB  M] where t* = min{t>ST, t=M-k*MB}
# USES:
#monthdeltaMF

def pay_float(M,ST,freq):
    #'//' integer division
    MB = 12//freq                            #Number of months back  
    #now we round to the lower integer part because we don't want to overstep ST
    NB = int((M-ST).days/365*freq)           #Number of times back 
    #inizialize the list assign at each element the value of the last
    payments = (NB+1)*[M] 
    #assign the value from the second last to the first
    for i in range(1,NB+1):
        payments[NB-i] = monthdeltaMF(M, -i*MB)
    return payments  
#---end-----------------------------pay float----------------------------------    

#--start--------------------------filter_pay_fix------------------------------- 
#

# INPUT:
#payments = list of dates (increasing)       [list of datetime.date]
#t0 = date to compare                        [datetime.date]
# OUTPUT:
#           list cut                         [list of datetime.date]
# CASE1:[t_{-1}    t_1  ...  M ]   
#               ^                                
#              t0                               
def filter_pay_fix(payments, t0):
    i=1
    while payments[i] <= t0:
        i += 1 
    return payments[(i-1):]

#---end---------------------------filter_pay_fix-------------------------------
        
#--start--------------------------filter_pay_flo-------------------------------
#cut the list payments with only the dates > st
 
# INPUT:
#payments = list of dates (increasing)       [list of datetime.date]
#st = date to compare                        [datetime.date]
# OUTPUT:
#           list cut                         [list of datetime.date]
# [st=t_0  t_1  ...  M]  

def filter_pay_flo(payments, st):
    return [st] + [x for x in payments if x > st]

#---end---------------------------filter_pay_flo-------------------------------        

#--start----------------------------find_t0------------------------------------
#find the t0 s.t. t0€[t0+2m,t0+10y] and t0 has the price for the bond

# INPUT:
#M = maturity                           [datetime.date]
#t0 = dates                             [Index of datetime.date]
#bond = bond name                       [string]
#bond_prices = prices dataframe         [dataframe]
# OUTPUT:
#t0_cut = dates cut                     [Index of datetime.date]
# USES:
#monthdeltaMF
import pandas as pd
def find_t0(M,t0,bond,bond_prices):
    low, up = monthdelta(M,-2), monthdelta(M,-12*10)
    #create a new dataframe with the prices
    df = pd.DataFrame(index=t0, columns=['price'])
    df.price = bond_prices[bond]    
    #cut the t0s which have not a price corresponding to that date
    df = df.copy().dropna(how='all')
    #cut the t0s outside the interval [t0+2m,t0+10y]  
    t0_cut = df.index[(df.index <= low) & (df.index >= up)]
    return t0_cut

#---end-----------------------------find_t0------------------------------------