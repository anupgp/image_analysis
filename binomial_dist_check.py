import numpy as np
from matplotlib import pyplot as plt

n = 10                          # number of attempts in a single experiment
p = 0.5                         # probability of each outcome
ntrials = 10000                  # number of experimental trials
k = 5                           # number of positive outcomes
s = np.random.binomial(n,p,ntrials)
counts = []
counts = np.array(([sum(s==i) for i in np.arange(0,n+1)]))/ntrials
print(counts)
fh = plt.figure()
ax = plt.subplot(111)
ax.plot(np.arange(0,n+1),counts)
plt.show()



