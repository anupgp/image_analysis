import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import math
from scipy import optimize
from scipy.optimize import minimize


def alphaFunction(t,delay,risetime,peak,decaytime):
    # alpha function for a single stimulus
    # In book: Computational Modeling Methods for Neuroscientists, chapter: Modeling synapses by Arnd Roth and Mark C. W. van Rossum
    tpeak = delay + (((decaytime*risetime)/(decaytime-risetime))*np.log(decaytime/risetime))
    peakNormFact =  1/(-np.exp(-(tpeak-delay)/risetime)+np.exp(-(tpeak-delay)/decaytime))
    h = peak*peakNormFact*(np.exp(-(t-delay)/decaytime)-np.exp(-(t-delay)/risetime))
    h[h<0] = 0
    return(h)

# def alphaFunctionMulti(t,args):
#     nparams = len(args)
#     print(nparams)
#     nstim = int((nparams)/4)
#     h = np.zeros(len(t))
#     for i in np.arange(0,nstim):
#         istart = i*4
#         delay = args[istart]
#         risetime = args[istart+1]
#         peak = args[istart+2]
#         decaytime = args[istart+3]
#         print(delay,risetime,peak,decaytime)
#         tpeak = delay + (((decaytime*risetime)/(decaytime-risetime))*np.log(decaytime/risetime))
#         peakNormFact =  1/(-np.exp(-(tpeak-delay)/risetime)+np.exp(-(tpeak-delay)/decaytime))
#         hnew = peak*peakNormFact*(np.exp(-(t-delay)/decaytime)-np.exp(-(t-delay)/risetime))
#         hnew[hnew<0] = 0
#         h = h + hnew
#     return(h)

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
        # print(delay,risetime,peak,decaytime)
        tpeak = delay + (((decaytime*risetime)/(decaytime-risetime))*np.log(decaytime/risetime))
        peakNormFact =  1/(-np.exp(-(tpeak-delay)/risetime)+np.exp(-(tpeak-delay)/decaytime))
        hnew = peak*peakNormFact*(np.exp(-(t-delay)/decaytime)-np.exp(-(t-delay)/risetime))
        hnew[hnew<0] = 0
        h = h + hnew
    return(h)

# def alphaFunctionMulti(params):
#     nparams = len(params)
#     nstim = int((nparams-1)/4)
#     t = params[0]               # the first argument is time
#     h = np.zeros(len(t))
#     for i in np.arange(0,nstim):
#         istart = (i*4)+1
#         delay = params[istart]
#         risetime = params[istart+1]
#         peak = params[istart+2]
#         decaytime = params[istart+3]
#         tpeak = delay + (((decaytime*risetime)/(decaytime-risetime))*np.log(decaytime/risetime))
#         peakNormFact =  1/(-np.exp(-(tpeak-delay)/risetime)+np.exp(-(tpeak-delay)/decaytime))
#         hnew = peak*peakNormFact*(np.exp(-(t-delay)/decaytime)-np.exp(-(t-delay)/risetime))
#         hnew[hnew<0] = 0
#         h = h + hnew
#     return(h)
        
# def splitArgs(npulses,isi):
#     def alphaFunctionMulti(t,*params):
#         # parse individual parameters
#         delays = np.zeros(npulses)
#         risetimes = np.zeros(npulses)
#         peaks  = np.zeros(npulses)
#         decaytimes  = np.zeros
#         for i in np.arange(0,npulses):
            
#         return(

roifn = '/Users/macbookair/20190828_s1c1s1_Image72Block1.csv'
# roifn = '/Users/macbookair/20190418_S1E1_Image22Block1.csv'
with open(roifn,'r') as csvfile:
    roicsv = pd.read_csv(csvfile)

fh = plt.figure()
ah = plt.subplot(111)

t = roicsv['time_trial2roi1'].to_numpy()
y = roicsv['spine_trial2roi1'].to_numpy()
s = roicsv['stim_trial2roi1'].to_numpy()
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
mindecaytimes = [0.005]*nstim
# -------
maxstimdelay = 0.01                       # max delay = 10 milliseconds
maxdelays = [(isi*i)+(toffset+maxstimdelay) for i in range(0,nstim)] # max delays for all the stimuli
print(maxdelays)
maxrisetimes = [0.05]*nstim
maxpeaks = [10]*nstim
maxdecaytimes = [0.2]*nstim
minbounds =tuple(np.ndarray.flatten(np.transpose(np.array([mindelays,minrisetimes,minpeaks,mindecaytimes]))))
maxbounds = tuple(np.ndarray.flatten(np.transpose(np.array([maxdelays,maxrisetimes,maxpeaks,maxdecaytimes]))))
print(minbounds,len(minbounds))
print(maxbounds,len(minbounds))
# 
plt.plot(t1,y1,color='black')
plt.plot(t1,s1,color='red')
initialparams = minbounds
# initialparams = [t1,0.1,0.005,0.3,0.1,0.1+0.125,0.005,0.3,0.1,0.1+(0.125*2),0.005,0.3,0.1,0.1+(0.125*3),0.005,0.3,0.1,0.1+(0.125*4),0.005,0.3,0.1,0.1+(0.125*5),0.005,0.3,0.1,0.1+(0.125*6),0.005,0.3,0.1,0.1+(0.125*7),0.005,0.3,0.1]
# initialparams = [0.1,0.005,0.3,0.1,0.1+0.125,0.005,0.3,0.1,0.1+(0.125*2),0.005,0.3,0.1,0.1+(0.125*3),0.005,0.3,0.1,0.1+(0.125*4),0.005,0.3,0.1,0.1+(0.125*5),0.005,0.3,0.1,0.1+(0.125*6),0.005,0.3,0.1,0.1+(0.125*7),0.005,0.3,0.1]

# h1 = alphaFunctionMulti(t1,initialparams)
# params,params_covariance = optimize.curve_fit(alphaFunctionMulti,t1,y1,initialparams)
params,params_covariance = optimize.curve_fit(alphaFunctionMulti,t1,y1,initialparams,bounds=(minbounds,maxbounds))
h1 = alphaFunctionMulti(t1,*params)
plt.plot(t1,h1,color='blue')
# h3 = alphaFunction(t1-t1[0],params[0],params[1],params[2],params[3])
# plt.plot(t1,h3)
plt.show()




