function [p, L] = constrained_optimization(T1, s1, T2, s2, tau)
% Compute the constrained linear regression solving a constrained least
% squares problem:
%
%     min  0.5*(NORM(C*x-d)).^2    
%     x                               
%
% INPUT:
% 	T1: first set abscissa.  [column vector]
% 	s1: first set ordinate.  [column vector]
%  	T2: second set abscissa.  [column vector]
% 	s2: second set ordinate.  [column vector]
%         
% OUTPUT:
%   p: [a1 b1 a2 b2] lines parameters.
%   L: minimum sum of squares.  [real]


n = length(T1);   

m = length(T2);

% Define the coefficient matrix (non singular).
C = [[T1; ones(m,1) * tau], ones(n+m,1), [zeros(n,1); T2-tau]];

d = [s1; s2];

% Solve the least squares problem.
x = C\d;

% Compute least sum of squares.
L = (norm(C*x-d)).^2;

% Vector of lines parameters.
p = [x; x(2) + x(1) * tau - x(3) * tau];

end %Function