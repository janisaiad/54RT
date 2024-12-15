import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Load the signal data from the specified file
npy_files = glob.glob(os.path.join('data/signals', '*.npy'))
signal_data = np.load(npy_files[0])  # Load the first (and only) .npy file

# Create a figure and axis
plt.figure(figsize=(12, 6))

# Create time axis based on signal length
time = np.arange(len(signal_data))

# Plot the signal
plt.plot(time, signal_data, 'b-', label='Signal')

# Customize the plot
plt.title('Signal Plot')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()

# Display the plot
plt.show()
