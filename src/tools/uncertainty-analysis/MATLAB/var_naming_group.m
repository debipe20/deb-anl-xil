
Dyno.spd        = Data.txt.Dyno_Spd_mph_;
Dyno.loadN      = Data.txt.Dyno_LoadCell_N_;
Dyno.force      = Data.txt.Dyno_TractiveForce_N_;

DAQtime                                             =    Data.txt.DAQ_Time_s_;

% HVbatt Voltage
HVbatt.HVBatt_volt_total_BECM__V                    =  Data.txt.HVBatt_volt_total_BECM__V;
HVbatt.HVBatt_voltage_HEV__V                        =  Data.txt.HVBatt_voltage_HEV__V;
HVbatt.HVBatt_voltage_CAN5__V                       =  Data.txt.HVBatt_voltage_CAN5__V;
HVbatt.Batt12V_volt_BECM__V                         =  Data.txt.Batt12V_volt_BECM__V;
HVbatt.Batt12V_volt_BECM__V                         =  Data.txt.Batt12V_volt_BECM__V;
HVbatt.Batt12V_Volt_ABS__V                          =  Data.txt.Batt12V_Volt_ABS__V;
HVbatt.Batt_12V_volt_EPS__V                         =  Data.txt.Batt_12V_volt_EPS__V;
HVbatt.DCDC_req_volt_HEV__V                         =  Data.txt.DCDC_req_volt_HEV__V;
HVbatt.motor_inverter_input_voltage_CAN5__V         =  Data.txt.motor_inverter_input_voltage_CAN5__V;
HVbatt.Motor_inverter_input_voltage_HEV__V          =  Data.txt.Motor_inverter_input_voltage_HEV__V;
HVbatt.compressor_input_volt_HVAC__V                =  Data.txt.compressor_input_volt_HVAC__V;
HVbatt.inverter_input_high_volt_MCM__V              =  Data.txt.inverter_input_high_volt_MCM__V;

HVbatt.HVBatt_SOC_HEV__per                          =  Data.txt.HVBatt_SOC_HEV__per;
HVbatt.Batt_SOC_CAN2__per                           =  Data.txt.Batt_SOC_CAN2__per;

% HVbatt Current
HVbatt.HVBatt_current_BECM__A                       =  Data.txt.HVBatt_current_BECM__A;
HVbatt.HVBatt_current_HEV__A                        =  Data.txt.HVBatt_current_HEV__A;
HVbatt.HVBatt_current_wide_CAN5__A                  =  Data.txt.HVBatt_current_wide_CAN5__A;
HVbatt.HVBatt_current2_CAN5__A                      =  Data.txt.HVBatt_current2_CAN5__A;
HVbatt.AC_Comp_Current_CALC__A                      =  Data.txt.AC_Comp_Current_CALC__A;
HVbatt.PTC_Current_CALC__A                          =  Data.txt.PTC_Current_CALC__A;
HVbatt.AC_Comp_Shielding_Current_CALC__A            =  Data.txt.AC_Comp_Shielding_Current_CALC__A;
HVbatt.PTC_Shielding_Current_CALC__A                =  Data.txt.PTC_Shielding_Current_CALC__A;
HVbatt.steering_motor_current_CAN4__A               =  Data.txt.steering_motor_current_CAN4__A;
HVbatt.steering_motor_current_EPS__A                =  Data.txt.steering_motor_current_EPS__A;
HVbatt.compressor_input_current_HVAC__A             =  Data.txt.compressor_input_current_HVAC__A;
HVbatt.PTC_current_consumption_HVAC__A              =  Data.txt.PTC_current_consumption_HVAC__A;

% HVbatt Power
HVbatt.AC_Comp_IH_CALC__Ah                          =  Data.txt.AC_Comp_IH_CALC__Ah;
HVbatt.AC_Comp_WP_CALC__Wh                          =  Data.txt.AC_Comp_WP_CALC__Wh;
HVbatt.AC_Comp_Power_CALC__W                        =  Data.txt.AC_Comp_Power_CALC__W;
HVbatt.PTC_IH_CALC__Ah                              =  Data.txt.PTC_IH_CALC__Ah;
HVbatt.PTC_Power_CALC__W                            =  Data.txt.PTC_Power_CALC__W;
HVbatt.PTC_WP_CALC__Wh                              =  Data.txt.PTC_WP_CALC__Wh;
% HVbatt.here         =  Data.txt.here;




Hioki.Time0                                          = Data.txt.Hioki_Time_H0_s_;
Hioki.Time1                                          = Data.txt.Hioki_Time_H1_s_;

