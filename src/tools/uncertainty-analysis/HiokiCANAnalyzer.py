"""
**********************************************************************************

HiokiCANAnalyzer.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
The `HiokiCANAnalyzer` class is responsible for generating and embedding visualizations for uncertainty and energy analysis into an Excel workbook. It integrates seamlessly with the summary data from MCT drive cycles and provides functionality to:


Methods:
--------

"""

import os
import platform
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
from openpyxl.drawing.image import Image
from nptdms import TdmsFile
from scipy.integrate import cumulative_trapezoid
from scipy.stats import linregress


class HiokiCANAnalyzer:
    def __init__(self, config: dict, test_id_list: list, output_file_path: str, plot_directory: str, sheet_name: str):
        """
        Initialize the HiokiCANAnalyzer class.

        Parameters:
        hioki_data (dict): Dictionary containing Hioki data with keys like 'voltage', 'current', 'power', etc.
        can_data (dict): Dictionary containing CAN data with keys like 'voltage', 'current', 'power', etc.
        """
        self.config = config
        self.test_id_list = test_id_list
        self.output_file_path = output_file_path
        self.plot_directory = plot_directory
        self.hioki_can_analysis_sheet_name = sheet_name
        self.image_position_List = ['A5', 'A40', 'S5', 'S40', 'AK5', 'AK40', 'BC5','BC40', 'BV5','BV40']
        self.image_position_index = -1
        
        # Validate workbook
        try:
            self.wb = openpyxl.load_workbook(self.output_file_path)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load workbook from {self.output_file_path}: {e}")
        
        self.sheet = self.wb.create_sheet(self.hioki_can_analysis_sheet_name)
        
    def set_tdms_data_directory(self):
        current_os = platform.system()

        if current_os == "Linux":
            self.tdms_data_directory = os.path.join(os.path.expanduser("~"), "Documents", "Data", "AMTL-Test-Data")
        
        elif current_os == "Windows":  
            self.tdms_data_directory = os.path.join(os.path.expanduser("~"), "Documents", "Data", "AMTL-Test-Data")
        
        else:
            raise OSError(f"Unsupported operating system: {current_os}")

    def manage_linear_fit_analysis(self):
        
        
        self.set_tdms_data_directory()
        
        for test_id in self.test_id_list:
            self.tdms_file_path = self.tdms_data_directory + f"/{test_id} Test Data.tdms"
            print(f"Conducting Linear Fit Analysis for '{self.tdms_file_path}' TDMS file")
            
            self.tdms_file = TdmsFile.read(self.tdms_file_path, memmap_dir=None)
            
            group_data = self.tdms_file["Data"]
            
            daq_time = group_data[self.config["Hioki-CAN-Analysis-Field"]["DAQ_Time"]].data
            hv_batt_voltage = group_data[self.config["Hioki-CAN-Analysis-Field"]["CAN_Voltage"]].data
            hv_batt_current = group_data[self.config["Hioki-CAN-Analysis-Field"]["CAN_Current"]].data
            hioki_U1 = group_data[self.config["Hioki-CAN-Analysis-Field"]["Hioki_Voltage"]].data
            hioki_I1 = group_data[self.config["Hioki-CAN-Analysis-Field"]["Hioki_Current"]].data
            hioki_P1 = group_data[self.config["Hioki-CAN-Analysis-Field"]["Hioki_Power"]].data
            hioki_WP1 = group_data[self.config["Hioki-CAN-Analysis-Field"]["IntegratedPower"]].data
            Dyno_spd = group_data[self.config["Hioki-CAN-Analysis-Field"]["Dyno_Speed"]].data

            # Calculate HVbatt power
            hv_batt_power = hv_batt_current * hv_batt_voltage

            # Find start index
            start_index = np.argmin(daq_time)

            # Define filtered data
            daqtime_filtered = daq_time[start_index:]
            hv_batt_voltage_filtered = hv_batt_voltage[start_index:]
            hv_batt_current_filtered = -hv_batt_current[start_index:]
            hv_batt_power_filtered = -hv_batt_power[start_index:]
            hioki_U1_filtered = hioki_U1[start_index:]
            hioki_I1_filtered = hioki_I1[start_index:]
            hioki_P1_filtered = hioki_P1[start_index:]
            Dyno_spd_filtered = Dyno_spd[start_index:]

            # Energy calculations
            CAN_power_cal = hv_batt_power_filtered / 1000  # Convert to kW
            index_ps = CAN_power_cal > 0
            index_ng = CAN_power_cal < 0
            hv_batt_pos = np.where(index_ps, CAN_power_cal, 0)
            hv_batt_neg = np.where(index_ng, CAN_power_cal, 0)

            can_power_pos = cumulative_trapezoid(hv_batt_pos, daqtime_filtered, initial=0)
            can_power_neg = cumulative_trapezoid(hv_batt_neg, daqtime_filtered, initial=0) 
            can_power_integrated = (can_power_pos + can_power_neg) / 3600  # Convert from seconds to hours

            # Compute Hioki integrated power in kW by removing initial power
            hioki_inP = (hioki_WP1[start_index:] - hioki_WP1[start_index]) / 1000
            
            # percentage_of_error = (can_power_integrated - hioki_inP) / hioki_inP
            with np.errstate(divide='ignore', invalid='ignore'):
                percentage_of_error = np.where(hioki_inP != 0, (can_power_integrated - hioki_inP) / hioki_inP, 0)

            # Filter logical conndition to address edge condition
            filter_condition = (hv_batt_power_filtered >= -np.inf) & (hioki_U1_filtered >= 250) & (Dyno_spd_filtered >= 0.01)

            self.plot_voltage_current_power(daqtime_filtered, hv_batt_voltage_filtered, hioki_U1_filtered, hv_batt_current_filtered, hioki_I1_filtered, hv_batt_power_filtered, hioki_P1_filtered, test_id)
            # Plot Linear Fit
            self.plot_linear_fit([
                    (hv_batt_voltage_filtered[filter_condition], hioki_U1_filtered[filter_condition], "CAN Voltage [V]", "Hioki Voltage [V]"),
                    (hv_batt_current_filtered[filter_condition], hioki_I1_filtered[filter_condition], "CAN Current [A]", "Hioki Current [A]"),
                    (hv_batt_power_filtered[filter_condition] / 1000, hioki_P1_filtered[filter_condition] / 1000, "CAN Power [kW]", "Hioki Power [kW]"),
                    (np.abs(can_power_integrated), hioki_inP, "CAN Integrated Power [kWh]", "Hioki Integrated Power [kWh]")
                ], test_id)

    def plot_voltage_current_power(self, daqtime_filtered, hv_batt_voltage_filtered, hioki_U1_filtered, hv_batt_current_filtered, hioki_I1_filtered, hv_batt_power_filtered, hioki_P1_filtered, test_id):
 
            plt.figure(figsize=(10, 6))

            plt.subplot(3, 1, 1)
            plt.plot(daqtime_filtered, hv_batt_voltage_filtered, label="CAN Voltage")
            plt.plot(daqtime_filtered, hioki_U1_filtered, label="Hioki Voltage", linestyle="--")
            plt.grid(True)
            plt.xlabel("DAQ Time [s]")
            plt.ylabel("Voltage [V]")
            plt.legend()

            plt.subplot(3, 1, 2)
            plt.plot(daqtime_filtered, hv_batt_current_filtered, label="CAN Current")
            plt.plot(daqtime_filtered, hioki_I1_filtered, label="Hioki Current", linestyle="--")
            plt.grid(True)
            plt.xlabel("DAQ Time [s]")
            plt.ylabel("Current [A]")
            plt.legend()

            plt.subplot(3, 1, 3)
            plt.plot(daqtime_filtered, hv_batt_power_filtered, label="CAN Power")
            plt.plot(daqtime_filtered, hioki_P1_filtered, label="Hioki Power", linestyle="--")
            plt.grid(True)
            plt.xlabel("DAQ Time [s]")
            plt.ylabel("Power [W]")
            plt.legend()

            plt.suptitle(f"Voltage, Current, and Power Analysis for Test ID: {test_id}", fontsize=14, fontweight="bold")
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for the title
            # plt.show()
            # Save the chart as an image and close the plot
            chart_name = f'{test_id}_voltage_current_power_plot.jpg'
            chart_path = os.path.join(self.plot_directory, chart_name)
            plt.savefig(chart_path)
            plt.close()
            
            # Insert the chart image into the workbook at the specified cell
            self.image_position_index += 1
            img = Image(chart_path)
            self.sheet.add_image(img, self.image_position_List[self.image_position_index]) 

    def plot_linear_fit(self, datasets, test_id):
        """
        Plot multiple linear fits in a 2x2 grid and display slope, intercept, R^2, RMS, and Pearson correlation coefficient on the graph.

        Parameters:
        datasets (list of tuples): Each tuple contains (x, y, xlabel, ylabel).
        """
        fig, axs = plt.subplots(2, 2, figsize=(10, 6))

        for ax, (x, y, xlabel, ylabel) in zip(axs.flat, datasets):
            # Linear regression
            slope, intercept, r_value, _, _ = linregress(x, y)

            # RMS calculation
            # residuals = y - (slope * x + intercept) # quantifies how far the observed data (y) is from the predicted data based on the linear regression (slope * x + intercept).
            # rms = np.sqrt(np.mean(residuals**2))
            rms = np.sqrt(np.mean((x - y)**2)) #direct differences between two datasets (x and y), element by element.

            # Pearson correlation coefficient
            pearson_corr = r_value  # Directly from linregress

            # Debugging outputs
            print(f"Dataset: {xlabel} vs {ylabel}")
            print(f"  Slope: {slope:.4f}")
            print(f"  Intercept: {intercept:.4f}")
            print(f"  R^2: {r_value**2:.4f}")
            print(f"  RMS: {rms:.4f}")
            print(f"  Pearson Coefficient: {pearson_corr:.4f}")

            # Scatter plot and regression line
            ax.scatter(x, y, s=10, label="Data")
            ax.plot(x, slope * x + intercept, "r-", label=f"Fit: y={slope:.2f}x + {intercept:.2f}")
            ax.set_title(f'Linear Fit Plot for Test ID: {test_id}')
            # Axis labels
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.grid(True)
            ax.legend()

            # Annotate slope, intercept, R^2, RMS, and Pearson correlation
            annotation_text = (
                f"Slope: {slope:.5f}\n"
                f"Intercept: {intercept:.2f}\n"
                f"$R^2$: {r_value**2:.1f}\n"
                f"RMS: {rms:.5f}\n"
                f"$\\rho$: {pearson_corr:.1f}"  # Pearson correlation coefficient
            )
            ax.text(0.7, 0.45, annotation_text, transform=ax.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        plt.tight_layout()
        # plt.show()
        chart_name = f'{test_id}_linear_fit_plot.jpg'
        chart_path = os.path.join(self.plot_directory, chart_name)
        plt.savefig(chart_path)
        plt.close()
        
        # Insert the chart image into the workbook at the specified cell
        self.image_position_index += 1
        img = Image(chart_path)
        self.sheet.add_image(img, self.image_position_List[self.image_position_index])

    def __del__(self):
        """
        Cleans up resources upon object destruction.
        """
        self.wb.save(self.output_file_path)
        self.wb.close()
        
        object_name = "HiokiCANAnalyzer object"
        print(f"{object_name} is destroyed.")
        
'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    
    # config_file_name = os.path.join("config-files", "configuration_leaf.json")
    config_file_name = os.path.join("config-files", "configuration_tesla.json")
    configFile = open(config_file_name, 'r', encoding='utf-8')
    config = (json.load(configFile))
    configFile.close()
    
    output_file_path = "Analysis/Tesla-Model3/2020-tesla-model3-uncertainty-analysis.xlsx"
    plot_directory = os.path.join("Analysis", "Tesla-Model3")
    sheet_name = "1_Hioki_vs_CAN"
    # test_id_list = [62007023]
    test_id_list = [62005016]
    hioki_CAN_analyzer = HiokiCANAnalyzer(config, test_id_list, output_file_path, plot_directory, sheet_name)
    hioki_CAN_analyzer.manage_linear_fit_analysis()
    del hioki_CAN_analyzer