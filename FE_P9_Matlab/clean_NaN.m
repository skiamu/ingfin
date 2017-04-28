function [ Vector_OUT ] = clean_NaN( Vector_IN )
% 'Clean' Vector_IN cutting the 'NaN' elements.
%
% INPUT:
%	 Vector_IN  = vector containig reals and Nan
%
% OUTPUT: 
% 	 Vector_OUT = vector containig reals

Vector_OUT = Vector_IN( ~isnan(Vector_IN));

end %Function