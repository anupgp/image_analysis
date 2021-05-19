import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import os
import sys
import re
import olympus_image_file as oif
sys.path.append("/home/anup/goofy/codes/ephys_analysis/")
import ephys_functions as ephysfuns

path_ophysdata = "/home/anup/gdrive-beiquelabdata/Imaging Data/Olympus 2P/Anup/"
path_ephysdata="/home/anup/gdrive-beiquelabdata/Ephys Data/Olympus 2P/Anup/" # common to all ephys data
path_ms="/home/anup/goofy/data/beiquelab/hc_ca1_glu_uncage_spine_single_epsp/" # local to the ephys project: Ca1 single spine
name_ms = "hc_ca1_glu_uncage_spine_single_mastersheet.xlsx"           # local to the ephys project

# specify columns to load
loadcolumns1 = ["expdate","dob","sex","animal","strain","region","area","side","group","neuronid","dendriteid","spineid"]
loadcolumns2 = ["unselectfile","badsweeps","ephysfile","clamp","stimpower","isi","ophysfile"]
loadcolumns = loadcolumns1 + loadcolumns2
masterdf = pd.read_excel(os.path.join(path_ms,name_ms),header=0,usecols=loadcolumns,index_col=None,sheet_name=0)
masterdf = masterdf.dropna(how='all') # drop rows with all empty columns
masterdf = masterdf.reset_index(drop=True) # don't increment index for empty rows
# remove files that are marked to unselect from analysis
masterdf = masterdf[masterdf["unselectfile"]!=1]
# create a unique spine name
masterdf["spinename"] = ephysfuns.combine_columns(masterdf,['expdate','group','neuronid','dendriteid','spineid'])
spines = masterdf["spinename"].unique()
print(spines)
print(masterdf)
for ispine in range(0,len(spines)):
    print("spine: {}".format(spines[ispine]))
    dfspine = masterdf.loc[masterdf["spinename"] == spines[ispine]]
    dfspine = dfspine.reset_index()
    print(dfspine)
    input()
    templatefiles_cc =  list(dfspine[dfspine["clamp"] == "cc"]["ephysfile"])
    # for itfile in range(len(templatefiles_cc)):
    for itfile in range(0,1):
        tfile = templatefiles_cc[itfile]
        neuronid = list(dfspine.loc[dfspine["ephysfile"] == tfile,"neuronid"].astype(int).astype(str))[0]
        ophysfile = dfspine.loc[dfspine["ephysfile"] == tfile,"ophysfile"].values[0]
        expdate = list(dfspine.loc[dfspine["ephysfile"] == tfile,"expdate"].astype(int).astype(str))[0]
        ephysname = os.path.join(path_ephysdata,expdate,"".join(("C",neuronid)),tfile)
        ophysname = os.path.join(path_ophysdata,expdate,"".join(("C",neuronid)),ophysfile)
        print(ephysname)
        print(ophysname)
        oi = oif.OlympusImageClass(ophysname)
        oi.show_metadata()
        oi.display_image_with_markers()
        # oz = oif.OlympusImageClass(zstackfile)
#     input()
