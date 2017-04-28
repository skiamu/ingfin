function B = Discount_factors(dates, discounts, t, t0)
% This function returns the vectors of the discounts via interpolation on
% the zero rates, obtained by the discount factors.
%
% INPUT:
%	dates: Column vector of dates where discounts have been already 
%           computed. [serial date number]
%   discounts: Vector of discounts already computed. [real]
%   t0: Settlement date. [serial date number]
%   t: Column vector of dates in which the interpolation is provided. It 
%       must be in ascending order. [serial date number]
%
% OUTPUT:
%   B: Discount factors at t.  


% Day-count convention for the computation of zero rates from the
% discount factor
Act_365 = 3;

% Compute the zero rates from the bootsrapped discounts. 
z_r = - log(discounts) ./ yearfrac(t0,dates, Act_365);       

% Initialization of the interpolated zero rates.
z = zeros(length(t),1);

i = 1;
 
% If the dates in which interpolate are less or equal to the first date in
% which the discount factor is computed, the interpolated zero rate is 
% constant and equal to the one of the first discount.
while t(i) <= dates(1)
    z(i) = z_r(1);
    i=i+1;
end

% The other zero rates are computed via a linear interpolation.
z(i:end) = interp1(dates, z_r, t(i:end));               

% The interpolated discounts factors are obtained by inverse formula of 
% zero rates.
B = exp(- z .* yearfrac(t0, t, Act_365));                                        

end %Function