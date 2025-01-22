% clear;close all;clc
% addpath('C:\Users\lzhan\Desktop\Lu_start\Archive_Research\Sample_analysis\LZhan\Custom_functions_ANL');
% addpath('C:\Users\lzhan\Desktop\Lu_start\Archive_Research\Sample_analysis\LZhan\Custom_functions');

%% Load data
datapath = 'C:\Users\ddas\Documents\Data\AMTL-Test-Data\';

% Data.mat = load([datapath,'XILresults_72405033.mat']);
% Data.txt = readtable([datapath,'62008001 Test Data.txt']);
Data.txt = TDMS_readTDMSFile([datapath,'62007023 Test Data.tdms']);

%% Load Vars
var_naming_group;
HVbatt.power__w = HVbatt.HVBatt_current_wide_CAN5__A.*HVbatt.HVBatt_voltage_CAN5__V;

%% check plot

% DAQ time does not start from zero in the dataset
[~,min_ind] = min(DAQtime);
start_index = min_ind;

% figmk(.5,.6);
figure;
subplot(3,1,1);hold on;
plot(DAQtime(start_index:end), HVbatt.HVBatt_voltage_CAN5__V(start_index:end))
plot(DAQtime(start_index:end), Hioki.U1(start_index:end));
grid on;box on; xlabel('DAQ time [s]');ylabel('Voltage [V]')

subplot(3,1,2);hold on;
plot(DAQtime(start_index:end),-HVbatt.HVBatt_current_wide_CAN5__A(start_index:end))
plot(DAQtime(start_index:end),Hioki.I1(start_index:end));
grid on;box on; xlabel('DAQ time [s]');ylabel('Current [Amps]')

subplot(3,1,3);hold on;
plot(DAQtime(start_index:end),-HVbatt.power__w(start_index:end))
plot(DAQtime(start_index:end), Hioki.P1(start_index:end));
grid on;box on; xlabel('DAQ time [s]');ylabel('Power [W]')
% plot(Hioki.U2(start_index:end))
% plot(Hioki.U3(start_index:end))
% plot(Hioki.U4(start_index:end))
% plot(Hioki.U5(start_index:end))
% plot(Hioki.U6(start_index:end))
% plot(Hioki.U7(start_index:end))
% plot(Hioki.U8(start_index:end))
%% Calculation

CANpower_cal    = HVbatt.power__w/1000 ;
index_ps        = CANpower_cal > 0;
index_ng        = CANpower_cal < 0;
HVbattpos       = CANpower_cal;HVbattpos(index_ng) = 0;
HVbattneg       = CANpower_cal;HVbattneg(index_ps) = 0;


Dpos = cumtrapz(DAQtime(start_index:end), HVbattpos(start_index:end));
Dneg = cumtrapz(DAQtime(start_index:end), HVbattneg(start_index:end));
Dint = (Dpos + Dneg)/3600;  % unit kwh

hioki_inP = (Hioki.WP1(start_index:end) -Hioki.WP1(start_index))/1000; %kw


%%
Pe = (Dint - hioki_inP)./hioki_inP;

