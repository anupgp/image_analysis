import numpy as np
import re
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import font_manager
import matplotlib

datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis_old/' 

fname_success_avg = 'iglusnfr_ca1_success_avg.csv'
fname_tsuccess = 'iglusnfr_ca1_tsuccess.csv'
fname_ysuccess = 'iglusnfr_ca1_ysuccess.csv'

# fname_test = '2hz/20190418_S1E1_Image18Block1.csv' # nice events
fname_test = '8hz/20190418_S1E3_Image48Block1.csv' # ok events
# fname_test = '20hz/20190418_S1E3_Image57Block1.csv' # ok events
# fname_test = '20hz/20190418_S1E3_Image53Block1.csv' # ok events
# fname_test = '2hz/20190418_S1E4_Image61Block1.csv' # mostly no events

# load data
success_avg = np.loadtxt(datapath+fname_success_avg,delimiter=',')
# tsuccess = np.loadtxt(datapath+fname_tsuccess,delimiter=',')
# ysuccess = np.loadtxt(datapath+fname_ysuccess,delimiter=',')
test = pd.read_csv(datapath+fname_test,header=0,sep=',')
print(test.columns)


avgt = success_avg[2:-1,0]
avgy = success_avg[2:-1,1]
avgy[np.where(avgy<0)[0]] = 0 
avgt = avgt - avgt[0]
print(avgt.shape,avgy.shape)
avgy = np.pad(avgy,((0,10),),'constant',constant_values=((0,0.0),))
avgtisi = np.diff(avgt[:]).mean()
avgtpads = [avgtisi * i for i in np.arange(len(avgt),len(avgt)+10)]
avgt = np.concatenate((avgt,avgtpads),axis=0) 
print(avgt,avgy)
t = test['time_trial1roi2'].iloc[1:].to_numpy()
y = test['dendrite_trial1roi2'].iloc[1:].to_numpy()
s = test['stim_trial1roi2'].iloc[1:].to_numpy()
t = t - t[0]
# find index of the first nan value
itnans = np.where(np.isnan(t))[0]
# find index of the first zero value
itzeros = np.where(t[1:]==0)[0]
if (len(itnans) > len(itzeros)):
    t = t[0:itnans[0]]
elif (len(itnans) < len(itzeros)):
    t = t[0:itzeros[0]]

tt = t
yy = np.zeros(t.shape)

istims = np.where(s>0)[0]       # find the index of all stimulus locations
nstim = len(istims)             # number of stimulii
tstim0 = t[istims[0]]           # time of first stimulus
tlag = 0.010                    #  max response delay
# average inter-stimulus interval round to 3 decimal places
# isi = np.round(np.mean(np.diff(t[np.where(s>0)[0]])),3)
tdur = 0.1
# crop avgy to tdur
ilastavgt = np.where(avgt>=tdur)[0][0]
avgt = avgt[0:ilastavgt]
avgy = avgy[0:ilastavgt]
avgy = avgy.reshape((len(avgy),1))
avgt = avgt.reshape((len(avgt),1))

# print(avgt.shape,avgy.shape)
# print(t.shape,y.shape)
# input('key')

tprestim = tstim0-(tdur+tlag)
iprestim = np.where(t>=tprestim)[0][0]
istims = np.concatenate(([iprestim],istims))
tstims_begin = t[istims]
istims_begin = [np.where(t>=tstim)[0][0] for tstim in tstims_begin]
tstims_end = np.concatenate((tstims_begin[1:],[tstims_begin[-1] + tdur]),axis=0)
istims_end = [np.where(t>=tstim)[0][0] for tstim in tstims_end]

print(tstims_begin,istims_begin,tstims_begin.shape)
print(tstims_end,istims_end,tstims_end.shape)
print(tstims_end-tstims_begin)

matplotlib.use("TkAgg")
plt.ion()
font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)
# plot the full trial with stimulus marker
fh1 = plt.figure()
ah1 = fh1.add_subplot(111)
ph1, = ah1.plot(t,y)
ph2, = ah1.plot(t,s)
input('press a key')
# plot the average trace without shift and amplification
ph3, = ah1.plot(0,0,color='black')
# plot the average trace with shift and amplification
ph4, = ah1.plot(0,0,color='red')

# # ph3, = ah1.plot(0,0,'o',color='red',markersize=5)
# ph3, = ah1.plot(avgt,avgy,color='k',linewidth=2)

for i in np.arange(0,len(istims_begin)):
    t1  = t[istims_begin[i]:istims_end[i]]
    t10 = t1[0]
    t1 = t1 - t1[0]
    y1  = y[istims_begin[i]:istims_end[i]]
    # find last search time delay
    itlaglast = np.where(t1>=tlag)[0][0]
    avgy2 = (avgy - np.mean(avgy))/np.std(avgy)
    arraylen = min(len(y1),len(avgy2))
    avgy2 = avgy2[0:arraylen-itlaglast]
    c = np.zeros(itlaglast)
    print(itlaglast,len(avgy2),len(y1))
    
    for j in np.arange(0,itlaglast):
        y2 = y1[j:(arraylen-itlaglast+j)]
        y3 = (y2 - np.mean(y2))/np.std(y2)
        y3  = y3.reshape((len(y3),1))
        print(j,avgy2.shape,y2.shape)
        c[j] = np.correlate(y3[:,0],avgy2[:,0])

    icmax = np.where(c>=np.max(c))[0][0]
    # shift y1 to max correlation
    y2 = y1[icmax:arraylen - itlaglast + icmax]
    y2 = y2.reshape((len(y2),1))
    t2 = t1[icmax:arraylen - itlaglast + icmax]
    t2 = t2.reshape((len(y2),1))
    # solve normal equation to estimate beta
    avgy3 = yy[istims_begin[i]+icmax:istims_begin[i]+icmax+y2.shape[0]] + avgy[0:y2.shape[0],0]
    avgy3 = avgy3.reshape((avgy3.shape[0],1))
    print(icmax,y2.shape,avgy3.shape,avgy.shape)
    beta  = np.linalg.pinv(avgy3.dot(avgy3.T)).dot(avgy3).T.dot(y2)
    print(beta)
    yy[istims_begin[i]+icmax:istims_begin[i]+icmax+avgy.shape[0]] = yy[istims_begin[i]+icmax:istims_begin[i]+icmax+avgy.shape[0]] + (avgy[:,0] * beta)
    # ----------------
    ph3.set_xdata(avgt+t[istims_begin[i]])
    ph3.set_ydata(avgy)
    ph4.set_xdata(tt)
    ph4.set_ydata(yy)
    fh1.canvas.draw()
    fh1.canvas.flush_events()
    ah1.set_xlim([min(t),max(t)])
    ah1.set_ylim([min(y),max(y)])
    input('press a key')



