# Defines a function that implement an algorithm for mathing template to a timeseries to detect iGluSNFR responses
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager
import math
from scipy import optimize
from scipy.optimize import minimize
from scipy.signal import butter, lfilter, freqz, detrend
import re
import os

font_path = '/home/anup/.matplotlib/fonts/arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)

def background_subtract(t,f,tstim0,tpre=0):
    # t: time, f: raw fluorescence, tpre: time from start for background substraction
    # print(t,f,tpre)
    f = f + min(f)
    itstim0 = np.where(t>tstim0)[0][0]-1
    itpre = np.where(t>tpre)[0][0]-1
    baseline = np.mean(f[min(itstim0,itpre):max(itpre,itstim0)])
    # print('baseline: ',baseline)
    return((baseline-f)/baseline)

def smooth(y,windowlen=3,window = 'hanning'):
    s = np.concatenate([y[windowlen-1:0:-1],y,y[-2:-windowlen-1:-1]])
    if (window == 'flat'):
        w = np.ones(windowlen,dtype='double')
    else:
        w = eval('np.'+window+'(windowlen)')
        
    yy = np.convolve(w/w.sum(),s,mode='same')[windowlen-1:-windowlen+1]
    return (yy)


def plot_data(t,y,s,nt,ny,ft,fy,dct,dcy,tpeaks,ypeaks,tstims_begin,tstims_end,lags,tsep,ysep,stimfreq,figtitle):
    fh1 = plt.figure(figsize=[12,6])
    ah1 = fh1.add_subplot(111)
    ah1.plot(t,y,color='grey')
    ah1.plot(nt,ny,color='black')
    ah1.plot(ft,fy,color = 'orange')
    ah1.plot(dct,dcy,color='purple')
    ah1.plot(t,s,'red')
    ah1.plot(tpeaks,ypeaks,color='red',marker='o',linestyle = 'None',markersize = 5)
    ah1.plot(tstims_begin + lags,np.zeros(len(lags)),color='green',marker='o',linestyle = 'None',markersize = 5)
    # plot all the individual traces
    fh2 = plt.figure(figsize=[12,6])
    ah2 = fh2.add_subplot(111)
    plotcolors = ["red","grey"] # prestimulus response ios plotted in red
    # --------------------------
    # plot ysep
    for k in np.arange(0,tsep.shape[1]):
        ah2.plot(tsep[:,k],ysep[:,k],color = plotcolors[int(k>0)])
        ah2.plot(tsep[:,0],np.mean(ysep[:,1:],axis=1),color='black')
        # ----------------
    ah1.spines["right"].set_visible(False)
    ah1.spines["top"].set_visible(False)
    ah1.spines["bottom"].set_linewidth(1)
    ah1.spines["left"].set_linewidth(1)
    ah1.set_xlabel('Time (s)',fontproperties=fontprop)
    ah1.set_ylabel(r'$\Delta$F/F',fontproperties=fontprop)
    ah1.tick_params(axis='both',length=6,direction='out',width=1,which='major')
    ah1.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
    ah1.tick_params(axis='both', which='major', labelsize=16)
    ah1.tick_params(axis='both', which='minor', labelsize=12)
    ah1.set_title(figtitle+"_"+str(stimfreq) + 'Hz',fontproperties=fontprop)
    ah1.set_xlim([tstims_begin[0],tstims_end[-1]])
    ah1.set_ylim([min(y),max(y)])
    # --------------
    ah2.spines["right"].set_visible(False)
    ah2.spines["top"].set_visible(False)
    ah2.spines["bottom"].set_linewidth(1)
    ah2.spines["left"].set_linewidth(1)
    ah2.set_xlabel('Time (s)',fontproperties=fontprop)
    ah2.set_ylabel(r'$\Delta$F/F',fontproperties=fontprop)
    ah2.tick_params(axis='both',length=6,direction='out',width=1,which='major')
    ah2.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
    ah2.tick_params(axis='both', which='major', labelsize=16)
    ah2.tick_params(axis='both', which='minor', labelsize=12)
    ah2.set_title(figtitle+"_"+str(stimfreq) + 'Hz',fontproperties=fontprop)
    ah2.set_xlim([np.min(tsep),np.max(tsep)])
    ah2.set_ylim([np.min(ysep),np.max(ysep)])
    return(fh1,ah1,fh2,ah2)


