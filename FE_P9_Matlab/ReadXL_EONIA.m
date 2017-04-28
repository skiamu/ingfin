function  [reference, rates] = ReadXL_EONIA( FileName, Sheet, Range, t_1, t_N)
% Read EONIA data from the file Excel and perform datamining. It returns 
% a column vector with the business days in the time interval considered in
% ascending order and a matrix with the OIS rates, each row contains the
% rates for the selected maturities and for a fixed value date.
% 
% INPUT:
%   FileName: [string]
%   Sheet: [string]
%   Range: excel range to read the whole matrix. [string]
%   t_1, t_N: time interval to be studied. [serial date number]
% 
% OUPUT:
%   reference: business days in the time interval [t_1,t_N].   
%              [serial date number]
%   rates: OIS rates corresponding to the considered dates.    [real]
%
% USES:
%   clean_NaN 
%   eurCalendar


EONIA_data = xlsread(FileName, Sheet, Range);
% With the previous line we access the .xlsx file only one time (that is
% faster comparing to accessing it one time for each column). 
% The price to pay is that at the end of some columns there are NaN 
% corresponding to the empty cells.
% To solve this problem it is used 'clean_NaN()' that cuts the 'NaN'.

% Change all dates from Excel to Matlab convention.
index_dates = 1:2:size(EONIA_data,2);
EONIA_data(:,index_dates) = x2mdate(EONIA_data(:,index_dates));    

% Clean the vector from 'NaN' elements and consider only dates in the
% considered time interval [t_1,t_N].
reference = clean_NaN(EONIA_data(:,end-1)); 
reference = reference((reference >= t_1) & (reference <= t_N));          

% In the file Excel there are some dates in which the rates are not quoted 
% for each maturiry. To solve this problem, these dates are not considered
% (filter1).

N_before_f1 = length(EONIA_data(EONIA_data(:,1)>= t_1 & EONIA_data(:,1)<= t_N, 1));
for j = 1:2:size(EONIA_data,2)-2
    dates_temp = clean_NaN(EONIA_data(:,j));                               
    reference = reference(ismember(reference, dates_temp));   
end
N_after_f1 = length(reference);

% Print how much data has been filtered out by filter1.
disp('-----------');
disp([num2str(N_before_f1 - N_after_f1),...
     ' dates have been filtered out because of no quoted rates, out of ', ...
     num2str(N_before_f1)]);
disp('-----------');

% Select only the business days, according to the European Calendar
% (filter2).
reference = reference(isbusday(reference, eurCalendar));
reference = flip(reference);        %ascending order.
N_after_f2 = length(reference);

% Print how much data has been filtered out by filter2.
disp([num2str(N_after_f1 - N_after_f2),...
    ' dates have been filtered out because of no business, out of ',...
    num2str(N_after_f1)]);
disp('-----------');

% Initialization of the matrix which will contain all the rates. 
rates = zeros(length(reference),size(EONIA_data,2)/2);

% Counter in order to save the rates.
k = 1;

% Save the OIS rates corresponding to the selected dates.
for j = 1:2:size(EONIA_data,2) 
    dates_temp = clean_NaN(EONIA_data(:,j));  
    
    % In the file excel the rates are in percentage, so they are divided by
    % 100.
    rates(:,k) = 1/100 * EONIA_data(ismember(dates_temp,reference),j+1);  
    k = k+1;
end

rates = flip(rates);     % ascending order.

end %Function