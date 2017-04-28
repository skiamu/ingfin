function dates = pay_fixed( settle, FC, T, freq)
% This function finds, starting backwards from the expiry T, the business 
% days with the given frequency. It stops when the last dates is very close
% to the first coupon date (not exactly this, since it can differ for the
% business day convention). At the end, the settlement date is added in 
% order to simplify the computations when the accrual interest has to be
% computed.
% The payment dates are business days, computed with the modified following
% convention.
%                                                                          
% INPUT:
%   settle: settlement date. [serial date number]
%   T: contract expiry.  [serial date number]
%   freq: frequency of payment dates. [real]   
%
% OUPUT:
%   dates: vector of the business days found. 
%
% USES:
%   eurCalendar


% Calculate the number of months to going back.
MB = 12 / freq;

% Evaluate the number of fixed payements will occur. 
n_pay = round(yearfrac(FC,T)*freq);

% Initialization of the vector of final dates (n_pay+1 to include also the
% expiry date).
dates = zeros(n_pay+1,1);
% Impose the first date equal to the expiry.
dates(1) = T;
% Compute the other dates going backward from the expiry.
dates(2:end) = datemnth(T, -(1:n_pay)*MB);

% Check if they are business days according to Euro Calendar, if not change
% them with the next business days according to the Modified Following 
% Convention.
dates(~isbusday(dates,eurCalendar)) = busdate(dates(~isbusday(dates,eurCalendar)),...
                'modifiedfollow', eurCalendar);

% Sort the vector 'dates' in ascending order.           
dates = sort(dates,'ascend');

% Add the settlement date at the beginning of the vector.
dates = [settle; dates];

end %Function

