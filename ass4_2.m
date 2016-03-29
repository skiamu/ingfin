%%%%%%%%%%%%%%%% assignment 4_2  %%%%%%%%%%%%%%%
clc;close all;clear variables;

%% simulation
lambda=3.5*10^-3;
P=@(T)exp(-lambda*T);    
T=linspace(0,1000,100);
figure(1)
plot(T,P(T),'LineWidth',3);   %plotto la survival probability
xlabel('T');grid;legend('P(0,T)','location','best');
N=20;
u=rand(N,1);                  %capione di uniformi in [0,1]
tau_u=@(u)-log(u)./lambda;    %inversa della survival probability
tau=tau_u(u);                 %vettore delle tau osservate
t=0:(25/10^5):25;               
prob=ones(1,length(t));       
for i=1:length(t)             % distribuzione empirica
    x=tau(tau<=t(i));         %estraggo le tau minori di t nel continuo
    prob(i)=1-length(x)/length(tau); %experimantal survival probability
end

%% plot
figure
plot(t,prob,'b-');            
hold on
plot(t,P(t),'r-');
xlabel('years');
legend('experimental','theoretical','location','best');
figure
semilogy(t,prob,t,P(t));
xlabel('years');
legend('experimental','theoretical','location','best');
%% goodness of fit
cdf_theoric=makedist('exponential','mu',1/lambda);
[h,p]=kstest(tau,'CDF',cdf_theoric);


    
