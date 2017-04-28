%% Run B - ASW spread over EONIA
% Run B computes Asset Swap Spread over Eonia, that is a swap term
% structure ( a swap for different bond maturity) for every value date 
% (elements of the vector reference)

load('EONIA.mat');
load('bond.mat');
load('payments.mat');

% Compute asset swap spread term structure for every day in reference
[count, tot] = make_spreads(reference, EONIA, bond, Payments);


disp([num2str(count),' jumps have been filtered out']);
disp('-----------');


%% plot
% uncomment line below  to get plot of ASWS curve

%plot_run_B;