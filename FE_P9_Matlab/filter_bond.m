function [bond_out, payments_out] = filter_bond(value_date, bond, payments)
% This function filters the bonds requiring for every business day t0 
% between t1 and tN to select available bonds with expiry in the range 
% [t0 + 2m, t0 + 10y]. 
% Moreover, there are some filters needed to overcome to some outlier.
%
% INPUT:
%   value_date: date in which the contract is evaluated. [serial date
%               number]
%   bond: vector of struct containing all informations about the bonds.
%   payments: vector of struct containing all the fixed and floating
%             payment dates of each bond.
%
% OUTPUT:
%   bond_out: vector of struct containing only the filtered bonds.
%   payments_out: vector of struct containing all the fixed and floating
%                payment dates of the filtered bonds.


% Evaluate the dates corresponding to the extremes of the interval:
t0_2m = datemnth(value_date, 2);   % [value_date + 2 months,
t0_10y = datemnth(value_date, 10*12);   % value_date + 10 years]

% Initialization of the struct 'bond_out' which will contain the
% information about the filtered bonds, and 'payments_out', which will
% contain the floating and fixed payments of the selected bonds.
bond_out = struct('BBGname', {}, 'settleDate', {}, 'expDate', {}, ...
       'firstCouponDate', {}, 'couponValue', {}, 'couponFrequency', {}, ...
       'pricesDates', {}, 'pricesCleanValues', {});

payments_out = struct('floating', {}, 'fixed', {});

N = length(bond);
k = 1; 
for j = 1 : N 
    i = bond(j);
    p = payments(j);
    
    % Consider the bonds which expiry is in the interval [value_date + 2m,
    % value_date + 10y]
    condition_1 = (t0_2m <= i.expDate) && (i.expDate <= t0_10y);
    
    % There are some bonds for which there is a price in a date before the
    % settlement date, hence consider only bonds for which the value_date
    % is after the settlement.
    condition_2 = i.settleDate < value_date;
    
    % There are some bonds not priced for every dates, hence consider only
    % the bonds for which there is a price for the condisered value_date.
    condition_3 = ismember(value_date, i.pricesDates);
    
    % There are some bond prices surely incorrect. To solve this problem
    % consider only bonds for which the price is below a certain threshold:
    % suppose this equal to 10.
    condition_4 = i.pricesCleanValues((i.pricesDates) == (value_date)) < 10;

    if condition_1 && condition_2 && condition_3 && condition_4
        
        % Save the information about the bonds satisfying these conditions.
        bond_out(k) = i;
        payments_out(k) = p;
        k = k+1;
    end
    
end




end %Function