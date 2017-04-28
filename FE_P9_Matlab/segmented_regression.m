function [tau_star, L_star, first_slope] = segmented_regression(T, s, flag)
% This function detects the optimal single segmented line and choose 
% the optimal regression parameters.
%
% INPUT:
%	T: bond maturity dates [vector]
%      REM: T must be sorted.
%   s: corresponding asset swap spreads [vector]
%   flag : 1) plot activated
%          0) plot disactivated
% OUTPUT:
% 	tau_star: time-to-slope change [real]
%   L_star: least sum of squares [real]
%   first_slope: slope of the first line [real]
%
% USES:
%   constrained_optimization
%   linear_regression


N = length(T);

% Initialization
L = zeros(N - 3, 1);
tau = zeros(N - 3, 1);
lines_coeff = zeros(4, N - 3);

% First and second element are set to infinity.
L(1:2) = 1e+9;
tau(1:2) = 1e+9;

% Start the cycle from k = 3 to have in each segment at least 3 points, in
% order to have non-trivial fits.
for k = 3 : (N-3)
    
    % Split the sequence of s and T in two sub-intervals, one containing 
    % the first k points and the second containing the last N - k points.
    s1 = s(1:k);
    s2 = s((k+1):end);
    T1 = T(1:k);
    T2 = T((k+1):end);
    
    % Compute two independent linear regressions on each sub-interval:
    % coeff = regression coefficients
    % L = minimum sum of squares
    [coeff1, L1] = linear_regression (T1, s1);
    [coeff2, L2] = linear_regression (T2, s2);
    
    % Update the matrix of regression coefficients.
    lines_coeff(:,k) = [coeff1; coeff2];
    
    % Compute the candidate for the least residual sum of squares.
    L(k) = L1 + L2;
    
    % Check if the two regressions have a unique fit.
    if coeff1 == coeff2  
        % Set the time-to-slope to infinity
        tau(k)=1e+9;   
        
    else   
        % The two stright lines are different, hence find the intercept.
        t = (coeff2(2)-coeff1(2)) / (coeff1(1)-coeff2(1));  
        
        % Check if they meet inside the interval between the k-th
        % (included) and the (k+1)-th expiries
        if t < T(k+1)  &&  t >= T(k)
            % The intercept is the k-th candidate point of time-break.
            tau(k) = t;
            
        else
            % Otherwise, the algorithm tests both extreme expiries (t_k and
            % t_(k+1)) as abscissa of the change point. 
            % Perform two constrained linear regressions.
            % Since the residual sum of squares in the constrained case is
            % always greater or equal to the independent case.
            % This test is performed only if the residual sum of squares 
            % for the two independent regression is lower than all 
            % candidate values computed up to step k.
            if L(k) < min(L(1:(k-1)))
                
                % Left constrained optimization
                [p_L, L_l] = constrained_optimization(T1, s1, T2, s2, T(k));
                
                % Right constrained optimization
                [p_R, L_r] = constrained_optimization(T1, s1, T2, s2, T(k+1));
                
                % Check which optimization gives the lower residual sum of
                % squares and set this value and the corresponding
                % time-break as the candidate value for the k-th step.
                if L_l > L_r
                    tau(k) = T(k+1);
                    L(k) = L_r;
                    lines_coeff(:,k) = p_R;
                else
                    tau(k) = T(k);
                    L(k) = L_l;
                    lines_coeff(:,k) = p_L;
                end
                
            end
        end
    end
end

% Determine the index K that corresponds to the least sum of squares and
% also the corresponding value.
[L_star, K] = min(L);
% Determine the corresponding time-break.
tau_star = tau(K);
% Consider the corresponding slope of the first line.
first_slope = lines_coeff(1,K);

%% plot

if flag == 1
    p = lines_coeff(:,K)';
    s1_line =  polyval(p(1:2),[T(1:K); tau_star])*10000;
    s2_line = polyval(p(3:4),[tau_star; T((K+1):end)])*10000;
    plot([T(1:K); tau_star], s1_line,'r-', ...
        [tau_star ;T((K+1):end)], s2_line, 'r-',...
        T, s*10000,'bo-','linewidth',2);
    datetick('x','mm/yy','keepticks');
    ylabel('asset spread [bps]');
    grid on
end




end %Function