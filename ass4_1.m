%%%%%%%%%%%%%%%% Assignment 4 %%%%%%%%%%%%%%

clc;clear variables;close all;
load('data.mat');
s=[25,28,32]*10^-4;pi=0.25;
formatdata='dd/mm/yyyy';
settlement='07/02/2012';
settlement=datenum(settlement,formatdata);
year1='07/02/2013';year2='07/02/2014';year3='09/02/2015';
year=[datenum(year1,formatdata),datenum(year2,formatdata),datenum(year3,formatdata)];
B=discounts(find(ismember(days,year)));
%%%%%%%%%%%%%%%%%%% bootstrap %%%%%%%%%%%%%%%%%%%%%%

%Bootstrap(No accrual)
D(1)=B(1);
P(1)=(1-pi)*D(1)/((s(1)+1-pi)*B(1));
lambda(1)=-log(P(1))/yearfrac(settlement,year(1),2);
D(2)=B(2)*P(1)+B(1)*(1-P(1));
P(2)=((1-pi)*D(2)-s(2)*B(1)*P(1))/((s(2)+1-pi)*B(2));
lambda(2)=-(log(P(2)/P(1)))/yearfrac(year(1),year(2),2);
D(3)=B(3)*P(2)+(B(1)*(1-P(1))+B(2)*(P(1)-P(2)));
P(3)=((1-pi)*D(3)-s(3)*(B(1)*P(1)+B(2)*P(2)))/((s(3)+1-pi)*B(3));
lambda(3)=-log(P(3)/P(2))/yearfrac(year(2),year(3),2);

%Bootstrap(Accrual)
D_acc(1)=B(1);
P_acc(1)=(1-pi-s(1)/2)*D_acc(1)/((s(1)+1-pi-s(1)/2)*B(1));
lambda_acc(1)=-log(P_acc(1))/yearfrac(settlement,year(1),2);
D_acc(2)=B(2)*P_acc(1)+B(1)*(1-P_acc(1));
P_acc(2)=((1-pi-s(2)/2)*D_acc(2)-s(2)*B(1)*P_acc(1))/((s(2)+1-pi-s(2)/2)*B(2));
lambda_acc(2)=-(log(P_acc(2)/P_acc(1)))/yearfrac(year(1),year(2),2);
D_acc(3)=B(3)*P_acc(2)+(B(1)*(1-P_acc(1))+B(2)*(P_acc(1)-P_acc(2)));
P_acc(3)=((1-pi-s(3)/2)*D_acc(3)-s(3)*(B(1)*P_acc(1)+B(2)*P_acc(2)))/((s(3)+1-pi-s(3)/2)*B(3));
lambda_acc(3)=-log(P_acc(3)/P_acc(2))/yearfrac(year(2),year(3),2);

%%%%%%%%%%%%%%%%%%% plot %%%%%%%%%%%%%%%%%%%%
%plot solo lambda piece-wise constant
x=[settlement:0.1:year(1),year(1):0.1:year(2),year(2):0.1:year(3)];
y=[lambda(1)*ones(1,length(settlement:0.1:year(1)))...
   lambda(2)*ones(1,length(year(1):0.1:year(2)))...
   lambda(3)*ones(1,length(year(2):0.1:year(3)))];
figure(1)
plot(x,y,'b-','linewidth',2);
grid;datetick('x','mm/yyyy');
legend('lambda','location','best');
%plot accrual/no accrual
x=[settlement:0.1:year(1),year(1):0.1:year(2),year(2):0.1:year(3)];
y=[lambda(1)*ones(1,length(settlement:0.1:year(1)))...
   lambda(2)*ones(1,length(year(1):0.1:year(2)))...
   lambda(3)*ones(1,length(year(2):0.1:year(3)))];
y_acc=[lambda_acc(1)*ones(1,length(settlement:0.1:year(1)))...
   lambda_acc(2)*ones(1,length(year(1):0.1:year(2)))...
   lambda_acc(3)*ones(1,length(year(2):0.1:year(3)))];
figure
plot(x,y,'b-','linewidth',2);
hold on
plot(x,y_acc,'r:','linewidth',2);
grid;datetick('x','mm/yyyy');
legend('no accruel','accruel');
hold off

%%%%%%%%% Jurrow-turnball approximation %%%%%%%%%%%%%%%%%%%

lambda_JT=mean(s)/(1-pi);
figure
plot(x,lambda_JT*ones(1,length(x)),'g--','linewidth',3);
hold on
plot(x,y,'b-','linewidth',2);
plot(x,mean(lambda)*ones(1,length(x)),'r:','linewidth',3);
legend('lambdaJT','lambda pw-const','lambda mean','location','best');
disp('differenza lambda_const e mean(pw_lambda)=');
abs(mean(lambda)-lambda_JT)
hold off





