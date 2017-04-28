function t_1 = find_dates(today, T)
% This function finds, starting from today, the business days related to 
% the given maturity T.
%
% INPUT:
%   today: starting point.  [serial date number]
%   T: vector of maturities (must be expressed in months).  [real]
%
% OUTPUT:
%   t_1: first business day after T.  [serial date number]
%
% USES:
%   eurCalendar


% Determine the future dates by a given number of months(T) starting from 
% today.
t_1 = datemnth(today, T);

% Check if each element of t_1 is business day, if not change them with the
% next business day according to the Modified Following Convention.
t_1(~isbusday(t_1,eurCalendar)) = busdate(t_1(~isbusday(t_1,eurCalendar)), ...
                'modifiedfollow', eurCalendar);

end  % Function