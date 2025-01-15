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

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class HiokiCANAnalyzer:
    def __init__(self, hioki_data, can_data):
        """
        Initialize the HiokiCANAnalyzer class.

        Parameters:
        hioki_data (dict): Dictionary containing Hioki data with keys like 'voltage', 'current', 'power', etc.
        can_data (dict): Dictionary containing CAN data with keys like 'voltage', 'current', 'power', etc.
        """
        self.hioki_data = hioki_data
        self.can_data = can_data

    def plot_linear_fit(self, x, y, xlabel, ylabel, title, ax):
        """
        Plot linear fit for a pair of data (x and y).

        Parameters:
        x (array): X-axis data.
        y (array): Y-axis data.
        xlabel (str): Label for the X-axis.
        ylabel (str): Label for the Y-axis.
        title (str): Title of the plot.
        ax (matplotlib.axes.Axes): Axes object to plot on.
        """
        x = np.array(x).reshape(-1, 1)
        y = np.array(y)
        
        # Perform linear regression
        model = LinearRegression().fit(x, y)
        slope = model.coef_[0]
        intercept = model.intercept_
        y_pred = model.predict(x)
        
        # Calculate RMS and R^2
        rms = np.sqrt(mean_squared_error(y, y_pred))
        r2 = r2_score(y, y_pred)
        
        # Plot data points and linear fit
        ax.scatter(x, y, color='gray', alpha=0.5, label='Data Points')
        ax.plot(x, y_pred, color='red', linewidth=2, label='Linear Fit')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fontsize=9, framealpha=0.7)
        
        # Add annotations
        ax.set_title(f"{title}\nRMS: {rms:.5f}")
        ax.text(0.05, 0.95, f"Slope = {slope:.4f}\nIntercept = {intercept:.2f}\n$R^2$ = {r2:.2f}",
                transform=ax.transAxes, verticalalignment='top', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

    def analyze_and_plot(self, output_file="linear-fit-analysis.jpg"):
        """
        Analyze Hioki and CAN data, and generate linear fit plots.

        Parameters:
        output_file (str): File path to save the resulting plot.
        """
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        
        # Analyze voltage
        self.plot_linear_fit(
            self.can_data['voltage'],
            self.hioki_data['voltage'],
            "CAN Voltage [V]",
            "Hioki Voltage [V]",
            "Voltage Comparison",
            axs[0, 0]
        )
        
        # Analyze current
        self.plot_linear_fit(
            self.can_data['current'],
            self.hioki_data['current'],
            "CAN Current [A]",
            "Hioki Current [A]",
            "Current Comparison",
            axs[0, 1]
        )
        
        # Analyze power
        self.plot_linear_fit(
            self.can_data['power'],
            self.hioki_data['power'],
            "CAN I*V [kW]",
            "Hioki Active Power [kW]",
            "Power Comparison",
            axs[1, 0]
        )
        
        # Analyze integrated power
        self.plot_linear_fit(
            self.can_data['integrated_power'],
            self.hioki_data['integrated_power'],
            "CAN Integrated Power [kWh]",
            "Hioki Integrated Power [kWh]",
            "Integrated Power Comparison",
            axs[1, 1]
        )
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(output_file)
        plt.close()
        print(f"Plot saved to {output_file}")
