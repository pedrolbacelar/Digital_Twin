import matplotlib.pyplot as plt

# Sample data
x = [1, 2, 3, 4, 5]  # X-axis values
y = [2, 4, 6, 8, 10]  # Y-axis values
error_min = [0.5, 1, 0.8, 0.3, 0.9]  # Minimum error values
error_max = [1, 1.5, 1.2, 0.6, 1.4]  # Maximum error values

# Plotting the range with error bars
plt.errorbar(x, y, yerr=[error_min, error_max], fmt='o', capsize=4)

# Add labels and title
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Plot with Error Range')

# Display the plot
plt.show()
