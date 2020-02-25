import numpy as np
import pandas as pd
import math
import seaborn as sns
import re
from scipy import stats as scipystats

# ----------------
from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager
sns.set()
sns.set_style("white")
sns.set_style("ticks")
# ---------------
font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)

def format_plot(fh,ah,xlab="",ylab="",title=""):
    ah.spines["right"].set_visible(False)
    ah.spines["top"].set_visible(False)
    ah.spines["bottom"].set_linewidth(1)
    ah.spines["left"].set_linewidth(1)
    ah.set_title(title,FontProperties=fontprop)
    ah.set_xlabel(xlab,FontProperties=fontprop)
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
datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/' 
fname = 'iglusnfr_ca1_main_dataframe.csv'
with open(datapath+fname,'r') as csvfile:
    df = pd.read_csv(csvfile)
# ----------------
## Calculate potency and release probability for each roid+stimfreq+stimid
def calculate_potency_pr(x):
    ntrials = len(x["success"])
    nsuccess = len(x[x["success"] == True]["success"])
    nfailure = len(x[x["success"] == True]["success"])
    pr = np.repeat(nsuccess/ntrials,(len(x)))
    potency = np.repeat(x[x["success"] == True]["peak"].mean(),(len(x)))
    df = pd.DataFrame({"pr" : pr, "potency" : potency},index = x.index)
    return(df)
df[["pr","potency"]] = df.groupby(["roiid","stimfreq","stimid"]).apply(calculate_potency_pr)
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
prpt = df[(df["itrial"]==1) & (df["roitype"] == "spine") & (df["stimfreq"]>=2) & (df["stimfreq"] <=20) &
          (df["stimid"] > 0) & (df["stimid"] <9)][["pr","potency","delay","stimid","roiid","stimfreq","roitype"]]
prpt["delay"] = prpt["delay"]*1000
# create a new MultiIndex for prpt
prptmidx = prpt.set_index(["roiid","stimfreq","stimid"],drop=True)
stimfreq=8
statmean = "nanmean"
staterror = "nansem"
param = "pr"
# filter roiids
roiids = df["roiid"].unique()
srois = [roi for roi in roiids if re.search(".*spine.*",roi)]
print(srois)
drois = [roi for roi in roiids if re.search(".*dendrite.*",roi)]
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
prpt = prpt[~prpt.roiid.isin(omitrois)]
# --------------
# compute stats on prpt
prptstats = prpt.groupby(["stimfreq","stimid","roitype"])["pr","potency","delay"].apply(compute_simplestats) 
# note: MultiIndex index and columns
# plot individual data points using sns
fh = plt.figure(figsize=(10,5))
ah = fh.add_subplot(111)
sns.scatterplot(x="stimid",y=param,hue="roiid",data=prpt[prpt["stimfreq"] == stimfreq],ax=ah,s=60)
stats = prptstats.xs(("spine",stimfreq,param),level=("roitype","stimfreq",None),axis=0)[["nanmean","nansem","nanstd"]]
stats["stimid"] = stats.index
ah.errorbar(stats["stimid"],stats[statmean],stats[staterror])
if param == "pr": ylab = "Release probability"
if param == "potency": ylab = r"Potency ($\Delta$F/F)"
if param == "delay": ylab = r"Delay (ms)"
fh,ah = format_plot(fh,ah,"Stimulus number",ylab,"Stimulation at "+str(stimfreq)+"Hz")
# Shrink current axis by 20%
box = ah.get_position()
# Put a legend to the right of the current axis
ah.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
# plt.tight_layout(pad=0.4, w_pad=0.6, h_pad=1.0)
# tight_layout(fig, rect=[0, 0, 0.5, 1])
# ah.set_position([box.x0, box.y0, box.width * 0.8, box.height])
# ----------------
# perform paired t-test
g1 = prpt[(prpt["stimfreq"]==stimfreq) & (prpt["stimid"]==1)][param].to_numpy()
g2 = prpt[(prpt["stimfreq"]==stimfreq) & (prpt["stimid"]==2)][param].to_numpy()
pval = scipystats.ttest_rel(g1,g2)
print("pvalue: ",pval) 
# ---------------
plt.show()
