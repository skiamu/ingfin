function [s_asw, expDates, name] = Asset_spread(bond, value_date, t0, EONIA, payments)
% This function filters the bonds according to the 'filter_bond' function, 
% then, fixing a value_date, computes Asset Swap Spread over EONIA for 
% every selected bond, where the set of floating leg is equal to the 
% corresponding 3m OIS.
% The Asset Swap spreads are functions of bond expiry dates.
%
% INPUT:
%   bond: vector of structs with all information about the bonds. 
%   value_date: date in which evaluate the Asset Swap Spread.
%               [serial date number]
%   t0: settlement date (2 days after the value date). [serial date number]
%   EONIA: struct with discount factors and corresponding dates, computed
%          in the value date, with settlement date t0.
%   payments: vector of structs with floating and fixed payment dates for 
%             each bond.
%
% OUTPUT:
%   s_asw: Asset Swap Spread over EONIA.
%   expDates: expiry dates corresponding to each asset swaps.
%   name: name of the selected bonds.
%
% USES:
%   Discount_factors
%   filter_bond


% Select just bonds that satisfy the criteria
[bond_filtered, payments] = filter_bond(value_date, bond, payments);

% Day-count convention for the 'yearfrac'.
conv_act_act = 0;
conv_30_360  = 6;
conv_act_360 = 2; 

% Initialization.
s_asw = zeros(length(bond_filtered),1);
expDates = zeros(length(bond_filtered),1);
name = cell(length(bond_filtered),1);

for j = 1:length(bond_filtered);
    
    i = bond_filtered(j);
    p = payments(j);
    
    % In order to compute the asset swap, the clean price of the bond at
    % value date is considered.
    cleanP_0 = (i.pricesCleanValues((i.pricesDates) == (value_date)));
%    dirtyP_0 = (i.pricesDirtyValues((i.pricesDates) == (value_date)));

    % Coupon Value of the bond. 
    c = i.couponValue;
    
    % Select the index of the vector of fixed payments for the first date
    % exceeding the settement date.
    index_t1_F = find(p.fixed > t0,1);
    
    % Consider the dates from the previous date of t0 in order to compute
    % the accrual interest.
    % The index_t1_F is always greater or equal to 2, since the first
    % element of the fixed payments is the settlement date of the bond 
    % by construction.
    fixed_dates = p.fixed((index_t1_F)-1:end);
    % fixed_dates = [t_-1  t_1  ...  T]   CASO t_-1 < t_0
    %               [t_0   t_1  ...  T]   CASO t_-1 = t_0
    
    % Consider the floating payments dates after the settlement date.
    float_paym = p.floating( p.floating > t0 );
    
    % The settlement date is added to the vector of floating payment dates,
    % in order to compute the floating leg for the shor stub in advance.
    % The OIS rate considere fot this shorter lag is the one with a tenor
    % equal to the the corresponding period.
    float_dates = [t0; float_paym];
    % float_dates = [t_0   t_1  ...  T]  (t_1-t_0)<6m, (t_2-t_1)=6m, ...  CASO t_-1 < t_0 
    %               [t_0   t_1  ...  T]  (t_1-t_0)=6m, (t_2-t_1)=6m, ...  CASO t_-1 = t_0
    
    % Interpolate the discount factors in the fixed payment dates.
    fixed_B = Discount_factors( EONIA.Dates, EONIA.DiscountFactors,...
              fixed_dates(2:end), t0 );
    % fixed_B = [B(t_0,t_1)  B(t_0,t_2)  ...  B(t_0,T)]   
    % REM: #fixed_B = #fixed_dates - 1 
    
    % Interpolate the discount factors in the floating payment dates.
    float_B = Discount_factors( EONIA.Dates, EONIA.DiscountFactors, ...
        float_dates(2:end), t0 ); 
    % REM: Consider (2:end) since the first element of the vector of dates
    % contain t0.
    % float_B = [B(t_0,t_1)  B(t_0,t_2)  ...  B(t_0,T)]   
    
    % The discount factor at maturity is equal to the last computed
    % discount factor on the fixed payment dates.
    matur_B = fixed_B(end);
    
    % Compute the Basis Point Value for the fixed payments, with day-count 
    % convention ACT/ACT.
    fixed_BPV = fixed_B' * yearfrac( fixed_dates(1:(end-1)), ...
        fixed_dates(2:end), conv_act_act  ); 
    
    % Compute the Basis Point Value for the floating payments, with day-count 
    % convention ACT/360.
    float_BPV = float_B' * yearfrac( float_dates(1:(end-1)), ...
        float_dates(2:end), conv_act_360 ); 
    
    % Compute the accrual interest (day-count convention 30/360), in order 
    % to obtain the dirty price of the bond. 
    acc_perc = yearfrac(fixed_dates(1), t0, conv_30_360);    
    accrual = c * acc_perc;    
    dirtyP_0 = cleanP_0 + accrual;
    
    % Compute the Asset Swap Spread over EONIA, requiring that the Net
    % Present Value of the Asset Swap is equal to zero at value date.
    s_asw(j) = ( matur_B + c * fixed_BPV - dirtyP_0 ) / float_BPV;
    
    % Save the expiry date of the bond.
    expDates(j) = i.expDate;
    
    % Save the name of the bond.
    name(j) = i.BBGname;

end

end