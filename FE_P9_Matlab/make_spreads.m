function [count, tot] = make_spreads(reference, EONIA, bond, payments)
% This function computes the Asset Swap Spread over EONIA for all dates in
% the considered interval. Then a filter is applied in order to eliminate 
% unrealistic values. For a given bond it is possible for the Asset Swap
% spread to present large jumps from one day to the following business day. 
% So whenever it happens for two consecutive days with the opposite sign, 
% the central value in the triplet is filtered out and replaced with the
% average spread between the first and the third values of these three 
% business days intervals.
% At the end, save the results in 'spread.mat', which is a vector 
% containing for every business day in the considered interval a struct
% with 2 fields: 'ASWSpreads', with the computed spreads, and
% 'ExpiryDates', with the expiry of the bonds for which the spreads are
% evaluated.
% Observe that in ASWSpread the vectors of structs refer to reference in
% descending order.
%
% INPUT :
%   reference: value dates. [vector of serial date number]
%   EONIA: vector of structs (Dates, Rates, Discount)
%   bond: vector of structs containing information about all bonds.
% 
% OUTPUT:
%   None

% USES:
%   Asset_spread
%   eurCalendar


% Initialization of the 'ASWSpread' struct, with 3 fields: ASWSpreads,
% ExpiryDates, Name. The last field is not saved at the end of function
% since it is useful only for the filter about the jumps.
ASWSpread = struct('ASWSpreads', {}, 'ExpiryDates', {}, 'Name', {});

% First 2 step of the loop on reference. They are done separately because
% it is useless evaluate the filter if there are less of 3 values.
for k = 1 : 2
    
    % t0: settlement day, two business day after the value date.
    t0 = reference(k)+ 2;
    t0(~isbusday(t0, eurCalendar)) = busdate(t0, 'follow', eurCalendar);
    
    % Select the value date.
    value_date = reference(k);
    
    % Select the corresponding discount factors curve, that discounts at
    % t0.
    curve = EONIA(k);
    
    % Compute the Asset Swap Spread over EONIA for the selected value date.
    [ASWSpread(k).ASWSpreads, ASWSpread(k).ExpiryDates, ASWSpread(k).Name] = ...
        Asset_spread(bond, value_date, t0, curve, payments);
    
end

% Threshold, in order to evaluate the jumps.
threshold = 50e-4;

% Initialization filter counters.
count = 0;
tot = 0;

for k = 3 : length(reference)
    
    % t0: settlement day, two business day after the value date.
    t0 = reference(k)+ 2;
    t0(~isbusday(t0, eurCalendar)) = busdate(t0, 'follow', eurCalendar);
 
    % Select the value date.
    value_date = reference(k);
    
    % Select the corresponding discount factors curve, that discounts at
    % t0.
    curve = EONIA(k);   
    
    % Compute the Asset Swap Spread over EONIA for the selected value date.
    [ASWSpread(k).ASWSpreads,  ASWSpread(k).ExpiryDates, ASWSpread(k).Name] = ...
        Asset_spread(bond, value_date, t0, curve, payments);
    
    % Bonds for which the spreads are computed in both the two value date
    % before.
    inters1 = intersect(ASWSpread(k-1).Name, ASWSpread(k-2).Name);
    
    % Bonds present in all the last three curves.
    inters_bond = intersect(inters1, ASWSpread(k).Name);
    
    % Select spreads in the two-step-ago curve corresponding to the
    % selected bonds.
    spread_2 = ASWSpread(k-2).ASWSpreads(ismember(ASWSpread(k-2).Name, inters_bond));
    
    % Select spreads in the one-step-ago curve corresponding to the
    % selected bonds.   
    spread_1 = ASWSpread(k-1).ASWSpreads(ismember(ASWSpread(k-1).Name, inters_bond));
    
    % Select spreads in the current-step curve corresponding to the
    % selected bonds.     
    spread = ASWSpread(k).ASWSpreads(ismember(ASWSpread(k).Name, inters_bond));
    
    % Spread difference between two-step-ago and one-step-ago.
    diff1 = spread_2 - spread_1;
    
    % Spread difference between one-step-ago and current.
    diff2 = spread_1 - spread;
    
    % Select differences greater than the threshold (50bps). 
    condition1 = abs(diff1) > threshold; 
    condition2 = abs(diff2) > threshold;
    
    % Select only differences with opposite sign
    sign = diff1 .* diff2 <0;
    
    % Vector of logicals: the i-th component is 1 if the selected bond
    % satisfy all conditions(condition 1, condition 2 and sign), 0 
    % otherwise.
    index_jump = condition1 & condition2 & sign;
        
    % Increment the jump counter.
    count = count + sum(index_jump);
    
    % Increment total counter.
    tot = tot + numel(index_jump);
    
    % For the bonds that satisfy the conditions, in the central date (in
    % which there is a jump of 50 bps) compute the mean value between the 
    % spreads computed in the previous and next date.
    spread_1(index_jump) = 1/2 *(spread_2(index_jump) + spread(index_jump));
    ASWSpread(k-1).ASWSpreads(ismember(ASWSpread(k-1).Name, inters_bond)) = spread_1;
    
    
end

% Delete the field 'Name' from the struct ASWSpread.
ASWSpread = rmfield(ASWSpread, 'Name');

% Store the results of the computed Asset Swap Spread in 'spread.mat'.
save('spread.mat','ASWSpread');

end %Function