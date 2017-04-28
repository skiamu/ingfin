function R_2 = coefficient_of_determination(L_star, ASWSpread, reference)
% Compute the the coefficient of determination R^2, that is an indicator 
% about the quality of model fit.
%
% INPUT:
%    L_star:  column vector of least residual sum of squares. [real]
%    ASWSpread: vector of structs containing the computed spreads in the
%               field 'ASWSpreads' and the corresponding expiry of the 
%               bonds in 'ExpiryDates'. 
%    reference: vector of business day in the considered time interval.
%               [serial date number]
%
% OUTPUT:
%    R_2: coefficient of determination [percentage]

% Initialization.
TSS = zeros(length(reference),1);

% Compute the total sum of square for each day in reference.
for k = 1:length(reference)
    
    % Residual square of the Asset Swap spreads.
    tss = (ASWSpread(k).ASWSpreads - mean(ASWSpread(k).ASWSpreads)).^2;
    
    % Total sum of squares
    TSS(k) = sum(tss);
end

% Compute the coefficients of determination
R_2 = 1 - L_star./TSS;
avg = mean(R_2);

disp(['On average the value of the coefficient of determination is equal to: ' ,num2str(avg)])
disp('-----------');
end %Function