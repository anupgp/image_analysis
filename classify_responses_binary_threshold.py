import numpy as np
import pandas as pd
import math
import re

from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager

font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)

# Set some pandas options
pd.set_option('display.notebook_repr_html', False)
# pd.set_option('display.max_columns', 10)
# pd.set_option('display.max_rows', 10)

def beautify_plot(fh,ah,xlab="",ylab=""):
    ah.spines["right"].set_visible(False)
    ah.spines["top"].set_visible(False)
    ah.spines["bottom"].set_linewidth(1)
    ah.spines["left"].set_linewidth(1)
    ah.set_xlabel('Time (s)',FontProperties=fontprop)
    ah.set_ylabel(r'$\Delta$F/F',fontproperties=fontprop)
    ah.tick_params(axis='both',length=6,direction='out',width=1,which='major')
    ah.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
    ah.tick_params(axis='both', which='major', labelsize=16)
    ah.tick_params(axis='both', which='minor', labelsize=12)
    return(fh,ah)
    
def extract_info_from_filename(fname):
    print(fname)
    fname = fname
    roitype = re.search("(spine|dendrite)",fname)[0]
    roicount = re.search("[(spine)|(dendrite)](\d+)",fname)[1]
    roiid = re.search("^[0-9]{8,8}_.[^Image.*]+",fname)[0][0:-1]+"_"+roitype+roicount
    roicount = int(roicount)
    fileid = re.search("^.*?(?=(_delay))",fname)[0]
    trialid = int(re.search("trial(\d+)",fname)[1])
    stimfreq = int(re.search("_(\d+)Hz",fname)[1])
    stimid = int(re.search("trace(\d+)",fname)[1])
    delay =  float(re.search("delay(\d+)",fname)[1])/1000000
    peak = float(re.search("(?<=peak).*",fname)[0])/1000000
    record = {"fname0ext":fname,"fileid":fileid,"roiid":roiid,"roicount":roicount,"roitype":roitype,"trialid":trialid,"stimfreq":stimfreq,"stimid":stimid,"delay":delay,"peak":peak}
    return(record)

    
# open the csv file containing the list of roi timeseries data
datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/' 
fname = 'iglusnfr_response_traces_all.txt'
batchfname = datapath + fname
# ----------------
with open(batchfname,'r') as csvfile:
    batchcsv = pd.read_csv(csvfile)
df = pd.DataFrame()
traces = {}
print("Total number of files:\t",len(batchcsv))

for i in np.arange(0,len(batchcsv)):
# for i in np.arange(0,1000): 
    fname = batchcsv['filename'][i] # complete filename with path
    fpath = re.search('^.+/+',fname)[0][0:-1] # path to filename
    fname0ext = re.search('[^/]+.csv$',fname)[0][0:-4] # filename without extension
    fileid = re.search("^.*?(?=(_delay))",fname0ext)[0]
    record = extract_info_from_filename(fname0ext)
    df = df.append(record,ignore_index = True)
    dat = np.loadtxt(fname,delimiter=",")
    traces[fileid] = dat
# ------------------
omitsrois2hz = ['20190418_S1E3_spine1']
omitsrois8hz = [""]
omitsrois20hz = ['20190801_S1C1S2_spine1','20190726_S1C1S1_spine1','20190725_S1C1S1_spine1']
omitsrois = omitsrois2hz + omitsrois8hz + omitsrois20hz
# print(df["roiid"].unique())
# df = df[~df["roiid"].isin(omitsrois)]
# print(df["roiid"].unique())
# input("press a key")
# ------------------
# convert some columns from float to int dtype
intcolumns = ["roicount","stimfreq","stimid","trialid"]
for column in intcolumns:
     df[column] = df[column].astype(int)
# -----------------
# print(traces)
# -----------------
# get all roiids
roiids = df["roiid"].unique()
print(roiids)

srois = [roi for roi in roiids if re.search(".*spine.*",roi)]
drois = [roi for roi in roiids if re.search(".*dendrite.*",roi)]
# change index
# df.index = df["roiid"]
# find trial number per roiid,stimfreq & stimid
df["numtrials"] = df.groupby(["roiid","stimfreq","stimid"])["trialid"].transform("count")
df["itrial"] = df.groupby(["roiid","stimfreq","stimid"]).apply(
    lambda x: pd.DataFrame({"itrial": np.arange(1,x["numtrials"].max()+1)},
                           index=x.index))