% Hioki Voltage
Hioki.PDM_Volt_Hioki_U1__V                          = Data.txt.PDM_Volt_Hioki_U1__V;
Hioki.x12V_Batt_Volt_Hioki_U4__V                    = Data.txt.x12V_Batt_Volt_Hioki_U4__V;
% Hioki Current
Hioki.PDM_Curr_In_Hioki_I1__A           = Data.txt.PDM_Curr_In_Hioki_I1__A;
Hioki.DCDC_Out_Curr_Hioki_I2__A         = Data.txt.DCDC_Out_Curr_Hioki_I2__A;
Hioki.x12VBatt_Curr_Hioki_I4__A         = Data.txt.x12VBatt_Curr_Hioki_I4__A;
Hioki.AC_Comp_PosLeg_Curr_Hioki_I5__A   = Data.txt.AC_Comp_PosLeg_Curr_Hioki_I5__A;
Hioki.AC_Comp_NegLeg_Curr_Hioki_I6__A   = Data.txt.AC_Comp_NegLeg_Curr_Hioki_I6__A;
Hioki.PTC_PosLeg_Curr_Hioki_I7__A       = Data.txt.PTC_PosLeg_Curr_Hioki_I7__A;
Hioki.PTC_NegLeg_Curr_Hioki_I8__A       = Data.txt.PTC_NegLeg_Curr_Hioki_I8__A;
% Hioki Power
Hioki.PDM_Power_Hioki_P1__kW            = Data.txt.PDM_Power_Hioki_P1__kW;
Hioki.DCDC_Out_Power_Hioki_P2__W        = Data.txt.DCDC_Out_Power_Hioki_P2__W;
Hioki.x12VBatt_Power_Hioki_P4__W        = Data.txt.x12VBatt_Power_Hioki_P4__W;
Hioki.AC_Comp_PosLeg_Power_Hioki_P5__W  = Data.txt.AC_Comp_PosLeg_Power_Hioki_P5__W;
Hioki.AC_Comp_NegLeg_Power_Hioki_P6__W  = Data.txt.AC_Comp_NegLeg_Power_Hioki_P6__W;
Hioki.PTC_PosLeg_Power_Hioki_P7__W      = Data.txt.PTC_PosLeg_Power_Hioki_P7__W;
Hioki.PTC_NegLeg_Power_Hioki_P8__W      = Data.txt.PTC_NegLeg_Power_Hioki_P8__W;
% Hioki.Here  = Data.txt.Here;




Hioki.U1    = Data.txt.U1;
Hioki.I1    = Data.txt.I1;
Hioki.P1    = Data.txt.P1;
Hioki.IH1   = Data.txt.IH1;
Hioki.PWP1  = Data.txt.PWP1;
Hioki.MWP1  = Data.txt.MWP1;
Hioki.WP1   = Data.txt.WP1;

Hioki.U2    = Data.txt.U2;
Hioki.I2    = Data.txt.I2;
Hioki.P2    = Data.txt.P2;
Hioki.IH2   = Data.txt.IH2;
Hioki.PWP2  = Data.txt.PWP2;
Hioki.MWP2  = Data.txt.MWP2;
Hioki.WP2   = Data.txt.WP2;

Hioki.U3    = Data.txt.U3;
Hioki.I3    = Data.txt.I3;
Hioki.P3    = Data.txt.P3;
Hioki.IH3   = Data.txt.IH3;
Hioki.PWP3  = Data.txt.PWP3;
Hioki.MWP3  = Data.txt.MWP3;
Hioki.WP3   = Data.txt.WP3;

Hioki.U4    = Data.txt.U4;
Hioki.I4    = Data.txt.I4;
Hioki.P4    = Data.txt.P4;
Hioki.IH4   = Data.txt.IH4;
Hioki.PWP4  = Data.txt.PWP4;
Hioki.MWP4  = Data.txt.MWP4;
Hioki.WP4   = Data.txt.WP4;

Hioki.U5    = Data.txt.U5;
Hioki.I5    = Data.txt.I5;
Hioki.P5    = Data.txt.P5;
Hioki.IH5   = Data.txt.IH5;
Hioki.PWP5  = Data.txt.PWP5;
Hioki.MWP5  = Data.txt.MWP5;
Hioki.WP5   = Data.txt.WP5;

Hioki.U6    = Data.txt.U6;
Hioki.I6    = Data.txt.I6;
Hioki.P6    = Data.txt.P6;
Hioki.IH6   = Data.txt.IH6;
Hioki.PWP6  = Data.txt.PWP6;
Hioki.MWP6  = Data.txt.MWP6;
Hioki.WP6   = Data.txt.WP6;

Hioki.U7    = Data.txt.U7;
Hioki.I7    = Data.txt.I7;
Hioki.P7    = Data.txt.P7;
Hioki.IH7   = Data.txt.IH7;
Hioki.PWP7  = Data.txt.PWP7;
Hioki.MWP7  = Data.txt.MWP7;
Hioki.WP7   = Data.txt.WP7;

Hioki.U8    = Data.txt.U8;
Hioki.I8    = Data.txt.I8;
Hioki.P8    = Data.txt.P8;
Hioki.IH8   = Data.txt.IH8;
Hioki.PWP8  = Data.txt.PWP8;
Hioki.MWP8  = Data.txt.MWP8;
Hioki.WP8   = Data.txt.WP8;

