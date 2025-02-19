"""
**********************************************************************************

PlotManager.py
Created by: Debashis Das
Argonne National Laboratory
Transportation and Power Systems Division

**********************************************************************************

Description:
------------
The `PlotManager` class is responsible for generating and embedding visualizations for uncertainty and energy analysis into an Excel workbook. It integrates seamlessly with the summary data from MCT drive cycles and provides functionality to:

- Plot uncertainty percentages for various drive cycles.
- Plot discharge energy and corresponding uncertainty for comparison.
- Save the plots as images and embed them into the specified Excel sheet.

Methods:
--------
- __init__(self, summary1, summary2, test_id_list, output_file_path, plot_directory, sheet_name): Initializes the PlotManager instance.
- plot_uncertainty_percentage(self): Plots a bar chart comparing uncertainty percentages for drive cycles and embeds it in the Excel sheet.
- plot_energy_analysis(self): Plots a bar chart comparing discharge energy and uncertainty for drive cycles and embeds it in the Excel sheet.
- __del__(self): Cleans up resources by saving and closing the workbook upon object destruction.

"""

import os
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
from openpyxl.drawing.image import Image

class PlotManager:
    def __init__(self, summary1: list, summary2: list, test_id_list: list, output_file_path: str, plot_directory: str, sheet_name: str):
        """
        Initializes the PlotManager instance.

        Args:
        - summary1 (list): Summary data sequence 1 for the drive cycles.
        - summary2 (list): Summary data sequence 2 for the drive cycles.
        - test_id_list (list): List of test IDs for comparison.
        - output_file_path (str): Path to the Excel file where plots will be embedded.
        - plot_directory (str): Directory where plot images will be saved.
        - sheet_name (str): Name of the sheet in the Excel workbook for embedding plots.

        Raises:
        - ValueError: If the lengths of summary1 and summary2 are not equal.
        - FileNotFoundError: If the Excel workbook cannot be loaded.
        """
        self.summary_data_sequence1, self.summary_data_sequence2 = summary1, summary2
        self.bar_chart_test_id_list = test_id_list
        self.output_file_path = output_file_path
        self.plot_directory = plot_directory
        self.sheet_name = sheet_name

        if len(self.summary_data_sequence1) != len(self.summary_data_sequence2):
            raise ValueError("Plotting requires both sequences to have the same length.")

        # Validate workbook
        try:
            self.wb = openpyxl.load_workbook(self.output_file_path)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load workbook from {self.output_file_path}: {e}")
        
    def plot_uncertainty_percentage(self):
        """
        Plots a bar chart comparing uncertainty percentages for MCT Drive cycles.

        Categories:
        - UDDS1, UDDS2, Highway, US06, and Total.

        Embeds the plot into the specified Excel sheet.

        Args:
        None

        Returns:
        None
        """

        try:
            sheet = self.wb[self.sheet_name]
        except KeyError:
            print(f"Sheet '{self.sheet_name}' not found in workbook.")
            return

        # Define categories and set bar positions
        categories = ['UDDS1', 'UDDS2', 'Highway', 'US06', 'Total']

        u_energy_percent_1 = self.summary_data_sequence1[3][2:]
        u_energy_percent_2 = self.summary_data_sequence2[3][2:]

        x = np.arange(len(categories))
        width = 0.35  # Width of a bar

        # Plotting the bars
        fig, ax = plt.subplots(figsize=(10, 6))
        bars1 = ax.bar(x - width / 2, u_energy_percent_1, width, label=self.bar_chart_test_id_list[0], color='skyblue')
        bars2 = ax.bar(x + width / 2, u_energy_percent_2, width, label=self.bar_chart_test_id_list[1], color='orange')

        # Adding labels, title, and customization
        # ax.set_xlabel('Categories')
        ax.set_ylabel('Uncertainty [%]')
        ax.set_title('Uncertainty Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=10)
        ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.7, color='gray')
        # Adding value labels on top of each bar
        for bar in bars1 + bars2:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.02, f'{yval:.1f}%', ha='center', va='bottom')

        # Save the chart as an image and close the plot
        chart_name = f'{self.bar_chart_test_id_list[0]}_vs_{self.bar_chart_test_id_list[1]}_uncertainty_comparison.png'
        chart_path = os.path.join(self.plot_directory, chart_name)
        
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        # Insert the chart image into the workbook at the specified cell
        img = Image(chart_path)
        sheet.add_image(img, 'K5')  # Position the chart in cell K5

    def plot_energy_analysis(self):
        """
        Plots a bar chart comparing discharge energy (primary y-axis) and uncertainty (secondary y-axis) for MCT Drive cycles.

        Features:
        - Categories: UDDS1, UDDS2, Highway, US06, and Total.
        - Dual y-axis: 
            - Primary axis for discharge energy (Wh).
            - Secondary axis for uncertainty (%) with synchronized scaling.
        - Combined legend for bars and lines.

        Embeds the plot into the specified Excel sheet.

        Args:
        None

        Returns:
        None
        """
        try:
            sheet = self.wb[self.sheet_name]
        except KeyError:
            print(f"Sheet '{self.sheet_name}' not found in workbook.")
            return

        # Define categories
        categories = ['UDDS1', 'UDDS2', 'Highway', 'US06', 'Total']

        # Extract data for Energy [Wh] and u (Energy) [%]
        self.energy_values_1 = self.summary_data_sequence1[1][2:]
        self.energy_values_2 = self.summary_data_sequence2[1][2:]
        u_energy_percent_1 = self.summary_data_sequence1[3][2:]
        u_energy_percent_2 = self.summary_data_sequence2[3][2:]

        x = np.arange(len(categories))
        width = 0.35

        # Create the figure and axes
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot Energy [Wh] on the primary y-axis
        # bars1 = ax1.bar(x - width / 2, self.energy_values_1, width, label=self.bar_chart_test_id_list[0], color='gray')
        # bars2 = ax1.bar(x + width / 2, self.energy_values_2, width, label=self.bar_chart_test_id_list[1], color='orange')
        bars1 = ax1.bar(x - width / 2, self.energy_values_1, width, label=f'Energy_{self.bar_chart_test_id_list[0]}', color='slateblue')
        bars2 = ax1.bar(x + width / 2, self.energy_values_2, width, label=f'Energy_{self.bar_chart_test_id_list[1]}', color='goldenrod')
        ax1.set_ylabel('Discharge Energy [Wh]', fontsize=12)
        ax1.set_title('Discharge Energy and Uncertainty by Drive Cycle', fontsize=14)
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.grid(True, which='both', axis='y', linestyle='--', linewidth=0.7, color='gray')
        # ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=10)

        # Create the secondary y-axis
        ax2 = ax1.twinx()
        # ax2.plot(x, u_energy_percent_1, color='blue', marker='o')
        # ax2.plot(x, u_energy_percent_2, color='red', marker='s')
        line1, = ax2.plot(x, u_energy_percent_1, color='blue', marker='o', label=f'Uncertainty_{self.bar_chart_test_id_list[0]}')
        line2, = ax2.plot(x, u_energy_percent_2, color='red', marker='s', label=f'Uncertainty_{self.bar_chart_test_id_list[1]}')
        ax2.set_ylabel('Uncertainty [%]', fontsize=12)

        # Synchronize secondary y-axis scale
        primary_y_max = ax1.get_ylim()[1]
        secondary_y_max = primary_y_max / 1000 * 2  # Scale: 1000 units = 2%
        ax2.set_ylim(0, secondary_y_max)
        # ax2.legend(loc='upper right', fontsize=10)

        # Add value labels for the bars (Energy [Wh])
        for bar in bars1 + bars2:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, yval + 50, f'{yval:.0f}', ha='center', va='bottom', fontsize=8)

        # Fetch legend handles and labels from both axes, and combine all legend elements
        handles1, labels1 = ax1.get_legend_handles_labels()  # Bar chart handles and labels
        handles2, labels2 = ax2.get_legend_handles_labels()  # Line chart handles and labels
        fig.legend(handles1 + handles2, labels1 + labels2,
                        loc='lower center', ncol=4, fontsize=10)

        # Save the chart
        chart_name = f'{self.bar_chart_test_id_list[0]}_vs_{self.bar_chart_test_id_list[1]}_energy_with_uncertainty.png'
        chart_path = os.path.join(self.plot_directory, chart_name)
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)  # Push the plot upward to make space for the legend
        plt.savefig(chart_path)
        plt.close()

        # Insert the chart image into the workbook
        img = Image(chart_path)
        sheet.add_image(img, 'K40')

    def __del__(self):
        """
        Cleans up resources upon object destruction.
        """
        # Save workbook before destroying the plot_manager object
        self.wb.save(self.output_file_path)
        self.wb.close()
        
        object_name = "PlotManager object"
        print(f"{object_name} is destroyed.")