%% figure check
% filter = logical((HVbatt.power__w>=-Inf).*(Hioki.U1>=-Inf).*(Dyno.spd>=0.01).*((1:length(DAQtime))>=start_index)');
% filter = logical((HVbatt.power__w>=-Inf).*(Hioki.U1>=-Inf).*(Dyno.spd>=0.01).*((1:length(DAQtime))>=start_index)');
filter = logical((HVbatt.power__w>=-Inf).*(Hioki.U1>=250).*(Dyno.spd>=0.01).*((1:length(DAQtime))>=start_index)');

% figmk(.35,.6);
figure;
subplot(2,2,1);
plot_lin_fit(HVbatt.HVBatt_voltage_CAN5__V(filter), Hioki.U1(filter));
xlabel('CAN voltage [v]');ylabel('Hioki Voltage [v]')
grid on;box on;axis equal;axis tight
title(['RMS:',num2str(rms(HVbatt.HVBatt_voltage_CAN5__V(filter) - Hioki.U1(filter)))])

subplot(2,2,2);
plot_lin_fit(-HVbatt.HVBatt_current_wide_CAN5__A(filter), Hioki.I1(filter) );
xlabel('CAN current [A]');ylabel('Hioki current [A]')
grid on;box on;axis equal;axis tight;
title(['RMS:',num2str(rms(-HVbatt.HVBatt_current_wide_CAN5__A(filter) - Hioki.I1(filter)))])

subplot(2,2,3);
plot_lin_fit(-HVbatt.power__w(filter)/1000, Hioki.P1(filter)/1000);
xlabel('CAN I*V [kw]');ylabel('Hioki Active Power [kw]')
grid on;box on;axis equal;axis tight;
title(['RMS:',num2str(rms(-HVbatt.power__w(filter)/1000 - Hioki.P1(filter)/1000))])

subplot(2,2,4);
plot_lin_fit(abs(Dint), hioki_inP);
xlabel('CAN Integrated power [kwh]');ylabel('Hioki Integrated Power [kwh]')
grid on;box on;axis tight;axis equal;
title(['RMS:',num2str(rms(abs(Dint) - hioki_inP))])
%% Time series 
DAQT_fil    = DAQtime(start_index:end);
CAN_Vfil    = HVbatt.HVBatt_voltage_CAN5__V(start_index:end);
CAN_Ifil    = -HVbatt.HVBatt_current_wide_CAN5__A(start_index:end); % flip the sign here
CAN_Pfil    = -HVbatt.power__w(start_index:end); % flip the sign here
HiokiVfil   = Hioki.U1(start_index:end);
HiokiIfil   = Hioki.I1(start_index:end);
HiokiPfil   = Hioki.P1(start_index:end);

Dynospd_fil = Dyno.spd(start_index:end);

index_pick_UIP = logical((HiokiVfil < 250));%.*(abs(CAN_Vfil - HiokiVfil) > 1).*(abs(CAN_Ifil - HiokiIfil) > 0.1).*(abs(CAN_Pfil - HiokiPfil) > 0.1));
% index_pick_I = abs(CAN_Ifil - HiokiIfil);
% index_pick_P = abs(CAN_Pfil - HiokiPfil);

figmk(.5,.6);
subplot(3,1,1);
yyaxis left;hold on;
plot(DAQT_fil, CAN_Vfil)
plot(DAQT_fil, HiokiVfil,'--');
plot(DAQT_fil(index_pick_UIP), CAN_Vfil(index_pick_UIP),'k.')
grid on;box on; xlabel('DAQ time [s]');ylabel('Voltage [V]')
yyaxis right;plot(DAQT_fil,Dynospd_fil);ylabel('dyno spd [mph]')


subplot(3,1,2);
yyaxis left;hold on;
plot(DAQT_fil, CAN_Ifil)
plot(DAQT_fil, HiokiIfil,'--');
plot(DAQT_fil(index_pick_UIP), CAN_Ifil(index_pick_UIP),'k.')
grid on;box on; xlabel('DAQ time [s]');ylabel('Current [Amps]')
yyaxis right;plot(DAQT_fil,Dynospd_fil);ylabel('dyno spd [mph]')

subplot(3,1,3);
yyaxis left;hold on;
plot(DAQT_fil, CAN_Pfil)
plot(DAQT_fil, HiokiPfil,'--');
plot(DAQT_fil(index_pick_UIP), CAN_Pfil(index_pick_UIP),'k.')
grid on;box on; xlabel('DAQ time [s]');ylabel('Power [W]')
yyaxis right;plot(DAQT_fil,Dynospd_fil);ylabel('dyno spd [mph]')

%%
index_f = Dynospd_fil > 0.01;
figmk(.6,.4);
subplot(1,3,1)
plot(Dynospd_fil(index_f), abs(CAN_Vfil(index_f) - HiokiVfil(index_f)),'k.')
grid on;box on;xlabel('dyno spd [mph]');ylabel('|Ucan - Uhioki|');
subplot(1,3,2)
plot(Dynospd_fil(index_f), abs(CAN_Ifil(index_f) - HiokiIfil(index_f)),'k.')
grid on;box on;xlabel('dyno spd [mph]');ylabel('|Ican - Ihioki|');
subplot(1,3,3)
plot(Dynospd_fil(index_f), abs(CAN_Pfil(index_f) - HiokiPfil(index_f)),'k.')
grid on;box on;xlabel('dyno spd [mph]');ylabel('|Pcan - Phioki|');
% 
% figure;
% yyaxis left;
% plot(DAQT_fil,Dynospd_fil);
% yyaxis right;hold on;
% plot(DAQT_fil,gradient(Dynospd_fil))
% grid on;box on;
% xlabel('DAQ time [s]');ylabel('dyno spd [mph]')

%% check hioki
% hiokipower_cal  = Hioki.P1;
% index_ps        = hiokipower_cal > 0;
% index_ng        = hiokipower_cal < 0;
% hiokipos       = hiokipower_cal;hiokipos(index_ng) = 0;
% hiokineg       = hiokipower_cal;hiokineg(index_ps) = 0;
% 
% start_index = 205;
% 
% Cpos = cumtrapz(DAQtime(start_index:end),hiokipos(start_index:end));
% Cneg = cumtrapz(DAQtime(start_index:end),hiokineg(start_index:end));
% Cint = Cpos + Cneg;
% figure;hold on;
% plot(Hioki.WP1(start_index:end) - Hioki.WP1(start_index));
% plot(Cint/3600,'--');
% 
