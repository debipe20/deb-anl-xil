import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from nptdms import TdmsFile

class PlotManager:
    def __init__(self, config):
        self.config = config
        self.title_status = self.config['SetTitle']
        self.plot_save = self.config['PlotSave']
    
    def plot_primary_yaxis(self, x_data, y_data, x_label, y_label, title, fileName):

        plt.plot(x_data, y_data, label="Speed")
        # plt.title(title, fontsize=18, fontweight='bold')
        # plt.xlabel(x_label, color='tab:green', fontsize=16)
        # plt.ylabel(y_label, color='tab:blue', fontsize=16)
        # plt.tick_params(axis='both', which='major', labelsize=12)
        # plt.legend(fontsize=16)
        if self.title_status: 
            plt.title(title, fontweight='bold')
        # plt.xlabel(x_label, color='tab:green')
        plt.ylabel(y_label, color='tab:blue')
        plt.tick_params(axis='both', which='major')
        plt.grid(True)
        
        if self.plot_save:
            file_directory = "figure/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("saved file")
        
        else:plt.show()
        
        plt.close()

    def plot_primary_secondary_yaxis(self, x_data, y_data1, y_data2, x_label, y_label1, y_label2, title, fileName):
        # # Create a figure and axis object
        fig, ax1 = plt.subplots()

        # ax1.set_xlabel(x_label, color='tab:green', fontsize=16)
        # ax1.set_ylabel(y_label1, color='tab:blue', fontsize=16)
        # primary_axis_line, = ax1.plot(x_data, y_data1, color='tab:blue', label='Speed')
        # ax1.tick_params(axis='y', labelcolor='tab:blue', labelsize=12)
        # ax1.tick_params(axis='x', labelsize=12)  # Set label size for x-axis ticks
        # ax1.set_xlabel(x_label, color='tab:green')
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


    def plot_twice_secondary_yaxis(self, x_data, y_data1, y_data2, y_data3, x_label, y_label1, y_label2, title, fileName):
        # Create a figure and axis object
        fig, ax1 = plt.subplots()

        # ax1.set_xlabel(x_label, color='tab:green')
        ax1.set_ylabel(y_label1, color='tab:blue')
        primary_axis_line, = ax1.plot(x_data, y_data1, color='tab:blue', label='Speed[mph]')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Instantiate a second axes that shares the same x-axis
        ax2 = ax1.twinx()
        ax2.set_ylabel(y_label2, color='tab:red')
        secondary_axis_line, = ax2.plot(x_data, y_data2, color='tab:red', label='Accel Req[m/s²]')
        tertiary_axis_line, = ax2.plot(x_data, y_data3, color='tab:green', label='Accel Achv[m/s²]')
        ax2.tick_params(axis='y', labelcolor='tab:red')


        # Combine legends from all axes
        lines = [primary_axis_line, secondary_axis_line, tertiary_axis_line]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc='upper right', fontsize=10, bbox_to_anchor=(1, 1), ncol=1, frameon=True)

        ax1.grid(True)
        if self.title_status:
            plt.title(title, fontweight='bold')
        
        if self.plot_save:
            file_directory = "figure/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=600)
            print("saved file")
        else:
            plt.show()

        plt.close(fig)


    