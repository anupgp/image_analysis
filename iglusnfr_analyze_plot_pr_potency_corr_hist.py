import numpy as np
import pandas as pd
import math
import seaborn as sns
import re
import os
from scipy import stats as scipystats
from matplotlib import pyplot as plt
import matplotlib
import matplotlib.font_manager as font_manager
from matplotlib.lines import Line2D

sns.set()
sns.set_style("white")
sns.set_style("ticks")
# ---------------
colors_rgb = np.array([
    [0,0,255],
    [0,255,0],
    [255,0,0],
    [0,255,255],
    [255,0,255],
    [255,255,0],
    [0,0,128],
    [0,128,0],
    [128,0,0],
    [0,128,128],
    [128,0,128],
    [128,128,0],
    [0,0,64],
    [0,64,0],
    [64,0,0],
    [0,64,64]
])/255
colors_hex = [matplotlib.colors.to_hex(colorval) for colorval in colors_rgb]

def format_plot(fh,ah,xlab="",ylab="",title=""):
    font_path = '/home/anup/.matplotlib/fonts/arial.ttf'
    fontprop = font_manager.FontProperties(fname=font_path,size=18)
    ah.spines["right"].set_visible(False)
    ah.spines["top"].set_visible(False)
    ah.spines["bottom"].set_linewidth(1)
    ah.spines["left"].set_linewidth(1)
    ah.set_title(title,fontproperties=fontprop)
    ah.set_xlabel(xlab,fontproperties=fontprop)
    ah.set_ylabel(ylab,fontproperties=fontprop)
    ah.tick_params(axis='both',length=6,direction='out',width=1,which='major')
    ah.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
    ah.tick_params(axis='both', which='major', labelsize=16)
    ah.tick_params(axis='both', which='minor', labelsize=12)
    return(fh,ah)

# Set some pandas options
pd.set_option('display.notebook_repr_html', False)
# pd.set_option('display.max_columns', 10)
# pd.set_option('display.max_rows', 10)

# open the csv file containing the main dataframe
datapath = '/home/anup/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/' 
fname = 'iglusnfr_ca1_data_success_noise_mean_plus_4noise_std.csv'
df = pd.read_csv(os.path.join(datapath,fname))
print(df.columns)
print(df.head)
# ----------------
## Calculate potency and release probability for each roid+stimfreq+stimid
def calculate_potency_pr(x):
    ntrials = len(x["success"])
    nsuccess = len(x[x["success"] == True])
    nfailure = len(x[x["success"] == False])
    pr = [nsuccess/ntrials]
    potency = [np.mean((x[x["success"] == True]["peak"]))]
    # potency = list(map(lambda x: x if x == x else 0,potency)) # potency = 0 if pr = 0
    x["pr"] = np.repeat(pr,len(x))
    x["potency"] = np.repeat(potency,len(x))
    # print(x[["roiname","stimfreq","stimid","trialid","peak","threshold","success","pr","potency"]])
    # input()
    return(x)
# }
# ---------------------
df = df.groupby(["roiname","stimfreq","stimid"],group_keys=False).apply(calculate_potency_pr)
df.reset_index(inplace=True,drop=True)
print(df.head())
print(df.columns)
# ----------------
# Calculate average potency and release probability for each stimfreq+stimid
def nanmean(x):
    return(x.mean(axis=0,skipna=True,numeric_only=True))
def nanvar(x):
    return(x.var(axis=0,skipna=True,numeric_only=True))
def nanstd(x):
    return(x.std(axis=0,skipna=True,numeric_only=True))
def nansem(x):
    return(x.std(axis=0,skipna=True,numeric_only=True)/np.sqrt(x.count(axis=0,numeric_only=True)))
def nancount(x):
    return(x.count(axis=0,numeric_only=True))
def compute_simplestats(x):
    df=pd.DataFrame({"nanmean":nanmean(x),
                     "mean":x.mean(),
                     "nanvar":nanvar(x),
                     "var":x.var(),
                     "nanstd":nanstd(x),
                     "std":x.std(),
                     "nansem":nansem(x),
                     "nancount":nancount(x),
                     "count":x.count()})
    return(df)
# -----------------
df["delay"] = df["delay"]*1000
df["stimfreq"] = df["stimfreq"].astype('int')
roitype = "spine"
parameter = "potency"
stimfreq = 20
roinames = df[(df["trialid"]==1) & (df["stimid"] > 0) & (df["stimid"] < 9)& (df["roitype"] == roitype)]["roiname"].unique()
roinames = [roiname[5:] for roiname in roinames]
prpt = df[(df["trialid"]==1) & (df["stimfreq"] == stimfreq) & (df["stimid"] > 0) & (df["stimid"] < 9)& (df["roitype"] == roitype)][[parameter,"stimid","roiname","stimfreq","roitype","ntrials"]]
corrdf = df[(df["trialid"]==1) & (df["stimfreq"] == stimfreq) & (df["stimid"] > 0) & (df["stimid"] < 9)& (df["roitype"] == roitype)][["pr","potency","stimid","roiname",
                                                                                                                                      "stimfreq","roitype","ntrials"]]
