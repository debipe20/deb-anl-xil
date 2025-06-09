import os
import platform
import numpy as np
from nptdms import TdmsFile
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

class EnergyConsumptionModel:
    """A class to model energy consumption based on vehicle speed, tractive force, road grade, current, and voltage."""
    
    def __init__(self, config):
        self.config = config
        self.debug_status = self.config['Debug']
        self.title_status = self.config['SetTitle']
        self.plot_save = False if self.debug_status else self.config['PlotSave']
        self.road_grade_test_file_list = self.config['RoadGradeFileList']
        self.road_grade_list = self.config['RoadGrade']
        self.grade_data = []
        self.speed_data_mps = []
        self.speed_data_mph = []
        self.energy_consumed_list, self.energy_regenerated_list, self.net_energy_used_list, self.average_energy_rate_list = [], [], [], []
        
    def get_data_directory(self):
        """
            Method to get the Data directory irrespective of operating system
        """
        current_os = platform.system()

        if current_os == "Linux":
            data_directory = os.path.join(os.path.expanduser("~"), "Downloads", "2020-Tesla-Model3")
        # elif current_os == "Windows":
        #     data_directory = os.path.join("C:\\", "Users", "ddas", "Documents", "Data", "2020-Tesla-Model3", "road-grada-data")
            
        elif current_os == "Windows":
            user_directory = os.environ['USERPROFILE']  # This retrieves the user's home directory in Windows
            data_directory = os.path.join(user_directory, "Documents", "Data", "2020-Tesla-Model3", "road-grada-data")

        else:
            raise OSError(f"Unsupported operating system: {current_os}")
        
        return data_directory      
        
    def get_data_from_group_channel(self):
        """
            Method to get data from group and channel
        """
        
        self.group_data = self.tdms_file["Data"]

        self.time_channel = self.group_data['Time[s]']
        self.speed_channel_kph = self.group_data['veh_speed']       
        self.voltage_channel = self.group_data['BMS_packVoltage']
        self.current_channel = self.group_data['BMS_packCurrent']
        self.drive_trace_speed_channel = self.group_data['Dyno_Data_Drivetrace_Spd_Vspy']
        self.tractive_force_channel = self.group_data['Dyno_TractiveForce[N]']
        
        # self.tractive_force_front_channel = self.group_data['Dyno_TractiveForce_Front[N]']
        self.tractive_force_front_channel = self.group_data['Dyno_LoadCell_Front[N]']
        self.tractive_force_rear_channel = self.group_data['Dyno_TractiveForce_Rear[N]']
        
        self.time_data = self.time_channel[:]
        self.speed_data_mph = self.speed_channel_kph[:] * 0.62137 
        self.speed_data_mps = self.speed_channel_kph[:] * 0.277778
        self.drive_trace_speed_data_mph = self.drive_trace_speed_channel[:]
        
        self.voltage = self.voltage_channel[:]
        self.current = self.current_channel[:]
        self.power_kw = (self.voltage * self.current) / 1000
        
        self.tractive_force = self.tractive_force_channel[:]
        self.tractive_force_front = self.tractive_force_front_channel[:]
        self.tractive_force_rear = self.tractive_force_rear_channel[:]
        
        # Define regeneration logic: when current is positive, we are recovering energy
        self.regen_flag = np.where(self.current > 0, 1, 0)  # 1 when regenerative braking occurs, 0 when consumption

    def data_preprocessing(self):
        """
        Prepare the data: Extract relevant features and target variable.
        """
        speed_mph_list = []
        road_grade_list = []
        tractive_force_list = []
        tractive_force_front_list = []
        tractive_force_rear_list = []
        power_kw_list = []
        regen_flag_list = []
        
        data_directory = self.get_data_directory()
        
        for index, test_file_name in enumerate(self.road_grade_test_file_list):
            tdms_file_path = os.path.join(data_directory, test_file_name)
            
            # Check if the file exists
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            print(f"Processing test file: {test_file_name}")
            
            road_grade = self.road_grade_list[index]
            print(f"Road Grade: {road_grade} %")
            
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_data_from_group_channel()
            
            for i in range(1, len(self.time_data)):
                speed_mph_list.append(self.speed_data_mph[i])
                road_grade_list.append(road_grade)
                tractive_force_list.append(self.tractive_force[i])
                tractive_force_front_list.append(self.tractive_force_front[i])
                tractive_force_rear_list.append(self.tractive_force_rear[i])
                power_kw_list.append(self.power_kw[i])
                regen_flag_list.append(self.regen_flag[i])
                
        # Convert features to numpy arrays for processing
        speed = np.array(speed_mph_list)  # Speed in mph
        tractive_force = np.array(tractive_force_list)  # Tractive force in N
        tractive_force_front = np.array(tractive_force_front_list)  # Front tractive force in N
        tractive_force_rear = np.array(tractive_force_rear_list)  # Rear tractive force in N
        grade = np.array(road_grade_list)  # Road grade
        power_kw = np.array(power_kw_list)  # Power in kW
        regen_flag = np.array(regen_flag_list)  # Regeneration flag
        
        # Stack features into a single matrix (X)
        # X = np.column_stack((speed, tractive_force, grade, regen_flag))
        X = np.column_stack((speed, tractive_force, grade))

        # Target variable (y) is the energy consumed
        y = power_kw

        return X, y
    
    def calculate_energy_with_regeneration(self):
        """
        Compute energy consumed and regenerated, adjusting for regeneration during deceleration or downhill.
        """
        # Extract data
        current = np.array(self.current)
        voltage = np.array(self.voltage)

        # Calculate energy consumed: Energy = current * voltage
        energy = (current * voltage) / 1000  # Convert from W to kW
        
        # Define regeneration logic: when current is positive, we are recovering energy
        regen_energy = np.where(current > 0, energy, 0)  # Only when current is positive (regeneration)
        
        # Define consumption: when current is negative, we are consuming energy
        consumed_energy = np.where(current < 0, energy, 0)  # Only when current is negative (consumption)
        
        # Calculate net energy
        net_energy = np.sum(consumed_energy) - np.sum(regen_energy)  # Total energy consumed minus regeneration
        
        print(f"Total Energy Consumed: {np.sum(consumed_energy):.3f} kWh")
        print(f"Total Energy Regenerated: {np.sum(regen_energy):.3f} kWh")
        print(f"Net Energy Used: {net_energy:.3f} kWh")

        return consumed_energy, regen_energy, net_energy

    def cross_validate_model(self, model, X, y):
        """
        Performs K-Fold Cross Validation on the given model and returns the Mean Squared Error.
        """
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X, y, cv=kf, scoring='neg_mean_squared_error')

        # Convert negative MSE to positive
        mean_mse = -cv_scores.mean()
        print(f"Cross-Validation MSE: {mean_mse:.4f}")
        return mean_mse

    def linear_regression(self, title="Linear Regression Model", fileName="linear_regression_plot"):
        """
        Fit a linear regression model to the data.
        """
        
        # Preprocess the data
        X, y = self.data_preprocessing()

        # Create and train the linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Perform cross-validation
        # self.linear_mse = self.cross_validate_model(model, X, y)

        # Make predictions
        y_pred = model.predict(X)

        # Calculate Mean Squared Error
        mse = mean_squared_error(y, y_pred)
        print(f"Linear Regression MSE: {mse:.4f}")

        # Print coefficients
        print(f"Intercept (β0): {model.intercept_:.4f}")
        print(f"Coefficients (β1, β2, β3): {model.coef_}")

        # Plot predicted vs actual energy consumption
        plt.figure(figsize=(8, 6))
        plt.scatter(y, y_pred, color='blue')
        plt.plot([min(y), max(y)], [min(y), max(y)], color='red', linestyle='--')
        # plt.legend(["Predicted vs Actual", "Ideal Line"], loc='upper left')
        plt.xlabel("Actual Energy Consumed (kWh)")
        plt.ylabel("Predicted Energy Consumed (kWh)")
        plt.title("Linear Regression: Actual vs. Predicted Energy Consumption")
        
        # Title and grid
        if self.title_status:
            plt.title(title, fontweight='bold')
        plt.grid(True)

        # Save or show
        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("Saved plot successfully at:", file_directory)
        else:
            plt.show()

        plt.close()

    def polynomial_regression(self, degree=2, title="Polynomial Regression Model", fileName="polynomial_regression_plot"):
        """
        Fit a polynomial regression model to the data for better fit.
        """
        # Preprocess the data
        X, y = self.data_preprocessing()

        # Transform the features to polynomial features (degree 2)
        poly = PolynomialFeatures(degree)
        X_poly = poly.fit_transform(X)

        # Create and train the polynomial regression model
        model = LinearRegression()
        
        # # Perform cross-validation
        # self.poly_mse = self.cross_validate_model(model, X_poly, y)
        
        model.fit(X_poly, y)
        
        # Make predictions
        y_pred_poly = model.predict(X_poly)

        # Calculate Mean Squared Error
        mse_poly = mean_squared_error(y, y_pred_poly)
        print(f"Polynomial Regression MSE: {mse_poly:.4f}")

        # Print coefficients
        print(f"Intercept (β0): {model.intercept_:.4f}")
        print(f"Polynomial Coefficients: {model.coef_}")

        # Plot predicted vs actual energy consumption
        plt.figure(figsize=(8, 6))
        plt.scatter(y, y_pred_poly, color='blue')
        plt.plot([min(y), max(y)], [min(y), max(y)], color='red', linestyle='--')
        # plt.legend(["Predicted vs Actual", "Ideal Line"], loc='upper left')
        plt.xlabel("Actual Energy Consumed (kWh)")
        plt.ylabel("Predicted Energy Consumed (kWh)")
        plt.title(f"Polynomial Regression (Degree {degree}): Actual vs. Predicted Energy Consumption")
        
        # Title and grid
        if self.title_status:
            plt.title(title, fontweight='bold')
        plt.grid(True)

        # Save or show
        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("Saved plot successfully at:", file_directory)
        else:
            plt.show()

        plt.close()
        
    def plot_actual_vs_predicted(self, y_actual, y_pred):
        """
        Plots the Actual vs Predicted Energy Consumption.
        """
        plt.figure(figsize=(8, 6))
        plt.scatter(y_actual, y_pred, color='blue', label="Predicted vs Actual")
        plt.plot([min(y_actual), max(y_actual)], [min(y_actual), max(y_actual)], color='red', linestyle='--', label="Ideal Line")
        plt.xlabel("Actual Energy Consumed (kWh)")
        plt.ylabel("Predicted Energy Consumed (kWh)")
        plt.title("Actual vs Predicted Energy Consumption")
        plt.legend()
        plt.grid(True)
        plt.show()


'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    energyConsumptionModel = EnergyConsumptionModel(config)
    energyConsumptionModel.linear_regression(title="Linear Regression Model", fileName="linear_regression_plot")
    energyConsumptionModel.polynomial_regression(degree=2, title="Polynomial Regression Model", fileName="polynomial_regression_plot")