function  [ASWSpread_out, dates_out, spread_10y] = filter_spread (threshold, ASWSpread_in, dates_in )
% This function filters out the months in which the monthly average of the 
% ASW spread is constantly below threshold.
%
% INPUT:
%   threshold: value below which the monthly average of the spreads is
%              filtered out.   [real]
%   ASWSpread_in: vector of structs containing the spread and the 
%                 corresponding expiry dates for every day in dates_in.
%                 [real]
%   dates_in: dates on which evaluate the monthly average. [serial date
%             number]
%          (REM1: dates MUST be increasing t_(i)<t_(i+1), so if they are  
%                 decreasing call the function like this:
%                 >>filter_spread( threshold, flip(ASWSpread), flip(dates))
%          (REM2: ASWSpread_in and dates in must have the same length)
% OUTPUT:
%   ASWSpread_out: filtered ASWSpread_in. [vector of structs]
%   dates_out: filtered dates_in. [column vector]
%   spread_10y: (needed for the plot) [real]
%
% USES:
%    monthly_avg


% Select the 10y-spreads.
spread_10y = zeros(length(dates_in),1);
for i = 1: length(dates_in)
    
    % Sort the vector of the expiry dates.
    [~ ,q] = sort([ASWSpread_in(i).ExpiryDates],1);     % q = index vector related to the order of dates.
    % Consider the spreads according to the order of the expiry dates.
    sorted_spreads = ASWSpread_in(i).ASWSpreads(q);
    % Since the vector of the spreads is sorted in ascending order, the
    % 10y-spread is just the last element of the vector.
    spread_10y(i) = sorted_spreads(end);
    
end

% Compute the monthly average of the 10y-spreads. 
[avg, i_first, ~] = monthly_avg(spread_10y, dates_in); 

% Add the last indeces of dates_in +1 in order to simplify the computations 
% to select the dates in the intervals given by 'i_first'.
i_first = [i_first, numel(dates_in)+1];
% Example:
%	BEFORE ---> i_first = [1 9 29]
%	AFTER  ---> i_first = [1 9 29 35]  where dates(35-1)=dates(end)     

% Initialization of the vector index_out (containing the indeces to be 
% filtered out). It is initialized as empty vector in order to attach for
% every step the indeces that no satisfy the condition.
index_out = []; 

% Copy 'dates_in' in 'dates_out' and 'ASWSpread_in' in 'ASWSpread_out', in
% order to drop out from the new vectors the dates satisfying the
% condition.
dates_out = dates_in;
ASWSpread_out = ASWSpread_in;
k = 0;

for j = 1:length(avg)
    % Verify if the monthly average is below he threshold (if this
    % condition is satisfied, j will denote the position of months in the
    % vector i_first)
    if avg(j) < threshold    
        k = k + 1;
        
        % Update the vector index_out, adding the indeces of dates_in to be
        % filtered out.
        index_out = [index_out, i_first(j):(i_first(j+1)-1)];   
    end
end

disp([num2str(k),' months have an average 10y_spread below 20bps']);
disp('-----------');

% Drop out the selected dates.
dates_out(index_out) = []; 
ASWSpread_out(index_out) = [];

end