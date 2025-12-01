import pandas as pd
import matplotlib.pyplot as plt

def accel_decel_analysis():
    # Path to your Excel file (put it in the same folder as this script or use a full path)
    file_path = "output-file/comparison-analysis.xlsx"  # <- change this if your file is elsewhere

    # Read the sheet that contains the data
    # If your sheet has a different name, update sheet_name accordingly
    sheet_name = "Accel_Decel_Time"

    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Ensure numeric types and handle any non‑numeric placeholders like "--"
    df["Acceleration (mps2)"] = pd.to_numeric(df["Acceleration (mps2)"], errors="coerce")
    df["Before"] = pd.to_numeric(df["Before"], errors="coerce")
    df["After"] = pd.to_numeric(df["After"], errors="coerce")

    # Sort by acceleration just to make the plot lines nice and ordered
    df = df.sort_values("Acceleration (mps2)")

    # Create the figure
    plt.figure(figsize=(8, 5))

    # Plot Before and After vs Acceleration
    plt.plot(
        df["Acceleration (mps2)"],
        df["Before"],
        marker="o",
        linestyle="-",
        label="Before",
    )

    plt.plot(
        df["Acceleration (mps2)"],
        df["After"],
        marker="s",
        linestyle="-",
        label="After",
    )

    plt.xlabel("Acceleration (m/s²)")
    plt.ylabel("Accel/Decel Time (s)")  # change label if your y‑axis is something else
    plt.title("Accel/Decel Time Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # plt.show()
    file_directory = "figures/accel_decel_time_comparison.jpg"
    plt.savefig(file_directory, bbox_inches='tight', dpi=300)
    print("saved plot successfully")
    plt.close()

def response_time_analysis():
    # Path to your Excel file (put it in the same folder as this script or use a full path)
    file_path = "output-file/comparison-analysis.xlsx"  # <- change this if your file is elsewhere

    # Read the sheet that contains the data
    # If your sheet has a different name, update sheet_name accordingly
    sheet_name = "Response_Time"

    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Ensure numeric types and handle any non‑numeric placeholders like "--"
    df["Acceleration (mps2)"] = pd.to_numeric(df["Acceleration (mps2)"], errors="coerce")
    df["Before"] = pd.to_numeric(df["Before"], errors="coerce")
    df["After"] = pd.to_numeric(df["After"], errors="coerce")

    # Sort by acceleration just to make the plot lines nice and ordered
    df = df.sort_values("Acceleration (mps2)")

    # Create the figure
    plt.figure(figsize=(8, 5))

    # Plot Before and After vs Acceleration
    plt.plot(
        df["Acceleration (mps2)"],
        df["Before"],
        marker="o",
        linestyle="-",
        label="Before",
    )

    plt.plot(
        df["Acceleration (mps2)"],
        df["After"],
        marker="s",
        linestyle="-",
        label="After",
    )

    plt.xlabel("Acceleration (m/s²)")
    plt.ylabel("Response Time (s)")  # change label if your y‑axis is something else
    plt.title("Response Time Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # plt.show()
    file_directory = "figures/response_time_comparison.jpg"
    plt.savefig(file_directory, bbox_inches='tight', dpi=300)
    print("saved plot successfully")
    plt.close()


def main():
    accel_decel_analysis()
    response_time_analysis()

if __name__ == "__main__":
    main() 