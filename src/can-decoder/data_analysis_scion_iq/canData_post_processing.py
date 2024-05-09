import numpy as np
import pandas as pd
import canDecoding_scionIQ as CAN
from openpyxl import load_workbook
from scipy.interpolate import interp1d

from bokeh.plotting import figure, show, output_file
from bokeh.models.tools import HoverTool

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def dataProcessing(idxStart,idxEnd,df_in):
    """
    Notes: get section of the input data, and add more outputs
    Inputs:
        idxStart, idxEnd: int, start and end index
        df_in: DataFrame
    
    Outputs:
        df_out: DataFrame
    """
    df_out = df_in.iloc[idxStart:idxEnd,:]
    print("selected data length:")
    print(len(df_out))
    df_out['time_s'] = (df_out['time_ref_millis'] - df_out['time_ref_millis'].iloc[0])/1000
    energy = np.cumsum(df_out['bat_power_W']*df_out['time_gap_millis']*0.001/3600)
    df_out['energy'] = energy

    dt = df_out['time_gap_millis']/1000
    v = df_in['vehicle_speed_kmph']/3.6
    distance = np.cumsum(v*dt)

    df_out['distance'] = distance

    distance_miles = df_out['distance']/1.6*1/1000 # to miles
    df_out['energy_Whpm'] = energy/distance_miles

    return df_out

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def data_fine_processing(raw_test_datas):
    """
    Notes: fine section of the raw test data, cut the unnecessary zero speed profile 
    to make the energy consumption and mean speed calculation more accurate
    Inputs:
        raw_test_datas: list of dataframes
    Outputs:
        fine_test_datas: list of dataframes
    """
    fine_test_datas = []
    for raw_data in raw_test_datas:
        idx_test = np.where( raw_data['vehicle_speed_kmph'] > 0 )[0]

        idx0 = max (idx_test[0] - 5, 0)
        idx1 = min (idx_test[-1] + 5, len(raw_data))

        fine_data = raw_data[idx0:idx1]
        fine_data['time_s'] = fine_data['time_s'] - fine_data['time_s'].iloc[0]
        
        fine_test_datas.append(fine_data)

    return fine_test_datas

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def data_fine_processing_by_duration(raw_test_datas, durations=200, key_x='time_s', key_y='vehicle_speed_kmph'):
    """
    Notes: fine section of the raw test data, cut the unnecessary zero speed profile 
    to make the energy consumption and mean speed calculation more accurate
    Inputs:
        raw_test_datas: list of dataframes
        durations: test duration in seconds
    Outputs:
        fine_test_datas: list of dataframes
    """
    
    if type(durations) is not list:
        durations = [durations]*len(raw_test_datas)
    
    print(durations)
    
    fine_test_datas = []
    for raw_data, duration in zip(raw_test_datas, durations):
        print(duration)
        # start from speed larger than 0
        idx_test = np.where( raw_data[key_y] > 0 )[0]
        idx0 = max (idx_test[0] - 1, 0)

        fine_data_temp = raw_data[idx0:]
        fine_data_temp[key_x] = fine_data_temp[key_x] - fine_data_temp[key_x].iloc[0]

        # the last one smaller than duration
        idx1 = np.where( fine_data_temp[key_x] < duration )[0][-1]

        fine_data = fine_data_temp[:idx1]      
        fine_test_datas.append(fine_data)

    return fine_test_datas

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def get_closest_index(all_data, target_timestamp_str, target_timestamp_format='%Y%m%d-%H%M%S%f'):
    """
    Notes: get the index of the closest time stamp
    """
    # Target time as a datetime object
    target_time = pd.to_datetime(target_timestamp_str, format=target_timestamp_format)

    # Compute the absolute time difference between each time in 'time_inter_formatted' and the target time
    time_difference = abs( pd.to_datetime(all_data['time_inter'])- target_time )

    # Find the index with the smallest time difference
    closest_index = time_difference.idxmin()

    return closest_index


#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def get_all_data(can_data, can_length=61):
    """
    Note: get decoded can data
    """
    data = CAN.Decoding(can_data, can_length=can_length)

    data.dec024()
    data.dec025()
    data.dec224()
    data.dec245()
    data.dec0B4()
    data.dec3CE()
    data.dec800()
    data.dec74F()
    data.dec7B8()
    data.dec7C8()
    data.dec7DA_bat1_c()
    data.dec7DA_bat2_c()
    data.dec7DA_bat1_v()
    data.dec7DA_bat2_v()
    data.dec7DA_ac_power()
    data.getBatPower()
    data.get_phone_data()
    data.get_combined_data()
    
    all_data = data.all_data

    print("Done!")

    return all_data, data.phone_data, data.combined_data

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def plottingFct(title, x_label, y_label, set_height=600, set_width=1200, 
                y_range_min=None, y_range_max=None, axis_label_font_size="26pt", tooltips=None):

    plot = figure(title=title, height=int(set_height), width=int(set_width)) 
    # plot = figure(title=title, height=set_height, width=set_width,y_range=[y_range_min, y_range_max],tooltips=tooltips) 
    plot.title.text_font_size = axis_label_font_size
    plot.xaxis.axis_label_text_font_size = axis_label_font_size
    plot.xaxis.major_label_text_font_size = axis_label_font_size
    plot.yaxis.axis_label_text_font_size = axis_label_font_size
    plot.yaxis.major_label_text_font_size = axis_label_font_size
    plot.xaxis.axis_label = x_label
    plot.yaxis.axis_label = y_label

    if y_range_min is not None:
        plot.y_range.start = y_range_min

    if y_range_max is not None:
        plot.y_range.end = y_range_max

    if tooltips is not None:
        hover = HoverTool(tooltips=tooltips)
        plot.add_tools(hover)

    return plot

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def plot_datas(plot, x_key, y_key, legend_labels, widths, datas, colors, line_dashs, sample_rate=1, alpha=1):
    
    # convert inputs to list if they're not
    datas = convert_to_list(datas)

    legend_labels = convert_to_list(legend_labels, len(datas))
    widths = convert_to_list(widths, len(datas))
    colors = convert_to_list(colors, len(datas))
    line_dashs = convert_to_list(line_dashs, len(datas))

    for i, data in enumerate(datas):
        # ith scenario data
        data_desample = data.iloc[::sample_rate, :]
        # print(len(data_desample[x_key]), len(data_desample[y_key]))
        # print(data_desample[x_key])
        # print(data_desample[y_key])
        plot.line(x=x_key, y=y_key, legend_label=legend_labels[i], width=widths[i], 
                source=data_desample, color=colors[i], alpha=alpha, line_dash=line_dashs[i]) 
    
    return plot

