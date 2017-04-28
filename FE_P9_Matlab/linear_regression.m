function [p, L] = linear_regression (x, y)
% Compute linear regression of x against y.
% 
% INPUT:
%   x: abscissa values [column vector]
%   y: ordinate values [column vector]
% 
% OUTPUT:
%   p: regression line coefficient ( y = p(1) * x + p(2) )
%   L: minumum sum of squares


n = length(x);

% Define the coefficient matrix.
C = [x ones(n, 1)];

% Solve least squares problem
p = C\y;

% Compute the least sum of squares.
L = (norm(C * p - y)).^2;

end %Function


