# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 18:06:25 2016

@author: Comandini Leonardo, Nicoletti Antea, Schiavon Andrea
"""

#This library contains the 'business days' functions used in the project

# 1} EurHolidayCalendar (class, to generate 2] )
# 2] bday               (object, used in 3) 4) 5) )
# 3) isbday
# 4) busday
# 5) busdayMF
# 6) monthdelta
# 7) monthdeltaMF

#--start-----------------------------examples----------------------------------
'''
import datetime
t = datetime.date(2015,1,1)
isbday(t); busday(t,5); busdayMF(t); monthdelta(t, 2); monthdeltaMF(t, 2)
'''
#---end------------------------------examples----------------------------------

#--start------------------------------import-----------------------------------

from pandas.tseries.holiday import (AbstractHolidayCalendar, 
                                    EasterMonday, GoodFriday, Holiday)  # 1}
from pandas.tseries.offsets import CDay   #Custom business days         #    2]
 
#---end-------------------------------import-----------------------------------
 
#--start---------------------------support class-------------------------------
#Source:
#http://mapleoin.github.io/perma/python-uk-business-days
class EurHolidayCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('New Years Day', month=1, day=1, observance=None),
        GoodFriday,
        EasterMonday,
        Holiday('Early May bank holiday',
                month=5, day=1),
        Holiday('Christmas Day', month=12, day=25, observance=None),
        Holiday('Boxing Day',
                month=12, day=26, observance=None)
    ]
    
bday = CDay(calendar=EurHolidayCalendar())

#---end----------------------------support class-------------------------------

#--start------------------------------isbday-----------------------------------
# INPUT:
#t                           [datetime.date]
# OUTPUT:
#True (if t is business day) or False 
def isbday(t):
    return (t == (t+bday-bday).date())   #suboptimal

#---end-------------------------------isbday-----------------------------------

#--start-----------------------------busbday-----------------------------------
#go forward of n business days 
# INPUT:
#t                           [datetime.date]
#n                           [int]
# OUTPUT:
#True (if t is business day) or False 
def busday(t,n):
    return (t+n*bday).date()

#---end-------------------------------isbday-----------------------------------

#--start-----------------------------busdayMF----------------------------------    
#find the following business day with convention 'modified follow'
# INPUT:
#t                           [datetime.date]
# OUTPUT:
#following business day      [datetime.date]
def busdayMF(t): 
    f = t+bday   #following business day 
    if t.month == f.month: 
        return f.date()
    else: #if f is of the following month the previous business day is picked
        return (f-bday).date()
        
#---end------------------------------busdayMF----------------------------------    

#--start----------------------------monthdelta---------------------------------
#Source:
#http://stackoverflow.com/questions/3424899/whats-the-simplest-way-to-subtract-a-month-from-a-date-in-python
#Add (subtract) delta months
# INPUT:
#date                                   [datetime.date]
# OUTPUT:
#day after delta months                 [datetime.date]
def monthdelta(date, delta):
    # '%' rest of the division, '//' integer division
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12 #set to 12 if m is 0
    d = min(date.day, [31,29 if y%4==0 and not y%400==0 else 28,31,30,31,30,
                       31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)
    
#---end-----------------------------monthdelta---------------------------------

#--start---------------------------monthdeltaMF--------------------------------
#Add (subtract) delta months with the modified follow convention
# INPUT:
#date                                   [datetime.date]
# OUTPUT:
#business day after delta months        [datetime.date]
def monthdeltaMF(t0, delta): 
    t1=monthdelta(t0, delta)
    if isbday(t1):
        return t1
    else:
        return busdayMF(t1)
        
#---end------------------------------monthdeltaMF--------------------------------