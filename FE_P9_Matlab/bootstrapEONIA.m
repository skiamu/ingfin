function bootstrapEONIA(reference, maturity, rates)
% Compute the bootstrap for the EONIA curve (chosen as the discount 
% factors' curve). The bootstrap technique is standard and uses market 
% quotes of Overnight Indexed Swap rates with increasing maturity.
% Swaps with a maturity up to one year and swaps with longer maturities 
% are managed in different ways within the bootstrap.
% The rates are assumed to be quoted in the value dates given by the vector 
% 'reference', but the settlement days to be considered in order to build 
% the curve are two business days after. 
% For this reason, the curves are built in the value dates and discount all 
% cash flows two business days after.
% Store the results in 'EONIA.mat'. It is a vector of structs; for every
% value date, there are 3 fields: Dates(related to the dates in which
% rates are quoted), Rates (OIS rates), DiscountFactors (computed in the
% corresponding dates with bootstrap tecnique).
% 
% INPUT:
%   reference: dates in which EONIA curves are evaluated. [column vector]
%   maturity: time-to-maturity (expressed in months) related to the rates.
%             [row vector]
%   rates: OIS rates quoted in the market.
%          [matrix: length of reference x length of  maturity]
%
% OUTPUT:
%   None
%
% USES:
%   find_dates
%   eurCalendar

% Find in the vector of maturities the index corresponding to 1 year 
% swap expiry.
index_1y = find(maturity == 12, 1);   

% Initialization of the struct in which data will be stored.
EONIA = struct('Dates', {}, 'Rates', {}, 'DiscountFactors', {});

% Day-count convention for the bootstrap tecnique.
act_360 = 2;

for j = 1 : length(reference)
   
    %t0: settlement date, two business days after value date (= reference(j)).
    t0 = reference(j)+ 2;   
    t0(~isbusday(t0, eurCalendar)) = busdate(t0, 'follow', eurCalendar);
    
    % Consider the rates for the given value date (selecting a row of the 
    % matrix rates each step). 
    rates_temp = rates(j,:);
    
    % Find, starting from the settlement day, the business days related to 
    % the given maturity.
    dates = find_dates(t0, maturity);                                     
    
    % Initialization of the vector of discount factors.
    discounts = zeros (1, length(dates));
    
    % Discounting curve up to 1year.
    discounts(1:index_1y) = 1 ./ ( 1 + yearfrac(t0, dates(1:index_1y), act_360) ...
                            .* rates_temp(1:index_1y));   
    
    % Discounting curve longer than 1year.
    somma = discounts(index_1y) * yearfrac(t0, dates(index_1y), act_360);
    for i= (index_1y + 1):length(discounts)
        discounts(i) = (1 - rates_temp(i) * somma)/(1 + yearfrac(dates(i-1),...
                        dates(i),act_360) * rates_temp(i));
        somma = somma + discounts(i) * yearfrac(dates(i-1), dates(i), act_360);
    end
    
    % Save the results in the EONIA struct. 
    % REM: we compute the transpose to save the results as column vectors.
    EONIA(j).Dates = dates';
    EONIA(j).Rates = rates_temp';
    EONIA(j).DiscountFactors = discounts';
    
end

save('EONIA.mat', 'EONIA', 'reference')

end %Function
