function [ avg, i_first, CI ] = monthly_avg ( values, dates )
% This function returns the monthly average values, the indeces in which
% the vector 'dates' changes the month and the confidence interval.
%
% INPUT:
% 	values: vector of values.   [real]
% 	dates: dates corresponding to values.  [serial date number]
%          (REM1: dates MUST be increasing t_(i)<t_(i+1), so if they are  
%                 decreasing call the function like this:
%                 >>monthly_avg ( flip(values), flip(dates) )
%          (REM2: Values and dates must have the same length)

% OUTPUT:
% 	avg: monthly averages of 'values'  [real]
%   i_first: indeces of the position in which the month changes w.r.t. to 
%            the previous date.
%          (REM: this output refers to the 'increasing' dates)
%   CI: confidence interval on the values.


% Sort the vector of dates in ascending order and, according to this, the
% vector of the values.
[dates, q] = sort(dates,'ascend');         % q = index vector related to the order of dates.
values = values(q);

% Determine the last day of the month of the first element of the vector 
% dates.
Flag_lastday = 2;
last = datemnth(dates(1), 0, Flag_lastday); 

j=1;

% Impose the first element of the vector i_first equal to 1.
i_first(1) = 1;     

% This cycle evaluates each date of the vector dates and when this exceeds
% the month attach to the vector i_first the index of the vector 'dates'
% that changes the month and compute for each month the mean of the values
% corresponding to these dates.
% EXAMPLE:
%      dates = [1/1/2007 10/1/2007 30/1/2007 2/2/2007 ...]
%      i_firts = [1 4 ...]

for i = 1 : numel(dates)
    
    % When the date exceeds the last day of the month
    if dates(i) > last                     
        
        % Compute the monthly average of values.        
        avg(j) = mean(values(i_first(j):i-1)); 
        % Compute the confidence interval.
        [~,~,CI(:,j)]=normfit(values(i_first(j):i-1));
        
        % Update the index in which save the result and add to the vector
        % i_first the index of month's change.
        j = j + 1;                             
        i_first(j) = i;                        
        
        % Update the last day of the 'new' month. 
        last = datemnth(dates(i), 0, Flag_lastday);       
    end
end

% The last month average and confidence interval is not computed inside
% the cycle in order to evaluate the mean value in all remaining dates.
avg(j) = mean(values(i_first(j):end)); 
CI(:,j) = normfit(values(i_first(j):i-1));

end %Function

