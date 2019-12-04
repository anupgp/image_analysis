import numpy as np
from matplotlib import pyplot as plt
import math
import scipy.special as sps

def gamma_distribution(shape=2,scale=2,n=1000):
    s = np.random.gamma(shape,scale,n)
    bin_edges = np.arange(0,max(s)*2,0.1)
    hist,bin_edges = np.histogram(s,bins=bin_edges,density = True)
    pdf = bin_edges**(shape-1)*(np.exp(-bin_edges/scale)/(sps.gamma(shape)*scale**shape))
    return(bin_edges,hist,pdf)


def plot_distribution(bin_edges,y,fh,ah,pdf=[]):
    ah.bar(bin_edges[0:-1],y)
    if (len(pdf) == len(bin_edges)):
        print("plotting pdf")
        ah.plot(bin_edges,pdf,color="red",linewidth=2)
    return(fh,ah)

# one vesicle and no change in quantal content
# Bernoulli distribution

n = 1
ntrials = 10000
p = 0.2
s = np.random.binomial(n,p,ntrials)

# counts = np.array(([sum(s==i) for i in np.arange(0,n+1)]))
bin_edges = np.arange(0,n+2,1)
histd_ber,bin_edges_ber = np.histogram(s,bin_edges,density = True)

# plot_distribution(bin_edges,hist,fh,ah)
# plt.show()

# plot gamma distribution
bin_edges_gam,histd_gam,pdf_gam = gamma_distribution(shape=6.8,scale=0.15)
# plot_distribution(bin_edges,hist,fh,ah,pdf)
ber_gam = np.convolve(histd_ber,histd_gam)
fh = plt.figure()
ah = plt.subplot(111)
# ah.plot(ber_gamma)
plot_distribution(bin_edges_gam,histd_gam,fh,ah,pdf_gam)
plt.show()


