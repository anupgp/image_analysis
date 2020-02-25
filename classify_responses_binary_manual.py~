import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager
import matplotlib
matplotlib.use("TkAgg")

import pandas as pd
import re

font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)

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

# --------------------------

def roidata_trace_extract(expfile,roitype,itrial,iroi,istim,min_isi):
    postfix = 'trial'+ str(itrial) + 'roi' + str(iroi)
    tcolname = 'time_' + postfix
    ycolname = roitype + '_' + postfix
    scolname = 'stim_' + postfix
    t = expfile[tcolname].to_numpy()
    y = expfile[ycolname].to_numpy()
    s = expfile[scolname].to_numpy()
    # find the number of stims
    istims = np.where(s==1)[0]
    nstims = len(istims)
    isi = np.mean(np.diff(t[istims]))
    istimstart = istims[istim-1]
    istimstop = np.where(t>=(t[istims[istim-1]])+min_isi)[0][0]
    # find the begin and end indices for the desired stim number
    tt = t[istimstart:istimstop]-t[istimstart]
    yy = y[istimstart:istimstop]
    return(isi,tt,yy)
    
        

datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis_old/' 
batchfname = datapath + 'iglusnfr_roi_timeseries_filenames_allV4.csv'
# open the csv file containing the list of roi timeseries data
with open(batchfname,'r') as csvfile:
    batchcsv = pd.read_csv(csvfile)

tsuccess=np.zeros((220,400))
ysuccess=np.zeros((220,400))
tfailure=np.zeros((220,400))
yfailure=np.zeros((220,400))

itrace = 0
isuccess = 0
ifailure = 0
plt.ion()
fh1 = plt.figure()
ah1 = fh1.add_subplot(111)
ph1, = ah1.plot(0,0)

fh2 = plt.figure()
ah2 = fh2.add_subplot(111)
ph2, = ah2.plot(0,0)

fh3 = plt.figure()
ah3 = fh3.add_subplot(111)
ph3, = ah3.plot(0,0)

# open pandas dataframe to populate data
successdf = pd.DataFrame()
failuredf = pd.DataFrame()
xlims = [0,0.1]
ylims = [0,1]

for i in range(0,len(batchcsv)):
# for i in range(0,20):
    expfname = batchcsv['filename'][i] # complete filename with path
    exppath = re.search('^.+/+',expfname)[0] # path to filename
    expfname2 = re.search('[^/]+.csv$',expfname)[0][0:-4] # filename without extension
    expdate = re.search('[0-9]{8,8}?',expfname2)[0]
    if (expdate is None):
        expdate = ''
        print('Warning expdate not found!')           
    print('opening roi timeseries file: ',expfname)
    # open one roi timeseries file 
    with open(expfname,'r') as csv_expfile:
        expfile = pd.read_csv(csv_expfile)
        
    expfileinfo = get_ntrialsrois(expfile)
    roitype = ["spine"]
    istim = 1
    min_isi = 0.1
    for itrial,iroi in expfileinfo['i'+roitype[0]+'s']:
        isi,t,y = roidata_trace_extract(expfile,roitype[0],itrial,iroi,istim,min_isi)
        if ((isi>min_isi) and (len(t)>0)):
            print(isi)
            print(t.shape)
            print(y.shape)
            ph1.set_xdata(t)
            ph1.set_ydata(y)
            fh1.canvas.draw()
            fh1.canvas.flush_events()
            ah1.set_xlim([min(t),max(t)])
            ah1.set_ylim([min(y),max(y)])
            success = input("Is success? y/n: ")
            if(success == 'y' or success == 'Y'):
                print('Success: ',isuccess + 1)
                tsuccess[0:t.shape[0],isuccess] = t
                ysuccess[0:y.shape[0],isuccess] = y
                ah2.plot(t,y)
                xlims[0] = min(t) if xlims[0]>min(t) else xlims[0]
                xlims[1] = max(t) if xlims[1]<max(t) else xlims[1]
                ylims[0] = min(y) if ylims[0]>min(y) else ylims[0]
                ylims[1] = max(y) if ylims[1]<max(y) else ylims[1]
                ah2.set_xlim(xlims)
                ah2.set_ylim(ylims)
                # fh2.canvas.draw()
                # fh2.canvas.flush_events()
                # ah2.set_xlim([min(t),max(t)])
                # ah2.set_ylim([min(y),max(y)])
                isuccess = isuccess + 1
            elif (success == 'x'):
                break
            else:
                print('Failure: ',ifailure + 1)
                tfailure[0:t.shape[0],ifailure] = t
                yfailure[0:t.shape[0],ifailure] = y
                ah3.plot(t,y)
                xlims[0] = min(t) if xlims[0]>min(t) else xlims[0]
                xlims[1] = max(t) if xlims[1]<max(t) else xlims[1]
                ylims[0] = min(y) if ylims[0]>min(y) else ylims[0]
                ylims[1] = max(y) if ylims[1]<max(y) else ylims[1]
                ah3.set_xlim(xlims)
                ah3.set_ylim(ylims)
                # fh3.canvas.draw()
                # fh3.canvas.flush_events()
                # ah3.set_xlim([min(t),max(t)])
                # ah3.set_ylim([min(y),max(y)])
                ifailure= ifailure + 1


# crop empty columns
tsuccess = tsuccess[:,0:isuccess]
ysuccess = ysuccess[:,0:isuccess]
fname_tsuccess = "iglusnfr_ca1_tsuccess.csv"
fname_ysuccess = "iglusnfr_ca1_ysuccess.csv"
np.savetxt(datapath+fname_tsuccess,tsuccess,delimiter=',')
np.savetxt(datapath+fname_ysuccess,ysuccess,delimiter=',')

tfailure = tfailure[:,0:ifailure]
yfailure = yfailure[:,0:ifailure]
fname_tfailure = "iglusnfr_ca1_tfailure.csv"
fname_yfailure = "iglusnfr_ca1_yfailure.csv"
np.savetxt(datapath+fname_tfailure,tfailure,delimiter=',')
np.savetxt(datapath+fname_yfailure,yfailure,delimiter=',')
