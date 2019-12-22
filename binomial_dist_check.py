import numpy as np
from matplotlib import pyplot as plt
import math

savepath= '/Users/macbookair/goofy/data/beiquelab/presentations/labmeet20191202'
figname = 'binomila_poisson_comparison_p5.png'


n = 100                         # number of attempts in a single experiment
p = 0.5                         # probability of each outcome
ntrials = 500                  # number of experimental trials
k = 5                           # number of positive outcomes
m = n*p
s = np.random.binomial(n,p,ntrials)
counts = []
counts = np.array(([sum(s==i) for i in np.arange(0,n+1)]))/ntrials
# check Poisson distribution
poissond = np.array([np.exp(-m)*pow(m,i)/math.factorial(i) for i in np.arange(0,n+1)])
print(counts)
plt.rc('xtick',labelsize=18)
plt.rc('ytick',labelsize=18)
fh = plt.figure()
ah = plt.subplot(111)
ah.bar(np.arange(0,n+1),counts)
ah.plot(np.arange(0,n+1),poissond,color='red')
ah.text(60,0.05,"n = "+str(n)+'\n'+'p = '+str(p)+'\n'+'m = '+str(m)+'\n\n'+'Trials = '+str(ntrials),fontsize=14)
plt.ylabel("Probability density",fontsize=20)
plt.xlabel("No of positive outcomes",fontsize=20)
# plt.rc('axes',labelsize=18)
# plt.rc('xtick',labelsize=18)
# plt.rc('ytick',labelsize=18)
plt.tight_layout()
plt.savefig(savepath+'/'+figname)

# plt.show()



