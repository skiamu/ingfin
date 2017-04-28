%%%%%%%%%% plot discount curve   %%%%%%%%%%

load('EONIA');
i = 500;
Act_365 = 3;

% plot discount curve
figure
plot(EONIA(i).Dates, EONIA(i).DiscountFactors, 'ob-',...
    'linewidth',1.3,...
    'markersize',5);
grid on
h = legend('$B(t_0,t_i)$');
title('Discount factors curve');
datetick('x','mm/yy','keepticks');
set(h,'interpreter','latex','fontsize',18,'location','best');

% plot zero rates
figure
z_r = - log(EONIA(i).DiscountFactors) ./ yearfrac(reference(i),EONIA(i).Dates, Act_365);       
plot(EONIA(i).Dates, z_r*100, 'ob-',...
    'linewidth',1.3,...
    'markersize',5);
grid on
h = legend('$z(t_0,t_i)$');
title('zero-rates curve');
datetick('x','mm/yy','keepticks');
ylabel('zero-rates[%]')
set(h,'interpreter','latex','fontsize',18,'location','best');