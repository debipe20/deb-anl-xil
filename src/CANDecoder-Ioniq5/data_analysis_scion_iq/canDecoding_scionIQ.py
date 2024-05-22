import itertools
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time

def twos_complement(val, nbits):
    """Compute the 2's complement of int value val"""
    #print(val)
    if val < 0:
        val = (1 << nbits) + val
    else:
        if (val & (1 << (nbits - 1))) != 0:
            # If sign bit is set.
            # compute negative value.
            val = val - (1 << nbits)
    return val

class Decoding:

    def __init__(self,can_data, can_length=61):

        # extract message from the bulk message variable    
        def mult_to_single_list(arbID,stacked_msgs):
            stacked_can_msgs_out_tuple = [(idx,val) for idx,val in enumerate(stacked_msgs) if val[:len(arbID)].find(arbID)>-1]
            stacked_can_msgs_out_idx = [i[0] for i in stacked_can_msgs_out_tuple[:]]
            stacked_can_msgs_out = [i[1] for i in stacked_can_msgs_out_tuple[:]]
            return stacked_can_msgs_out_idx, stacked_can_msgs_out

        # assign the raw data to can_data
        self.can_data = can_data
        self.can_length = can_length

        stacked_can_msgs = []
        stacked_phone_msgs = []
        timestamp_idx = []
        timestamp_idx.append(can_length-1)
        phone_idx = []
        phone_idx.append(0)
        keys = list(self.can_data.keys())
        
        for n,k in enumerate(keys):
            print("progress {0:.2f}".format(n/len(keys)))
            can_msg_temp = self.can_data[k]                                             # assign instantaneous batch of can msgs       
            stacked_can_msgs_temp = can_msg_temp.split('999 ')[1:-1]                    # split based on seperater '999 ' exclude first (id etc) and last msg (phone based)
             # stacked_can_msgs.append(stacked_can_msgs_temp)              
             # stacked_can_msgs += stacked_can_msgs_temp
            
            if (len(stacked_can_msgs_temp[0]) == 0):
                # in case 999 appears in randID
                stacked_can_msgs_temp = stacked_can_msgs_temp[1:]
            stacked_can_msgs.append([j for j in stacked_can_msgs_temp]) 
            stacked_phone_msgs.append([can_msg_temp.split('BatteryTemp: ')[1]])         # phone related messages

            # corrected on 2023/10/26
            # timestamp_idx.append(timestamp_idx[-1] + len(stacked_can_msgs_temp)-1)
            timestamp_idx.append(timestamp_idx[-1] + len(stacked_can_msgs_temp))

            phone_idx.append(len(stacked_can_msgs_temp)+phone_idx[-1])                  # save indicies for new upload
        
        self.phone_idx = phone_idx
        stacked_can_msgs = list(itertools.chain.from_iterable(stacked_can_msgs))        # flatten list of lists
        self.stacked_phone_msgs = stacked_phone_msgs
        self.timestamp_idx = timestamp_idx
        self.keys = keys

        # create dataframe with all can messages
        all_data = pd.DataFrame()
        self.stacked_can_msgs = stacked_can_msgs
        all_data['can_msgs'] = stacked_can_msgs
        all_data['arb_id'] = [str("".join(i.split(" ")[:2]))[1:] for i in stacked_can_msgs]
        all_data['timestamps'] = np.nan
        all_data['timestamps'].loc[timestamp_idx[:-1]] = keys
        
        timestamps_datetime = [datetime.strptime(i, '%Y%m%d-%H%M%S%f') for i in keys]
        timestamps_datetime_gap = [(timestamps_datetime[n+1] - timestamps_datetime[n]).total_seconds() * 1000  for n,i in enumerate(timestamps_datetime[:-1])]
        timestamp_interpolated = []
        timestamp_interpolated.append(timestamps_datetime[0])
        timestamp_millis_reference = []
        timestamp_millis_reference.append(0)

        # linearily interpolate between timestamps
        for i,k in enumerate(timestamps_datetime_gap):
            for j in range(can_length): # there is always 61 messages between two uploads
                timestamp_interpolated.append(timestamp_interpolated[-1] + timedelta(milliseconds=k/can_length))
                timestamp_millis_reference.append(timestamp_millis_reference[-1] + k/can_length)

        self.time_gaps = timestamps_datetime_gap
        self.t_inter = timestamp_interpolated
        all_data['time_inter'] = np.nan
        all_data['time_inter'][timestamp_idx[0]:] = timestamp_interpolated
        all_data['time_ref_millis'] = np.nan
        all_data['time_ref_millis'][timestamp_idx[0]:] = timestamp_millis_reference
        all_data['time_gap_millis'] = np.nan
        all_data['time_gap_millis'][timestamp_idx[0]:-1] = np.diff(timestamp_millis_reference)

        # save all data as global class variable
        self.all_data = all_data

        # single out messages
        self.idx_024, self.can_024  = mult_to_single_list('00 24',stacked_can_msgs) # yaw rate / acceleration y /  steering torque
        self.idx_025, self.can_025  = mult_to_single_list('00 25',stacked_can_msgs) # steering angle, rate etc
        self.idx_224, self.can_224  = mult_to_single_list('02 24',stacked_can_msgs) # brake signal and force
        self.idx_245, self.can_245  = mult_to_single_list('02 45',stacked_can_msgs) # acc pedal 
        self.idx_3CE, self.can_3CE  = mult_to_single_list('03 CE',stacked_can_msgs) # remaining range
        self.idx_0B4, self.can_0B4  = mult_to_single_list('00 B4',stacked_can_msgs) # veh speed
        self.idx_800, self.can_800  = mult_to_single_list('08 00',stacked_can_msgs) # turn signal
        self.idx_801, self.can_801  = mult_to_single_list('08 01',stacked_can_msgs) # gyro
        self.idx_802, self.can_802  = mult_to_single_list('08 02',stacked_can_msgs) # estimated angle
        self.idx_74F, self.can_74F = mult_to_single_list('07 4F 06 61 01',stacked_can_msgs)   # SOC of all batteries
        self.idx_7B8, self.can_7B8 = mult_to_single_list('07 B8 06 61 03',stacked_can_msgs)   # individual wheel speed
        self.idx_7C8, self.can_7C8 = mult_to_single_list('07 C8 03 61 64',stacked_can_msgs)   # ambient and ESP32 temperature
        self.idx_7DA_bat1_c, self.can_7DA_bat1_c = mult_to_single_list('07 DA 04 61 8A',stacked_can_msgs)   # battery 1 current   
        self.idx_7DA_bat1_v, self.can_7DA_bat1_v = mult_to_single_list('07 DA 06 61 81',stacked_can_msgs)   # battery 1 voltage   
        self.idx_7DA_bat2_c, self.can_7DA_bat2_c = mult_to_single_list('07 DA 04 61 8B',stacked_can_msgs)   # battery 2 current   
        self.idx_7DA_bat2_v, self.can_7DA_bat2_v = mult_to_single_list('07 DA 06 61 83',stacked_can_msgs)   # battery 2 voltage 
        self.idx_7DA_ac_power, self.can_7DA_ac_power = mult_to_single_list('07 DA 03 61 7D',stacked_can_msgs)   # ac power 
    
    def decAnyUnassigned(self, byteS, byteE, bitS, bitE, res, offset, key_name):
        
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_024]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]

        self.brake_force = [i*res + offset for i in numbOI] 
        self.all_data[key_name] = np.nan   
        self.all_data[key_name].loc[self.idx_024] = self.brake_force
        self.all_data[key_name].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    # yaw rate / steering torque / acceleration y
    def dec024(self):
        # yaw rate
        key_name = "yaw_rate_radps"
        byteS = 1
        byteE = 2
        bitS = 2
        bitE = 11
        # calculated based on data on 2023/10/24 afternoon 
        # --> 0.114861 based on yaw rate estimation from RL * RR wheel speeds
        # --> 0.115154 based on phone yGyro
        res = 0.115
        offset = -16.0*res
        self.decAnyUnassigned(byteS, byteE, bitS, bitE, res, offset, key_name)

        # steering torque
        key_name = "steering_torque_nan"
        byteS = 3
        byteE = 4
        bitS = 2
        bitE = 11
        res = 1
        offset = -16
        self.decAnyUnassigned(byteS, byteE, bitS, bitE, res, offset, key_name)

        # acceleration y
        key_name = "accel_y_nan"
        byteS = 5
        byteE = 6
        bitS = 2
        bitE = 11
        res = 1
        offset = -272
        self.decAnyUnassigned(byteS, byteE, bitS, bitE, res, offset, key_name)

    # steering angle
    def dec025(self):
        byteS = 1
        byteE = 2
        bitS =4
        bitE=-1
        res=1.5
        offset=0

        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_025]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]

        self.steering_angle = [twos_complement(i, 12)*res + offset for i in numbOI]
        self.all_data['steering_angle_deg'] = np.nan   
        self.all_data['steering_angle_deg'].loc[self.idx_025] = self.steering_angle
        self.all_data['steering_angle_deg'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)
        # raw data    
        self.all_data['steering_angle_raw_deg'] = np.nan   
        self.all_data['steering_angle_raw_deg'].loc[self.idx_025] = self.steering_angle

    # Brake force
    def dec224(self):
        byteS = 5
        byteE = 6
        bitS =0
        bitE=-1
        res=8
        offset=0

        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_224]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]

        self.brake_force = [i*res + offset for i in numbOI] 
        self.all_data['brake_force_N'] = np.nan   
        self.all_data['brake_force_N'].loc[self.idx_224] = self.brake_force
        self.all_data['brake_force_N'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    # Pedal position
    def dec245(self):
        byteS = 3
        byteE = 3
        bitS =0
        bitE=-1
        res=0.5
        offset=0

        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_245]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]

        self.pedal_position = [i*res + offset for i in numbOI] 
        self.all_data['pedal_position_perc'] = np.nan   
        self.all_data['pedal_position_perc'].loc[self.idx_245] = self.pedal_position
        self.all_data['pedal_position_perc'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)


    # remaining range
    def dec3CE(self):
        byteS = 5
        byteE = 6
        bitS =4
        bitE=-1
        res=0.1
        offset=0

        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_3CE]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]

        self.remaining_range = [i*res + offset for i in numbOI]         
        self.all_data['remaining_range_km'] = np.nan   
        self.all_data['remaining_range_km'].loc[self.idx_3CE] = self.remaining_range
        self.all_data['remaining_range_km'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)


    # Vehicle Speed
    def dec0B4(self):
        byteS = 6
        byteE = 7
        bitS =0
        bitE=-1
        res=0.01
        offset=0

        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_0B4]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]

        self.vehicle_speed = [i*res + offset for i in numbOI] 
        self.all_data['vehicle_speed_kmph'] = np.nan   
        self.all_data['vehicle_speed_kmph'].loc[self.idx_0B4] = self.vehicle_speed
        self.all_data['vehicle_speed_kmph'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    # Turn signal
    def dec800(self):
        byteS = 1
        byteE = 2     
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_800]
        turn_signal = []
        for i in bytesOI_hex:
            if i == 256:
                # left turn, "0100"
                turn_signal.append(1)
            elif i == 1:
                # right turn, "0001"
                turn_signal.append(-1)
            elif i == 0:
                # no turning
                turn_signal.append(0)
            else:
                # wrong signal
                turn_signal.append(-2)

        self.all_data['turn_signal'] = np.nan   
        self.all_data['turn_signal'].loc[self.idx_800] = turn_signal
        self.all_data['turn_signal'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    # # Accelerations
    # def dec800(self):
    #     # x-accelerations
    #     byteS = 1
    #     byteE = 2
    #     bitS =0
    #     bitE=-1
    #     res=1
    #     offset=0        
    #     bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_800]
    #     bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

    #     if bitE == -1:
    #         numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
    #     else:
    #         numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
    #     self.acc_x = [i*res + offset for i in numbOI]         
    #     self.all_data['acc_x'] = np.nan   
    #     self.all_data['acc_x'].loc[self.idx_800] = self.acc_x
    #     self.all_data['acc_x'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    #     # y-accelerations
    #     byteS = 3
    #     byteE = 4
    #     bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2][::-1]),16) for i in self.can_800]
    #     bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

    #     if bitE == -1:
    #         numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
    #     else:
    #         numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
    #     self.acc_y = [i*res + offset for i in numbOI]   
    #     self.all_data['acc_y'] = np.nan   
    #     self.all_data['acc_y'].loc[self.idx_800] = self.acc_y
    #     self.all_data['acc_y'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    #     # z-accelerations
    #     byteS = 5
    #     byteE = 6
    #     bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2][::-1]),16) for i in self.can_800]
    #     bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

    #     if bitE == -1:
    #         numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
    #     else:
    #         numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
    #     self.acc_z = [i*res + offset for i in numbOI] 
    #     self.all_data['acc_z'] = np.nan   
    #     self.all_data['acc_z'].loc[self.idx_800] = self.acc_y
    #     self.all_data['acc_z'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    def dec7DA_bat1_c(self):
        byteS = 4
        byteE = 5
        bitS =0
        bitE=-1
        res=0.01
        offset=-327.68       
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_7DA_bat1_c]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.bat1_c = [i*res + offset for i in numbOI] 
        self.all_data['bat1_c_A'] = np.nan   
        self.all_data['bat1_c_A'].loc[self.idx_7DA_bat1_c] = self.bat1_c
        self.all_data['bat1_c_A'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)


    def dec7DA_bat2_c(self):
        byteS = 4
        byteE = 5
        bitS =0
        bitE=-1
        res=0.01
        offset=-327.68       
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_7DA_bat2_c]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.bat2_c = [i*res + offset for i in numbOI] 
        self.all_data['bat2_c_A'] = np.nan   
        self.all_data['bat2_c_A'].loc[self.idx_7DA_bat2_c] = self.bat2_c
        self.all_data['bat2_c_A'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    def dec7DA_bat1_v(self):
        byteS = 6
        byteE = 7
        bitS =0
        bitE=-1
        res=0.1
        offset=0       
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_7DA_bat1_v]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.bat1_v = [i*res + offset for i in numbOI] 
        self.all_data['bat1_v_V'] = np.nan   
        self.all_data['bat1_v_V'].loc[self.idx_7DA_bat1_v] = self.bat1_v
        self.all_data['bat1_v_V'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    def dec7DA_bat2_v(self):
        byteS = 6
        byteE = 7
        bitS =0
        bitE=-1
        res=0.1
        offset=0       
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_7DA_bat2_v]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.bat2_v = [i*res + offset for i in numbOI]         
        self.all_data['bat2_v_V'] = np.nan   
        self.all_data['bat2_v_V'].loc[self.idx_7DA_bat2_v] = self.bat2_v
        self.all_data['bat2_v_V'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)


    def getBatPower(self):
        self.all_data['bat_power_W'] = np.nan   
        self.all_data['bat_power_W'] = self.all_data['bat1_v_V']*self.all_data['bat1_c_A'] + self.all_data['bat2_v_V']*self.all_data['bat2_c_A']
        self.all_data['energy_cons'] = np.nan
        self.all_data['energy_cons'] = np.cumsum(self.all_data['bat_power_W']*self.all_data['time_gap_millis'])

        #self.all_data['bat_power'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    # AC power 
    def dec7DA_ac_power(self):
        byteS = 4
        byteE = 4
        bitS =0
        bitE=-1
        res=50
        offset=0       
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_7DA_ac_power]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.ac_power_w = [i*res + offset for i in numbOI]         
        self.all_data['ac_power_W'] = np.nan   
        self.all_data['ac_power_W'].loc[self.idx_7DA_ac_power] = self.ac_power_w
        self.all_data['ac_power_W'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)


    # SOC
    def dec74F(self):
        byteS = 7
        byteE = 7
        bitS =0
        bitE=-1
        res=0.39216
        offset=0       
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_74F]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.soc = [i*res + offset for i in numbOI]         
        self.all_data['soc_perc'] = np.nan   
        self.all_data['soc_perc'].loc[self.idx_74F] = self.soc
        self.all_data['soc_perc'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    # all individual wheel speeds
    def dec7B8(self):
        # ############ fitted with data on 2023/10/23 afternoon
        res=1.2952811967
        offset=0   
        # RF (right front) wheel at byte4 (not include arbID)    
        key_name = 'wheel_speed_RF_kmph'
        byteS = 4
        byteE = 4
        self.dec7B8_individual(byteS, byteE, key_name, res, offset)
        # LF (left front) wheel at byte5 (not include arbID)    
        key_name = 'wheel_speed_LF_kmph'
        byteS = 5
        byteE = 5
        self.dec7B8_individual(byteS, byteE, key_name, res, offset)
        # RR (right rear) wheel at byte4 (not include arbID)    
        key_name = 'wheel_speed_RR_kmph'
        byteS = 6
        byteE = 6
        self.dec7B8_individual(byteS, byteE, key_name, res, offset)
        # LR (left rear) wheel at byte4 (not include arbID)    
        key_name = 'wheel_speed_LR_kmph'
        byteS = 7
        byteE = 7
        self.dec7B8_individual(byteS, byteE, key_name, res, offset)

    
    def dec7B8_individual(self, byteS, byteE, key_name, res, offset):

        bitS =0
        bitE=-1
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_7B8]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.wheel_speed = [i*res + offset for i in numbOI]         
        self.all_data[key_name] = np.nan   
        self.all_data[key_name].loc[self.idx_7B8] = self.wheel_speed
        self.all_data[key_name].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    # ambient / esp32 temperature
    def dec7C8(self):
        # Ambient Temperature
        byteS = 4
        byteE = 4
        bitS =0
        bitE=-1
        res=0.5
        offset=-40       
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_7C8]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.ambient_temperature = [i*res + offset for i in numbOI]         
        self.all_data['ambient_temperature_degC'] = np.nan   
        self.all_data['ambient_temperature_degC'].loc[self.idx_7C8] = self.ambient_temperature
        self.all_data['ambient_temperature_degC'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

        # ESP32 Temperature
        byteS = 8
        byteE = 8
        bitS =0
        bitE=-1
        res=1
        offset=0       
        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_7C8]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]
        self.esp_temperature = [i*res + offset for i in numbOI]         
        self.all_data['esp32_temperature_degC'] = np.nan   
        self.all_data['esp32_temperature_degC'].loc[self.idx_7C8] = self.esp_temperature
        self.all_data['esp32_temperature_degC'].interpolate(method='pad',axis=0,limit_direction='forward',inplace=True)

    # get all phone data
    def get_phone_data(self):
        phone_data = pd.DataFrame(columns=["timestamps", "phn_batt_temp_degC",
                                           "phn_batt_level_perc", "phn_xAcc_mps2",
                                           "phn_yAcc_mps2", "phn_zAcc_mps2",
                                           "phn_xGyro_radps", "phn_yGyro_radps",
                                           "phn_zGyro_radps", "phn_GPS_lat_deg", 
                                           "phn_GPS_lng_deg", "phn_GPS_speed_mps",
                                           "phn_GPS_bearing_deg", "phn_GPS_altitude_m",
                                           "phn_GPS_hrztl_accuracy_m", "phn_GPS_vrtcl_accuracy_m",
                                           "phn_GPS_speed_accuracy_mps", "phn_GPS_bearing_accuracy_deg"])
        phone_data_list = []
        for key, stacked_phone_msg in zip(self.keys, self.stacked_phone_msgs):
            phone_data_row = []
            phone_data_row.append(key)
            # split each phone message by ": "
            # print(stacked_phone_msg)
            temp1 = stacked_phone_msg[0].split(": ")
            for data in temp1:
                # split splitted phone message by ", "
                temp2 = data.split(", ")
                phone_data_row.append(float(temp2[0]))

            phone_data_list.append(phone_data_row)

        phone_data = phone_data.append(pd.DataFrame(phone_data_list, columns=phone_data.columns), ignore_index=True)
        self.phone_data = phone_data

    # get combined can data and phone data
    def get_combined_data(self):

        if not hasattr(self, 'phone_data') :
            self.get_phone_data()

        phone_data = self.phone_data
        expanded_phone_data = phone_data.loc[phone_data.index.repeat(self.can_length)].reset_index(drop=True)
        combined_data = pd.concat([self.all_data, expanded_phone_data], axis=1)
        combined_data = combined_data.reset_index(drop=True)

        self.combined_data = combined_data



"""     # Gyro
    def dec800(self):
        byteS = 6
        byteE = 7
        bitS =0
        bitE=-1
        res=0.01
        offset=0

        bytesOI_hex = [int("".join(i.split(" ")[byteS+1:byteE+2]),16) for i in self.can_0B4]
        bytesOI_bin = [bin(i)[2:].zfill(16) for i in bytesOI_hex]

        if bitE == -1:
            numbOI = [int(i[bitS:],2) for i in bytesOI_bin]
        else:
            numbOI = [int(i[bitS:bitE],2) for i in bytesOI_bin]

        self.gyr = [i*res + offset for i in numbOI]    """              