prpt.reset_index(inplace=True,drop=True)
statmean = "nanmean"
staterror= "nansem"
plotdf = prpt[(prpt["roitype"] == "spine") & (prpt["stimfreq"] == stimfreq)]
statdf = prpt.groupby(["stimfreq","stimid","roitype"])[[parameter]].apply(compute_simplestats)
print("corrdf\n",pd.pivot_table(corrdf,values=["pr","potency"],index=["roiname","stimfreq"],columns=["stimid"]))
# print("plotdf\n",plotdf)
# print("statsdf\n",statdf)
print("{} : {}".format(roitype,roinames))
# --------------
# note: MultiIndex index and columns
# plot individual data points using sns
fh1 = plt.figure(figsize=(6,4))
ah1 = fh1.add_subplot(111)
zorder = 0
for name,group in plotdf.groupby(["roiname"]):
    icolor = [j for j in np.arange(0,len(roinames)) if name[5:] == roinames[j]][0]
    ah1.plot(group["stimid"],group[parameter],color = colors_rgb[icolor,:],label=roinames[icolor],marker='o',linewidth=2,markersize=5,markerfacecolor=colors_rgb[icolor,:],zorder=zorder)
    zorder = zorder + 1
    print(name,icolor,roinames[icolor])
# }
ah1.plot(statdf.index.get_level_values("stimid"),statdf[statmean],color="k",linewidth=3,markersize=5,markerfacecolor='k',zorder=zorder+1)
ah1.vlines(statdf.index.get_level_values("stimid"),statdf[statmean]+statdf[staterror],statdf[statmean]-statdf[staterror],linewidth=3,color='k',zorder=zorder+2)
# -------------------
fh1,ah1 = format_plot(fh1,ah1,"Stimulus number","Potency of release","".join((str(stimfreq),"Hz train")))
fh1.tight_layout()
fh1.savefig(os.path.join(datapath,"test.png"),transparent=True,dpi=300)
# ----------------
# perform paired t-test
for i in np.arange(2,9):
    g1 = prpt[(prpt["stimid"]==1)][parameter].to_numpy()
    gi = prpt[(prpt["stimid"]==i)][parameter].to_numpy()
    pval = scipystats.ttest_rel(g1,gi,nan_policy='omit')[1]
    print("Paired T-test between stimulus 1 & stimulus {} for {} at {} Hz stimulation train: pvalue = {} ".format(i,parameter,stimfreq,pval)) 
# ---------------
fh2 = plt.figure(figsize=(4,4))
ah2 = fh2.add_subplot(111)
for name,group in corrdf[corrdf["stimid"] == 1].groupby(["roiname"]):
    icolor = [j for j in np.arange(0,len(roinames)) if name[5:] == roinames[j]][0]
    ah2.plot(group["pr"],group["potency"],color = colors_rgb[icolor,:],marker='o',markersize=10,markerfacecolor=colors_rgb[icolor,:])
# }
ah2.plot(corrdf[corrdf["stimid"]==1]["pr"],corrdf[corrdf["stimid"]==1]["potency"],linestyle="-",linewidth=2,color="black",marker=None)

for name,group in corrdf[corrdf["stimid"] == 2].groupby(["roiname"]):
    icolor = [j for j in np.arange(0,len(roinames)) if name[5:] == roinames[j]][0]
    ah2.plot(group["pr"],group["potency"],color = colors_rgb[icolor,:],marker='*',markersize=10,markerfacecolor=colors_rgb[icolor,:])
# }
ah2.plot(corrdf[corrdf["stimid"]==2]["pr"],corrdf[corrdf["stimid"]==2]["potency"],linestyle="-",linewidth=2,color="grey",marker=None)
ah2.set_xlim([-0.1,1.1])
ah2.set_ylim([-0.1,1.1])

fh2,ah2 = format_plot(fh2,ah2,"Probability of release","Potency of release","".join((str(stimfreq),"Hz train")))
legend_elements = [Line2D([0],[0],marker='o',color="black",label="Stim 1",markersize=10),
                   Line2D([0],[0],marker="*",color="grey",label="Stim2",markersize=10)]
ah2.legend(handles=legend_elements)
fh2.tight_layout()
fh2.savefig(os.path.join(datapath,"test2.png"),transparent=True,dpi=300)
# ---------------
# plot histograms of noise & response (stimid:1 to 8) peaks
hdf = df[(df["roitype"] == roitype)][["peak","stimid","roiname","stimfreq","roitype","ntrials","threshold","noise_std"]].reset_index()
edges = np.arange(-0.3,1,0.02)
histdf = hdf.groupby(["roiname","stimfreq","stimid"]).apply(lambda x: pd.DataFrame({"edges":edges[:-1],"hist":np.histogram(x["peak"],edges,density=True)[0],"std":x["noise_std"].mean(),"threshold":x["threshold"].mean(),"avg":x["peak"].mean() }))
histdf.reset_index(inplace=True)
stathistdf = histdf.groupby(["edges","stimid"]).apply(lambda x: pd.DataFrame({"avg": [np.mean(x["hist"])],
                                                                            "std": [np.std(x["hist"])],"sem": [np.std(x["hist"])/np.sqrt(len(x))]}))
