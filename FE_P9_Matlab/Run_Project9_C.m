%% Run C - ASW spread over EONIA

load('EONIA.mat');
load('bond.mat');
load('spread.mat');


% Count how many bonds on average the asset swap curve.
count = zeros(1,length(ASWSpread));
for j = 1:length(ASWSpread)
    count(j) = numel(ASWSpread(j).ASWSpreads);
end
disp(['There are on average ', num2str(mean(count)),' asset spreads in a term structure']);
disp('-----------');

% Set the threshold for the average 10y_spread.
threshold = 20e-4;

% Filter 10y_spreads whose monthly average is below the threshold.
[ASWSpread, filtered_reference, spread_10y] = filter_spread (threshold, ASWSpread, reference );

% Compute ATSC (Average Time to Slope Change).
[ATSC, ATSC_reference, L_star, first_slope, CI] = Avg_TTSC(filtered_reference, ASWSpread);

% Compute the coefficient of determination.
R_2 = coefficient_of_determination(L_star, ASWSpread, filtered_reference);

% Plot the financial instability measures.
plot_run_C;

