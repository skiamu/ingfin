%% Read EONIA data from Excel
% The sheet can be represented as a big matrix, columns are EONIA swap
% rate quotes for different days and rows are EONIA term  structure
% for a fixed value date.
%
% REMARK : while reading data different filters have been applied (please 
% see the report for more information)

% Set Excel filename, sheet, and range to get EONIA data.
FileName = 'INPUT_rate_curves.xlsx';
Sheet = 'EONIA';
Range = 'A4:AF2355';   

% Set italian format data
formatData = 'dd/mm/yyyy';

% Time lag of interest
t_1 = datenum('01/01/2007',formatData);
t_N = datenum('31/12/2015',formatData);

% Read EONIA data from Excel spreadsheet + data mining
[reference, rates] = ReadXL_EONIA(FileName, Sheet, Range, t_1, t_N);

% Set Eonia swap rate maturity
maturity = [(1:6), (1:10)*12]; 

% Bootstrap EONIA curve for every day in reference
bootstrapEONIA(reference, maturity, rates);


%% Read bond data from Excel
% Read from an Excel spreadsheet bond (Italian BTP) info, all bonds are
% supposed to be involved in an Asset Swap. Save all the information
% in a vector of structs with variuos fields.

% Set the frequency of the floating leg in a Asset swap contract
% 1 = yearly
% 2 = semiannualy
% 4 = quarterly
floatFrequency = 4;

% Read data + data mining
ReadXL_bond('INPUT_BTP_Dirty.xlsx', 'Info', 'A3:I143', 'Data', 'A3:UQ2350',...
            formatData, reference, floatFrequency);
        
 %% Plots
 % Plot a discount factors curve and zero-rates curve as an example.
 % Uncomment the line below to get plots.
 %plot_run_A;
 
 
 
 
        
        