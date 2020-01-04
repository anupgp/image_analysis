import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager
import math
from scipy import optimize
from scipy.optimize import minimize
from scipy.signal import butter, lfilter, freqz, detrend
import re
import copy
import os

font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)

def smooth(y,windowlen=3,window = 'hanning'):
    s = np.concatenate([y[windowlen-1:0:-1],y,y[-2:-windowlen-1:-1]])
    if (window == 'flat'):
        w = np.ones(windowlen,dtype='double')
    else:
        w = eval('np.'+window+'(windowlen)')
        
    yy = np.convolve(w/w.sum(),s,mode='same')[windowlen-1:-windowlen+1]
    return (yy)

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
    # print(ntrialsrois)
    return(ntrialsrois)

def background_subtract(t,f,tstim0,tpre=0):
    # t: time, f: raw fluorescence, tpre: time from start for background substraction
    print(t,f,tpre)
    f = f + min(f)
    itstim0 = np.where(t>tstim0)[0][0]-1
    itpre = np.where(t>tpre)[0][0]-1
    baseline = np.mean(f[min(itstim0,itpre):max(itpre,itstim0)])
    print('baseline: ',baseline)
    return((baseline-f)/baseline)

def template_match(expfile,itrial,iroi,roitype,tt,yy,tmaxlag = 0.01):
    # template matching algorithm
    # tt: t of template
    # yy: y of template
    # tlag: maximum lag to search for correlations, typically 10 ms
    # --------------------
    postfix = 'trial'+ str(itrial) + 'roi' + str(iroi)
    print('itrial: ',itrial,' iroi: ', iroi, ' roitype: ',roitype)
    tcolname = 'time_' + postfix
    ycolname = roitype + '_' + postfix
    scolname = 'stim_' + postfix
    t = expfile[tcolname].iloc[1:-1].to_numpy()
    t = t - t[0]
    y = expfile[ycolname].iloc[1:-1].to_numpy()
    s = expfile[scolname].iloc[1:-1].to_numpy()
    # find index of the first nan value
    itnans = np.where(np.isnan(t))[0]
    # find index of the first zero value
    itzeros = np.where(t[1:]==0)[0]
    if (len(itnans) > len(itzeros)):
        t = t[0:itnans[0]]
    elif (len(itnans) < len(itzeros)):
        t = t[0:itzeros[0]]    
    # ------
    istims = np.where(s>0)[0]
    tstims = t[istims]

    toffset = 0.1
    tpre = tstims[0]-toffset
    itpre = np.where(t>tpre)[0][0]-1
    tpost = tstims[-1]+toffset
    itpost = np.where(t>tpost)[0][0]-1
    tstims_begin = np.concatenate(([tpre],tstims))
    tstims_end = np.concatenate((tstims,[tpost]))
    istims_begin = [np.where(t>tstim)[0][0]-1 for tstim in tstims_begin]
    istims_end = [np.where(t>tstim)[0][0]-1 for tstim in tstims_end]
    # -------------
    # polynomial fit on smooth data
    model = np.polyfit(t,smooth(y,windowlen=7,window='hanning'),16)
    predicted = np.polyval(model,t)
    y = y - predicted
    y = background_subtract(t,y,tstims[0],tpre)
    # -------------
    # create arrays to hold the new trace obtained through template match
    ft = np.zeros((len(t),1))
    ft[:,0] = t
    dct = np.zeros((len(t),1))
    dct[:,0] = t
    fy = np.zeros((len(t),1))
    dcy = np.zeros((len(t),1))
    lags = np.zeros(len(istims_begin))
    tpeaks = np.zeros(len(istims_begin))
    ypeaks = np.zeros(len(istims_begin))
    # ---------------------
    for i in np.arange(0,len(istims_begin)):
        tres  = t[istims_begin[i]:istims_end[i]]
        tres = tres - t[istims_begin[i]]
        yres  = y[istims_begin[i]:istims_end[i]]
        # -----------
        # find last search time delay
        itmaxlag = np.where(tres>tmaxlag)[0][0]-1
        # normalize template so that the correlation is amplitude independent
        yynormlong = (yy - np.mean(yy))/np.std(yy)
        # find the minimum of actual and template trace
        minlen = min(len(yres),len(yynormlong))
        # crop the template to the minimum length
        yynorm = yynormlong[0:minlen-itmaxlag]
        # array to hold the correlations at different time lags
        c = np.zeros(itmaxlag)
        # print(itlaglast,len(avgy2),len(y1))
        # -----------------------------
        for j in np.arange(0,itmaxlag):
            # select a portion of actual trace to correlate with the template trace
            yshift = yres[j:(minlen-itmaxlag+j)]
            # normalize the actual trace
            ynorm = (yshift - np.mean(yres))/np.std(yres)
            # reshape the actual trace to a column vector
            ynorm  = ynorm.reshape((len(ynorm),1))
            # perform correlation between the actual trace and the template
            c[j] = np.correlate(ynorm[:,0],yynorm[:,0])
        # --------------------
        # get the index at which the correlation is maximum
        icmax = np.where(c>=np.max(c))[0][0]
        # shift y1 to max correlation
        yshift = yres[icmax:minlen - itmaxlag + icmax]
        # reshape actual trace to a column vector
        yshift = yshift.reshape((len(yshift),1))
        # crop the time of actual trace for the max correlation lag
        tshift = t[icmax:minlen - itmaxlag + icmax]
        # rehape time of actual trace to a column vector
        tshift = tshift.reshape((len(yshift),1))
        # create a new template trace by adding the original template and portion of the actual trace 
        yysolve = fy[istims_begin[i]+icmax:istims_begin[i]+icmax+yshift.shape[0],0] + yy[0:yshift.shape[0],0]
        yysolve = yysolve.reshape((yysolve.shape[0],1))
        # solve normal equation to estimate beta
        beta  = np.linalg.pinv(yysolve.dot(yysolve.T)).dot(yysolve).T.dot(yshift)
        print(beta)
        id1 = istims_begin[i]+icmax
        id2 = istims_begin[i]+icmax + yy.shape[0]
        print(yynormlong.shape,fy[istims_begin[i]+icmax:istims_begin[i]+icmax+yy.shape[0],0].shape)
        fy[istims_begin[i]+icmax:istims_begin[i]+icmax+yy.shape[0],0] = fy[istims_begin[i]+icmax:istims_begin[i]+icmax+ yy.shape[0],0] + (yy[:,0] * beta)
        dcy[istims_begin[i]+icmax:istims_begin[i]+icmax+yy.shape[0],0] = (yy[:,0] * beta)
        ypeaks[i] = beta * np.max(yy)
        tpeaks[i] = tstims_begin[i] + tt[np.where(yysolve>=max(yysolve))[0][0] + icmax]
        lags[i] = tstims_begin[i] + tt[icmax]
        
    # --------------------
    fh = plt.figure(figsize=[12,6])
    ah = fh.add_subplot(111)
    ah.plot(t,y)
    ah.plot(ft,fy)
    ah.plot(dct,dcy,color='grey')
    ah.plot(t,s,'red')
    ah.plot(tpeaks,ypeaks,color='black',marker='o',linestyle = 'None',markersize = 5)
    ah.plot(lags,np.zeros(len(lags)),color='red',marker='o',linestyle = 'None',markersize = 5)
    plt.show()
    plt.close()
    # return (ft,fy,lags,betas)

