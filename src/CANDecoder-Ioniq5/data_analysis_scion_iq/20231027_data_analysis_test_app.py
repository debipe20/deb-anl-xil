#pip install -r requirements.txt
# .venv\Scripts\activate

#%% import libarries
# %load_ext autoreload
# %autoreload 2

import os
import mat73
from PIL import Image

import itertools
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import canDecoding_scionIQ as CAN
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

from bokeh.palettes import Category10
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import row, gridplot, layout, column
from bokeh.io import push_notebook, show, output_notebook
from bokeh.models import Tabs, BoxZoomTool, PanTool, ResetTool, BoxAnnotation, Toggle, ColorPicker, ColumnDataSource
from bokeh.palettes import inferno, Blues256, Reds256, Greens256, Purples256, Oranges256, Magma256

from canData_post_processing import dataProcessing, get_all_data, plottingFct, plot_datas, save_values, get_diff, get_interp, collect_dsapce_data

# Customize the tooltips with additional information from the dataframe
# assign customized bokeh design features
tooltips = [("index", "$index"), ("(x,y)", "($x, $y)")]
scale = 1.5

#%% CAN data path
#--------------------------------------------------------------------------------------------------------------------------
data_path = os.getcwd() + '/data/'
# path = "U:/00_Argonne/00_Projects/02_AIBasedMobility/02_Codes/Python/data_analysis_scion_iq/data/"
# files = ["20231026_ScioniQ_scion0133DAQ_Data.p"]
files = ["20231030_scion0676_Data.p"]


# %% data definition
#--------------------------------------------------------------------------------------------------------------------------
# scenario settings, used in section plot data
legend_labels = ["On road test"]
widths = [2]*6
line_dashs = ['solid']*6

# plot variables setting, used in section plot data
titles = ["Speed Profiles", "Power Profiles", "Energy Profiles", "Distance Profiles",
          "Brake Force", "Steering", "Acc Pedal", "Remaining Range",
          "Bat1 Current", "Bat2 Current", "Bat1 Voltage", "Bat2 Voltage", "Turn Signal"]
x_labels = ["Time [s]"]*13
y_labels = ["Speed [km/h]", "Power [W]", "Energy [Wh]", "Distance [meter]",
            "Brake Force [N]", "Steering Angle [deg]", "Acc Pedal [%]", 'Range [km]',
            "Current [A]", "Current [A]", "Voltage [V]", "Voltage [V]", "Turn Signal [1:left, -1:right]"]
x_keys = ["time_s"]*13
y_keys = ['vehicle_speed_kmph', 'bat_power_W', 'energy', 'distance',
          'brake_force_N', 'steering_angle_deg', 'pedal_position_perc', 'remaining_range_km',
          'bat1_c_A', 'bat2_c_A', 'bat1_v_V', 'bat2_v_V', 'turn_signal']

# other plot settings
# colors = Category10[6]
colors = ['blue']*2
alpha = 1


# %% Decode raw CAN data for each scenario
#--------------------------------------------------------------------------------------------------------------------------
scenario_datas = []
file_old = ""
for i, file in enumerate(files):

    if file != file_old:
        can_data = pd.read_pickle(data_path+file)
        # all_data, phone_data, combined_data = get_all_data(can_data)

        # for data collected from 2023/10/26
        all_data, phone_data, combined_data = get_all_data(can_data, can_length=62)
    file_old = file

    # scenario_data = dataProcessing(idx0s[i]+shifts[i], idx1s[i], combined_data)
    scenario_data = dataProcessing(61, len(all_data), combined_data)
    # scenario_data = dataProcessing(47000, 202000, combined_data)
    # scenario_data = dataProcessing(409500, 584300, combined_data)
    scenario_datas.append(scenario_data)
    print("Data collection Done!")

#%%
print(can_data[list(can_data.keys())[0]])
print(can_data[list(can_data.keys())[1]])

#%%
test_pickle = pd.read_pickle(data_path+file)
keys_list = list(test_pickle.keys())
print(len(keys_list))
print(keys_list[-12000])
new_test_pickle = test_pickle['20231030-062950778']
print(len(new_test_pickle))

#%%
print(np.shape(scenario_datas[0]))
test_scenario = scenario_datas[0][['can_msgs', 'arb_id', 'timestamps']][-96408:-56856]
test_scenario.to_csv('thisisatest.csv', index=False)
print(np.shape(test_scenario))

#%%
print(scenario_data.columns)

# %% plot for all scenarios
#--------------------------------------------------------------------------------------------------------------------------
plots = []
for j in range(11, 13):
# for j in range(1):
    # jth plot
    title, x_label, y_label, x_key, y_key = titles[j], x_labels[j], y_labels[j], x_keys[j], y_keys[j]

    plot = plottingFct(title=title, x_label=x_label, y_label=y_label, tooltips=tooltips)
    plot = plot_datas(plot, x_key, y_key, legend_labels, widths, scenario_datas, colors, line_dashs, sample_rate=10)

    plot.legend.location = "bottom_center"
    plots.append(plot)
show(column(*plots))

# %% plot for all scenarios
plots = []
for j in np.arange(6, len(titles)):
# for j in range(1):
    # jth plot
    title, x_label, y_label, x_key, y_key = titles[j], x_labels[j], y_labels[j], x_keys[j], y_keys[j]

    plot = plottingFct(title=title, x_label=x_label, y_label=y_label, tooltips=tooltips)
    plot = plot_datas(plot, x_key, y_key, legend_labels, widths, scenario_datas, colors, line_dashs, sample_rate=10)

    plot.legend.location = "bottom_center"
    plots.append(plot)
show(column(*plots))

#%%