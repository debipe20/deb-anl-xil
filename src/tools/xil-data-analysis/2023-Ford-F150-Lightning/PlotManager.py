import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

class PlotManager:
    def __init__(self, config):
        self.config = config
        self.title_status = self.config['SetTitle']
        self.plot_save = self.config['PlotSave']
    
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
            file_directory = "figure/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved file")
        
        else:plt.show()
        
        plt.close()

    def plot_primary_secondary_yaxis(self, fig_size_status, x_data, y_data1, y_data2, x_label, y_label1, y_label2, title, fileName):
        # # Create a figure and axis object
        if fig_size_status:
            # fig, ax1 = plt.subplots(figsize=(10,4.55))
            fig, ax1 = plt.subplots(figsize=(14,5))
        else: fig, ax1 = plt.subplots()

        # ax1.set_xlabel(x_label, color='tab:green', fontsize=16)
        # ax1.set_ylabel(y_label1, color='tab:blue', fontsize=16)
        # primary_axis_line, = ax1.plot(x_data, y_data1, color='tab:blue', label='Speed')
        # ax1.tick_params(axis='y', labelcolor='tab:blue', labelsize=12)
        # ax1.tick_params(axis='x', labelsize=12)  # Set label size for x-axis ticks
        # ax1.set_xlabel(x_label, color='tab:green')
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y_label1, color='tab:blue')
        primary_axis_line, = ax1.plot(x_data, y_data1, color='tab:blue', label='Speed')
        ax1.tick_params(axis='y', labelcolor='tab:blue')


        ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
        # ax2.set_ylabel(y_label2, color='tab:red', fontsize=16)
        ax2.set_ylabel(y_label2, color='tab:red')
        secondary_axis_line, = ax2.plot(x_data, y_data2, color='tab:red', label='Acceleration')
        # ax2.tick_params(axis='y', labelcolor='tab:red', labelsize=12)
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # Combine legends from both axes
        lines = [primary_axis_line, secondary_axis_line]  # Handles for both lines
        labels = [line.get_label() for line in lines]  # Labels for the lines

        # ax1.legend(lines, labels, loc='upper right', fontsize=16)
        ax1.grid(True)
        # plt.title(title, fontsize=18, fontweight='bold')
        if self.title_status:
            plt.title(title, fontweight='bold')
        
        if self.plot_save:
            file_directory = "figure/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved file")

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
            file_directory = "figure/" + fileName + ".jpg"
            # plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            plt.tight_layout()
            plt.savefig(file_directory, dpi=300)
            print("saved file")
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
            file_directory = "figure/" + fileName + ".jpg"
            plt.savefig(file_directory, dpi=300)
            print("saved file")
        else:
            plt.show()

        plt.close(fig)



        