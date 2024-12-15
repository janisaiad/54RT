import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Read the CSV file
data = np.genfromtxt('signal_data.csv', delimiter=',', dtype=None, names=True, encoding=None)

# Convert timestamp strings to datetime objects
timestamps = np.array([datetime.fromisoformat(t) for t in data['timestamp']])

# Create subplots for real, imaginary and magnitude components
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

# Plot real component
ax1.plot(timestamps, data['real'], 'b-', label='Real')
ax1.set_ylabel('Real')
ax1.grid(True)
ax1.legend()

# Plot imaginary component  
ax2.plot(timestamps, data['imag'], 'r-', label='Imaginary')
ax2.set_ylabel('Imaginary')
ax2.grid(True)
ax2.legend()

# Plot magnitude
ax3.plot(timestamps, data['magnitude'], 'g-', label='Magnitude')
ax3.set_xlabel('Time')
ax3.set_ylabel('Magnitude')
ax3.grid(True)
ax3.legend()

# Format timestamp labels
plt.gcf().autofmt_xdate()

plt.tight_layout()
plt.show()
