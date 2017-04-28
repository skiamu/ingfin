# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 18:04:32 2016

@author: Comandini Leonardo, Nicoletti Antea, Schiavon Andrea
"""

#Library for Project9 including the functions that perform the regressions

# 1) linear_regression
# 2) constrained_optimization
# 3) segmented_regression

#--start------------------------------import-----------------------------------
import numpy as np                        # 1) 2) 3)
import matplotlib.pyplot as mpl           #       3)
import datetime                           #       3)

#---end-------------------------------import-----------------------------------

#-start---------------------------regression-----------------------------------
#compute the linear regression of x against y 

# INPUT:
#x = abscissa values             [row np.array]
#y = ordinate values             [row np.array]
#flag = 1 uses 'np.linalg.lstsq'
#       0 uses 'np.linalg.pinv', (Moore-Penrose) pseudo-inverse matrix   
# OUTPUT:
#p = line parameters             [np.array]
#L = minimum sum of squares      [scalar]

def linear_regression(x, y, flag):
    
    # coefficient matrix  (len(x) x 2)
    C = np.array([x, np.ones(len(x))]).T
     
    if flag == 1:   #using 'np.linalg.lstsq'
        # solve least squares problem
        # m is a tuple with the following info: 
        # m[0] = array with the solution of the overdetermined system C * p = y
        # m[1] = "fake" array with 1 element L, the least sum of squares 
        #                                   (e.g. L = norm(C * p - y)^2)
        m = np.linalg.lstsq(C,y) 
        # extract the first element of the tuple
        p = m[0]   
        
        # extract the second element of the tuple and select its first element
        L = m[1][0]  
    
    else:        #using 'np.linalg.pinv', (Moore-Penrose) pseudo-inverse matrix
        p = np.dot(np.linalg.pinv(C), y)

        # extract the second element of the tuple and select its first element
        L = np.linalg.norm(np.dot(C, p) - y) ** 2  
         
    return p, L       
#--end----------------------------regression-----------------------------------
    
#-start--------------------constrained_optimization----------------------------
#compute the constrained linear regression solving a constrained least 
#squares problem
#INPUT:
#x1 = first set abscissa  [column np.array]
#x2 = second set abscissa [column np.array]
#y1 = first set ordinate  [column np.array]
#y2 = second set ordinate [column np.array]   
#flag = 1 uses 'np.linalg.lstsq'
#       0 uses 'np.linalg.pinv', (Moore-Penrose) pseudo-inverse matrix   
#OUTPUT:
#p = vector of lines parameters (e.g [a1 b1 a2 b2]) [column np.array]
#L = least sum of squares [scalar]  
    
def constrained_optimization(x1, y1, x2, y2, tau, flag):
    n = len(x1)  # length of the first set
    m = len(x2)  # length of the second set
    
    col1 = np.concatenate((x1, np.ones(m) * tau))    # first column of C
    col2 = np.ones(n + m)                            # second column of C
    col3 = np.concatenate((np.zeros(n), x2 - tau))   # third column of C
    
    C = np.array([col1, col2, col3])                 # coefficient matrix
    C = C.transpose()                           # dimensions = len(x1 + x2) x 4
    
    y = np.concatenate((y1, y2))               # construct left-handside vector
    
    # initialization
    p = np.zeros(4)
   
    # solve least squares problem
    # m is a tuple with the following info: 
    # m[0] = np.array with the solution of the overdetermined system C * p = y
    # m[1] = 1-d  np.array with 1 element = L, the least sum of squares 
    #        (e.g. L = norm(C * p - y)^2)
    if flag == 1: #using 'np.linalg.lstsq'
        m = np.linalg.lstsq(C,y)
        # extract the first element of the tuple(e.g. p = [a1 b1 a2])
        p[:3] = m[0]
        # compute b2 = b1 + a1 * tau - a2 * tau
        p[3] = p[1] + p[0] * tau - p[2] * tau
        # extract the second element of the tuple and select its first element
        L = m[1][0]
        
    else:        #using 'np.linalg.pinv', (Moore-Penrose) pseudo-inverse matrix
        p[:3] = np.dot(np.linalg.pinv(C), y)
        # compute least sum of squares
        L = np.linalg.norm(np.dot(C, p[:3]) - y) ** 2
        # compute b2 = b1 + a1 * tau - a2 * tau
        p[3] = p[1] + p[0] * tau - p[2] * tau
        
    return p, L  

#--end---------------------constrained_optimization----------------------------

#-start----------------------segmented_regression------------------------------
#computes the segmented regression (two lines broken in one point)

#INPUT:
#T = abscissa values [np.array]
#s = ordinate values [np.array]
#flag = 1) plot activated
#       0) plot disactivated
#OUTPUT:
#tau_star = time-to-slope change (point where the two lines broke) 
#L_star = least sum of squares 
#first_slope = slope of the first regression line
# 
#USES:
#linear_regression
#constrained_optimization

def segmented_regression(T, s, flag):
             
#       data scaling
#    m = (100 - 1) / (T[-1] - T[0])
#    scaling = lambda x : 1 + m * (x - T[0])
#    inv_scaling = lambda x : (y - 1) / m + T[0]
#    T = scaling(T)
    
    # flag to choose the method to solve the system 
    flag_reg = 0 #(Moore-Penrose) pseudo-inverse matrix
    #flag_reg = 1 #'solving with backslash'
    
    N = len(T)  # length of abscissa vector 
    
    # initialization vector of minimum sum of squares
    L = np.zeros(N - 3)
    # initialization vector of time-to-slope change
    tau = np.zeros(N - 3)
    # initialization vector of line coefficients
    lines_coeff = np.zeros((4, N - 3))
    
    # set the first two to infty
    L[:2] = 1e9
    #  set the first two to infty 
    tau[:2] = 1e9
    
    # for loop that starts for k = 2 and ends for k = N - 3
    for k in range(2, N - 3):
        # select the first k elements
        s1 = s[:k + 1]
        T1 = T[:k + 1]
        # select the remaining N - k elements
        s2 = s[k + 1:]
        T2 = T[k + 1:]
        
        # inpidendent linear regessions on the two set of data
        coeff1, L1 = linear_regression(T1, s1, flag_reg)
        coeff2, L2 = linear_regression(T2, s2, flag_reg)
        # save the lines coefficients
        lines_coeff[:,k] = np.concatenate((coeff1, coeff2))
        # sum of the two minumum sum of squares (k 'cause the first index is 0)
        L[k] = L1 + L2
        #  if there's a unique fit there's no ttsc
        #  the method .all() returns True if all components are equal
        if (coeff1 == coeff2).all():
            # set tau to infty
            tau[k] = 1e9
            # save the lines coefficents
            lines_coeff[:,k] = np.concatenate((coeff1, coeff2))
        #  else the two lines are different so they intercept  
        else:
            # a guess for tau is where the lines intercept
            t = (coeff2[1]-coeff1[1]) / (coeff1[0]-coeff2[0])
            # if t belongs to the current interval 
            if  (t >= T[k]  and t < T[k + 1]):
                # set t = tau
                tau[k] = t
                # save the lines coefficents
                lines_coeff[:,k] = np.concatenate((coeff1, coeff2))
            # t doesn't belong to the current interval   
            else:
                # if the current least sum of squares is still good (else do 
                #nothing)
                if L[k] < min(L[:k]):                    
                    # segmented regression  with break point equals LEFT 
                    #interval bound
                    p_L, L_l = constrained_optimization(T1, s1, T2, s2, 
                                                        T[k], flag_reg)
                    #  segmented regression  with break point equals RIGHT 
                    #interval bound
                    p_R, L_r = constrained_optimization(T1, s1, T2, s2, 
                                                        T[k + 1], flag_reg)
                    # if the right sum of squares is better
                    if L_l > L_r:                        
                        tau[k] = T[k + 1]                        
                        # update the new minimum sum of squares
                        L[k] = L_r                        
                        lines_coeff[:,k] = p_R                        
                    else:                        
                        tau[k] = T[k]                        
                        # update the new minimum sum of squares
                        L[k] = L_l                        
                        lines_coeff[:,k] = p_L
    
    # least minimum sum of squares        
    L_star = np.min(L)         
    # corresponding index
    index = np.argmin(L)    
    # select the time when the lines break
    tau_star = tau[index]      
    # select the slope of the first regression line    
    first_slope = lines_coeff[0, index]
        
    # the plot flag has been activated
    if flag == 1:
        p = lines_coeff[:, index]
        T1 = np.append(T[:index], tau_star)
        T2 = np.append(tau_star, T[(index+1):])
        s1_line = np.polyval(p[:2], T1).tolist()
        s2_line = np.polyval(p[2:], T2).tolist()
        
        T1_date = [datetime.date.fromordinal(int(i)) for i in T1.tolist()]
        T2_date = [datetime.date.fromordinal(int(i)) for i in T2.tolist()]

        mpl.figure()
        mpl.plot(T1_date, s1_line, 'r-',
                 T2_date, s2_line, 'r-',
                 T, s, 'b*-')
        mpl.ylabel('spreads')
        mpl.gcf().autofmt_xdate()
        mpl.show()
        
    return tau_star, L_star, first_slope
    
#--end-----------------------segmented_regression------------------------------
