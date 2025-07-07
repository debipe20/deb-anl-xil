import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
# from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import matplotlib.colors as colors


class PlotManager:
    def __init__(self, config):
        self.config = config
        self.debug_status = self.config['Debug']
        self.title_status = self.config['SetTitle']
        self.plot_save = False if self.debug_status else self.config['PlotSave']
        
    def plot_primary_yaxis(self, x_data, y_data, x_label, y_label, title, fileName):

        plt.figure(figsize=(12, 4.0))
        plt.plot(x_data, y_data, label="Speed")
        # plt.title(title, fontsize=18, fontweight='bold')
        # plt.xlabel(x_label, color='tab:green', fontsize=16)
        # plt.ylabel(y_label, color='tab:blue', fontsize=16)
        # plt.tick_params(axis='both', which='major', labelsize=12)
        # plt.legend(fontsize=16)
        if self.title_status: 
            plt.title(title, fontweight='bold')
        # plt.xlabel(x_label, color='tab:green')
        plt.xlabel(x_label)
        plt.ylabel(y_label, color='tab:blue')
        plt.tick_params(axis='both', which='major')
        plt.grid(True)
        
        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved plot successfully")
        
        else:plt.show()
        
        plt.close()

    def plot_primary_secondary_yaxis(self, fig_size_status, x_data, y_data1, y_data2, x_label, y_label1, y_label2, title, fileName):
        # # Create a figure and axis object
        if fig_size_status:
            # fig, ax1 = plt.subplots(figsize=(10,5))
            fig, ax1 = plt.subplots(figsize=(14,5))
            # fig, ax1 = plt.subplots(figsize=(12,6))
        else: fig, ax1 = plt.subplots()
        
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y_label1, color='tab:blue')
        primary_axis_line, = ax1.plot(x_data, y_data1, color='tab:blue', label='Speed')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.grid(True)

        ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
        ax2.set_ylabel(y_label2, color='tab:red')
        secondary_axis_line, = ax2.plot(x_data, y_data2, color='tab:red', label='Acceleration')
        ax2.tick_params(axis='y', labelcolor='tab:red')
        tick_values = np.arange(min(y_data2), max(y_data2), 0.5)
        ax2.set_yticks(tick_values)
        # Set secondary y-axis ticks at intervals of 0.5
        # ax2.set_ylim(-0.6, 0.6)  # Make sure 0.5 is in range
        # ax2.yaxis.set_major_locator(MultipleLocator(0.5))

        # Combine legends from both axes
        lines = [primary_axis_line, secondary_axis_line]  # Handles for both lines
        labels = [line.get_label() for line in lines]  # Labels for the lines

        if self.title_status:
            plt.title(title, fontweight='bold')
        
        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved plot successfully")

        else:plt.show()

        plt.close(fig)


    def plot_two_data_on_secondary_yaxis(self, x_data, y_data1, y_data2, y_data3, x_label, y_label1, y_label2, title, fileName):
        # Create a figure and axis object
        fig, ax1 = plt.subplots(figsize=(14,5))

        # ax1.set_xlabel(x_label, color='tab:green')
        ax1.set_ylabel(y_label1, color='tab:blue', fontsize=16)
        ax1.set_xlabel(x_label, fontsize=16)
        # ax1.set_ylabel(y_label1, color='tab:blue')
        primary_axis_line, = ax1.plot(x_data, y_data1, color='tab:blue', label='Speed[mph]')
        # ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue', labelsize=12)
        ax1.tick_params(axis='x', labelsize=12)  # Set label size for x-axis ticks

        # Instantiate a second axes that shares the same x-axis
        ax2 = ax1.twinx()
        # ax2.set_ylabel(y_label2, color='tab:red')
        ax2.set_ylabel(y_label2, color='tab:red', fontsize=16)
        secondary_axis_line, = ax2.plot(x_data, y_data2, color='tab:red', label='Accel Req[m/s²]')
        tertiary_axis_line, = ax2.plot(x_data, y_data3, color='tab:green', label='Accel Achv[m/s²]')
        # ax2.tick_params(axis='y', labelcolor='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red', labelsize=12)
        # Set secondary y-axis ticks at intervals of 0.5
        ax2.yaxis.set_major_locator(MultipleLocator(0.5))
                                
        # Combine legends from all axes
        lines = [primary_axis_line, secondary_axis_line, tertiary_axis_line]
        labels = [line.get_label() for line in lines]
        # ax1.legend(lines, labels, loc='upper right', fontsize=10, bbox_to_anchor=(1, 1), ncol=1, frameon=True)
        # ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(1.0, 1.0), prop={"size": 10})
        # ax1.legend(lines, labels, loc='upper right', fontsize=16, bbox_to_anchor=(1.005, 1.0), prop={"size": 9})
        ax1.legend(lines, labels, loc='upper left', fontsize=16, bbox_to_anchor=(0, 1.0), prop={"size": 9})

        ax1.grid(True)
        if self.title_status:
            # plt.title(title, fontweight='bold')
            plt.title(title, fontsize=18, fontweight='bold')
        
        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            # plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            plt.tight_layout()
            plt.savefig(file_directory, dpi=300)
            print("saved plot successfully")
        else:
            plt.show()

        plt.close(fig)

    def plot_specific_accelerations(self, time_data, speed_data_mph, accel_data, specific_accelerations, x_label, y_label1, y_label2, title, fileName):
        # Filter data for the specific acceleration values
        filtered_time_data = []
        filtered_speed_data = []
        filtered_accel_data = []

        # Iterate through the acceleration data and find matching values
        for accel_value in specific_accelerations:
            indices = np.where(accel_data == accel_value)[0]

            # Extract data for matching indices
            for idx in indices:
                filtered_time_data.append(time_data[idx])
                filtered_speed_data.append(speed_data_mph[idx])
                filtered_accel_data.append(accel_data[idx])

        # Plotting the data
        fig, ax1 = plt.subplots()

        # Primary y-axis for speed
        ax1.set_xlabel(x_label, color='tab:green')
        ax1.set_ylabel(y_label1, color='tab:blue')
        primary_axis_line, = ax1.plot(filtered_time_data, filtered_speed_data, color='tab:blue', label='Speed')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Secondary y-axis for acceleration
        ax2 = ax1.twinx()
        ax2.set_ylabel(y_label2, color='tab:red')
        secondary_axis_line, = ax2.plot(filtered_time_data, filtered_accel_data, color='tab:red', label='Acceleration')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # Combine legends from both axes
        lines = [primary_axis_line, secondary_axis_line]
        labels = [line.get_label() for line in lines]

        ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(1, 1), fontsize=10, ncol=1, frameon=True)
        ax1.grid(True)
        plt.title(title, fontweight='bold')

        # Save or show the plot
        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, dpi=300)
            print("saved plot successfully")
        else:
            plt.show()

        plt.close(fig)


    def generate_vehicle_envelope_scatter_plot(self, acc_override_speed_mph, acc_override_acceleration, stock_acc_speed_mph, stock_acc_acceleration):
        """
        Generates a scatter plot for acceleration vs speed in mps, with additional overlay for ACC override data.
        """
        if not acc_override_acceleration or not acc_override_speed_mph:
            print("No data available for plotting. Please ensure data is processed first.")
            return

        plt.figure(figsize=(12, 8))
        
        # Plot the Stock ACC  data
        if stock_acc_speed_mph and stock_acc_acceleration:
            plt.scatter(stock_acc_speed_mph, stock_acc_acceleration, alpha=0.7, label="ACC Override OFF", color="orange", s=10)
        
        # Plot the main vehicle envelope data
        plt.scatter(acc_override_speed_mph, acc_override_acceleration, alpha=0.7, label="ACC Override ON", color="blue", s=10)
                
        # Add labels, title, and legend
        plt.title("2023 Hyundai Ioniq5 Acceleration Envelope", fontsize=16, weight="bold")
        plt.xlabel("Speed [mph]", fontsize=14)
        plt.ylabel("Acceleration [g]", fontsize=14)
        plt.legend(loc="upper right", fontsize=12)
        
        # Grid and formatting
        plt.grid(True, linestyle="--", alpha=0.6)

        # Save or show the plot
        if self.plot_save:
            file_directory = "figures/acceleration-envelop.jpg"
            plt.savefig(file_directory, dpi=300)
            print("saved plot successfully")
        else:
            plt.show()
        
        plt.close()    
            
    def plot_respose_time_heat_map(self):

        # Load the Excel file
        file_path = "output-file/auxiliary-analysis-data.xlsx"
        xls = pd.ExcelFile(file_path)

        # Define the sheet names corresponding to speed ranges
        # speed_ranges = ['0-20mph', '20-40mph', '30-50mph', '50-70mph']
        speed_ranges = ['0-20mph', '30-50mph', '50-70mph']
        
        # Load data from all sheets into a dictionary of DataFrames
        data_dict = {speed: pd.read_excel(xls, sheet_name=speed) for speed in speed_ranges}

        # Create a combined DataFrame for heatmap visualization
        heatmap_data_response_time = []
        for speed_range, df in data_dict.items():
            df_cleaned = df[['Accel_Value', 'Response_Time']].dropna()  # Select relevant columns
            for _, row in df_cleaned.iterrows():
                heatmap_data_response_time.append([speed_range, row['Accel_Value'], row['Response_Time']])

        # Convert to DataFrame
        heatmap_df = pd.DataFrame(heatmap_data_response_time, columns=['Speed Range', 'Acceleration (m/s²)', 'Response Time (s)'])

        # Pivot table to format for heatmap
        heatmap_pivot_reponse_time = heatmap_df.pivot_table(values='Response Time (s)', index='Speed Range', columns='Acceleration (m/s²)')

        # Plot heatmap
        plt.figure(figsize=(12, 6))
        ax = sns.heatmap(heatmap_pivot_reponse_time, annot=True, cmap="coolwarm", linewidths=0.5, fmt=".2f")
        plt.title("Response Time Analysis", fontdict={'fontsize': 18})
        plt.xlabel("Acceleration Request (m/s²)", fontdict={'fontsize': 16})
        plt.ylabel("Speed Range (mph)", fontdict={'fontsize': 16})
        cbar = ax.collections[0].colorbar
        cbar.set_label('Response Time (s)', fontdict={'fontsize': 16})
        
        if self.plot_save:
            file_directory = "figures/respose_time_heat_map.jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved plot successfully")
        
        else:plt.show()
         
        plt.close()
        
    def plot_accel_decel_time_heat_map(self):

        # Load the Excel file
        file_path = "output-file/auxiliary-analysis-data.xlsx"
        xls = pd.ExcelFile(file_path)

        # Define the sheet names corresponding to speed ranges
        # speed_ranges = ['0-20mph', '20-40mph', '30-50mph', '50-70mph']
        speed_ranges = ['0-20mph', '30-50mph', '50-70mph']

        # Load data from all sheets into a dictionary of DataFrames
        data_dict = {speed: pd.read_excel(xls, sheet_name=speed) for speed in speed_ranges}
    
        # Create a combined DataFrame for heatmap visualization using Accel/Decel Time
        heatmap_data_accel_decel = []
        for speed_range, df in data_dict.items():
            df_cleaned = df[['Accel_Value', 'Accel/Decel_Time']].dropna()  # Select relevant columns
            for _, row in df_cleaned.iterrows():
                heatmap_data_accel_decel.append([speed_range, row['Accel_Value'], row['Accel/Decel_Time']])

        # Convert to DataFrame
        heatmap_df_accel_decel = pd.DataFrame(heatmap_data_accel_decel, 
                                            columns=['Speed Range', 'Acceleration (m/s²)', 'Accel/Decel Time (s)'])

        # Pivot table to format for heatmap
        heatmap_pivot_accel_decel = heatmap_df_accel_decel.pivot_table(values='Accel/Decel Time (s)', 
                                                                    index='Speed Range', 
                                                                    columns='Acceleration (m/s²)')

        
        # Plot heatmap
        plt.figure(figsize=(12, 6))
        ax = sns.heatmap(heatmap_pivot_accel_decel, annot=True, cmap="coolwarm", linewidths=0.5, fmt=".2f")
        plt.title("Accel/Decel Time Analysis", fontdict={'fontsize': 18})
        plt.xlabel("Acceleration Request (m/s²)", fontdict={'fontsize': 16})
        plt.ylabel("Speed Range (mph)", fontdict={'fontsize': 16})
        cbar = ax.collections[0].colorbar
        cbar.set_label('Accel/Decel Time (s)', fontdict={'fontsize': 16})
        
        if self.plot_save:
            file_directory = "figures/accel_decel_time_heat_map.jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved plot successfully")
        
        else:plt.show()
        
        plt.close()
        
        
    def plot_respose_time_line_graph(self):

        # Load the Excel file
        file_path = "auxiliary-analysis-data.xlsx"
        xls = pd.ExcelFile(file_path)

        # Define the sheet names corresponding to speed ranges
        speed_ranges = ['0-20mph', '20-40mph', '30-50mph', '50-70mph']

        # Load data from all sheets into a dictionary of DataFrames
        data_dict = {speed: pd.read_excel(xls, sheet_name=speed) for speed in speed_ranges}

        # Create a line chart for Acceleration vs. Response Time for different speed ranges
        plt.figure(figsize=(12, 8))

        for speed_range, df in data_dict.items():
            df_cleaned = df[['Accel_Value', 'Response_Time']].dropna()  # Select relevant columns
            df_sorted = df_cleaned.sort_values(by='Accel_Value')  # Ensure acceleration values are sorted for plotting
            
            # Plot line for each speed range
            plt.plot(df_sorted['Accel_Value'], df_sorted['Response_Time'], marker='o', linestyle='-', label=f"Speed {speed_range}")

        # Customize the plot
        plt.xlabel("Acceleration (m/s²)", fontsize=14)
        plt.ylabel("Response Time (s)", fontsize=14)
        plt.title("Acceleration vs. Response Time for Different Speed Ranges", fontsize=16)
        plt.legend(title="Speed Range (mph)")
        plt.grid(True)

        
        if self.plot_save:
            file_directory = "figures/respose_time_line_chart.jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved plot successfully")
        
        else:plt.show()
         
        plt.close()
        
        
    def plot_respose_time_surface_plot(self):

        # Load the Excel file
        file_path = "auxiliary-analysis-data.xlsx"
        xls = pd.ExcelFile(file_path)

        # Define the sheet names corresponding to speed ranges
        speed_ranges = ['0-20mph', '20-40mph', '30-50mph', '50-70mph']

        # Load data from all sheets into a combined DataFrame for 3D plotting
        plot_data = []
        for speed_range, df in {speed: pd.read_excel(xls, sheet_name=speed) for speed in speed_ranges}.items():
            df_cleaned = df[['Accel_Value', 'Response_Time']].dropna()  # Select relevant columns
            for _, row in df_cleaned.iterrows():
                plot_data.append([speed_range, row['Accel_Value'], row['Response_Time']])

        # Convert to DataFrame
        plot_df = pd.DataFrame(plot_data, columns=['Speed Range', 'Acceleration (m/s²)', 'Response Time (s)'])

        # Convert Speed Range to numeric values for plotting
        plot_df['Speed Numeric'] = plot_df['Speed Range'].astype('category').cat.codes

        # Create 3D surface plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Create a meshgrid for surface plotting
        X, Y = np.meshgrid(sorted(plot_df['Acceleration (m/s²)'].unique()), sorted(plot_df['Speed Numeric'].unique()))
        Z = np.array([plot_df[(plot_df['Acceleration (m/s²)'] == x) & (plot_df['Speed Numeric'] == y)]['Response Time (s)'].mean()
                    for x, y in zip(np.ravel(X), np.ravel(Y))])
        Z = Z.reshape(X.shape)

        # Create colormap
        cmap = cm.viridis
        norm = colors.Normalize(vmin=Z.min(), vmax=Z.max())

        # Plot the surface
        surf = ax.plot_surface(X, Y, Z, cmap=cmap, edgecolor='k', alpha=0.8)

        # Add color bar
        cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=10, pad=0.05)
        cbar.set_label("Response Time (s)", fontsize=12)

        # Labels and title
        ax.set_xlabel("Acceleration (m/s²)", fontsize=12)
        ax.set_ylabel("Speed Range (mph)", fontsize=12, labelpad=15)
        ax.set_zlabel("Response Time (s)", fontsize=12)
        ax.set_title("3D Surface Plot: Acceleration vs. Response Time across Speed Ranges", fontsize=14)

        # Set Y-axis labels to actual speed ranges
        ax.set_yticks(sorted(plot_df['Speed Numeric'].unique()))
        ax.set_yticklabels(sorted(plot_df['Speed Range'].unique()))

        if self.plot_save:
            file_directory = "figures/respose_time_surface_chart.jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved plot successfully")
        
        else:plt.show()
         
        plt.close()
        

    