stathistdf.reset_index(inplace=True)
fh3 = plt.figure(figsize=(6,4))
ah3 = fh3.add_subplot(111)
# ---------------------------------
# average across all rois
edges = stathistdf[(stathistdf["stimid"]==0)]["edges"].to_numpy()
hist0 = stathistdf[(stathistdf["stimid"]==0)]["avg"]
hist1 = stathistdf[(stathistdf["stimid"]>0) & (stathistdf["stimid"]<9)].groupby(["edges"]).mean()["avg"]
noise_avg = histdf[(histdf["stimid"]==0)]["avg"].mean()
noise_std = histdf[(histdf["stimid"]==0)]["std"].mean()
threshold = histdf[(histdf["stimid"]==0)]["threshold"].mean()
res_mean = histdf[(histdf["stimid"]>0) & (histdf["stimid"]<9)]["avg"].mean()
# ----------------------------------
# plot per roi
# edges = histdf[(histdf["roiname"]==histdf["roiname"].unique()[0])].groupby(["edges"])["edges"].mean()
# hist0 = histdf[(histdf["roiname"]==histdf["roiname"].unique()[0]) & (histdf["stimid"]==0)].groupby(["edges"])["hist"].mean()
# hist1 = histdf[(histdf["roiname"]==histdf["roiname"].unique()[0]) & (histdf["stimid"]>0) & (histdf["stimid"]<9)].groupby(["edges"])["hist"].mean()
# noise_avg = histdf[(histdf["roiname"]==histdf["roiname"].unique()[0]) & (histdf["stimid"]==0)]["avg"].mean()
# noise_std = histdf[(histdf["roiname"]==histdf["roiname"].unique()[0]) & (histdf["stimid"]==0)]["std"].mean()
# res_mean = histdf[(histdf["roiname"]==histdf["roiname"].unique()[0]) & (histdf["stimid"]>0) & (histdf["stimid"]<9)]["avg"].mean()
# threshold = histdf[(histdf["roiname"]==histdf["roiname"].unique()[0])]["threshold"].mean()
# ----------------------------------
ah3.bar(edges,hist0,width=0.02)
ah3.bar(edges,hist1,width=0.02,alpha=0.5)
ah3.vlines(noise_avg,0,5,color="black",linewidth=2,label = "Noise mean")
ah3.vlines(noise_std,0,5,color="blue",linewidth=2,label="Noise std. dev")
ah3.vlines(threshold,0,5,color="red",linewidth=2,label = "Threshold")
ah3.vlines(res_mean,0,5,color="grey",linewidth=2,label = "Response mean")
# plot errorbars noise
sem_pos_noise = hist0.to_numpy() +  stathistdf[(stathistdf["stimid"]==0)].groupby(["edges"]).mean()["sem"].to_numpy()
sem_neg_noise = hist0.to_numpy() - stathistdf[(stathistdf["stimid"]==0)].groupby(["edges"]).mean()["sem"].to_numpy()
sem_pos_res = hist1.to_numpy() + stathistdf[(stathistdf["stimid"]>0) & (stathistdf["stimid"]<9)].groupby(["edges"]).apply(lambda x: np.std(x)/np.sqrt(len(x)))["avg"].to_numpy()
sem_neg_res = hist1.to_numpy() - stathistdf[(stathistdf["stimid"]>0) & (stathistdf["stimid"]<9)].groupby(["edges"]).apply(lambda x: np.std(x)/np.sqrt(len(x)))["avg"].to_numpy()
print(sem_neg_res,sem_pos_res,len(sem_pos_res))      
for i in np.arange(0,len(edges)):
    ah3.plot([edges[i],edges[i]],[sem_pos_noise[i],sem_neg_noise[i]],linewidth=2,color="grey")
    ah3.plot([edges[i],edges[i]],[sem_pos_res[i],sem_neg_res[i]],linewidth=2,color="grey")
# ah3.vlines(noise_avg+noise_std*4,0,5,color="orange",linewidth=2)
# histdf[histdf["stimid"]==0][["peak"]].hist(edges,ax=ah3)
# histdf[histdf["stimid"]==1][["peak"]].hist(alpha=0.5,ax=ah3)
# print(histdf[histdf["stimid"]==0]["peak"].mean())
# fh3,ah3 = format_plot(fh3,ah3,"Amplitude ($\Delta$F/F)","Density",histdf["roiname"].unique()[0][5:])
fh3,ah3 = format_plot(fh3,ah3,"Amplitude ($\Delta$F/F)","Density","")
ah3.legend()
fh3.tight_layout()
fh3.savefig(os.path.join(datapath,"fig3.png"),transparent=True,dpi=300)
# --------------
plt.show()


