# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 17:56:57 2016

@author: Comandini Leonardo, Nicoletti Antea, Schiavon Andrea
"""
#Library for Project9 including the functions that read and BOOTSTRAP the data

# 1) readXL_EONIA
# 2) readXL_BTP_info
# 3) readXL_BTP_data
# 4) bootstrap_EONIA

#Intro:
#The function in this library are suited for the data given for the project, a 
#little change in the input files may lead to something unexpected or errors.
#The bootstrap is in this library because of two reasons: the first is its 
#'need of customization' around the data and the second is that bootstrap 
#results are needed to perform the very next computations.

#--start------------------------------import-----------------------------------
import os                                       # 1) 2) 3) 
import numpy as np                              # 1)    3) 4)
import pandas as pd                             # 1) 2) 3) 4)
from p9_support import (xldate_to_datetime,     # 1)    3) 
                        str_to_date,            #    2) 
                        yearfrac)               #          4)
from p9_business import (monthdeltaMF,          #          4)
                         busday)                #          4)

#---end-------------------------------import-----------------------------------

#--start---------------------------readXL_EONIA--------------------------------
#Read the rates from an excel file and store in a dataframe 'rates'
#Remark: for a date, if at least one rate (before 10 years) is missing the 
#        entire line is dropped. (few lines are actually dropped)

# INPUT:
#path = path of the file                       [string]
#file = name of the file                       [string]
#sheet = name of the sheet containing the data [string]
#old_col = list(16) of list(2) of the columns names in which the data are  
#          stored                              [list of list of string]
#new_col = list(16) of the new columns names   [list of string]                                   
# OUTPUT:
#rates = dataframe containing the rates        [dataframe]
#               1m   2m   3m   ... 10y
#  2012-4-6 
#  2012-4-7
#    ...
#  2015-1-30
# USES:
#xldate_to_datetime

def readXL_EONIA(path,file,sheet,old_col,new_col):
    #join path and file
    path_file = os.path.join(path,file)
    
    #read the file
    EONIA = pd.read_excel(path_file, 
                          sheetname=sheet, 
                          header=[1],         #read from the second row    
                          skiprows=[2],       #skip the third
                          index_col=None,)    #assign a new label to the rows 
                                              #[0, 1, ...] 
    #read the rates corresponding to 1 month and store them in 'rates'
    rates = EONIA.ix[EONIA.index,old_col[0]].copy()     #copy BY VALUE    
    rates = rates.dropna()                              #drop the NaN cells
    rates.columns = ['Date',new_col[0]]                 #rename the columns
    
    #Read the rates corresponding to 2 months and store them in 'add',
    #then, using 'Date' as key, merge 'add' and 'rates' and put the result in 
    #'rates',
    #'rates' will be now a dataframe with 3 columns: 'Dates','1m','2m'.
    #The new column 'Dates' will be the INTERSECTION of the two previous 
    #'Dates' columns and the rows whose elements are outside the intersection 
    #are dropped.
    #Then this procedure is iterated for 3 months,..., up to 10y
    for i in range(1,np.size(new_col)):  #from the SECOND to the last
        add = EONIA.ix[EONIA.index,old_col[i]].copy()   #copy BY VALUE 
        add = add.dropna()                              #drop the NaN cells
        add.columns = ['Date',new_col[i]]               #rename the columns  
        
        rates = pd.merge(rates,add,      #merge rates and add
                         on='Date',      #'Date' is used as key
                         how='inner')    #inner so an intersection is perfomed 
    
    #Put the column 'Date' as index and drop it as a column    
    new_index = rates['Date'].copy()         #copy by value of the column Date
    new_index = new_index.tolist()           #convert the dataframe to list
    new_index = [int(i) for i in new_index]  #convert from float to int
    new_index = [xldate_to_datetime(i) for i in new_index] #convert into datetime
    rates.index = new_index                  #assign Date as index
    del rates['Date']                        #delete the (now useless) column 
                                             #of dates        
    #REMARK: 
    #The row indeces are not ordered, in case of need use:
    #rates=rates.sort_index()
    
    #rates were in percentage points        
    rates = rates/100             
        
    return rates #[dataframe]
    
#---end----------------------------readXL_EONIA--------------------------------
    
#--start--------------------------readXL_BTP_info------------------------------
#Read the BTP info from an excel file and store in a dataframe 'bond_info'
#Remark: the Zero-Coupon BTP are dropped

# INPUT:
#path = path of the file                        [string]
#file = name of the file                        [string]
#sheet = name of the sheet containing the data  [string]                                   
# OUTPUT:
#bond_info = dataframe containing the bond info [dataframe]
# USES:
#str_to_date    
    
def readXL_BTP_info(path,file,sheet):
    #join path and file
    path_file = os.path.join(path,file)
    
    #read the file
    bond_info = pd.read_excel(path_file, 
                              sheetname=sheet, 
                              header=[0],      #read from the first row
                              skiprows=[1],    #skip the second
                              index_col=[0])   #assign a new label to the rows
                                               #[0, 1, ...]
                  
    #Cut the Zero-Coupon BTP since they are not used and so the conversion of 
    #the date to datetime.date can be done also for the whole first coupon date 
    #column
    bond_info = bond_info[bond_info.CPN_TYP != 'ZERO COUPON']
                         
    #Convert the dates form string to 'datetime.date'
    bond_info.FIRST_SETTLE_DT=bond_info.FIRST_SETTLE_DT.apply(str_to_date)
    bond_info.MATURITY       =bond_info.MATURITY.apply(str_to_date)
    bond_info.FIRST_CPN_DT   =bond_info.FIRST_CPN_DT.apply(str_to_date)
    
    #REMARK: 
    #The row indeces are not ordered, in case of need use:
    #bond_info=bond_info.sort_index()
    
    #coupon were *100         
    bond_info.CPN = bond_info.CPN/100     
    
    return bond_info #[dataframe]
    
#---end---------------------------readXL_BTP_info------------------------------
    
#--start--------------------------readXL_BTP_data------------------------------
#Read the BTP prices from an excel file and store in a dataframe 'bond_prices'
#The file is not 'well' written and the read is not as simple as bond_info.
#We procede as follows:
#STEP1:
#read the file without the first line and store it in 'Data'
#STEP2:
#read only the first line and store in 'BTP_names' the names of the bonds.
#STEP3:
#read bond per bond and merge them in 'bond_prices'
#STEP4:
#Put the column 'Date' as index and drop it (as a column)

def readXL_BTP_data(path,file,sheet):
    #join path and file
    path_file = os.path.join(path,file)
    
    #------STEP1: read the file without the first line
    #header=[0,1] would be the best but this problem would occur:
    #https://github.com/pydata/pandas/issues/11733  
    #'MultiIndex vs index_col=None' problem
    Data = pd.read_excel(path_file, 
                         sheetname=sheet, 
                         header=[1],       #read from the second row      
                         index_col=None)   #assign a new label to the rows 
                                           #[0, 1, ...]        
    
    #------STEP2: read only the first line
    row_to_skip = np.size(Data.index) #skip all the rows
    first_line = pd.read_excel(path_file, 
                               sheetname=sheet, 
                               header=[0],      #read from the first row      
                               skip_footer=row_to_skip, 
                               index_col=None) #assign a new label to the  
                                               #rows [0, 1, ...] 
    #Between two BTP names there are three empty cells, so:                       
    N_bond = 1+np.size(first_line.columns)//4            #Number of bond 
    BTP_names = first_line.columns[0:4*N_bond:4]   #Names of the BTP    
    #Need a list?
    #Use listBTP=BTP_names.copy().tolist()
    
    #------STEP3: read bond per bond and merge them in 'bondPrices'
    #Create a list(N_bond) of list(2) with the names of the columns in 
    #which dates and prices of each bond are stored.
    #for the clean:
    #old_col = [['Date','PX_LAST']]   
    #old_col += [['Date.'+str(i),'PX_LAST.'+str(i)] for i in range(1,N_bond)]
    #for the dirty:
    old_col = [['Date','PX_DIRTY_MID']] 
    old_col += [['Date.'+str(i),'PX_DIRTY_MID.'+str(i)] for i in range(1,N_bond)]
        
    #read the prices corresponding to the first bond and store them in 
    #'bond_prices'    
    bond_prices = Data.ix[Data.index,old_col[0]].copy() #copy BY VALUE 
    bond_prices = bond_prices.dropna()                  #drop the NaN cells
    bond_prices.columns = [['Date',BTP_names[0]]]       #rename the columns
    
    #Read the second bond prices and store them in 'add', then using 'Date' as
    #key, merge 'add' and 'bond_prices' and put the result in 'bond_prices',
    #'bond_prices' will be now a dataframe with 3 columns: 'Dates',
    #'name_of_first_bond','name_of_second_bond.
    #The new column 'Dates' will be the UNION of the two previous 'Dates' 
    #columns and the rows whose elements are outside the intersection 
    #are filled with NaN (the previous values are not overwritten).
    #Then this procedure is iterated up to the last bond.
    for i in range(1,N_bond):             #from the SECOND to the last
        add = Data.ix[Data.index,old_col[i]].copy()    #copy BY VALUE
        add = add.dropna()                             #drop the NaN cells
        add.columns = [['Date',BTP_names[i]]]          #Rename the columns
        
        bond_prices = pd.merge(bond_prices,add, #merge bond_prices and add
                               on='Date',       #'Date' is used as key
                               how='outer')     #outer so a union is perfomed 
    #------STEP4:
    #Put the column 'Date' as index and drop it as a column   
    new_index = bond_prices['Date'].copy()   #copy by value of the column Date
    new_index = new_index.tolist()           #convert the dataframe to list    
    new_index = [int(i) for i in new_index]  #convert from float to int
    new_index = [xldate_to_datetime(i) for i in new_index] #convert into datetime
    bond_prices.index = new_index            #assign Date as index
    del bond_prices['Date']                  #delete the (now useless) column 
                                             #of dates
        
    #REMARK: 
    #The row indeces are not ordered, in case of need use:
    #bond_prices=bond_prices.sort_index()
    
    #prices were *100         
    bond_prices = bond_prices/100             
        
    return bond_prices #[dataframe]
        
#---end---------------------------readXL_BTP_data------------------------------ 

#--start--------------------------bootstrap_EONIA------------------------------
#Compute the dates corresponding to:
#[t0+1m  t0+2m  t0+3m  ...  t0+10y]
#Compute the corresponding discount factors and zero rates
#store them in 4 dataframes: 
#'dates', 'rates', 'discount', 'zero_rates' 
#with the same structure of rates  

# INPUT:
#rates = dataframe of the EOINA rates            [dataframe]
#            1m   2m   3m   ... 10y
#2012-4-6 
#    ...
#2015-1-30
#mta = list of months to add                     [list of int]
#    = [1,2,3,4,5,6,12,2*12,3*12,4*12,5*12,6*12,7*12,8*12,9*12,10*12] 
# OUTPUT:
#dates, rates, discount, zero_rates              [dataframe]
# USES:
#yearfrac
        
def bootstrap_EONIA(rates,mta):
    col = rates.columns
    #initialize the new dataframes
    dates      = rates.copy()
    discount   = rates.copy()
    zero_rates = rates.copy()

    for i in rates.index:    #cycle on the value dates
        ST = busday(i,2)     #settlement = 2 business days after value date
        #compute the dates
        dt = [monthdeltaMF(ST,j) for j in mta]
        dates.loc[[i],:] = dt
        
        #I largelely 'abuse' of the fact that the last discount that is 
        #computed with the 'easy' formula is the 7th
        for j in range(0,7):                 #up to 1y            
            discount[col[j]][i]=1/(1+yearfrac(ST,dt[j],2)*    
                                           rates[col[j]][i])    #act/360   
        summa = discount[col[6]][i]*yearfrac(ST,dt[6],2)         #act/360
        for j in range(7,np.size(col)):  #behond 1y                              
            discount[col[j]][i]=(1-rates[col[j]][i]*summa)/(1+
                                         yearfrac(dt[j-1],dt[j],2)*
                                         rates[col[j]][i])      #act/360
            summa += discount[col[j]][i]*yearfrac(dt[j-1],dt[j],2)
                                                                #act/360
        zero_rates.loc[[i],:] = [-np.log(discount[k][i])/yearfrac(ST,dates[k][i],1) for k in col]
   
    return dates, rates, discount, zero_rates #[dataframe]
        
#---end---------------------------bootstrap_EONIA------------------------------