import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import os
import re
import olympus_image_file as oif

ophysdatapath="/Volumes/GoogleDrive/Shared drives/Beique Lab DATA/Imaging Data/Olympus 2P/Anup/"
masterdfpath = "/Users/macbookair/goofy/data/beiquelab/pfc_clusterd_inputs"
masterdf = "pfc_clustered_glu_uncaging.xlsx"

masterdf = pd.read_excel(os.path.join(masterdfpath,masterdf),header=0,use_cols=10)
masterdf["datefolder"] = masterdf["datefolder"].astype(int)
masterdf["date"] = pd.to_datetime(masterdf["datefolder"],format="%Y%m%d")

for row in range(0,masterdf.shape[0]):
    datefolder = str(masterdf.loc[row,"datefolder"])
    zstack = str(masterdf.loc[row,"zstack"])
    zstackfolder = str(masterdf.loc[row,"zstackfolder"])
    cellfolder = str(masterdf.loc[row,"cellfolder_ophys"])
    imagefile = str(masterdf.loc[row,"imagefile"])
    ophysfile = os.path.join(ophysdatapath,datefolder,cellfolder,imagefile)
    zstackfile = os.path.join(ophysdatapath,datefolder,zstackfolder,zstack)
    print(ophysfile)
    print(zstackfile)
    oi = oif.OlympusImageClass(ophysfile)
    # oz = oif.OlympusImageClass(zstackfile)
    oi.show_metadata()
    oi.display_image_with_markers()
    input()
