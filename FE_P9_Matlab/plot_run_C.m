%%%%%%%%%%%%%% plot part 3 %%%%%%%%%%%%%%%%%%


% % 10y_spread plot
% figure
% plot(reference, spread_10y * 10000, 'r-');
% ax = gca;
% ax.XTick = datenum('05/01/2007','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
% datetick('x','mm/yy','keepticks');
% ylabel('10y spread [bps]');
% title('10y asset swap spread');
% legend('10y asset spread', 'location','best')
% grid on

% short spread
figure
plot(filtered_reference, spread_10y(ismember(reference,filtered_reference)) * 10000, 'r-');
ax = gca;
ax.XTick = datenum('01/01/2008','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
datetick('x','mm/yy','keepticks');
ylabel('10y spread [bps]');
title('10y asset swap spread');
legend('10y asset spread', 'location','best')
grid on

% plot first slope
figure
plot(filtered_reference, first_slope* 10000 * 365,'r-')
ax = gca;
ax.XTick = datenum('05/01/2008','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
datetick('x','mm/yy','keepticks');
title('first slope[bps/y]');
legend('first slope','location','best');
grid on

%plot avarege time-to-slope change
figure
plot(ATSC_reference', ATSC, 'rx-', ATSC_reference', 2 * ones(1, length(ATSC_reference)),...
    'linewidth',1.6,'markersize',6,'markeredgecolor','b');
ax = gca;
ax.XTick = datenum('05/01/2008','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
datetick('x','mm/yy','keepticks');
ylabel('ATSC');
grid on

% plot ttsc with confidence interval
figure
plot(ATSC_reference', ATSC, 'r.-',....
     ATSC_reference', 2 * ones(1, length(ATSC_reference)),...
     'markersize',8,'linewidth',0.8);
ax = gca;
ax.XTick = datenum('05/01/2008','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
datetick('x','mm/yy','keepticks');
ylabel('ATSC[y]');
title('ATSC with confidence interval');

hold on
plot(ATSC_reference, CI(1,:)','.b-',ATSC_reference, CI(2,:)','.b-',...
    'markersize',8,'linewidth',0.9);
h = legend('ATSC','CI');
set(h, 'location','best');
grid on

% plot R^2
figure
plot(filtered_reference, R_2)
ax = gca;
ax.XTick = datenum('05/01/2008','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
datetick('x','mm/yy','keepticks');
title('R^{2}')
grid on;

figure
subplot(3,1,1)
plot(ATSC_reference', ATSC, 'rx-', ATSC_reference', 2 * ones(1, length(ATSC_reference)),...
    'linewidth',1.5,'markersize',5,'markeredgecolor','b');
ax = gca;
ax.XTick = datenum('05/01/2008','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
datetick('x','mm/yy','keepticks');
ylabel('ATSC');
title('ATSC');
legend('ATSC','2 years','location','best')
grid on

subplot(3,1,2)
plot(filtered_reference, first_slope * 10000 * 365,'r-')
ax = gca;
ax.XTick = datenum('05/01/2008','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
datetick('x','mm/yy','keepticks');
title('first slope');
ylabel('first slope [bps/y]')
legend('first slope', 'location','best');
grid on

subplot(3,1,3)
plot(filtered_reference, spread_10y(ismember(reference, filtered_reference))*10000, 'r-');
ax = gca;
ax.XTick = datenum('05/01/2008','dd/mm/yyyy'):365:datenum('05/01/2016','dd/mm/yyyy');
datetick('x','mm/yy','keepticks');
ylabel('10y spread [bps]');
title('10y asset swap spread');
legend('10y asset spread','location','best')
grid on

