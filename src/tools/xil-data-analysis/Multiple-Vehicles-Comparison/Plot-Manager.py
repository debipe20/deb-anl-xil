import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import scipy.interpolate

class PlotManager:
    def __init__(self, config):
        self.config = config
        self.input_file_path = config["InputFileName"]

    def plot_all_heatmaps(self):
        """Generates heatmaps for all speed ranges."""
        xls = pd.ExcelFile(self.input_file_path)
        speed_ranges = ["0-20mph", "30-50mph", "50-70mph"]

        for sheet in speed_ranges:
            df = pd.read_excel(xls, sheet_name=sheet)
            df["Vehicle Name"] = df["Vehicle Name"].ffill()

            heatmap_data = df.pivot_table(values="Response Time", index="Vehicle Name", columns="Acceleration Request", aggfunc="mean")

            plt.figure(figsize=(10, 6))
            ax = sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", linewidths=0.5, fmt=".2f")

            # Add colorbar label
            cbar = ax.collections[0].colorbar
            cbar.set_label("Response Time (s)")

            plt.title(f"Acceleration Request vs Response Time ({sheet})", fontsize=14)
            plt.xlabel("Acceleration Request (m/s²)", fontsize=12)
            plt.ylabel("Vehicle Type", fontsize=12)
            
            plt.savefig(f"figures/heatmap_{sheet}.png", bbox_inches="tight", dpi=300)
            print(f"Saved: heatmap_{sheet}.png")
            plt.close()

    def plot_contour_plot(self):
        """Generates contour plots for all speed ranges."""
        xls = pd.ExcelFile(self.input_file_path)
        speed_ranges = ["0-20mph", "30-50mph", "50-70mph"]

        for sheet in speed_ranges:
            df = pd.read_excel(xls, sheet_name=sheet)
            df["Vehicle Name"] = df["Vehicle Name"].ffill()

            x = df["Acceleration Request"]
            y = df["Vehicle Name"].astype('category').cat.codes
            z = df["Response Time"]

            xi = np.linspace(x.min(), x.max(), 100)
            yi = np.linspace(y.min(), y.max(), 100)
            xi, yi = np.meshgrid(xi, yi)
            zi = scipy.interpolate.griddata((x, y), z, (xi, yi), method='cubic')

            plt.figure(figsize=(10, 6))
            contour = plt.contourf(xi, yi, zi, cmap="coolwarm", levels=20)
            
            # Add colorbar label
            cbar = plt.colorbar(contour)
            cbar.set_label("Response Time (s)")

            plt.title(f"Acceleration vs Response Time ({sheet})", fontsize=14)
            plt.xlabel("Acceleration Request (m/s²)", fontsize=12)
            plt.ylabel("Vehicle Type", fontsize=12)

            # Adjust Y-tick positions and labels
            unique_y_positions = np.unique(y)
            vehicle_names = df["Vehicle Name"].unique()

            plt.yticks(ticks=unique_y_positions, labels=vehicle_names, va="center", rotation=90)  # Center-align and rotate

            plt.savefig(f"figures/contour_{sheet}.png", bbox_inches="tight", dpi=300)
            print(f"Saved: contour_{sheet}.png")
            plt.close()


    def plot_3d_surface_plot(self):
        """Generates 3D surface plots for all speed ranges."""
        xls = pd.ExcelFile(self.input_file_path)
        speed_ranges = ["0-20mph", "30-50mph", "50-70mph"]

        for sheet in speed_ranges:
            df = pd.read_excel(xls, sheet_name=sheet)
            df["Vehicle Name"] = df["Vehicle Name"].ffill()

            x = df["Acceleration Request"]
            y = df["Vehicle Name"].astype('category').cat.codes
            z = df["Response Time"]

            xi = np.linspace(x.min(), x.max(), 100)
            yi = np.linspace(y.min(), y.max(), 100)
            xi, yi = np.meshgrid(xi, yi)
            zi = scipy.interpolate.griddata((x, y), z, (xi, yi), method='cubic')

            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(xi, yi, zi, cmap="coolwarm", edgecolor='k', alpha=0.8)
            ax.set_xlabel("Acceleration Request (m/s²)")
            # ax.set_ylabel("Vehicle Type")
            ax.set_zlabel("Response Time (s)")
            ax.set_title(f"Acceleration vs Response Time ({sheet})")
            ax.set_yticks(ticks=np.unique(y))
            ax.set_yticklabels(df["Vehicle Name"].unique())
            plt.savefig(f"figures/3d_surface_{sheet}.png", bbox_inches="tight", dpi=300)
            print(f"Saved: 3d_surface_{sheet}.png")
            #plt.show()
            plt.close()
            
            
    def plot_3d_surface_plot_seperate(self):
        """Generates 3D curve plots for each vehicle in all speed ranges."""
        xls = pd.ExcelFile(self.input_file_path)
        speed_ranges = ["0-20mph", "30-50mph", "50-70mph"]

        for sheet in speed_ranges:
            df = pd.read_excel(xls, sheet_name=sheet)
            df["Vehicle Name"] = df["Vehicle Name"].ffill()

            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111, projection='3d')

            # Assign colors for different vehicles
            colors = ["red", "blue", "green", "purple", "orange"]

            for i, (vehicle, df_vehicle) in enumerate(df.groupby("Vehicle Name")):
                x = df_vehicle["Acceleration Request"]
                y = df_vehicle["Response Time"]
                z = np.full_like(x, i)  # Give each vehicle a unique Z level

                # Plot each vehicle's response curve
                ax.plot(x, y, z, marker='o', linestyle='-', label=vehicle, color=colors[i % len(colors)])
                # xi = np.linspace(x.min(), x.max(), 100)
                # yi = np.linspace(y.min(), y.max(), 100)
                # xi, yi = np.meshgrid(xi, yi)
                # zi = scipy.interpolate.griddata((x, y), z, (xi, yi), method='cubic')
                # ax.plot_surface(xi, yi, zi, cmap="coolwarm", edgecolor='k', alpha=0.8)
                
            # Customize the 3D plot
            ax.set_xlabel("Acceleration Request (m/s²)")
            ax.set_ylabel("Response Time (s)")
            ax.set_zlabel("Vehicle Index (for separation)")
            ax.set_title(f"Acceleration vs Response Time ({sheet})")
            ax.legend()

            # Save the plot
            plt.savefig(f"figures/3d_curves_{sheet}.png", bbox_inches="tight", dpi=300)
            print(f"Saved: 3d_curves_{sheet}.png")
            #plt.show()
            plt.close()

'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    plot_manager = PlotManager(config)
    plot_manager.plot_all_heatmaps()
    plot_manager.plot_contour_plot()
    plot_manager.plot_3d_surface_plot()
    plot_manager.plot_3d_surface_plot_seperate()



