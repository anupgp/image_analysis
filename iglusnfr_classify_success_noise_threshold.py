# accompanying file to plot the responses: plot_responses_already_classified.py
import numpy as np
import pandas as pd
import math
import re
import os

# Set some pandas options
pd.set_option('display.notebook_repr_html', False)
# pd.set_option('display.max_columns', 10)
# pd.set_option('display.max_rows', 10)

    
def extract_info_from_filename(fname):
    print(fname)
    fname = fname
    expdate = re.search("(^[0-9]{8})(?:.*)",fname)[1]
    folderid = re.search("(?:^[0-9]{8}_)([^_]*)",fname)[1]
    imageid = re.search("(?:.*Image_)([\d]+)",fname)[1]
    # blockid =  re.search("(?:.*Block_)([\d]+)",fname)[1]
    roitype = re.search("(spine|dendrite)",fname)[0]
    roicount = re.search("[(spine)|(dendrite)](\d+)",fname)[1]
    roiname = re.search("^[0-9]{8,8}_.[^Image.*]+",fname)[0][0:-1]+"_"+roitype+roicount
    roicount = int(roicount)
    fileid = re.search("^.*?(?=(_delay))",fname)[0]
    scanid = int(re.search("trial(\d+)",fname)[1])
    stimfreq = int(re.search("_(\d+)Hz",fname)[1])
    stimid = int(re.search("trace(\d+)",fname)[1])
    delay =  float(re.search("delay(\d+)",fname)[1])/1000000
    peak = float(re.search("(?<=peak).*",fname)[0])/1000000
    record = {"fname":fname,"expdate":expdate, "folder":folderid, "imageid":imageid,"roiname":roiname,"roicount":roicount,"roitype":roitype,"scanid":scanid,
              "stimfreq":stimfreq,"stimid":stimid,"delay":delay,"peak":peak}
    return(record)

    
# open the csv file containing the list of roi timeseries data
datapath = '/home/anup/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/' 
fname = 'iglusnfr_response_traces_all.txt'

batchfname = datapath + fname
# ----------------
with open(batchfname,'r') as csvfile:
    batchcsv = pd.read_csv(csvfile)
df = pd.DataFrame()

print("Total number of files:\t",len(batchcsv))

for i in np.arange(0,len(batchcsv)):
# for i in np.arange(0,100): 
    fname = batchcsv['filename'][i] # complete filename with path
    fpath = re.search('^.+/+',fname)[0][0:-1] # path to filename
    fname0ext = re.search('[^/]+.csv$',fname)[0][0:-4] # filename without extension
    fileid = re.search("^.*?(?=(_delay))",fname0ext)[0]
    record = extract_info_from_filename(fname0ext)
    df = df.append(record,ignore_index = True)
    # dat = np.loadtxt(fname,delimiter=",")
    # traces[fileid] = dat
# ------------------
# find trial number per roiname,stimfreq & stimid
df.sort_values(by=["roiname","stimfreq","stimid","imageid","scanid"],ascending=True,inplace=True)
df["ntrials"] = df.groupby(["roiname","stimfreq","stimid"])["scanid"].transform("count")
df["trialid"] = df.groupby(["roiname","stimfreq","stimid"]).apply(
    lambda x: pd.DataFrame({"trialid": np.arange(1,x["ntrials"].max()+1)},
                           index=x.index))
df.reset_index(inplace=True,drop=True)
# -----------------
# convert some columns from float to int dtype
intcolumns = ["imageid","roicount","stimfreq","stimid","scanid","ntrials","trialid","ntrials"]
for column in intcolumns:
     df[column] = df[column].astype(int)
# -----------------
# find mean and standard deviation of noise peak across trials for each roiname
df[["noise_avg","noise_std","threshold"]] = df.groupby(["roiname"]).apply(
    # df[["noise_avg","noise_std","threshold"]] = df.groupby(["roiname","stimfreq"]).apply(
# df[["noise_avg","noise_std","threshold","threshold2","threshold3"]] = df.groupby(["roiname"]).apply(
    lambda x: pd.DataFrame({"noise_avg" : np.repeat(x[x["stimid"]==0]["peak"].mean(),len(x)),
               "noise_std" : np.repeat(x[x["stimid"]==0]["peak"].std(),len(x)),
               "threshold" : np.repeat(x[x["stimid"]==0]["peak"].mean() + (4*x[x["stimid"]==0]["peak"].std()),len(x))
    },index=x.index))
df.reset_index(inplace=True,drop=True)
# classify each response as success/failure if amplitude is above or equal /below noise_avg + (2*noise_std)
# failure of release if the observed peak fluorescence is less than twice the standard deviation of the optical noise
df[["success"]] = df.groupby(["roiname","stimfreq","trialid","stimid"]).apply(
    lambda x: pd.DataFrame({"success" : np.repeat(x["peak"] >= x["threshold"],len(x))
                            },index = x.index))
df.reset_index(inplace=True,drop=True)
# -------------------------
df.sort_values(by=["roiname","stimfreq","stimid","imageid","scanid","trialid"],ascending=True,inplace=True)
df.reset_index(inplace=True,drop=True)
df.to_csv(os.path.join(datapath,"".join(("test.csv"))),index=False)
df.to_csv(os.path.join(datapath,"iglusnfr_ca1_data_success_noise_mean_plus_4noise_std.csv"),index=False)
print(df.columns)
# -----------------

