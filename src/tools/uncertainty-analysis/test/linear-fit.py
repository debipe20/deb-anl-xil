import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Function to plot linear fit
def plot_linear_fit(x, y, ax, xlabel, ylabel, title):
    # Reshape data for LinearRegression
    x = np.array(x).reshape(-1, 1)
    y = np.array(y)
    
    # Fit linear regression
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
    
    # Move legend outside the plot
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fontsize=9, framealpha=0.7)
    
    # Add annotations
    ax.set_title(f"{title}\nRMS: {rms:.5f}")
    ax.text(0.05, 0.95, f"Slope = {slope:.4f}\nIntercept = {intercept:.2f}\n$R^2$ = {r2:.2f}",
            transform=ax.transAxes, verticalalignment='top', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

# Example data
np.random.seed(42)
x1 = np.linspace(360, 380, 100)
y1 = 1.01 * x1 - 5 + np.random.normal(0, 0.5, size=len(x1))

x2 = np.linspace(-50, 100, 100)
y2 = 1.007 * x2 - 0.01 + np.random.normal(0, 1, size=len(x2))

x3 = np.linspace(-20, 20, 100)
y3 = 1.01 * x3 + np.random.normal(0, 0.3, size=len(x3))

x4 = np.linspace(0, 1, 100)
y4 = 1.006 * x4 + np.random.normal(0, 0.02, size=len(x4))

# Plotting
fig, axs = plt.subplots(2, 2, figsize=(12, 8))

plot_linear_fit(x1, y1, axs[0, 0], "CAN voltage [V]", "Hioki Voltage [V]", "Voltage Comparison")
plot_linear_fit(x2, y2, axs[0, 1], "CAN current [A]", "Hioki Current [A]", "Current Comparison")
plot_linear_fit(x3, y3, axs[1, 0], "CAN I*V [kW]", "Hioki Active Power [kW]", "Power Comparison")
plot_linear_fit(x4, y4, axs[1, 1], "CAN Integrated Power [kWh]", "Hioki Integrated Power [kWh]", "Integrated Power Comparison")

plt.tight_layout(rect=[0, 0, 1, 0.95])  # Add space for legends outside the subplots
plt.savefig("linear-fit-plot.jpg")
plt.close()
