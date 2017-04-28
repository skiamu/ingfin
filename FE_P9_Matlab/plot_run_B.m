%%%%%%%%%%%%%%%% plot run B  %%%%%%%%%%%%%%%%%%%%%
load('spread')
flag = 1;
i = 1122;
t0 = reference(i)+ 2 ;   
    if ~ isbusday(t0, eurCalendar())
        t0 = busdate(t0, 'follow', eurCalendar());
    end
    
figure
plot(ASWSpread(i).ExpiryDates, ASWSpread(i).ASWSpreads * 10000, 'bo-',...
    'markersize',6,'linewidth',1.4);
datetick('x','mm/yy','keepticks');
ylabel('asset swap spread [bps]');
title(['ASWS curve @',datestr(reference(i),'dd-mmm-yyyy')]);
grid on

figure
[tau_star, L_star, first_slope] = segmented_regression(ASWSpread(i).ExpiryDates,...
    ASWSpread(i).ASWSpreads, flag);
title(['ASWS curve @',datestr(reference(i),'dd-mmm-yyyy')]);