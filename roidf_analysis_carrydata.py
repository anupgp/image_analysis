import numpy as np
import pandas as pd
import math
import seaborn as sns
import re
import os
from scipy import stats as scipystats
from scipy import signal
from timeseries_template_match_algorithm import template_match
import time

# ----------------
import matplotlib
matplotlib.use("gtk3agg")
print(matplotlib.get_backend())

from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager
sns.set()
sns.set_style("white")
sns.set_style("ticks")
# ---------------


def format_plot(fh,ah,xlab="",ylab="",title=""):
    font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
    fontprop = font_manager.FontProperties(fname=font_path,size=18)
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

def add_stimulus_markers(df,xlabel,stimoffset=0,stimfreq=0,nstims=0,prestimoffset=0):
    # create stimulus markers
    if ((stimoffset > 0) and (stimfreq > 0) and (nstims > 0)):
        stims = np.zeros(np.shape(df[xlabel]))
        # stimpos = stimoffset + (np.arange(0,ntsims,1)*(1/stimfreq))
        stimpositions = [np.where(df[xlabel]>=item)[0][0] for item in stimoffset + (np.arange(0,nstims,1)*(1/stimfreq))]
        if (prestimoffset != 0):
            # insert prestim position to the begining of stimulus positions
            prestimpos = np.where(df[xlabel] >= (df[xlabel][stimpositions[0]]-abs(prestimoffset)))[0][0]
            stimpositions.insert(0,prestimpos)
            # -------------------
        stims[stimpositions] = 100
        # add marker as a separate column of the df
        df["stims"] = stims
        # print("Success: Added stimulus markers to the dataframe")
        # ----------------------
        

def plot_trials_with_avg(df,xprefix="time",groupprefixes=["spine","dendrite","stims"],stimprefix="stims",title=""):
    # plot all the trials of a given [project_cell_exp] combination with the avg
    # trials are grouped and plotted according to the Y labels
    # get all the columns corresponding to each ylabel for grouping
    groups = {groupprefix: [column for column in list(df.columns) if groupprefix in column] for groupprefix in list(set(groupprefixes))}
    groupkeys = list(groups.keys())
    print("Group keys: ",groupkeys)
    fh,ah = plt.subplots(nrows=len(groupkeys),ncols=1,sharex=True)
    fh.subplots_adjust(hspace=0.5)
    fh.suptitle(title)
    for i in range(len(groupkeys)):
        for j in range(len(groups[groupkeys[i]])):
            ycolumn = groups[groupkeys[i]][j]
            id = re.search("(?:^.*[^0-9]+)([0-9]+)",ycolumn).groups(2)[0]
            xcolumn = "".join((xprefix,id))
            ah[i].plot(df[xcolumn], df[ycolumn],color="gray")
            if (len(stimprefix) >0):
                stimcolumn = "".join((stimprefix,id))
                ah[i].plot(df[xcolumn], df[stimcolumn],color="red")
            ah[i].set_title(groupkeys[i])
            ah[i].plot(df[xcolumn], df[groups[groupkeys[i]]].mean(axis=1),color="black")
    plt.show()
    return()
    # -------------------------------
       
# Set some pandas options
pd.set_option('display.notebook_repr_html', False)
# pd.set_option('display.max_columns', 10)
# pd.set_option('display.max_rows', 10)

# open the csv file containing the main dataframe
datapath = "/home/anup/gdrive-beiquelab/CURRENT LAB MEMBERS/Anup Pillai/iglusnfr_carrydata"
projectdir="trains"
filenames = [entry for entry in os.listdir(os.path.join(datapath,projectdir)) if re.search(".*.csv",entry)]
# filename decompopose structure: project_cell_exp_trial.csv
# get unique projects
projects = list(set([re.search("([^\_]+)(?:.*)",entry).group(1) for entry in filenames]))
print("Unique projects:\t",projects)
# get unique cells
cells = list(set([re.search("(?:[^\_]+)(?:\_)([^\_]+)(?:.*)",entry).group(1) for entry in filenames]))
# sort the list of cells
cells.sort()
print("Unique cells:\t",cells)
# get unique exps
exps = list(set([re.search("(?:[^\_]+)(?:\_)(?:[^\_]+)(?:\_)([^\_]+)(?:.*)",entry).group(1) for entry in filenames]))
# sort exps
exps.sort()
print("Unique experiments:\t",exps)
# load the template
fname_template = 'iglusnfr_ca1_success_avg.csv'
template = np.loadtxt(os.path.join(datapath,projectdir,"template",fname_template),delimiter=',')
# crop the template trace so that there is no delay
tt = template[2:-1,0]
yy = template[2:-1,1]
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
# yy = yy.reshape((len(yy),1))
# tt = tt.reshape((len(tt),1))
# create template dataframe
template = pd.DataFrame()
template["time"] = tt
template["y"] = yy
# ----------------
stimoffset = 0.5
nstims = 10
dfall = pd.DataFrame()          # DataFrame that has all the trials and rois for one experiment
resdfall = pd.DataFrame()       # DataFrame containing all the extracted data
roitypes = ["spine","dendrite"]
for i in range(0,len(projects)):
    for j in range(0,len(cells)):
        for k in range(0,len(exps)):
            # get frequency of stimulation
            stimfreq = int(re.search("([0-9]+)(?:.*)",exps[k]).groups(1)[0])
            print("stim frequency:\t",stimfreq)
            # input()
            # find all trials for a particular set of: [project_cell_exp]
            pattern = "".join((projects[i],"_",cells[j],"_",exps[k],"_"))
            trials = [entry for entry in filenames if re.search(pattern,entry)]
            trials.sort()
            # print("Trials:\t",trials)
            for l in range(0,len(trials)):
                fname = os.path.join(datapath,projectdir,trials[l])
                print(fname)
                with open(fname,'r') as csvfile:
                    readcount  = 1
                    while True:
                        try:
                            df = pd.read_csv(csvfile,engine="c")
                        except:
                            readcount = readcount + 1
                            print(" {} attempt to read file {} again....".format(readcount,fname))
                            time.sleep(5)
                            continue
                        break
                    add_stimulus_markers(df,xlabel="time",stimoffset=stimoffset,stimfreq=stimfreq,nstims=nstims,prestimoffset=0.2)
                    # remove any numbers from the end of column names
                    columnlabels = [re.search("(^.*[^0-9]+)(?:.*)",column).group(1) for column in list(df.columns)]
                    df.columns = columnlabels
                    figtitle = "".join((pattern,"trial",str(l)))
                    resdf = template_match(df,template,roilabels=roitypes,tmaxlag = 0.01,figtitle=figtitle,figpath="")
                    resdf["itrial"] = int(l)
                    resdfall = resdfall.append(resdf,ignore_index=True)
                    newcolumnlabels = ["".join((label,str(l))) for label in columnlabels]
                    dfall[newcolumnlabels] = df[columnlabels]
                    # print(resdf)
                    # ---------------------
            # plot all trials of all rois
            # print(resdfall)
            # input()
            # plot_trials_with_avg(dfall,xprefix="time",groupprefixes=roitypes,stimprefix="stims",title="")
            # ---------------------
        # ---------------
    # ---------------
# ----------------
# save dataframe
roidfname = "".join(("iglusnfr_ca1_carry_data_","trains_","v1.csv"))
roidfname_withpath = os.path.join(datapath,roidfname)
resdfall.to_csv(roidfname_withpath,index=False)