def convert_to_list(feature, list_length=1):
    # convert legend_labels, widths, colors, line_dashs to list if they're not
    if type(feature) is not list:
        return [feature]*list_length

    return feature
#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def save_values(data_names, datas, file_name_xlsx, sheet_name):
    # Create an empty DataFrame to store the results
    results = pd.DataFrame(columns=['Scenario', 'Travel Time (sec)', 'Final Speed [m/s]', 'Distance (mile)', 'Energy (Wh)', 'Energy (Wh/mile)', 'Vehicle Speed Mean (m/s)'])

    for data_name, data in zip(data_names, datas):
        travel_time_val = data.time_s.iloc[-1] - data.time_s.iloc[0]
        final_speed_val = data['vehicle_speed_kmph'].iloc[-1] / 3.6
        distance_val = data.distance.iloc[-1] / 1.6 * 1 / 1000
        energy_val = data.energy.iloc[-1]
        energy_Whpm_val = data.energy_Whpm.iloc[-1]
        vehicle_speed_mean_val = data['vehicle_speed_kmph'].mean() / 3.6

        print(f"Scenario: {data_name}")
        print(f"Travel Time: {travel_time_val}")
        print(f"Distance: {distance_val:.2f} mi")
        print(f"Energy: {energy_val:.2f} Wh")
        print(f"Energy_Whpm: {energy_Whpm_val:.2f} Wh per mile")
        print(f"Vehicle Speed Mean: {vehicle_speed_mean_val:.2f} m/s")
        print("-" * 50)  # Separator line
        print()  # Extra space

        # Append the results to the DataFrame
        results.loc[len(results)] = [data_name, travel_time_val, final_speed_val, distance_val, energy_val, energy_Whpm_val, vehicle_speed_mean_val]
    
    # load excel file if exist
    try:
        book = load_workbook(file_name_xlsx)
    except:
        print("Excel data sheet not exist, and create a new one")

    # with pd.ExcelWriter(file_name_xlsx, engine='xlsxwriter') as writer:
    with pd.ExcelWriter(file_name_xlsx, engine='openpyxl') as writer:
        try:
            writer.book = book
        except:
            print("Excel data sheet not exist")

        results.to_excel(writer, sheet_name=sheet_name, index=False)

    # # Save the DataFrame to a CSV file
    # file_name_csv = file_name + '.csv'
    # results.to_csv(file_name_csv, index=False)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def get_diff(part_datas, y_key, dx_interp=0.02, x_key="time_s"):

    x_val0 = part_datas[0][x_key].iloc[:]
    x_val1 = part_datas[1][x_key].iloc[:]

    x_interp = np.arange(0, min(max(x_val0), max(x_val1)), dx_interp)

    y_val0 = get_interp(part_datas[0], x_interp, y_key, x_key)
    y_val1 = get_interp(part_datas[1], x_interp, y_key, x_key)

    diff_y_val = y_val1 - y_val0

    return x_interp, diff_y_val

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################

def get_interp(data, x_interp, y_key, x_key="time_s", fill_value='extrapolate'):
    
    x_val = data[x_key].iloc[:]
    y_val = data[y_key].iloc[:]

    interp_func = interp1d(x_val, y_val, bounds_error=False, fill_value=fill_value)
    y_interp = interp_func(x_interp)

    return y_interp

#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################

def get_timestr(time_raws, delta_hour=0):
    """
    Notes: get time strings
    Example: 1:12:13 --> '011213'
    """
    time_strs = []
    for time in time_raws:
        temp = str(time).split(":")
        temp[0] = str( int(temp[0]) + delta_hour )

        time_strs.append( "".join(temp) )

    return time_strs


#-----------------------------------------------------------------------------------------------------------------------------------------------------
###########################################################################################################################################
def collect_dsapce_data(data_mat):
    """
    Note: function to extract dspace data from mat file
    """
    data_raw = data_mat['rec']

    # scion_time = data_raw['X'][1]['Data']
    dspace_time = data_raw['X'][2]['Data']

    dspace_time = dspace_time - dspace_time[0]

    # scion_APP = data_raw['Y'][1]['Data']
    dspace_acc_request = data_raw['Y'][2]['Data']
    dspace_speed_request = data_raw['Y'][3]['Data']

    FTPS2_TO_MPS2 = 0.3048
    MPH_TO_MPS = 0.44704
    
    dspace_acc_response = data_raw['Y'][4]['Data']*FTPS2_TO_MPS2
    dspace_speed_response = data_raw['Y'][5]['Data']*MPH_TO_MPS

    return dspace_time, dspace_acc_request, dspace_speed_request, dspace_acc_response, dspace_speed_response