# find mean and standard deviation of noise peak across trials for each roiid
df[["noise_avg","noise_std","threshold"]] = df.groupby(["roiid"]).apply(
    # df[["noise_avg","noise_std","threshold"]] = df.groupby(["roiid","stimfreq"]).apply(
# df[["noise_avg","noise_std","threshold","threshold2","threshold3"]] = df.groupby(["roiid"]).apply(
    lambda x: pd.DataFrame({"noise_avg" : x[x["stimid"]==0]["peak"].mean(),
                            "noise_std" : x[x["stimid"]==0]["peak"].std(),
                            "threshold" : x[x["stimid"]==0]["peak"].mean() + (2*x[x["stimid"]==0]["peak"].std())
                            # "threshold2": x[x["stimid"]==0]["peak"].mean() + (6*x[x["stimid"]==0]["peak"].std()),
                            # "threshold3": x[x["stimid"]==0]["peak"].mean() + (7*x[x["stimid"]==0]["peak"].std())
                            },index = x.index))
# classify each response as success/failure if amplitude is above or equal /below noise_avg + (2*noise_std)
# failure of release if the observed peak fluorescence is less than twice the standard deviation of the optical noise
df[["success"]] = df.groupby(["roiid","stimfreq","itrial","stimid"]).apply(
    lambda x: pd.DataFrame({"success" : x["peak"] >= x["threshold"]
                            },index = x.index)) 
# calssify all the traces to either success/failure
# fileids_success = df[(df["success"] == True) & (df["roitype"] == "spine") & (df["stimid"] >  0) ]["fileid"]
fileids_success = df[(~df["roiid"].isin(omitsrois)) & (df["success"] == True) & (df["roitype"] == "spine") & (df["stimid"] >  0) ]["fileid"]
# fileids_nearsuccess = df[(~df["roiid"].isin(omitsrois)) & (df["nearsuccess"] == True) & (df["roitype"] == "spine") & (df["stimid"] >  0) ]["fileid"]
fileids_failure = df[(~df["roiid"].isin(omitsrois)) & (df["success"] == False) & (df["roitype"] == "spine") & (df["stimid"] > 0) ]["fileid"]
fileids_noise = df[(~df["roiid"].isin(omitsrois)) & (df["roitype"] == "spine") & (df["stimid"] == 0) ]["fileid"]
# convert pandas series to list
fileids_success = [item for item in fileids_success]
# fileids_nearsuccess = [item for item in fileids_nearsuccess]
fileids_failure = [item for item in fileids_failure]
fileids_noise = [item for item in fileids_noise]

ttrace = np.pad(traces[fileids_success[0]][0:80,0],(0,20),mode='reflect',reflect_type='odd').reshape(100,1)
ysuccess = np.zeros((100,len(fileids_success)))
yfailure = np.zeros((100,len(fileids_failure)))
ynoise = np.zeros((100,len(fileids_noise)))

# copy success and failure traces
# remove the offset 
for item in enumerate(fileids_success):
    ysuccess[0:traces[item[1]].shape[0],item[0]] = traces[item[1]][:,1]-traces[item[1]][:,1][0]
    
for item in enumerate(fileids_failure):
    yfailure[0:traces[item[1]].shape[0],item[0]] = traces[item[1]][:,1]-traces[item[1]][:,1][0]

for item in enumerate(fileids_noise):
    ynoise[0:traces[item[1]].shape[0],item[0]] = traces[item[1]][:,1]-traces[item[1]][:,1][0]
    
# compute averaged success and failure trace
yavgsuccess = np.mean(ysuccess,axis = 1)
yavgfailure = np.mean(yfailure,axis = 1)
yavgnoise = np.mean(ynoise,axis = 1)

# --------------------
fh1 = plt.figure()
ah1 = fh1.add_subplot(111)
ah1tx = ah1.twinx()             # plot with two y-axis scales
for i in np.arange(0,ysuccess.shape[1]):
    ah1.plot(ttrace,ysuccess[:,i],color="grey")