def display_trace(expfile,itrial,iroi,roitype):
    # display each trial
    postfix = 'trial'+ str(itrial) + 'roi' + str(iroi)
    print('itrial: ',itrial,' iroi: ', iroi, ' roitype: ',roitype)
    tcolname = 'time_' + postfix
    ycolname = roitype + '_' + postfix
    scolname = 'stim_' + postfix
    t = expfile[tcolname].iloc[1:-1].to_numpy()
    t = t - t[0]
    y = expfile[ycolname].iloc[1:-1].to_numpy()
    s = expfile[scolname].iloc[1:-1].to_numpy()
    # ------
    istims = np.where(s>0)[0]
    tstims = t[istims]
    nstims = len(istims)
    toffset = 0.1
    tpre = tstims[0]-toffset
    itpre = np.where(t>tpre)[0][0]-1
    tpost = tstims[-1]+toffset
    itpost = np.where(t>tpost)[0][0]-1
    tstimsfirst = np.concatenate(([tpre],tstims))
    tstimslast = np.concatenate((tstims,[tpost]))
    # -------------
    # polynomial fit on smooth data
    model = np.polyfit(t,smooth(y,windowlen=7,window='hanning'),16)
    predicted = np.polyval(model,t)
    y1 = y - predicted
    y2 = background_subtract(t,y1,tstims[0],tpre)
    # -----
    fh = plt.figure(figsize=[12,6])
    ah = fh.add_subplot(111)
    ah.plot(t,y2)
    ah.plot(t,s,'red')
    plt.show()
    input('press any key')
    plt.close()

    # open the csv file containing the list of roi timeseries data
datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/' 
fname = 'iglusnfr_roi_all.csv'
batchfname = datapath + fname
# ------------------
# load the template
fname_success_avg = 'iglusnfr_ca1_success_avg.csv'
success_avg = np.loadtxt(datapath+fname_success_avg,delimiter=',')
tt = success_avg[2:-1,0]
yy = success_avg[2:-1,1]
yy[np.where(yy<0)[0]] = 0 
tt = tt - tt[0]
yy = np.pad(yy,((0,10),),'constant',constant_values=((0,0.0),))
si = np.diff(tt[:]).mean()
ttpads = [si * i for i in np.arange(len(tt),len(tt)+10)]
tt = np.concatenate((tt,ttpads),axis=0)
tdur = 0.1
# crop template to tdur
ittlast = np.where(tt>=tdur)[0][0]
tt = tt[0:ittlast]
yy = yy[0:ittlast]
yy = yy.reshape((len(yy),1))
tt = tt.reshape((len(tt),1))
# ----------------
with open(batchfname,'r') as csvfile:
    batchcsv = pd.read_csv(csvfile)

# open pandas dataframe to populate data
roidf = pd.DataFrame()

for i in range(0,len(batchcsv)):
    expfname = batchcsv['filename'][i] # complete filename with path
    exppath = re.search('^.+/+',expfname)[0] # path to filename
    expfname2 = re.search('[^/]+.csv$',expfname)[0][0:-4] # filename without extension
    # mkdir to place all the figures for that particular file
    # if(not os.path.isdir(exppath+"test20hz/"+expfname2)):
    #    os.mkdir(exppath+"test20hz/"+expfname2)                           
    figsavepath = exppath
    print('opening roi timeseries file: ',expfname)
    # open one roi timeseries file 
    with open(expfname,'r') as csv_expfile:
        expfile = pd.read_csv(csv_expfile)
    expfileinfo = get_ntrialsrois(expfile)
    print(expfileinfo)
    # get date field from file
    expdate = re.search('[0-9]{8,8}?',expfname)[0]
    if (expdate is not None):
        print('expdate: ',expdate[0])
    else:
        print('Warning expdate not found!')
        expdate = ''
    # process spine rois
    roitypes = ["spine","dendrite"]
    for roitype in roitypes:
        for itrial,iroi in expfileinfo['i'+roitype+'s']:
            # display_trace(expfile,itrial,iroi,roitype)
            template_match(expfile,itrial,iroi,roitype,tt,yy,tmaxlag=0.010)
