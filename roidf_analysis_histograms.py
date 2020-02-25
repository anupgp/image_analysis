import numpy as np
import pandas as pd
import math
import seaborn as sns
import re

from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

sns.set()
sns.set_style("white")
sns.set_style("ticks")
font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)
# -----------------
def beautify_plot(fh,ah,xlab="",ylab=""):
    ah.spines["right"].set_visible(False)
    ah.spines["top"].set_visible(False)
    ah.spines["bottom"].set_linewidth(1)
    ah.spines["left"].set_linewidth(1)
    ah.set_xlabel(r'$\Delta$F/F',fontproperties=fontprop)
    ah.set_ylabel('Probability density',FontProperties=fontprop)

    ah.tick_params(axis='both',length=6,direction='out',width=1,which='major')
    ah.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
    ah.tick_params(axis='both', which='major', labelsize=16)
    ah.tick_params(axis='both', which='minor', labelsize=12)
    return(fh,ah)

# ----------------------
# open the csv file containing the main dataframe
datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/' 
fname = 'iglusnfr_ca1_main_dataframe_noise_per_roi2.csv'
with open(datapath+fname,'r') as csvfile:
    df = pd.read_csv(csvfile)

roiids = df["roiid"].unique()
srois = [roi for roi in roiids if re.search(".*spine.*",roi)]
drois = [roi for roi in roiids if re.search(".*dendrite.*",roi)]
print(srois,drois)

# ---------------
# omitrois2hz = ['20190418_S1E3_spine1','20190417_S2C1_spine1']
omitrois2hz = ['20190418_S1E3_spine1']
omitrois8hz = [""]
omitrois20hz = ['20190801_S1C1S2_spine1','20190726_S1C1S1_spine1','20190725_S1C1S1_spine1']
# ---------------
# remove cells separately for each stimulation regime
# if stimfreq==2:  omitrois = omitrois2hz
# if stimfreq==8:  omitrois = omitrois8hz
# if stimfreq==20:  omitrois = omitrois20hz
# ---------------
# remove cells in all stimulation regime

omitrois = list(set(omitrois2hz+omitrois8hz+omitrois20hz))
srois = df[~df.roiid.isin(omitrois) & (df.roitype=="spine")].roiid.unique()
print(srois)
nedges = 51
edges = np.zeros((nedges,len(srois)+1))
noisehist = np.zeros((nedges-1,len(srois)+1))
responsehist = np.zeros((nedges-1,len(srois)+1))
noiseavgs = np.zeros(len(srois)+1)
noisestds = np.zeros(len(srois)+1)
thresholds = np.zeros(len(srois)+1)
noisepeaksall = []
responsepeaksall = []
# ---------------
for (i,sroi) in enumerate(srois):
    noisepeaks = df[(df["roiid"]==sroi) & (df["stimid"] == 0)]["peak"].to_numpy()
    noisepeaksall.append(noisepeaks)
    responsepeaks = df[(df["roiid"]==sroi) & (df["stimid"] > 0)]["peak"].to_numpy()
    responsepeaksall.append(responsepeaks)
    noiseavgs[i] = df[(df["roiid"]==sroi) & (df["stimid"] == 0)]["noise_avg"].unique()
    noisestds[i] = df[(df["roiid"]==sroi) & (df["stimid"] == 0)]["noise_std"].unique()
    thresholds[i] = df[(df["roiid"]==sroi) & (df["stimid"] == 0)]["threshold"].unique()
    peaks = np.concatenate((noisepeaks,responsepeaks))
    minpeak = np.min(peaks)
    maxpeak = np.max(peaks)
    edges[:,i] = np.arange(minpeak,maxpeak,(maxpeak-minpeak)/nedges)[0:nedges]
    noisehist[:,i] = np.histogram(noisepeaks,edges[:,i],density = True)[0]
    responsehist[:,i] = np.histogram(responsepeaks,edges[:,i],density = True)[0]
# ------------
# compute the histogram for all noise and responses put together
noisepeaksall.append(np.concatenate(noisepeaksall,axis=0))
responsepeaksall.append(np.concatenate(responsepeaksall,axis=0))
allpeaks = np.zeros((0))
minpeak = np.min(np.concatenate([noisepeaksall[i+1]]+[responsepeaksall[i+1]]))
maxpeak = np.max(np.concatenate([noisepeaksall[i+1]]+[responsepeaksall[i+1]]))
edges[:,i+1] = np.arange(minpeak,maxpeak,(maxpeak-minpeak)/nedges)[0:nedges]
noisehist[:,i+1] = np.histogram(noisepeaksall[i+1],edges[:,i+1],density = True)[0]
responsehist[:,i+1] = np.histogram(responsepeaksall[i+1],edges[:,i+1],density = True)[0]
noiseavgs[i+1] = np.mean(noisepeaksall[i+1])
noisestds[i+1] = np.std(noisepeaksall[i+1])
thresholds[i+1] = noiseavgs[i+1]+(2*noisestds[i+1])

# plot histogram of noise,success and failures for each spine

for i in np.arange(0,noisehist.shape[1]):
    fh1 = plt.figure(figsize=(10,10))
    ah1 = fh1.add_subplot(111)
    fh1,ah1 = beautify_plot(fh1,ah1)
    ph1 = ah1.bar(edges[:,i][0:-1],noisehist[:,i],width = np.mean(np.diff(edges[:,i])),alpha = 1,color="red")
    ph2 = ah1.bar(edges[:,i][0:-1],responsehist[:,i],width = np.mean(np.diff(edges[:,i])),alpha = 0.5,color="blue")
    yaxismax = np.max(np.array([np.max(noisehist[:,i]),np.max(responsehist[:,i])]))
    ph3, = ah1.plot([noiseavgs[i],noiseavgs[i]],[0,yaxismax],linewidth=2,color="black")
    ph4, = ah1.plot([thresholds[i],thresholds[i]],[0,yaxismax],linewidth=2,color="green")
    boxes=[]
    rect = Rectangle((noiseavgs[i]-(2*noisestds[i]),0),4*noisestds[i],yaxismax)
    boxes.append(rect)
    pc = PatchCollection(boxes,facecolor='purple',alpha = 0.1,edgecolor = 'None')
    ah1.add_collection(pc)
    if (i < len(srois)):
        ah1.set_title(srois[i],fontproperties=fontprop)
        print("ROI: ",i," ",srois[i])
    else:
        ah1.set_title("Data from all spines",fontproperties=fontprop)
        
    print("Edges: ",edges[:,i])
    print("Noise hist: ",noisehist[:,i])
    print("len edges:",len(edges))
    print("len noisehist",len(noisehist))
    print("Edge at peak noisehist: ",edges[np.where(noisehist[:,i]>=np.max(noisehist[:,i]))[0][0]])
    print("Noise peaks: ",noisepeaksall[i])
    print("Noise peaks mean: ",np.mean(np.array(noisepeaksall[i])))
    print("Noise peaks std: ",np.std(np.array(noisepeaksall[i])))
    print("Noise peaks max: ",np.max(np.array(noisepeaksall[i])))
    print("Noise peaks median: ",np.median(np.array(noisepeaksall[i])))
    print("Noise mean from df: ",noiseavgs[i])
    print("Noise std from df: ",noisestds[i])
    print("Threshold: ",thresholds[i])
    box = ah1.get_position()
    # Put a legend to the right of the current axis
    labels = ['Noise','Response','Mean','Threshold']
    ah1.legend([ph1,ph2,ph3,ph4],labels,loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.show()
    # input('key')
