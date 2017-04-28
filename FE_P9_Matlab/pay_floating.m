function dates = pay_floating(t0, T, freq)
% This function finds the business days in the interval (settlement date, 
% expiry date] with the given frequency. 
% The payment dates are business days, computed with the modified following
% convention.
%                                                                         
% INPUT:
%   settle: settlement date. [serial date number]
%   T: contract expiry.  [serial date number]
%   freq: frequency of payment dates. [real]  
%
% OUPUT:
%   dates: vector of the business days found.  [serial date number]
%
% USES:
%   eurCalendar


% Calculate the number of months to going back.
MB = 12 / freq;

% Evaluate the number of fixed payements will occur. 
n_pay = floor(yearfrac(t0,T)*freq);

% Initialization of the vector of final dates (n_pay+1 to include also the
% expiry date).
dates = zeros(n_pay+1,1);
% Impose the first date equal to the expiry.
dates(1) = T;
% Compute the other dates going backward from the expiry.
dates(2:end) = datemnth(T, -(1:n_pay)*MB);

% Check if they are business days according to the Euro Calendar, if not
% change them with the next business days according to the Modified 
% Following Convention.
dates(~isbusday(dates,eurCalendar)) = busdate(dates(~isbusday(dates,eurCalendar)),...
                      'modifiedfollow', eurCalendar);

% Sort the vector 'dates' in ascending order.           
dates = sort(dates,'ascend');

% The dates computed going backward with the matlab function 'datemnth' can
% return a date before the settlement date, for rounding problems.
% To solve this, only dates after the settlement are considered.
dates = dates(dates>t0);                                                   

end %Function

