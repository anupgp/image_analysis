import pandas  as pd
import numpy as np
import os
import re
from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager

font_path = '/home/anup/.matplotlib/fonts/arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)

def beautify_plot(fh,ah,xlabel="",ylabel=""):
    ah.spines["right"].set_visible(False)
    ah.spines["top"].set_visible(False)
    ah.spines["bottom"].set_linewidth(1)
    ah.spines["left"].set_linewidth(1)
    ah.set_xlabel(xlabel,fontproperties=fontprop)
    ah.set_ylabel(ylabel,fontproperties=fontprop)
    ah.tick_params(axis='both',length=6,direction='out',width=1,which='major')
    ah.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
    ah.tick_params(axis='both', which='major', labelsize=16)
    ah.tick_params(axis='both', which='minor', labelsize=12)
    return(fh,ah)

# open the dataframe with preclassified success and failures
datapath = '/home/anup/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/' 
fname_tarces = 'iglusnfr_response_traces_all.txt'
fname_df = "iglusnfr_ca1_data_success_noise_mean_plus_4noise_std.csv"
# ----------------
df = pd.read_csv(os.path.join(datapath,fname_df))
print(df.columns)
traces = {}
for i in np.arange(0,len(df)):
    fname = df.loc[i,"fname"]
    fname_trace = "".join((fname,".csv"))
    expdate = str(df.loc[i,"expdate"])
    folder = df.loc[i,"folder"]
    path_trace = os.path.join(datapath,"_".join((expdate,folder)))
    dat = np.loadtxt(os.path.join(path_trace,fname_trace),delimiter=",")
    traces[fname] = dat
# }
print(df.head())
# get all roiids
roitype = "spine"
roinames = df[df["roitype"] == roitype]["roiname"].unique()
print(roinames)
# calssify all the traces to either success/failure
# fnames_success = df[(df["success"] == True) & (df["roitype"] == "spine") & (df["stimid"] >  0) ]["fname"]
fnames_success = df[(df["success"] == True) & (df["roitype"] == roitype) & (df["stimid"] >  0) & (df["stimid"] <  9) & (df["stimfreq"] <  10)]["fname"].to_list()
fnames_failure = df[(df["success"] == False) & (df["roitype"] == roitype) & (df["stimid"] > 0) & (df["stimid"] <  9) & (df["stimfreq"] <  10)]["fname"].to_list()
fnames_noise = df[(df["roitype"] == roitype) & (df["stimid"] == 0) & (df["stimfreq"] <  10)]["fname"].to_list()
# ------------
ttrace = np.pad(traces[fnames_success[0]][0:80,0],(0,20),mode='reflect',reflect_type='odd').reshape(100,1)*1000
ysuccess = np.zeros((100,len(fnames_success)))
yfailure = np.zeros((100,len(fnames_failure)))
ynoise = np.zeros((100,len(fnames_noise)))
# copy success and failure traces
# remove the offset 
for item in enumerate(fnames_success):
    ysuccess[0:traces[item[1]].shape[0],item[0]] = traces[item[1]][:,1]-traces[item[1]][:,1][0]
# } 
for item in enumerate(fnames_failure):
    yfailure[0:traces[item[1]].shape[0],item[0]] = traces[item[1]][:,1]-traces[item[1]][:,1][0]
# }
for item in enumerate(fnames_noise):
    ynoise[0:traces[item[1]].shape[0],item[0]] = traces[item[1]][:,1]-traces[item[1]][:,1][0]
# }
# compute averaged success and failure trace
yavgsuccess = np.mean(ysuccess,axis = 1)
yavgfailure = np.mean(yfailure,axis = 1)
yavgnoise = np.mean(ynoise,axis = 1)
# --------------------
yall = ysuccess
yavg = yavgsuccess
yname = "".join(("Success traces from ",roitype,"s"," - 2 & 8Hz trains"))
figtitle = "".join((yname,": ",str(len(fnames_success)),'/',str(len(fnames_success)+len(fnames_failure)),"\n"))
# ---------
# yall = yfailure
# yavg = yavgfailure
# yname = "".join(("Failure traces from ",roitype,"s"," - 2 & 8Hz trains"))
# figtitle = "".join((yname,": ",str(len(fnames_failure)),'/',str(len(fnames_success)+len(fnames_failure)),"\n"))
# yscale = (yavgsuccess/np.max(yavgsuccess)) * np.max(yavgfailure)
# ---------
# yall = ynoise
# yavg = yavgnoise
# yname = "".join(("Noise traces from ",roitype,"s"," - 2 & 8Hz trains"))
# figtitle = "".join((yname,": ",str(len(fnames_noise)),'/',str(len(fnames_success)+len(fnames_failure)),"\n"))
# ---------------
iyavgmax = np.argmax(yavg)
tyavgmax= ttrace[iyavgmax]
yyavgmax = yavg[iyavgmax] 
# ---------------
fh1 = plt.figure(figsize=(6,4))
ah1 = fh1.add_subplot(111)
ah1tx = ah1.twinx()             # plot with two y-axis scales
zorder=0
for i in np.arange(0,yall.shape[1]):
    ah1.plot(ttrace,yall[:,i],color="grey",zorder=zorder)
    zorder =zorder + 1
# }
ah1.plot(ttrace,yavg,color="k",zorder=zorder+1)
ah1.hlines(ttrace[0],ttrace[-1],0,linestyle="--",color="black",linewidth=1,zorder=zorder+2)
ah1tx.plot(ttrace,yavg,color="r")
# ah1tx.plot(ttrace,yscale,color="b")
ah1tx.hlines(ttrace[0],ttrace[-1],0,linestyle="--",color="red",linewidth=1,zorder=zorder+3)
ah1tx.vlines(tyavgmax,0,yyavgmax,linestyle="--",color="orange",linewidth=1,zorder=zorder+4)
fh1,ah1 = beautify_plot(fh1,ah1,"Time (ms)",r'$\Delta$F/F')
fh1,ah1tx = beautify_plot(fh1,ah1tx)
ah1.set_title(figtitle,fontproperties=fontprop)
ah1.set_ylim([-2,3])
yticks = np.array([-2,-1,0,1,2,3])
ah1.set_yticks(yticks)
ah1.set_xlim([0,100])
xticks = np.array([0,25,50,75,100])
ah1.set_xticks(xticks)
ah1tx.set_ylabel(ah1.get_ylabel(),color='r')
ah1tx.tick_params('y',colors='r')
ah1tx.spines["right"].set_visible(True)
ah1tx.spines["right"].set_color('r')
ah1tx.spines["right"].set_linewidth(2)
ah1tx.set_ylim([-0.05,0.42])
ytickst = np.array([0,0.1,0.2,0.3,0.4])
ah1tx.set_yticks(ytickst)
fh1.tight_layout()
fh1.savefig(os.path.join(datapath,"traces.png"),transparent=True,dpi=300)
# --------------------
plt.show()
