import matplotlib.pyplot as plt
import numpy as np

# Data for the chart
categories = ['UDDS 1', 'UDDS 2', 'Highway', 'US06', 'TOTAL']
sequence_1 = [1000, 1100, 1200, 1300, 7000]  # Example data, replace with actual values
sequence_2 = [900, 1050, 1150, 1250, 6800]   # Example data, replace with actual values
uncert_seq_1 = [1, 1.2, 1.5, 1.8, 18]       # Example percentages, replace with actual values
uncert_seq_2 = [0.8, 1.1, 1.3, 1.6, 16]     # Example percentages, replace with actual values

x = np.arange(len(categories))  # The label locations
width = 0.35  # Width of the bars

fig, ax1 = plt.subplots(figsize=(10, 6))

# Plotting the bar charts
bar1 = ax1.bar(x - width/2, sequence_1, width, label='Energy_62005016', color='gray')
bar2 = ax1.bar(x + width/2, sequence_2, width, label='Energy_62005018', color='orange')

# Create a second y-axis for uncertainty percentages
ax2 = ax1.twinx()
line1, = ax2.plot(x, uncert_seq_1, label='Uncertainty_62005016', color='blue', marker='o', linestyle='-')
line2, = ax2.plot(x, uncert_seq_2, label='Uncertainty_62005018', color='red', marker='s', linestyle='-')

# Add titles and labels
ax1.set_title('DC Discharge Energy Uncertainty by Drive Cycle - MCT 1', fontsize=14)
ax1.set_xlabel('Drive Cycle', fontsize=12)
ax1.set_ylabel('Discharge Energy [Wh]', fontsize=12)
ax2.set_ylabel('Uncertainty [%]', fontsize=12)

# Set x-axis labels
ax1.set_xticks(x)
ax1.set_xticklabels(categories, fontsize=10)

# Create separate legends
handles1, labels1 = ax1.get_legend_handles_labels()  # Bar chart (primary axis)
handles2, labels2 = ax2.get_legend_handles_labels()  # Line chart (secondary axis)

# Primary axis legend (first line)
legend1 = fig.legend(handles1, labels1, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.1))
# Secondary axis legend (second line)
legend2 = fig.legend(handles2, labels2, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.2))

# Adjust spacing manually to leave enough space for both legends
plt.subplots_adjust(bottom=0.3)  # Push the plot upward to make space for legends
plt.savefig("test-plot.jpg")
plt.close()
