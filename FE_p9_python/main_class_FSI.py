# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 17:27:00 2016

@author: Comandini Leonardo, Nicoletti Antea, Schiavon Andrea
"""

#Main class FSI (Financial Stress Index)

#Structure:
#  1) __init__
#  2) filter_bond
#  3) filter_discount
#  4) compute_spread
#  5) filter_jumps
#  6) filter_too_low
#  7) single_seg_reg
#  8) ATSC               7)

#--start------------------------------import-----------------------------------

import pandas as pd                                     #    4)    6)    8)
import numpy as np                                      #             7)
from p9_business import (busday,                        #    4)
                         isbday)                        #    4)
from p9_support import (interp_bootstrap,               # 3)
                        BPV_fixed,BPV_float,            #    4) 
                        pay_fixed,pay_float,            #    4)
                        filter_pay_fix,filter_pay_flo,  #    4)
                        find_t0,                        #    4)
                        yearfrac)                       #    4) 
#yearfrac used if clean prices are used
from p9_reg import segmented_regression                 #          7)
import datetime                                         #          7)

#---end-------------------------------import-----------------------------------

#--start--------------------------------FSI------------------------------------
#
# ATTRIBUTES:
#dates, rates, discount, zero_rates                           [dataframe]
#           of the form of the output of bootstrap_EONIA
#bond_info = info of the bonds                                [dataframe]
#           of the form of the output of readXL_info
#bond_prices = prices of the bonds                            [dataframe]
#           of the form of the output of readXL_data

# METHODS:
#
#

class FSI(object):
#--start-----------------------__init__--(constructor)-------------------------

    def __init__(self,dates,rates,discount,zero_rates,
                 bond_info,bond_prices,spread):
        self.dates = dates
        self.rates = rates        
        self.discount = discount
        self.zero_rates = zero_rates
        self.bond_info = bond_info
        self.bond_prices = bond_prices
        #self.spread = None
        self.spread = spread
        self.result = None

#---end------------------------__init__--(constructor)-------------------------

#--start---------------------copy--(copy constructor)--------------------------
    def copy(self):
        return FSI(self.dates.copy(),self.rates.copy(),self.discount.copy(),
                   self.zero_rates.copy(),self.bond_info.copy(),
                    self.bond_prices.copy(),self.spread.copy())

#---end----------------------copy--(copy constructor)--------------------------

#--start---------------------------filter_bond---------------------------------    
#filter bond 
#1) Settlement in [ts,tN]                   ts,tN           [datetime.date]
#2) Bonds issued > liquidity_threshold      liquidity_threshold      [real]
#3) inflation linked: yes 'Y' or no 'N'     inflation                 [str]
#4) prices < outlier_price                  outlier_price            [real]
#     (prices in order to be realistic can't be more than ~10)
#flag = 1 to print the filtered bond
#       0 otherwise
    def filter_bond(self,ts,tN,liquidity_threshold,inflation,outlier_price,flag):
        
        if flag==1: #to print the filtered bond                
            #Show the outliers
            print('---')  
            print('Outlier Values: ')
            print(self.bond_prices[self.bond_prices>outlier_price].dropna(
                                   how='all').dropna(how='all',axis='columns'))
            print('Note: ''NaN'' where the price is absent or in the standard')
            print('---')        
            
            #Show the bonds whose settlement is not in [ts,tN] 
            print('---')  
            print('Bonds with settlement not in [ts,tN]: ')
            print(self.bond_info[(self.bond_info.FIRST_SETTLE_DT < ts) |
                         (self.bond_info.FIRST_SETTLE_DT > tN)].index.tolist())  
            print('---') 
            
            #Show the bonds with inflation linked
            print('---')  
            print('Bonds with inflation linked: ')
            print(self.bond_info[(self.bond_info.INFLATION_LINKED_INDICATOR != 
                                                    inflation)].index.tolist())  
            print('---')  
            
            #Show the bonds with liquidity below the threshold
            print('---')  
            print('Bonds with liquidity below the threshold: ')
            print(self.bond_info[(self.bond_info.AMT_ISSUED < 
                                          liquidity_threshold)].index.tolist())  
            print('---')
        
        #Filter the bond
        
        self.bond_info = self.bond_info[(self.bond_info.FIRST_SETTLE_DT >= ts) &
                                        (self.bond_info.FIRST_SETTLE_DT <= tN) &
                      (self.bond_info.INFLATION_LINKED_INDICATOR == inflation) & 
                              (self.bond_info.AMT_ISSUED > liquidity_threshold)] 
        #Note: the boolean indexing want '==' instead of '='
        
        #drop in the prices dataframe the bonds filtered in the previous   
        #passage (and in the passage inside readXL_info were the ZC-Bond are 
        #dropped) 
        self.bond_prices = self.bond_prices[self.bond_info.index]
            
        #find the outlier prices and remove that quotations (set to NaN as the 
        #ones missing)
        self.bond_prices[self.bond_prices>outlier_price] = float('NaN')
 
#---end----------------------------filter_bond--------------------------------- 

#--start-------------------------filter_discount-------------------------------
#1) t0 in [t1,tN]                           ts,tN           [datetime.date]
#2) t0 is business day
#flag = 1 to print the filtered discount
#       0 otherwise
    def filter_discount(self,t1,tN,flag):
        
        if flag==1: #to print the filtered dates
            #Show the dates not in [t1,tN] 
            print('---')  
            print('Dates not in [t1,tN]: ')
            for j in self.dates[(self.dates.index < t1) | 
                             (self.dates.index > tN)].index.tolist():
                print(j) 
            print('---') 
            
            #Show the dates that are not business days
            print('---')  
            print('Dates that are not business days: ')
            for j in self.dates[[not isbday(i) for i in 
                                    self.dates.index.tolist()]].index.tolist():
                print(j) 
            print('---') 
        
        ind = ((self.dates.index >= t1) & 
               (self.dates.index <= tN) &
               [isbday(i) for i in self.dates.index.tolist()])
        self.dates = self.dates[ind]
        self.rates = self.rates[ind]
        self.discount = self.discount[ind]
        self.zero_rates = self.zero_rates[ind]

#---end--------------------------filter_discount-------------------------------  

#--start-------------------------compute_spread--------------------------------
#create a new dataframe self.spread with the following structure:
#               bond1   bond2   bond3 ...
#  2012-4-6 
#  2012-4-7
#    ...
#  2015-1-30
#for each bond:
# 1) find the bond info (maturity,first cpn,settl,cpn,fix_freq) 
# 2) find the dates in which the float and fix payments occurs
# 3) select the indeces (t0) that are business days and s.t. M€[t0+2m,t0+10y]
# 4)     for each t0 (value date) selected:
#        4.1) find the settlement (2 bus days after value date)
#        4.2) select the dates in which the payments occur 'after' the t0
#        4.3) compute the corresponding discount facotrs
#        4.4) compute the BPV_fix and BPV_float
#        4.5) compute accrual and dirty price
#        4.6) compute the spread (in bps) and store it in the dataframe

# INPUT:
#f_float = floating frequency
# USES:
#pay_fixed
#pay_float
#find_t0
#busday
#filter_pay_fix
#filter_pay_flo
#BPV_fixed
#BPV_float
#interp_bootstrap

    def compute_spread(self,f_float):
        col = self.bond_prices.columns
        row = self.dates.index
        #initialize the dataframe (all NaN)
        self.spread=pd.DataFrame(index=row, columns=col) 
        j=1 
        N=len(col)
        for i in col: #cycle on the bond
            print('I am examining bond:  ',i,'  Number:  ',j,'/',N)
            j+=1
            #print('---')
            #Select the info of the bond
            M  = self.bond_info.MATURITY[i]
            FC = self.bond_info.FIRST_CPN_DT[i]
            ST = self.bond_info.FIRST_SETTLE_DT[i]
            c  = self.bond_info.CPN[i]
            f_fixed = self.bond_info.CPN_FREQ[i]
            #lists of dates in which th payments occur
            d_fixed = pay_fixed(M,FC,ST,f_fixed)
            d_float = pay_float(M,ST,f_float)
            #list of t0 (business days with a term structure) s.t. 
            #                                                  M€[t0+2m,t0+10y]
            t0s = find_t0(M,row,i,self.bond_prices)           
            
            for t in t0s: #cycle on suitable t0
                #t is value date
                st_t = busday(t, 2) #settlement after t
                
                #select the payments after st_t
                d_fixed_t = filter_pay_fix(d_fixed, st_t)
                #[t_{-1}     t_1  ...  M]
                #with t_{-1} <= st_t < t_1
                d_float_t = filter_pay_flo(d_float, st_t)
                #[st_t       t_1  ...  M]
                
                #compute the discount factors
                B_fixed_t = interp_bootstrap(self.dates.loc[[t], :],
                                             self.zero_rates.loc[[t], :],
                                             d_fixed_t[1:])
                B_float_t = interp_bootstrap(self.dates.loc[[t], :],
                                             self.zero_rates.loc[[t], :],
                                             d_float_t[1:])
                
                #compute the BPVs
                BPV_fl = BPV_float(d_float_t,B_float_t)
                BPV_fx = BPV_fixed(d_fixed_t,B_fixed_t,c)
                #compute the accrual and dirty price
                accrual = 0 #if in bond prices contains the dirty
                #accrual = c*yearfrac(d_fixed_t[0], st_t, 3)#30/360 #if clean
                dirty_price = accrual + self.bond_prices[i][t]
                #there is always a price (see t0 filter)
                #spread in bps
                self.spread[i][t] = 1e4*(BPV_fx - dirty_price)/BPV_fl  

#---end--------------------------compute_spread--------------------------------    
 
#--start--------------------------filter_jumps---------------------------------
#Find the jumps (up-and-down, down-and-up) of at least L bps and substitute the
#value of the peak with the mean of the values just before and just after

# INPUT:
#L = threshold in bps                                                  [real]
#flag = 1 to print the filtered discount
#       0 otherwise
    def filter_jumps(self,L,flag): 
        #Store in 'row' the sorted dates of spread
        row = self.spread.sort_index().index
        cont = 0
        if flag==1: #cycle with print
            print('---')
            print('Jumps: ')
            for i in self.spread.columns:
                S = self.spread[i] #for a lighter notation
                for j in range(1,len(row)-1): #from the 2nd to last-1
                    s1, s2, s3 = S[row[j-1]], S[row[j]], S[row[j+1]]
                    if ((abs(s1-s2,)>L) & 
                        (abs(s3-s2)>L) &
                        ((s2-s1)*(s3-s2)<0)):
                        cont += 1
                        print('t :',row[j],' bond :',i,
                              ' --     ',int(s1),'>>',int(s2),'<<',int(s3))
                        S[row[j]] = (S[row[j-1]]+S[row[j+1]])/2
            print('Jumps observed: ',cont)
            print('---')
        else:    #cycle without print
            for i in self.spread.columns:
                S = self.spread[i] #for a lighter notation
                for j in range(1,len(row)-1): #from the 2nd to last-1
                    s1, s2, s3 = S[row[j-1]], S[row[j]], S[row[j+1]]
                    if ((abs(s1-s2,)>L) & 
                        (abs(s3-s2)>L) &
                        ((s2-s1)*(s3-s2)<0)):
                        S[row[j]] = (S[row[j-1]]+S[row[j+1]])/2
                               
#---end---------------------------filter_jumps---------------------------------    
       
#--start-------------------------filter_too_low--------------------------------
#For each date find the (closest to 10y) last spread observed.
#For these spread a monthly average is computed.
#The months with average below L are filtered out.
       
# INPUT:
#L = threshold in bps                                                  [real]
#flag = 1 to print the filtered months
#       0 otherwise       
    def filter_too_low(self,L,flag):
        N = len(self.spread.index)
        #initialize 
        s_10y = N*[0] 
        df = pd.DataFrame(index=pd.DatetimeIndex(self.spread.index),
                          columns=['s_10y','month'])
        for i in range(N):
            #Find the s_10y
            row = self.spread.index[i]
            #a row is picked            
            s = self.spread.loc[[row],:].copy().dropna(how='all',axis='columns')
            if not s.empty: #if I have some spreads
                #Change the index label (bond name -> maturity)
                s.columns = self.bond_info.MATURITY.copy()[s.columns].tolist()
                #sort by columns, convert to list, pick the last one
                s_10y[i] = s.sort_index().loc[row].tolist()[-1]            
            
        #fill the new dataframe with the last (closest to 10y) spread observed 
        #and the month of the index
        df.s_10y = s_10y
        df.month = df.index.to_period('M')
        
        #avg will contain the mean by month
        g = df.groupby('month')
        avg = g.mean()
        
        #select the month with mean under L, print them and drop the spread of 
        #the corresponding dates
        out = avg.index[avg.s_10y<L] 
        if flag==1:
            print('---')
            print('Month with spread below',L,'bps')
            for i in out:
                print(i)
            print('---')
        ind_out = df.index[df.month.isin(out)]
        self.spread = self.spread.drop(ind_out)        
        
#---end--------------------------filter_too_low--------------------------------    

#--start-------------------------single_seg_reg--------------------------------
#extract a row from the spread dataframe and perform segmented regression of
#'dates vs spreads'

# INPUT:
#date = date under examination                             [datetime.date]
#flag_plot = 1 for plot the seg_reg
#            0 otherwise   
# OUTPUT:
#'t' = time-to-slope-change (TTSC)                         [datetime.date]
#L = least square error                                    [real]
#f = first slope                                           [real]
# USES:
#segmented_regression 
    def single_seg_reg(self,date,flag_plot):
        #extract the row and store it in a dataframe
        df = self.spread.loc[[date],:].copy()
        #set the maturities as columns labels        
        df.columns = [self.bond_info.MATURITY[i] for i in self.spread.columns] 
        df = df.dropna(axis='columns') 
        #Manage the case everything is dropped
        if df.empty:
            print('On the date',date,' there are no spreads') 
            print('t,L,f are set to some (unrealistic) default values')
            t,L,f = 1,1e9,-1e9
        else:
            #create the two array segmented regression needs change from 
            #datetime.date to serial number
            tt = np.array([j.toordinal() for j in df.columns])#df.columns.tolist()
            ss = np.array(df.loc[date].tolist())
            
            t,L,f = segmented_regression(tt, ss, flag_plot) #flag just for notation
        return datetime.date.fromordinal(int(t)),L,f
        
#---end--------------------------single_seg_reg--------------------------------

#--start------------------------------ATSC-------------------------------------
#Create a new dataframe 'result' with the following structure:
#             tau_star   TTSC   ATSC  month   L_star   first_slope 
#  2012-4-6 
#  2012-4-7
#    ...
#  2015-1-30
#where: tau_star    = date of time-to-slope-change           [datetime.date]
#       TTSC        = time-to-slope-change in years          [real]
#       ATSC        = monthly average TTSC in years          [real]
#       month       = month of the index                     [period]
#       L_star      = least square error                     [real]
#       first_slope = coefficient of the first segment       [real]
#       s_10y       = last spread (closest to 10 years)      [real]
#for each date:
# 1) perform segmented_regression
# 2) fill tau_star, L_star, first_slope and compute TTSC
#fill the month column
#compute the monthly avg and fill ATSC

# USES:
#self.single_seg_reg
    def ATSC(self):
        row = self.spread.index
        #initialize the dataframe with the results
        self.result = pd.DataFrame(index=row, 
                                   columns=['tau_star','TTSC','ATSC','month',
                                            'L_star','first_slope','s_10y'])
                                    
        for i in row:
            t,L,f = self.single_seg_reg(i,0)
            self.result.tau_star[i] = t   #already back to datetime.date
            self.result.L_star[i] = L 
            self.result.first_slope[i] = f * 365 #convert in bps/yrs
            #Compute the TTSC
            self.result.TTSC[i] = (t-i).days/365
            #Find the s_10y
            s = self.spread.loc[[i],:].copy().dropna(how='all',axis='columns') #a row is picked
            if not s.empty: #if I have some spread
                #Change the index label (bond name -> maturity)
                s.columns = self.bond_info.MATURITY.copy()[s.columns].tolist()
                #sort by columns, convert to list, pick the last one
                self.result.s_10y[i] = s.sort_index().loc[i].tolist()[-1]
            
        #filter out the days with first slope <= 0
        self.result = self.result[self.result.first_slope>0]
        
        #Compute the ATSC
        #I need result to have a DatetimeIndex
        Ind = self.result.index  #original Index
        self.result.index = pd.DatetimeIndex(Ind) #DatettimeIndex
                
        self.result.month = self.result.index.to_period('M')
        
        #initializing the dataframe as did before the elements of the dataframe 
        #are set to dtype=object which does not permit to perform a the mean, 
        #in order to accomplish that it is nedded to change the dtype of that 
        #column
        self.result.TTSC = self.result.TTSC.astype(float)
        g = self.result[['TTSC','month']].copy().groupby('month')
        avg = g.mean()        
        
        for i in avg.index:
            self.result.ATSC[self.result.month.isin([i])] = avg.TTSC[i]
            
        #Back to the previous Index
        self.result.index = Ind 
            
#---end-------------------------------ATSC------------------------------------- 

#---end---------------------------------FSI------------------------------------