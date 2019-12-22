import numpy as np
import re
from matplotlib import pyplot as plt
from matplotlib import font_manager
import matplotlib
matplotlib.use("TkAgg")


font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)

datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis_old/' 
fname_success_avg = 'iglusnfr_ca1_success_avg.csv'
fname_tsuccess = 'iglusnfr_ca1_tsuccess.csv'
fname_ysuccess = 'iglusnfr_ca1_ysuccess.csv'

success_avg = np.loadtxt(datapath+fname_success_avg,delimiter=',')
tsuccess = np.loadtxt(datapath+fname_tsuccess,delimiter=',')
ysuccess = np.loadtxt(datapath+fname_ysuccess,delimiter=',')

x = success_avg[:,1,np.newaxis]

plt.ion()
fh = plt.figure()
ah = fh.add_subplot(111)
ph1, = ah.plot(success_avg[:,0],success_avg[:,1])
ph2, = ah.plot(success_avg[:,0],success_avg[:,1])

xlims = [0,0.1]
ylims = [0,1]
for i in np.arange(0,ysuccess.shape[1]):
    y = ysuccess[:,i,np.newaxis]
    # crop vector to the first 0 or nan
    iy = np.where(y != 0)[0]
    y  = y[iy]
    t = tsuccess[iy,i]
    ph2.set_xdata(t)
    ph2.set_ydata(y)
    xlims[0] = min(t) if xlims[0]>min(t) else xlims[0]
    xlims[1] = max(t) if xlims[1]<max(t) else xlims[1]
    ylims[0] = min(y) if ylims[0]>min(y) else ylims[0]
    ylims[1] = max(y) if ylims[1]<max(y) else ylims[1]
    ah.set_xlim(xlims)
    ah.set_ylim(ylims)
    beta  = np.linalg.pinv(x.dot(x.T)).dot(x).T.dot(y)
    print(beta)
    input('press any key to continue')

