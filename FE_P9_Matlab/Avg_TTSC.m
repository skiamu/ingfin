function [ATSC, reference_out, L_star, first_slope, CI] = Avg_TTSC(reference, ASWSpread)
% This function computes the best fit of the ASW spreads with a straight 
% line broken in one point for every value date. Then, it considers only 
% days with first slope positive and compute the ATSC (Average Time to
% Slope Change). 
%
% INPUT:
%	reference: vector of days where an assest swap term structure has
%              been computed [serial date number]
%   ASWSpread: vector of structs with 2 fields : 
%               ASWSpreads - values of asset swap spread for each maturity 
%               of the bond   [real]
%               ExpiryDates - maturities of the bonds. [serial date
%               number]
%
% OUTPUT:
% 	ATSC: average time to slope change, that is the monthly average
%          of time when the spread term structure changes slope. 
%          [real, expressed in years]
%   refrence_out: vector of first day of the month, corresponding to the
%                 ATSC [serial date number]
%   L_star: vectors of minimum sum of squares [real]
%	first_slope: vector of first line slopes [real]
% 	CI: confidence intervals on the ATSC 
%
% USES:
%    segmented_regression
%    monthly_avg


% no plot flag
flag = 0;

% Iinitializations
n = length(reference);
tau_star = zeros(n,1);
first_slope = zeros(n,1);
L_star = zeros(n,1);

for i = 1 : n
    
    j = ASWSpread(i);
    
    % Apply the segmented regression algorithm for each business day in the
    % vector reference.
    [tau_star(i), L_star(i), first_slope(i)] = segmented_regression(j.ExpiryDates, j.ASWSpreads, flag);
 
end

% Consider only the time-break with positive first slope.
tau_star = tau_star(sign(first_slope) == 1);

% Select the corresponding days.
reference = reference(sign(first_slope) == 1);

% Compute the time to slope change (it is expressed in year as difference
% from the value date and the time-break).
time_to_slope_change = (tau_star - reference) / 365;

% Compute the Monthly Average of the Time to Slope Change(ATSC).
[ATSC , i_first, CI] = monthly_avg (time_to_slope_change, reference);

% Consider first days of the month (just for the plot).
reference_out = reference(i_first);


end %Function