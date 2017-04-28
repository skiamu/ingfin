# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 19:07:53 2016

@author: Comandini Leonardo, Nicoletti Antea, Schiavon Andrea
"""
#Before starting set your path:
#Remark: when you copy and paste the path remember to put '\\' instead of '\'

#path = #insert here and uncomment

path = 'C:\\Users\\Leonardo\\Desktop\\POLIMI\\ATTUALI\\Financial Engineering\\AAA - Final Lab\\Python'
#path = 'C:\\Users\\Antea\\Desktop\\Final Project\\Python'
#path = 'C:\\Users\\skiamu\\Documents\\Python finale2'

#Run project 9

#sections:                                    Note: t   (fast,          <5 sec)
#                                                   tt  (medium, 5 sec< <2 min)
#                                                   ttt (slow,   2 min<       )

# 1)  reading from excel                            ttt       
# 2)  bootstrap_EONIA                               tt
# 3)  initialize the class                          t
# 4)  filter bonds                                  t
# 5)  filter discount                               t
# 6)  compute spread                                ttt
# 7)  filter jumps                                  tt
# 8)  filter too low                                tt
# 9)  ATSC                                          tt
# 10) plot                                          t

from p9_read import (readXL_EONIA,    # 1)
                     readXL_BTP_info, # 1)
                     readXL_BTP_data, # 1)
                     bootstrap_EONIA) #    2)
from main_class_FSI import FSI        #       3) 
import matplotlib.pyplot as plt       #                            10)
import matplotlib                     #                            10)
matplotlib.style.use('ggplot')        #                            10)
import datetime
import numpy as np
import pandas as pd

#Disable some warning (after have taken care of them)
#Source:
#http://stackoverflow.com/questions/20625582/how-to-deal-with-this-pandas-warning
pd.options.mode.chained_assignment = None  #use when the project is finished
#pd.options.mode.chained_assignment = 'warn' #use when coding
#These warning are received because sometimes it is needed to copy by value a 
#dataframe and so the original dataframe won't be modified, pandas tells it but
#in this case it's fine.
np.seterr(invalid='ignore')

#used prices: DIRTY MID

#To pass from LAST CLEAN PRICES to MID DIRTY PRICES or viceversa
#comment and uncomment in:
#p9_read >> readXL_BTP_data >> lines 197-202 approx
#main_class_FSI >> compute_spread >> lines  250-251 approx

#%% 1)  reading from excel                                                  ttt
#--Settings--
#to access the files
files = {'path': path,
         'file_EONIA':'INPUT_rate_curves.xlsx',
         'file_BTP': 'INPUT_BTP_Dirty.xlsx',
         'sheet_EONIA': 'EONIA',
         'sheet_BTP_info': 'Info', 
         'sheet_BTP_prices': 'Data'}  
         
#new labels of the columns of 'rates'         
new_col = ['1m','2m','3m','4m','5m','6m',
           '1y','2y','3y','4y','5y','6y','7y','8y','9y','10y']

#labels assigned automatically by pandas to the 'rates'
old_col = [['Date','PX_LAST']]
old_col += [['Date.'+str(i),'PX_LAST.'+str(i)] for i in range(1,len(new_col))]
#when pandas reads a column with a name equal to the previous one it assigns to 
#the new one the name read adding at the end a .1,.2,...

#--To run--
rates=readXL_EONIA(files['path'],files['file_EONIA'],files['sheet_EONIA'],
                   old_col,new_col)               

bond_info=readXL_BTP_info(files['path'],files['file_BTP'],
                          files['sheet_BTP_info'])

bond_prices=readXL_BTP_data(files['path'],files['file_BTP'],
                            files['sheet_BTP_prices'])

#%% 2)  bootstrap_EONIA                                                      tt
#--Settings--
#months to add
mta = [1,2,3,4,5,6,12,2*12,3*12,4*12,5*12,6*12,7*12,8*12,9*12,10*12]

#--To run--
dates, rates, discount, zero_rates = bootstrap_EONIA(rates,mta)

#%% 3)  initialize the class                                                  t
#--To run--   
#Since the computation of spreads is quite slow one may prefer to initialize  
#the class assigning a dataframe of spreads already computed. 
#The following instruction check if one dataframe has not been defined yet and 
#in that case set it to 'None' 
if 'spread_stored' not in globals():
    test = FSI(dates,rates,discount,zero_rates,bond_info,bond_prices,None) 
else:
    test = FSI(dates,rates,discount,zero_rates,
               bond_info,bond_prices,spread_stored.copy())
    #We are aware of the warning and we are fine with that

#to create a copy of test
#test1 = test.copy()

#%% 4)  filter bonds                                                          t
#--Settings--
ts=datetime.date(1999, 1, 1)         #settlement of the bond in the interval 
tN=datetime.date(2015, 12, 31)       #                               [ts,tN]
liquidity_threshold=5e8              #bond issued > 5e8
inflation='N'                        #no inlfation linked
outlier_price=10                     #prices are in the order of 1
flag = 1 #to print the bond filtered
#flag = 0 #otherwise

#--To run--
test.filter_bond(ts,tN,liquidity_threshold,inflation,outlier_price,flag)

#%% 5)  filter discount                                                       t
#--Settings--
t1=datetime.date(2007, 1, 1)
tN=datetime.date(2015, 12, 31)
flag = 1 #to print the bond filtered
#flag = 0 #otherwise

#--To run--
test.filter_discount(t1,tN,flag)

#%% 6)  compute spread                                                      ttt
#--Settings--
freq_float = 4

#--To run--
test.compute_spread(freq_float)

#I store in 'spread_stored' a copy of the dataframe of the spreads, so when one
#needs to rinitialize the class the computation of spread (ttt) can be skipped
spread_stored = test.spread.copy()

#%% 7)  filter jumps                                                         tt
#--Settings--
jump_threshold = 50
flag = 1 #to print the bond filtered
#flag = 0 #otherwise

#--To run--
test.filter_jumps(jump_threshold,flag)

#%% 8)  filter too low                                                       tt
#--Settings--
too_low_threshold = 20
flag = 1 #to print the bond filtered
#flag = 0 #otherwise

#--To run--
test.filter_too_low(too_low_threshold,flag)

#%% 9)  ATSC                                                                 tt
#--To run--
test.ATSC()

#%% 10) Plot                                                                  t

#In the sections below one can display the data computed, here there are some 
#examples, modify the code below to show other things

#%% plot the ATSC, first slope and spread at (approx) 10 yrs 

plt.figure() 
test.result.ATSC.plot() 
plt.ylabel('ATSC (yrs)') 
plt.gcf().autofmt_xdate()
plt.show()

plt.figure() 
test.result.first_slope.plot() 
plt.ylabel('First slope (bps/yrs)') 
plt.gcf().autofmt_xdate()
plt.show()
print('Note: negative slopes are not plot')

plt.figure() 
test.result.s_10y.plot() 
plt.ylabel('10 yrs spread (bps)') 
plt.gcf().autofmt_xdate()
plt.show()

#%% plot one bond prices
#--Settings--
bond = 'EH227467 Corp'

#--To run--
if (bond == test.bond_prices.columns).any():
    plt.figure() 
    test.bond_prices[bond].plot()
    plt.ylabel('Prices of '+bond)
    plt.gcf().autofmt_xdate()
    plt.show()
else:
    print('The bond selected doesn''exist or has been filtered')
#%% plot the spreads for one date with the corresponding segmented regression
#--Settings--
t_plot = datetime.date(2011,6,1)

#--To run--
if (t_plot == test.spread.index).any():
    t,L,f = test.single_seg_reg(t_plot,1)       #1 to plot
    print('Value date  :',t_plot)
    print('TTSC        =',t)
    print('L           =',L)
    print('First_slope =',f * 365,'(bps/yrs)') #convert in bps/yrs
else:
    print('For the date selected there are no spreads')
