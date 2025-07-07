import os
import platform
import numpy as np
from nptdms import TdmsFile
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class EnergyConsumptionModel:
    """A class to model energy consumption based on vehicle speed, tractive force, road grade, current, and voltage."""
    
    def __init__(self, config):
        self.config = config
        self.debug_status = self.config['Debug']
        self.title_status = self.config['SetTitle']
        self.plot_save = False if self.debug_status else self.config['PlotSave']
        self.road_grade_test_file_list = self.config['EnergyModelRoadGradeFileList']
        self.road_grade_list = self.config['EnergyModelRoadGrade']
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
        # self.drive_trace_speed_channel = self.group_data['Dyno_Data_Drivetrace_Spd_Vspy']
        self.drive_trace_speed_channel = self.group_data['Dyno_Data_Drivetrace_Spd']
        self.tractive_force_channel = self.group_data['Dyno_TractiveForce[N]']
        
        self.tractive_force_front_channel = self.group_data['Dyno_TractiveForce_Front[N]']
        # self.tractive_force_front_channel = self.group_data['Dyno_LoadCell_Front[N]']
        self.tractive_force_rear_channel = self.group_data['Dyno_TractiveForce_Rear[N]']
                
        self.front_axle_speed_channel = self.group_data['DIF_axleSpeed']
        self.rear_axle_speed_channel = self.group_data['DIR_axleSpeed']
        self.front_torque_actual_channel = self.group_data['DIF_torqueActual']
        self.rear_torque_actual_channel = self.group_data['DIR_torqueActual']
        self.front_torque_commanded_channel = self.group_data['DIF_torqueCommand']
        self.rear_torque_commanded_channel = self.group_data['DIR_torqueCommand']
        self.front_electric_power_channel = self.group_data['DIF_elecPower']
        self.rear_electric_power_channel = self.group_data['DIR_elecPower']
        
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
        
        
        self.front_axle_speed = self.front_axle_speed_channel[:]
        self.rear_axle_speed = self.rear_axle_speed_channel[:]
        self.front_torque_actual = self.front_torque_actual_channel[:]
        self.rear_torque_actual = self.rear_torque_actual_channel[:]
        self.front_torque_commanded = self.front_torque_commanded_channel[:]
        self.rear_torque_commanded = self.rear_torque_commanded_channel[:]
        self.front_electric_power = self.front_electric_power_channel[:]
        self.rear_electric_power = self.rear_electric_power_channel[:]
        
        # Define regeneration logic: when current is positive, we are recovering energy
        self.regen_flag = np.where(self.current > 0, 1, 0)  # 1 when regenerative braking occurs, 0 when consumption


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
    
    
    def run_pearson_correlation_train_data(self):
        """
        Perform Pearson correlation analysis on training data only.
        """
        
        data_directory = self.get_data_directory()
        df_all = []

        # Use only training files (all except last)
        train_files = self.road_grade_test_file_list[:-1]
        train_grades = self.road_grade_list[:-1]

        for file, grade in zip(train_files, train_grades):
            tdms_file_path = os.path.join(data_directory, file)
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_data_from_group_channel()

            
            speed = self.speed_data_mph[1:]
            tractive_force = self.tractive_force[1:]
            tractive_force_front = self.tractive_force_front[1:]
            tractive_force_rear = self.tractive_force_rear[1:]
            current = self.current[1:]
            power_kw = self.power_kw[1:]
            power_consumed_kw = np.where(current < 0, -power_kw, 0)
            power_regenerated_kw = np.where(current > 0, power_kw, 0)
            regen_flag = self.regen_flag[1:]
            torque_actual_front = self.front_torque_actual[1:]
            torque_actual_rear = self.rear_torque_actual[1:]
            electric_power_front = self.front_electric_power[1:]
            electric_power_rear = self.rear_electric_power[1:]

            # Handle grade
            if isinstance(grade, str) and grade == "Dynamic":
                grade_data = self.group_data["Dyno_Data_Drivetrace_Grade"][:]
                grade_val = grade_data[1:]
            else:
                grade_val = np.full_like(speed, float(grade), dtype=float)

            df = pd.DataFrame({
                "Speed_mph": speed,
                "Grade_percent": grade_val,
                "RegenFlag": regen_flag,
                "TractiveForce_N": tractive_force,
                "TractiveForce_Front_N": tractive_force_front,
                "TractiveForce_Rear_N": tractive_force_rear,
                "Power_kW": power_kw,
                # "PowerConsumed_kW": power_consumed_kw,
                # "PowerRegenerated_kW": power_regenerated_kw,
                "Torque_Front": torque_actual_front,
                "Torque_Rear": torque_actual_rear,
                "ElectricPower_Front": electric_power_front,
                "ElectricPower_Rear": electric_power_rear
            })

            df_all.append(df)

        df_full = pd.concat(df_all, ignore_index=True)
        corr_matrix = df_full.corr()

        # Plot heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
        plt.title("Pearson Correlation (Train Data): Factors Impacting Energy Consumption")
        plt.tight_layout()

        if self.plot_save:
            plt.savefig("figures/pearson_correlation_train.jpg", dpi=300)
            print("Saved Pearson correlation heatmap as figures/pearson_correlation_train.jpg")
        else:
            plt.show()

        plt.close()

    

    def data_preprocessing(self):
        """
        Prepare the data: Extract relevant features and target variable.
        Splits into train (all files except last) and test (last file).
        """
        def extract_features_from_file(tdms_file_path, road_grade):
            self.tdms_file = TdmsFile.read(tdms_file_path)
            self.get_data_from_group_channel()

            speed = self.speed_data_mph[1:]
            tractive_force = self.tractive_force[1:]
            tractive_force_front = self.tractive_force_front[1:]
            tractive_force_rear = self.tractive_force_rear[1:]
            power_kw = self.power_kw[1:]
            regen_flag = self.regen_flag[1:]
            torque_actual_front = self.front_torque_actual[1:]
            torque_actual_rear = self.rear_torque_actual[1:]
            electric_power_front = self.front_electric_power[1:]
            electric_power_rear = self.rear_electric_power[1:]

            # Handle grade
            if isinstance(road_grade, str) and road_grade == "Dynamic":
                grade_data = self.group_data["Dyno_Data_Drivetrace_Grade"][:]
                grade = grade_data[1:]
            else:
                grade = np.full_like(speed, float(road_grade), dtype=float)

            # Assemble features
            # X = np.column_stack((speed, tractive_force, grade, regen_flag, torque_actual_rear, electric_power_rear))
            X = np.column_stack((speed, tractive_force, grade, electric_power_rear))
            y = power_kw

            return X, y


        data_directory = self.get_data_directory()

        # Split file lists
        train_files = self.road_grade_test_file_list[:-1]
        test_files = [self.road_grade_test_file_list[-1]]
        train_grades = self.road_grade_list[:-1]
        test_grades = [self.road_grade_list[-1]]

        # Collect train data
        X_train_list = []
        y_train_list = []
        for file, grade in zip(train_files, train_grades):
            tdms_file_path = os.path.join(data_directory, file)
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            print(f"Processing TRAIN file: {file} | Road Grade: {grade}")
            X_part, y_part = extract_features_from_file(tdms_file_path, grade)
            X_train_list.append(X_part)
            y_train_list.append(y_part)

        # Collect test data
        X_test_list = []
        y_test_list = []
        for file, grade in zip(test_files, test_grades):
            tdms_file_path = os.path.join(data_directory, file)
            if not os.path.isfile(tdms_file_path):
                raise FileNotFoundError(f"No such file: {tdms_file_path}")
            print(f"Processing TEST file: {file} | Road Grade: {grade}")
            X_part, y_part = extract_features_from_file(tdms_file_path, grade)
            X_test_list.append(X_part)
            y_test_list.append(y_part)

        # Combine arrays
        X_train = np.vstack(X_train_list)
        y_train = np.hstack(y_train_list)
        X_test = np.vstack(X_test_list)
        y_test = np.hstack(y_test_list)

        return X_train, y_train, X_test, y_test
    
    
    def linear_regression(self, title="Linear Regression Model", fileName="linear_regression_plot"):
        """
        Fit a linear regression model using training data and evaluate on test data.
        """
        # Preprocess the data
        X_train, y_train, X_test, y_test = self.data_preprocessing()

        # Create and train the linear regression model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Make predictions on test data
        y_pred = model.predict(X_test)

        # Calculate Mean Squared Error on test
        mse = mean_squared_error(y_test, y_pred)
        print(f"Linear Regression Test MSE: {mse:.4f}")

        # Print coefficients
        print(f"Intercept (β0): {model.intercept_:.4f}")
        print(f"Coefficients: {model.coef_}")

        # Plot predicted vs actual on test set
        self.plot_actual_vs_predicted(y_test, y_pred, title, fileName)

    def polynomial_regression(self, degree, title="Polynomial Regression Model", fileName="polynomial_regression_plot"):
        """
        Fit a polynomial regression model using training data and evaluate on test data.
        """
        X_train, y_train, X_test, y_test = self.data_preprocessing()

        # Transform features to polynomial features
        poly = PolynomialFeatures(degree)
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)

        # Create and train the model
        model = LinearRegression()  
        model.fit(X_train_poly, y_train)

        # Predict on test data
        y_pred = model.predict(X_test_poly)

        # Calculate MSE on test data
        mse = mean_squared_error(y_test, y_pred)
        print(f"Polynomial Regression (Degree {degree}) Test MSE: {mse:.4f}")

        # Print coefficients
        print(f"Intercept (β0): {model.intercept_:.4f}")
        print(f"Polynomial Coefficients: {model.coef_}")

        # Plot predicted vs actual
        self.plot_actual_vs_predicted(y_test, y_pred, title, fileName)


    def plot_actual_vs_predicted(self, y_actual, y_pred, title, fileName):
        """
        Plots the Actual vs Predicted Energy Consumption.
        """
        plt.figure(figsize=(8, 6))
        plt.scatter(y_actual, y_pred, color='blue', label="Predicted vs Actual")
        plt.plot([min(y_actual), max(y_actual)], [min(y_actual), max(y_actual)], color='red', linestyle='--', label="Ideal Line")
        plt.xlabel("Actual Energy Consumed (kWh)")
        plt.ylabel("Predicted Energy Consumed (kWh)")
        plt.title(title)
        plt.legend()
        plt.grid(True)

        if self.plot_save:
            file_directory = "figures/" + fileName + ".jpg"
            plt.savefig(file_directory, bbox_inches='tight', dpi=300)
            print("Saved plot successfully at:", file_directory)
        else:
            plt.show()

        plt.close()

'''##############################################
                   Unit testing
##############################################'''
if __name__ == "__main__":
    import json
    configFile = open("config-files/configuration.json", 'r')
    config = (json.load(configFile))
    configFile.close()
    energyConsumptionModel = EnergyConsumptionModel(config)
    # energyConsumptionModel.run_pearson_correlation_train_data()
    # energyConsumptionModel.linear_regression(title="Linear Regression Model", fileName="linear_regression_plot")
    energyConsumptionModel.polynomial_regression(degree=2, title="Polynomial Regression Model", fileName="polynomial_regression_plot")