ah1.plot(ttrace,yavgsuccess,color="k")
ah1tx.plot(ttrace,yavgsuccess,color="r")
fh1,ah1 = beautify_plot(fh1,ah1)
fh1,ah1tx = beautify_plot(fh1,ah1tx)
ah1.set_title('Success: '+str(len(fileids_success))+'/'+str(len(fileids_success)+len(fileids_failure)),fontproperties=fontprop)
# ah1.set_title('Far success (6>=thres<=7) / success: '+str(len(fileids_nearsuccess))+'/'+str(len(fileids_success)),fontproperties=fontprop)
ah1.set_ylim([-2,3])
yticks = np.array([-2,-1,0,1,2,3])
ah1.set_yticks(yticks)
ah1.set_xlim([0,0.1])
xticks = np.array([0,0.02,0.04,0.06,0.08,0.1])
ah1.set_xticks(xticks)
ah1tx.set_ylabel(ah1.get_ylabel(),color='r')
ah1tx.tick_params('y',colors='r')
ah1tx.spines["right"].set_visible(True)
ah1tx.spines["right"].set_color('r')
ah1tx.spines["right"].set_linewidth(2)
# ah1tx.set_ylim([-0.1,0.4])
# ytickst = np.array([-0.1,0,0.1,0.2,0.3,0.4])
ah1tx.set_ylim([-0.1,0.5])
ytickst = np.array([-0.1,0.0,0.1,0.2,0.3,0.4,0.5])
# ah1tx.set_ylim([-0.05,0.05])
# ytickst = np.array([-0.05,-0.025,0,0.025,0.05])
ah1tx.set_yticks(ytickst)
fh1.tight_layout()
# --------------------
fh2 = plt.figure()
ah2 = fh2.add_subplot(111)
ah2tx = ah2.twinx()             # plot with two y-axis scales
for i in np.arange(0,yfailure.shape[1]):
    ah2.plot(ttrace,yfailure[:,i],color = "grey")
ah2.plot(ttrace,yavgfailure,color="k")
ah2tx.plot(ttrace,yavgfailure,color="r")
ah2tx.plot(ttrace,yavgfailure-yavgnoise,color="blue")
fh2,ah2 = beautify_plot(fh2,ah2)
fh1,ah2tx = beautify_plot(fh1,ah2tx)
ah2.set_title('Failure: '+str(len(fileids_failure))+'/'+str(len(fileids_success)+len(fileids_failure)),fontproperties=fontprop)
ah2.set_ylim([-2,3])
yticks = np.array([-2,-1,0,1,2,3])
ah2.set_yticks(yticks)
ah2.set_xlim([0,0.1])
xticks = np.array([0,0.02,0.04,0.06,0.08,0.1])
ah2.set_xticks(xticks)
ah2tx.set_ylabel(ah1.get_ylabel(),color='r')
ah2tx.tick_params('y',colors='r')
ah2tx.spines["right"].set_visible(True)
ah2tx.spines["right"].set_color('r')
ah2tx.spines["right"].set_linewidth(2)
ah2tx.set_ylim([-0.1,0.1])
ytickst = np.array([-0.1,-0.05,0,0.05,0.1])
ah2tx.set_yticks(ytickst)
fh2.tight_layout()
# --------------------
fh3 = plt.figure()
ah3 = fh3.add_subplot(111)
ah3tx = ah3.twinx()             # plot with two y-axis scales
for i in np.arange(0,ynoise.shape[1]):
    ah3.plot(ttrace,ynoise[:,i],color="grey")
ah3.plot(ttrace,yavgnoise,color="k")
ah3tx.plot(ttrace,yavgnoise,color="r")
fh3,ah3 = beautify_plot(fh3,ah3)
fh3,ah3tx = beautify_plot(fh3,ah3tx)
ah3.set_title('Noise: '+str(len(fileids_noise))+' traces',fontproperties=fontprop)
ah3.set_ylim([-2,3])
yticks = np.array([-2,-1,0,1,2,3])
ah3.set_yticks(yticks)
ah3.set_xlim([0,0.1])
xticks = np.array([0,0.02,0.04,0.06,0.08,0.1])
ah3.set_xticks(xticks)
ah3tx.set_ylabel(ah1.get_ylabel(),color='r')
ah3tx.tick_params('y',colors='r')
ah3tx.spines["right"].set_visible(True)
ah3tx.spines["right"].set_color('r')
ah3tx.spines["right"].set_linewidth(2)
ah3tx.set_ylim([-0.1,0.1])
ytickst = np.array([-0.1,-0.05,0,0.05,0.1])
ah3tx.set_yticks(ytickst)
fh3.tight_layout()

# # # -----------------

success_figname = datapath + 'iglusnfr_ca1_farsuccess_allresponses_spine' + '.png'
# failure_figname = datapath + 'iglusnfr_ca1_failure_allresponses_spine' + '.png'
# noise_figname = datapath + 'iglusnfr_ca1_noise_allresponses_spine' + '.png'
# fh1.savefig(success_figname)
# fh2.savefig(failure_figname)
# fh3.savefig(noise_figname)
plt.show()
# # -----------------
df.sort_values(by=["roiid","stimfreq","stimid","itrial"],ascending=True,inplace=True)
df.to_csv(datapath+"iglusnfr_ca1_main_dataframe_noise_per_roi2.csv",index=True)
# # print(df)
# # print(df["roiid"])
input('key')
