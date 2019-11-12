import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import math
from scipy import optimize
from scipy.optimize import minimize
import re

def alphaFunction(t,delay,risetime,peak,decaytime):
    # alpha function for a single stimulus
    # In book: Computational Modeling Methods for Neuroscientists, chapter: Modeling synapses by Arnd Roth and Mark C. W. van Rossum
    tpeak = delay + (((decaytime*risetime)/(decaytime-risetime))*np.log(decaytime/risetime))
    peakNormFact =  1/(-np.exp(-(tpeak-delay)/risetime)+np.exp(-(tpeak-delay)/decaytime))
    h = peak*peakNormFact*(np.exp(-(t-delay)/decaytime)-np.exp(-(t-delay)/risetime))
    h[h<0] = 0
    return(h)

def alphaFunctionMulti(t,*args):
    nparams = len(args)
    # print(nparams)
    nstim = int((nparams)/4)
    h = np.zeros(len(t))
    for i in np.arange(0,nstim):
        istart = i*4
        delay = args[istart]
        risetime = args[istart+1]
        peak = args[istart+2]
        decaytime = args[istart+3]
        hnew = alphaFunction(t,delay,risetime,peak,decaytime)
        h = h + hnew
    return(h)

def alphaFunctionMultiExtract(t,params,n=100):
    nparams = len(params)
    nstim = int((nparams)/4)
    if (n > nstim):
        n = nstim
    print(len(t),int(n))
    y = np.zeros((len(t),int(n)),dtype=np.float)
    for i in np.arange(0,nstim):
        istart = i * 4
        istart = i*4
        delay = params[istart]
        risetime = params[istart+1]
        peak = params[istart+2]
        decaytime = params[istart+3]
        y[:,i] = alphaFunction(t,delay,risetime,peak,decaytime)
    return(y)

def get_ntrialsrois(roicsv):
    # Get relevant information from the csv file
    # find the number of ROI types, ROIs and trials in an roicsv file    
    colnames = roicsv.columns
    ispines = np.array(([[int(s) for s in re.findall(r'\d+',colname)] for colname in colnames if 'spine' in colname])) # itrial,iroi
    idendrites = np.array(([[int(s) for s in re.findall(r'\d+',colname)] for colname in colnames if 'dendrite' in colname])) # itrial, iroi
    ntrials1 = 0
    ntrials2 = 0
    nspines = 0
    ndendrites = 0
    if len(ispines)>0:
        ntrials1 = max(ispines[:,0])
        ntrials2 = ntrials1
        nspines = max(ispines[:,1])
        print('ispines',ispines)
    if len(idendrites)>0:
        ntrials2 = max(ispines[:,0])
        ntrial1 = ntrials2
        ndendrites = max(ispines[:,1])
        print('idendrites',idendrites)
    if(ntrials1 != ntrials2):
        print('warning non-equal trials between spine and dendrite rois')
    
    ntrials = ntrials1 if ntrials1 < ntrials2 else ntrials2
    ntrialsrois = {'ntrials':ntrials,'nspines':nspines,'ndendrites':ndendrites,'ispines':ispines,'idendrites':idendrites}
    print(ntrialsrois)
    return(ntrialsrois)

# ------------------------------------------------------------------ 

roifn = '/Volumes/Anup_2TB/iglusnfr_analysis/20hz/20190417_S2C1_Image73Block1.csv'
# roifn = '/Users/macbookair/20190828_s1c1s1_Image72Block1.csv'
# roifn = '/Users/macbookair/20190418_S1E1_Image22Block1.csv'


with open(roifn,'r') as csvfile:
    roicsv = pd.read_csv(csvfile)
    
fileinfo = get_ntrialsrois(roicsv)


t = roicsv['time_trial1roi2'].to_numpy()
y = roicsv['spine_trial1roi2'].to_numpy()
s = roicsv['stim_trial1roi2'].to_numpy()
# values to generate initial parameters for curve fit
nstim = len(np.where(s>0)[0])   # number of stimulii
tstim0 = t[np.where(s>0)[0][0]] # time of first stimulus
tstimn = t[np.where(s>0)[0][nstim-1]] # time of last stimulus
isi = np.round(np.mean(np.diff(t[np.where(s>0)[0]])),3) # average inter-stimulus interval
toffset = 0.1                                           # time offset before and after the stimulus
tstart = tstim0 - 0.1                                     # add offset time before the first stimulus
tstop = tstimn + 0.1                                      # add offser time after the last stimulus
t1 = t[(t>tstart) & (t<tstop)]                            # clip data
y1 = y[(t>tstart) & (t<tstop)]
s1 = s[(t>tstart) & (t<tstop)]
t1 = t1-t1[0]                         # time starts at t = 0
# ------
mindelays = [(isi* i)+toffset for i in range(0,nstim)] # min delays for all the stimulai
print(mindelays)
minrisetimes = [0.001]*nstim
minpeaks = [0.0]*nstim
mindecaytimes = [0.01]*nstim
# -------
maxstimdelay = 0.005                       # max delay = 10 milliseconds
maxdelays = [(isi*i)+(toffset+maxstimdelay) for i in range(0,nstim)] # max delays for all the stimuli
print(maxdelays)
maxrisetimes = [0.06]*nstim
maxpeaks = [10]*nstim
maxdecaytimes = [0.2]*nstim
# -----
minbounds = np.ndarray.flatten(np.transpose(np.array([mindelays,minrisetimes,minpeaks,mindecaytimes])))
maxbounds = np.ndarray.flatten(np.transpose(np.array([maxdelays,maxrisetimes,maxpeaks,maxdecaytimes])))
# initialparams = tuple((maxbounds-minbounds)/10)
minbounds = tuple(minbounds)
maxbounds = tuple(maxbounds)
initialparams = maxbounds
# -------------
params,params_covariance = optimize.curve_fit(alphaFunctionMulti,t1,y1,initialparams)
params,params_covariance = optimize.curve_fit(alphaFunctionMulti,t1,y1,initialparams,bounds=(minbounds,maxbounds))
h = alphaFunctionMulti(t1,*params)
yy = alphaFunctionMultiExtract(t1,params)
# ------------------
# plotting
fh = plt.figure()
ah = plt.subplot(111)
plt.plot(t1,y1,color='black')
plt.plot(t1,s1,color='red')
# -------------
plt.plot(t1,h,color='green',linewidth=2)
colours = ['blue','purple']
selectcolor = 0
for i in range(0,yy.shape[1]):
    plt.plot(t1,yy[:,i],linewidth=2,color=colours[selectcolor])
    selectcolor = not selectcolor
plt.show()