def template_match(df,temp,roilabels=[],tmaxlag = 0.01,figtitle="",figpath=""):
    # template matching algorithm
    # df: DataFrame containing: time,stims & rois (spines, dendrites)
    # temp a DateFrame with 2 columns: "time" and "response"
    # roilabels: a list containing roilabels: ["spine","dendrite"]
    # tmaxlag: maximum lag to search for correlations, typically 10 ms
    # --------------------        
    # find columns that match the rois in roilabels
    roidict = {roi: [column for column in df.columns if roi in column] for roi in roilabels}
    # print("Roi dict: ",roidict)
    t = df["time"].iloc[1:-1].to_numpy()
    t = t - t[0]
    # set stimulus timestamps
    s = df["stims"].iloc[1:-1].to_numpy()
    # get template columns
    tt = temp["time"].to_numpy()
    yy = temp["y"].to_numpy()
    # open pandas dataframe to populate data
    roidf = pd.DataFrame()
    # loop for each ROI type in roidict
    for roitype in list(roidict.keys()):
        rois = roidict[roitype]
        # loop for each ROI within the ROItype
        for iroi in range(0,len(rois)):
            y = df[rois[iroi]].iloc[1:-1].to_numpy()
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
            stimfreq = int(round(1/np.mean(tstims_end[1:-1]-tstims_begin[1:-1])))
            # -------------
            # polynomial fit on smooth data
            model = np.polyfit(t,smooth(y,windowlen=7,window='hanning'),16)
            predicted = np.polyval(model,t)
            y = y - predicted
            y = background_subtract(t,y,tstims[0],tpre)
            # -------------
            # create arrays to hold the new trace obtained through template match
            nt = np.zeros((len(t),1))
            nt[:,0] = t 
            ny = np.zeros((len(t),1))   # portion of y that maximally correlated with the template
            dct = np.zeros((len(t),1))
            dct[:,0] = t
            dcy = np.zeros((len(t),1))  # y deconvolved
            ft = np.zeros((len(t),1))
            ft[:,0] = t
            fy = np.zeros((len(t),1))   # new y from the shifted and scaled template
            tsep = np.zeros((len(tt),len(istims_begin))) # holds individual response traces
            ysep = np.zeros((len(tt),len(istims_begin))) # holds individual response traces
            # holds extracted lag and peak values of the deconvolved trace
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
                    c[j] = np.correlate(ynorm[:,0],yynorm)
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
                yysolve = fy[istims_begin[i]+icmax:istims_begin[i]+icmax+yshift.shape[0],0] + yy[0:yshift.shape[0]]
                yysolve = yysolve.reshape((yysolve.shape[0],1))
                # solve normal equation to estimate beta
                beta  = np.linalg.pinv(yysolve.dot(yysolve.T)).dot(yysolve).T.dot(yshift)
                # print(i,beta)
                id1 = istims_begin[i]+icmax
                id2 = istims_begin[i]+icmax + yy.shape[0]
                fy[istims_begin[i]+icmax:istims_begin[i]+icmax+yy.shape[0],0] = fy[istims_begin[i]+icmax:istims_begin[i]+icmax+ yy.shape[0],0] + (yy * beta)
                dcy[istims_begin[i]+icmax:istims_begin[i]+icmax+yy.shape[0],0] = (yy * beta)
                ny[istims_begin[i]+icmax:istims_begin[i]+icmax+yshift.shape[0],0] = yshift[:,0]
                # ----------------
                # ysep holds values from the start of the response, ie not from the start of the stimulus 
                # tsep[0:yshift.shape[0],i] = tshift[:,0]-tshift[0,0]
                # ysep[0:yshift.shape[0],i] = yshift[:,0]
                # ----------------
                # ysep holds values from the start of the stimulus
                tsep[0:minlen,i] = tres[0:minlen]
                ysep[0:minlen,i] = yres[0:minlen]
                # ----------------
                ypeaks[i] = beta * np.max(yy)
                tpeaks[i] = tstims_begin[i] + tt[np.where(yysolve>=max(yysolve))[0][0] + icmax]
                lags[i] = tt[icmax]
                # create a record to store  peaks for each stimulus,trials and roi types                
                record = {"filename":figtitle,"roitype": roitype,"iroi":iroi,"istim":i,"stimfreq":stimfreq,"delay":lags[i],"peak":ypeaks[i]}
                roidf = roidf.append(record,ignore_index = True) # append a record per stim,trial,roitype
                roidf = roidf.astype({"iroi":'int',"istim":"int"}) # conver indices to in datatype

            # --------------------
            # crop the empty rows
            if (len(np.where(ysep[1:,0] == 0)[0])>0):
                ilast0row = np.where(ysep[1:,0] == 0)[0][0]
                tsep = tsep[0:ilast0row,:]
                ysep = ysep[0:ilast0row,:]
            # ---------------------
            # plot the entire trace
            # fh1,ah1,fh2,ah2 = plot_data(t,y,s,nt,ny,ft,fy,dct,dcy,tpeaks,ypeaks,tstims_begin,tstims_end,lags,tsep,ysep,stimfreq,figtitle)
            # --------------
            # save figure 1 if savepath is not empty and exists
            # if(not os.path.exists(figpath)):
            #     print("Path to save the figure not found")
            #     plt.show()

            # ah1figname = figpath + "/" + figtitle + "_" + str(stimfreq) + "Hz" + ".png"
            # print("Saving the figure 1:\t" + ah1figname)
            # fh1.savefig(ah1figname)
            # ah2figname = figpath + "/" + figtitle + "_" + str(stimfreq) + "Hz" + "_traces" + ".png"
            # print("Saving the figure 2:\t" + ah2figname)
            # fh2.savefig(ah2figname)
            # ----------
            # plt.show()
            # input('press a key')
            # plt.close()
    return (roidf)
