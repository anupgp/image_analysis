import matplotlib.pyplot as plt
import scipy.special as sps
import numpy as np

# shape, scale = 2., 2.  # mean=4, std=2*sqrt(2)
shape, scale = 6.8, 0.15  # shape(gamma) = 6.8, scale(lambda) = 0.15
s = np.random.gamma(shape, scale, 10000)
count, bins, ignored = plt.hist(s, 20, density=True)
y = (bins**(shape-1))*(np.exp(-bins/scale) /(sps.gamma(shape)*(scale**shape)))
print(bins)
plt.plot(bins, y, linewidth=2, color='r')
plt.show()
