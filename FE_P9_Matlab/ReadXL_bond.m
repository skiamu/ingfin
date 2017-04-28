function  ReadXL_bond(FileName, Sheet1, Range1, Sheet2, Range2, formatData, reference, floatFrequency)
% Read the bond data from the file Excel and filter them, compute the dates 
% in which payments occur. Store all the results in 'bond.mat', which 
% contains all data about bond in the struct 'bond' and 'payments.mat' with
% the computed payment dates in the struct 'Payments'.
% 
% INPUT:
%   FileName: [string]
%   Sheet1: Worksheet related to the data of the bonds. In particular it 
%           should be structured as follow: in each row it must contain (in 
%           the following order) the name of the bond, the settlement date,
%           the expiry date, the first coupon date, kind of coupon ('FIXED', 
%           'ZERO COUPON'), coupon value, coupon frequency, inflation 
%           linked indicator (yes,'Y', or not,'N'), issue.   [string]
%   Range1: Range of the cells of the previous sheet to be read, using the
%           syntax 'A1:Z9'.   [string]
%   Sheet2: Worksheet containing the last prices and the dirty mid prices
%           for each value date.  [string]
%   Range2: Range of the cells of the previous sheet to be read. [string]
%   reference: business days in the time interval [t_1,t_N]. [column vector]
%   floatFrequency: frequency of the floating payments.  [real]
%   formatData: format data of the dates in the file Excel.  [string]
% 
% OUTPUT:
%    None
%
% USES:
%    Clean_NaN
%    pay_floating
%    pay_fixed


% Read data from the file Excel, using the matlab function 'xlsread'.
bond_data = xlsread(FileName, Sheet2, Range2); 

% In 'num' the numeric datas are stored, in 'txt' the text fields are 
% imported in cell arrays. 
[num, txt] = xlsread(FileName, Sheet1, Range1);  

% Constraint on bond liquidity.
LiquidityThreshold = 5e8;

% Set the bond cardinality.
N_bond = size(num,1);

% Initialization of the structs in which data will be stored.
bond = struct('BBGname', {}, 'settleDate', {}, 'expDate', {}, ...
       'firstCouponDate', {}, 'couponValue', {}, 'couponFrequency', {}, ...
       'pricesDates', {}, 'pricesCleanValues', {});

Payments = struct('floating', {}, 'fixed', {});

% Counter initialization.
k=1;

% Loop on the number of bond.
for i=1:N_bond
    % Conditions in order to filter dataset.
    condition1 = num(i,4) > LiquidityThreshold;                 % Issue size higher than 500 mlns. 
    condition2 = strcmp(txt(i,8), 'N');                         % No inflation.
    condition3 = strcmp(txt(i,5), 'FIXED');                     % Bond with fixed coupon.
    condition4 = datenum(txt(i,2),formatData) >= datenum('01/01/1999', 'dd/mm/yyyy') && ...
                 datenum(txt(i,2),formatData)<= reference(end); % SettleDate in ['01/01/1999' t_N].
    
    if (condition1 && condition2 && condition3 && condition4)
    % If a bond satisfies all requirements
    
        % Save this in the struct 'bond'.
        bond(k).BBGname           = txt(i,1);                              % Name of the bond.
        bond(k).settleDate        = datenum(txt(i,2), formatData);         % Settlement Date (SD).
        bond(k).expDate           = datenum(txt(i,3), formatData);         % Expiry Date (ED).
        bond(k).firstCouponDate   = datenum(txt(i,4), formatData);         % Date of the first coupon (FC).
        bond(k).couponValue       = 1/100 * num(i,1);                      % Coupon (in the file Excel it is in percentage).
        bond(k).couponFrequency   = num(i,2);                              % Coupon Frequency.
        bond(k).pricesDates       = x2mdate(clean_NaN(bond_data(:,4*i-3)));% Dates in which the prices of the bonds are evaluated.
        bond(k).pricesCleanValues = 1/100 * clean_NaN(bond_data(:,4*i-2)); % Last prices of the bond (in the file Excel they are in % of notional 100).

        % Save the payments dates in the struct 'Payments'.
        Payments(k).floating = pay_floating(bond(k).settleDate,...    
                                bond(k).expDate, floatFrequency);          % Floating payment dates in the interval [settleDate, expDate] plus the settlement date.
        % Payments(k).floating = [ P P ... P ED ], where P is a generic
        % payment date after the settlement date.
                            
        Payments(k).fixed = pay_fixed(bond(k).settleDate, bond(k).firstCouponDate,...
                                bond(k).expDate, bond(k).couponFrequency); % Coupon payment dates in the interval [firstCouponDate, expDate]. 
        % Payments(k).fixed = [ SD FC C ... C ED ]
                            
        k = k+1;
    end
end

% Bond survived to the filter.
n = numel(bond);

% Print how many bonds have survived the bond filter.
disp([num2str(N_bond - n),' bonds have been filtered out because of criteria, out of ',...
      num2str(N_bond)]);
disp('-----------');

% Save the results.
save('bond.mat','bond')
save('payments.mat','Payments')

end %Function