import matplotlib.pyplot as plt
import numpy as np
x_data = [324, 531, 806, 1152, 1576, 2081, 2672, 3285, 3979, 4736]
y_data = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
x =  np.array(x_data)
y = np.array(y_data)
model = np.poly1d(np.polyfit(x, y, 1))
ynew = model(x)
plt.plot(x, y, 'o', x, ynew, '-' , )
plt.ylabel( str(model).strip())
plt.show()